# rag-service/app/models/document.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class DocumentMetadata(BaseModel):
    source: str
    filename: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    processed_date: datetime
    chunk_id: Optional[int] = None
    total_chunks: Optional[int] = None

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(default=5, ge=1, le=50)
    filter_metadata: Optional[Dict[str, Any]] = None
    include_metadata: bool = True

class SearchResult(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any]
    score: float = Field(..., ge=0.0, le=1.0)

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_found: int
    processing_time: Optional[float] = None

class DocumentUploadResponse(BaseModel):
    message: str
    files: List[Dict[str, Any]]
    processing_status: str  # "completed", "in_progress", "failed"
    
class URLRequest(BaseModel):
    url: str = Field(..., regex=r'^https?://.+')
    title: Optional[str] = None
    
class DocumentStatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    sources: List[str]
    collection_name: str
    embedding_model: str