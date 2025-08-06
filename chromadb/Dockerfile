FROM python:3.11-slim

WORKDIR /chroma

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "chromadb==0.4.18" "chroma-hnswlib==0.7.3" "numpy<2" "uvicorn[standard]"

EXPOSE 8000

CMD ["uvicorn", "chromadb.app:app", "--host", "0.0.0.0", "--port", "8000"]
