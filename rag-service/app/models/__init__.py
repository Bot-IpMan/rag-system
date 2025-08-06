# rag-service/app/__init__.py
"""RAG Service Application Package"""

# rag-service/app/core/__init__.py
"""Core RAG functionality"""

# rag-service/app/models/__init__.py
"""Pydantic models"""

# rag-service/app/core/document_processor.py (завершення файлу)
import os
import requests
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import mimetypes

# Бібліотеки для обробки документів
from bs4 import BeautifulSoup
import PyPDF2
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

from markdown import markdown
import json
import csv
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Клас для обробки різних форматів документів"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        self.supported_formats = {
            '.pdf': self._process_pdf,
            '.txt': self._process_txt,
            '.md': self._process_markdown,
            '.html': self._process_html,
            '.htm': self._process_html,
            '.csv': self._process_csv,
            '.xlsx': self._process_excel,
            '.xls': self._process_excel,
            '.json': self._process_json
        }
        
        if DOCX_AVAILABLE:
            self.supported_formats['.docx'] = self._process_docx
    
    def _process_pdf(self, file_path: str) -> str:
        """Обробка PDF файлів"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Помилка обробки PDF {file_path}: {e}")
        return text
    
    def _process_txt(self, file_path: str) -> str:
        """Обробка текстових файлів"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='cp1251') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Помилка обробки TXT {file_path}: {e}")
                return ""
        except Exception as e:
            logger.error(f"Помилка обробки TXT {file_path}: {e}")
            return ""
    
    def _process_markdown(self, file_path: str) -> str:
        """Обробка Markdown файлів"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                md_content = file.read()
                html = markdown(md_content)
                soup = BeautifulSoup(html, 'html.parser')
                return soup.get_text()
        except Exception as e:
            logger.error(f"Помилка обробки MD {file_path}: {e}")
            return ""
    
    def _process_html(self, file_path: str) -> str:
        """Обробка HTML файлів"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                return soup.get_text()
        except Exception as e:
            logger.error(f"Помилка обробки HTML {file_path}: {e}")
            return ""
    
    def _process_csv(self, file_path: str) -> str:
        """Обробка CSV файлів"""
        try:
            df = pd.read_csv(file_path)
            text = f"CSV файл: {file_path}\n"
            text += f"Кількість записів: {len(df)}\n"
            text += f"Колонки: {', '.join(df.columns)}\n\n"
            
            text += "Опис даних:\n"
            text += df.describe(include='all').to_string()
            text += "\n\nПерші 10 записів:\n"
            text += df.head(10).to_string()
            
            return text
        except Exception as e:
            logger.error(f"Помилка обробки CSV {file_path}: {e}")
            return ""
    
    def _process_excel(self, file_path: str) -> str:
        """Обробка Excel файлів"""
        try:
            xl_file = pd.ExcelFile(file_path)
            text = f"Excel файл: {file_path}\n"
            text += f"Аркуші: {', '.join(xl_file.sheet_names)}\n\n"
            
            for sheet_name in xl_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                text += f"\nАркуш '{sheet_name}':\n"
                text += f"Кількість записів: {len(df)}\n"
                text += f"Колонки: {', '.join(df.columns)}\n"
                text += df.head(5).to_string()
                text += "\n" + "-"*50 + "\n"
            
            return text
        except Exception as e:
            logger.error(f"Помилка обробки Excel {file_path}: {e}")
            return ""
    
    def _process_docx(self, file_path: str) -> str:
        """Обробка Word документів"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Помилка обробки DOCX {file_path}: {e}")
            return ""
    
    def _process_json(self, file_path: str) -> str:
        """Обробка JSON файлів"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Помилка обробки JSON {file_path}: {e}")
            return ""
    
    def process_url(self, url: str) -> Dict[str, Any]:
        """Обробка веб-посилань"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.find('title')
            title = title.text.strip() if title else "Без назви"
            
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            
            return {
                'title': title,
                'text': text,
                'url': url,
                'processed_date': datetime.now().isoformat(),
                'type': 'url'
            }
            
        except Exception as e:
            logger.error(f"Помилка обробки URL {url}: {e}")
            return {
                'title': f"Помилка: {url}",
                'text': f"Не вдалося завантажити контент: {str(e)}",
                'url': url,
                'processed_date': datetime.now().isoformat(),
                'type': 'url_error'
            }
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Розбиття тексту на чанки"""
        if not text.strip():
            return []
        
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata.update({
                'chunk_id': i // (self.chunk_size - self.chunk_overlap),
                'chunk_size': len(chunk_words),
                'processed_date': datetime.now().isoformat()
            })
            
            chunks.append({
                'text': chunk_text,
                'metadata': chunk_metadata
            })
        
        return chunks
    
    def process_file(self, file_path: str) -> List[Dict]:
        """Обробка одного файлу"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension not in self.supported_formats:
            logger.warning(f"Непідтримуваний формат: {extension}")
            return []
        
        text = self.supported_formats[extension](str(file_path))
        
        if not text.strip():
            return []
        
        metadata = {
            'source': str(file_path),
            'filename': file_path.name,
            'extension': extension,
            'file_size': file_path.stat().st_size,
            'modified_date': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
        
        return self.chunk_text(text, metadata)