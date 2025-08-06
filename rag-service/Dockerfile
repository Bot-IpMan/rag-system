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
    && rm -rf /var/lib/apt/lists/*

# Копіювання requirements та встановлення Python залежностей
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Копіювання коду додатку
COPY app/ ./app/

# Створення директорій для даних
RUN mkdir -p /app/data/uploads /app/data/processed /app/vector_db

# Встановлення змінних середовища
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV HF_HUB_CACHE=/app/.cache/huggingface

# Встановлення прав доступу
RUN chmod -R 755 /app

# Відкриття порту
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Команда запуску
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]