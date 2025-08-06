# rag-service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Встановлення системних залежностей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Копіювання requirements
COPY requirements.txt .

# Встановлення Python залежностей
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання коду додатку
COPY app/ ./app/

# Створення директорій для даних
RUN mkdir -p /app/data/uploads /app/data/processed /app/vector_db

# Встановлення змінних середовища
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Відкриття порту
EXPOSE 8000

# Команда запуску
CMD ["python", "-m", "app.main"]