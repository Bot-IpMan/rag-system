# rag-service/app/main.py
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from typing import List, Optional
import asyncio
import logging
from pathlib import Path

from .core.rag_engine import RAGEngine
from .core.document_processor import DocumentProcessor
from .models.document import DocumentMetadata, SearchRequest, SearchResponse, DocumentUploadResponse
from .config import settings

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальні змінні для RAG компонентів
rag_engine: Optional[RAGEngine] = None
document_processor: Optional[DocumentProcessor] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager для FastAPI"""
    global rag_engine, document_processor
    
    logger.info("Ініціалізація RAG системи...")
    
    try:
        # Ініціалізація компонентів
        document_processor = DocumentProcessor(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        rag_engine = RAGEngine(
            chroma_host=settings.CHROMA_HOST,
            chroma_port=settings.CHROMA_PORT,
            embedding_model=settings.EMBEDDING_MODEL,
            collection_name=settings.COLLECTION_NAME
        )
        
        await rag_engine.initialize()
        logger.info("RAG система успішно ініціалізована")
        
        yield
        
    except Exception as e:
        logger.error(f"Помилка ініціалізації: {e}")
        raise
    finally:
        # Cleanup
        if rag_engine:
            await rag_engine.close()
        logger.info("RAG система зупинена")

app = FastAPI(
    title="RAG Service API",
    description="API для RAG системи з підтримкою різних форматів документів",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Перевірка здоров'я сервісу"""
    global rag_engine
    
    if not rag_engine or not rag_engine.is_ready():
        raise HTTPException(status_code=503, detail="RAG engine не готовий")
    
    stats = await rag_engine.get_collection_stats()
    return {
        "status": "healthy",
        "documents_count": stats.get("count", 0),
        "collection_name": settings.COLLECTION_NAME
    }

@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """Завантаження документів"""
    global rag_engine, document_processor
    
    if not rag_engine or not document_processor:
        raise HTTPException(status_code=503, detail="Сервіс не готовий")
    
    uploaded_files = []
    
    for file in files:
        try:
            # Збереження файлу
            file_path = Path(settings.UPLOAD_DIR) / file.filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            uploaded_files.append({
                "filename": file.filename,
                "size": len(content),
                "path": str(file_path)
            })
            
            # Обробка в фоні
            background_tasks.add_task(process_uploaded_file, str(file_path))
            
        except Exception as e:
            logger.error(f"Помилка завантаження файлу {file.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Помилка завантаження: {str(e)}")
    
    return DocumentUploadResponse(
        message=f"Завантажено {len(uploaded_files)} файлів",
        files=uploaded_files,
        processing_status="in_progress"
    )

async def process_uploaded_file(file_path: str):
    """Фонова обробка завантаженого файлу"""
    global rag_engine, document_processor
    
    try:
        logger.info(f"Обробка файлу: {file_path}")
        
        # Обробка документу
        chunks = document_processor.process_file(file_path)
        
        if chunks:
            # Додавання до векторної бази
            await rag_engine.add_documents(chunks)
            logger.info(f"Додано {len(chunks)} чанків з файлу {file_path}")
        else:
            logger.warning(f"Не вдалося витягти контент з файлу {file_path}")
            
    except Exception as e:
        logger.error(f"Помилка обробки файлу {file_path}: {e}")

@app.post("/documents/url")
async def add_url(
    background_tasks: BackgroundTasks,
    url: str,
    title: Optional[str] = None
):
    """Додавання контенту з URL"""
    global rag_engine, document_processor
    
    if not rag_engine or not document_processor:
        raise HTTPException(status_code=503, detail="Сервіс не готовий")
    
    try:
        # Обробка в фоні
        background_tasks.add_task(process_url, url, title)
        
        return {
            "message": f"URL {url} додано до черги обробки",
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Помилка додавання URL {url}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_url(url: str, title: Optional[str] = None):
    """Фонова обробка URL"""
    global rag_engine, document_processor
    
    try:
        logger.info(f"Обробка URL: {url}")
        
        # Обробка URL
        url_data = document_processor.process_url(url)
        
        # Створення чанків
        chunks = document_processor.chunk_text(
            url_data['text'],
            metadata={
                'source': url,
                'title': title or url_data['title'],
                'type': 'url',
                'processed_date': url_data['processed_date']
            }
        )
        
        if chunks:
            await rag_engine.add_documents(chunks)
            logger.info(f"Додано {len(chunks)} чанків з URL {url}")
        else:
            logger.warning(f"Не вдалося витягти контент з URL {url}")
            
    except Exception as e:
        logger.error(f"Помилка обробки URL {url}: {e}")

@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Семантичний пошук документів"""
    global rag_engine
    
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine не готовий")
    
    try:
        results = await rag_engine.search(
            query=request.query,
            n_results=request.limit,
            filter_metadata=request.filter_metadata
        )
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_found=len(results)
        )
        
    except Exception as e:
        logger.error(f"Помилка пошуку: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/stats")
async def get_document_stats():
    """Статистика документів у базі"""
    global rag_engine
    
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine не готовий")
    
    try:
        stats = await rag_engine.get_collection_stats()
        return stats
    except Exception as e:
        logger.error(f"Помилка отримання статистики: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/clear")
async def clear_documents():
    """Очищення всіх документів"""
    global rag_engine
    
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine не готовий")
    
    try:
        await rag_engine.clear_collection()
        return {"message": "Всі документи видалено"}
    except Exception as e:
        logger.error(f"Помилка очищення колекції: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/sources")
async def get_document_sources():
    """Список джерел документів"""
    global rag_engine
    
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine не готовий")
    
    try:
        sources = await rag_engine.get_sources()
        return {"sources": sources}
    except Exception as e:
        logger.error(f"Помилка отримання джерел: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )