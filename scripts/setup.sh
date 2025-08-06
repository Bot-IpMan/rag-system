#!/bin/bash

# scripts/setup.sh - Скрипт для налаштування та запуску RAG системи

set -e

echo "🚀 Налаштування RAG системи..."

# Створення необхідних директорій
echo "📁 Створення директорій..."
mkdir -p data/uploads
mkdir -p data/processed
mkdir -p data/vector_db
mkdir -p ~/.cache/huggingface

# Запуск docker-compose
echo "🐳 Запуск контейнерів..."
docker compose down --remove-orphans
docker compose up --build -d

echo "⏳ Очікування запуску сервісів..."
sleep 30

# Перевірка статусу сервісів
echo "🔍 Перевірка статусу сервісів..."

# Функція для перевірки здоров'я сервісу
check_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✅ $name готовий!"
            return 0
        fi
        echo "⏳ Очікування $name (спроба $attempt/$max_attempts)..."
        sleep 10
        attempt=$((attempt + 1))
    done
    
    echo "❌ $name не готовий після $max_attempts спроб"
    return 1
}

# Перевірка сервісів
check_service "http://localhost:8001/api/v1/heartbeat" "ChromaDB"
check_service "http://localhost:8002/health" "RAG Service"
check_service "http://localhost:11434/api/tags" "Ollama"

# Завантаження моделі Ollama
echo "📦 Завантаження моделі llama3.1:8b..."
docker exec -it rag-system-ollama-1 ollama pull llama3.1:8b

check_service "http://localhost:8003/health" "LLM Service"
check_service "http://localhost:3000" "Frontend"

echo ""
echo "🎉 RAG система успішно запущена!"
echo ""
echo "📍 Доступні сервіси:"
echo "  • Frontend:    http://localhost:3000"
echo "  • RAG API:     http://localhost:8002"
echo "  • LLM API:     http://localhost:8003"
echo "  • ChromaDB:    http://localhost:8001"
echo "  • Ollama:      http://localhost:11434"
echo ""
echo "🔧 Для перегляду логів: docker compose logs -f"
echo "🛑 Для зупинки: docker compose down"