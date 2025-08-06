from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
from typing import Dict, Any
import logging
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Service", description="Інтеграція з Ollama та RAG системою")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    use_rag: bool = True
    model: str = "llama3.1:8b"
    max_tokens: int = 1000

class ChatResponse(BaseModel):
    response: str
    sources: list = []
    model_used: str = ""

OLLAMA_BASE_URL = "http://ollama:11434"
RAG_SERVICE_URL = "http://rag-service:8000"

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "llm-service"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        context = ""
        sources = []
        
        if request.use_rag:
            # Пошук в RAG системі
            async with httpx.AsyncClient() as client:
                rag_response = await client.post(
                    f"{RAG_SERVICE_URL}/search",
                    json={
                        "query": request.message,
                        "limit": 3
                    }
                )
                
                if rag_response.status_code == 200:
                    rag_data = rag_response.json()
                    
                    for result in rag_data["results"]:
                        context += f"\n{result['text']}\n"
                        sources.append({
                            "source": result["metadata"].get("source", ""),
                            "score": result["score"]
                        })
        
        # Формування промпта
        if context:
            prompt = f"""
            Контекст з бази знань:
            {context}
            
            Питання користувача: {request.message}
            
            Дайте відповідь на основі наданого контексту. Якщо в контексті немає релевантної інформації, скажіть про це.
            """
        else:
            prompt = request.message
        
        # Запит до Ollama
        async with httpx.AsyncClient(timeout=30.0) as client:
            ollama_response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": request.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": request.max_tokens
                    }
                }
            )
            
            if ollama_response.status_code == 200:
                ollama_data = ollama_response.json()
                response_text = ollama_data.get("response", "")
                
                return ChatResponse(
                    response=response_text,
                    sources=sources,
                    model_used=request.model
                )
            else:
                raise HTTPException(status_code=500, detail="Помилка Ollama API")
                
    except Exception as e:
        logger.error(f"Помилка чату: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def get_available_models():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                return response.json()
            else:
                return {"models": []}
    except Exception as e:
        logger.error(f"Помилка отримання моделей: {e}")
        return {"models": []}
