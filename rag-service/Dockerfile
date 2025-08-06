# rag-service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Встановлення системних залежностей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    pkg-config \
    libpoppler-cpp-dev \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Створення користувача (безпека)
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Встановлення PATH для користувача
ENV PATH="/home/app/.local/bin:${PATH}"

# Копіювання та встановлення Python залежностей
COPY requirements.txt .
RUN pip install --user --no-cache-dir --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

# Копіювання коду додатку
COPY --chown=app:app app/ ./app/

# Створення директорій для даних
USER root
RUN mkdir -p /app/data/uploads /app/data/processed /app/vector_db && \
    chown -R app:app /app/data /app/vector_db
USER app

# Встановлення змінних середовища
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV HF_HUB_CACHE=/home/app/.cache/huggingface

# Попереднє завантаження моделі ембедінгів (опціонально)
RUN python -c "
from sentence_transformers import SentenceTransformer
import os
model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
print(f'Завантаження моделі: {model_name}')
SentenceTransformer(model_name)
print('Модель завантажена успішно!')
"

# Відкриття порту
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Команда запуску
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]