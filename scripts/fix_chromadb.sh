#!/bin/bash

# fix_chromadb.sh - Швидке виправлення проблем з ChromaDB

echo "🔧 Виправлення проблеми з ChromaDB..."

# Зупинка поточних контейнерів
echo "🛑 Зупинка контейнерів..."
docker compose down

# Очищення volumes (буде видалено дані!)
echo "🧹 Очищення volumes..."
docker volume rm rag-system_chroma_data 2>/dev/null || true
docker volume rm rag-system_ollama_data 2>/dev/null || true
docker volume rm rag-system_redis_data 2>/dev/null || true

# Очищення системи Docker
echo "🗑️  Очищення Docker системи..."
docker system prune -f

# Створення директорій
echo "📁 Створення директорій..."
mkdir -p data/uploads data/processed data/vector_db

# Запуск тільки ChromaDB для тестування
echo "🚀 Запуск ChromaDB..."
docker compose up -d chromadb

# Очікування запуску ChromaDB
echo "⏳ Очікування ChromaDB..."
sleep 30

# Перевірка статусу
echo "🔍 Перевірка статусу ChromaDB..."
for i in {1..10}; do
    if curl -f -s "http://localhost:8001/api/v1/heartbeat" > /dev/null; then
        echo "✅ ChromaDB працює!"
        break
    else
        echo "⏳ Спроба $i/10..."
        sleep 10
    fi
done

# Перевірка логів ChromaDB
echo "📋 Логи ChromaDB:"
docker compose logs chromadb --tail=10

# Запуск Redis
echo "🚀 Запуск Redis..."
docker compose up -d redis
sleep 5

# Запуск Ollama
echo "🚀 Запуск Ollama..."
docker compose up -d ollama
sleep 15

# Перевірка Ollama
echo "🔍 Перевірка Ollama..."
for i in {1..10}; do
    if curl -f -s "http://localhost:11434/api/tags" > /dev/null; then
        echo "✅ Ollama працює!"
        break
    else
        echo "⏳ Спроба $i/10..."
        sleep 10
    fi
done

# Запуск RAG Service
echo "🚀 Запуск RAG Service..."
docker compose up -d rag-service
sleep 20

# Перевірка RAG Service
echo "🔍 Перевірка RAG Service..."
for i in {1..10}; do
    if curl -f -s "http://localhost:8002/health" > /dev/null; then
        echo "✅ RAG Service працює!"
        break
    else
        echo "⏳ Спроба $i/10..."
        sleep 10
    fi
done

# Запуск LLM Service
echo "🚀 Запуск LLM Service..."
docker compose up -d llm-service
sleep 10

# Запуск Frontend
echo "🚀 Запуск Frontend..."
docker compose up -d frontend

# Завантаження моделі Ollama
echo "📦 Завантаження моделі llama3.1:8b..."
echo "   (Це може зайняти кілька хвилин...)"
docker exec rag-system-ollama-1 ollama pull llama3.1:8b

echo ""
echo "🎉 Система запущена!"
echo "📊 Статус сервісів:"
docker compose ps

echo ""
echo "🌐 Доступні URL:"
echo "  • Frontend:    http://localhost:3000"
echo "  • RAG API:     http://localhost:8002"
echo "  • LLM API:     http://localhost:8003"
echo "  • ChromaDB:    http://localhost:8001"
echo "  • Ollama:      http://localhost:11434"

echo ""
echo "🔍 Для діагностики запустіть: python3 scripts/diagnose.py"