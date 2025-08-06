# rag-service/app/core/rag_engine.py
import asyncio
import uuid
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

from ..models.document import SearchResult

logger = logging.getLogger(__name__)

class RAGEngine:
    """Основний клас для RAG операцій"""
    
    def __init__(
        self,
        chroma_host: str = "localhost",
        chroma_port: int = 8000,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        collection_name: str = "documents"
    ):
        self.chroma_host = chroma_host
        self.chroma_port = chroma_port
        self.embedding_model_name = embedding_model
        self.collection_name = collection_name
        
        self.client = None
        self.collection = None
        self.encoder = None
        self._ready = False
    
    async def initialize(self):
        """Ініціалізація RAG engine"""
        try:
            logger.info("Завантаження моделі ембедінгів...")
            # Завантаження в окремому потоці
            loop = asyncio.get_event_loop()
            self.encoder = await loop.run_in_executor(
                None, 
                SentenceTransformer, 
                self.embedding_model_name
            )
            
            logger.info("Підключення до ChromaDB...")
            self.client = chromadb.HttpClient(
                host=self.chroma_host,
                port=self.chroma_port,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Створення або отримання колекції
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            self._ready = True
            logger.info(f"RAG Engine ініціалізовано. Колекція: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Помилка ініціалізації RAG Engine: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Перевірка готовності engine"""
        return self._ready and self.client is not None and self.encoder is not None
    
    async def add_documents(self, chunks: List[Dict[str, Any]]):
        """Додавання документів до векторної бази"""
        if not self.is_ready():
            raise RuntimeError("RAG Engine не ініціалізовано")
        
        if not chunks:
            return
        
        try:
            texts = [chunk['text'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            ids = [str(uuid.uuid4()) for _ in chunks]
            
            logger.info(f"Генерація ембедінгів для {len(texts)} текстів...")
            
            # Генерація ембедінгів в окремому потоці
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self.encoder.encode(texts, show_progress_bar=False).tolist()
            )
            
            # Додавання до колекції
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Додано {len(chunks)} чанків до колекції {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Помилка додавання документів: {e}")
            raise
    
    async def search(
        self, 
        query: str, 
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[SearchResult]:
        """Семантичний пошук документів"""
        if not self.is_ready():
            raise RuntimeError("RAG Engine не ініціалізовано")
        
        try:
            logger.info(f"Пошук для запиту: '{query}'")
            
            # Генерація ембедінга запиту
            loop = asyncio.get_event_loop()
            query_embedding = await loop.run_in_executor(
                None,
                lambda: self.encoder.encode([query], show_progress_bar=False).tolist()
            )
            
            # Пошук у ChromaDB
            search_kwargs = {
                "query_embeddings": query_embedding,
                "n_results": n_results
            }
            
            if filter_metadata:
                search_kwargs["where"] = filter_metadata
            
            results = self.collection.query(**search_kwargs)
            
            # Форматування результатів
            search_results = []
            
            for i in range(len(results['documents'][0])):
                search_results.append(SearchResult(
                    text=results['documents'][0][i],
                    metadata=results['metadatas'][0][i],
                    score=1.0 - results['distances'][0][i],  # Конвертація distance в score
                    id=results['ids'][0][i] if 'ids' in results else str(i)
                ))
            
            logger.info(f"Знайдено {len(search_results)} результатів")
            return search_results
            
        except Exception as e:
            logger.error(f"Помилка пошуку: {e}")
            raise
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Статистика колекції"""
        if not self.is_ready():
            raise RuntimeError("RAG Engine не ініціалізовано")
        
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "count": count,
                "embedding_model": self.embedding_model_name
            }
        except Exception as e:
            logger.error(f"Помилка отримання статистики: {e}")
            raise
    
    async def clear_collection(self):
        """Очищення колекції"""
        if not self.is_ready():
            raise RuntimeError("RAG Engine не ініціалізовано")
        
        try:
            # Видалення колекції та створення нової
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Колекція {self.collection_name} очищена")
        except Exception as e:
            logger.error(f"Помилка очищення колекції: {e}")
            raise
    
    async def get_sources(self) -> List[str]:
        """Отримання унікальних джерел документів"""
        if not self.is_ready():
            raise RuntimeError("RAG Engine не ініціалізовано")
        
        try:
            # Отримання всіх метаданих
            results = self.collection.get()
            
            sources = set()
            for metadata in results.get('metadatas', []):
                if 'source' in metadata:
                    sources.add(metadata['source'])
            
            return sorted(list(sources))
            
        except Exception as e:
            logger.error(f"Помилка отримання джерел: {e}")
            raise
    
    async def delete_by_source(self, source: str):
        """Видалення документів за джерелом"""
        if not self.is_ready():
            raise RuntimeError("RAG Engine не ініціалізовано")
        
        try:
            # Пошук документів за джерелом
            results = self.collection.get(where={"source": source})
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"Видалено {len(results['ids'])} документів з джерела {source}")
            else:
                logger.info(f"Документів з джерела {source} не знайдено")
                
        except Exception as e:
            logger.error(f"Помилка видалення документів: {e}")
            raise
    
    async def get_document_by_id(self, doc_id: str) -> Optional[Dict]:
        """Отримання документа за ID"""
        if not self.is_ready():
            raise RuntimeError("RAG Engine не ініціалізовано")
        
        try:
            results = self.collection.get(ids=[doc_id])
            
            if results['ids']:
                return {
                    'id': results['ids'][0],
                    'text': results['documents'][0],
                    'metadata': results['metadatas'][0]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Помилка отримання документа {doc_id}: {e}")
            raise
    
    async def update_document(self, doc_id: str, text: str, metadata: Dict):
        """Оновлення документа"""
        if not self.is_ready():
            raise RuntimeError("RAG Engine не ініціалізовано")
        
        try:
            # Генерація нового ембедінга
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: self.encoder.encode([text], show_progress_bar=False).tolist()[0]
            )
            
            # Оновлення в колекції
            self.collection.update(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata]
            )
            
            logger.info(f"Документ {doc_id} оновлено")
            
        except Exception as e:
            logger.error(f"Помилка оновлення документа {doc_id}: {e}")
            raise
    
    async def close(self):
        """Закриття з'єднань"""
        try:
            # ChromaDB HTTP client не потребує явного закриття
            self.client = None
            self.collection = None
            self._ready = False
            logger.info("RAG Engine зупинено")
        except Exception as e:
            logger.error(f"Помилка закриття RAG Engine: {e}")


