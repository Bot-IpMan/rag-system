# rag-service/app/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Шлях до локальної бази ChromaDB
    CHROMA_DB_DIR: str = "/app/vector_db"

    # Модель для ембедінгів
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Настройки чанкування
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # База даних
    COLLECTION_NAME: str = "documents"
    
    # Директорії
    UPLOAD_DIR: str = "/app/data/uploads"
    PROCESSED_DIR: str = "/app/data/processed"
    
    # API настройки
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Логування
    LOG_LEVEL: str = "INFO"
    
    # Redis (опціонально)
    REDIS_URL: Optional[str] = "redis://redis:6379/0"
    
    # Максимальні розміри
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    MAX_CHUNK_SIZE: int = 2000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
