#!/bin/bash

# fix_dependencies.sh - Виправлення проблем з залежностями

set -e

echo "🔧 Виправлення проблем з залежностями..."

# 1. Створення резервних копій
echo "💾 Створення резервних копій..."
cp rag-service/Dockerfile rag-service/Dockerfile.backup || true
cp rag-service/requirements.txt rag-service/requirements.txt.backup || true

# 2. Виправлення requirements.txt
echo "📝 Оновлення requirements.txt..."
cat > rag-service/requirements.txt << 'EOF'
# rag-service/requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
pydantic-settings==2.1.0

# ChromaDB та векторні операції
chromadb==0.4.18

# Виправлені версії для сумісності
sentence-transformers==2.2.2
huggingface-hub==0.16.4
transformers==4.33.3
torch==2.0.1
numpy==1.24.4

# Обробка документів
PyPDF2==3.0.1
python-docx==1.1.0
beautifulsoup4==4.12.2
markdown==3.5.1
pandas==2.1.4
openpyxl==3.1.2

# HTTP запити
requests==2.31.0
httpx==0.25.2

# Логування та моніторинг
structlog==23.2.0

# Утіліти
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dateutil==2.8.2

# Для DOCX файлів
lxml==4.9.3
EOF

# 3. Виправлення Dockerfile
echo "🐳 Оновлення Dockerfile..."
cat > rag-service/Dockerfile << 'EOF'
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
EOF

# 4. Очищення Docker кешу
echo "🧹 Очищення Docker кешу..."
docker compose down || true
docker system prune -f
docker builder prune -f

# 5. Пересборка образів
echo "🔨 Пересборка образів..."
docker compose build --no-cache rag-service

echo ""
echo "✅ Виправлення завершено!"
echo ""
echo "🚀 Тепер можете запустити систему:"
echo "   docker compose up -d"
echo ""
echo "🔍 Або запустити діагностику:"
echo "   python3 scripts/diagnose.py"