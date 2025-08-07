"""Simple FastAPI server exposing retrieval functionality."""
from fastapi import FastAPI

# Correct import: retriever lives inside the `server` package
from server.retriever import fetch_relevant

app = FastAPI(title="RAG API Server")


@app.get("/health")
def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/query")
def query(payload: dict) -> dict:
    """Return documents relevant to the provided question.

    Parameters
    ----------
    payload: dict
        A JSON body containing a ``question`` field.
    """
    question = payload.get("question", "")
    docs = fetch_relevant(question)
    return {"answer": "", "context_docs": docs}
