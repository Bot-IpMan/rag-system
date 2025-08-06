# RAG System

Скелет системи Retrieval-Augmented Generation (RAG), що дозволяє завантажувати документи, індексувати їх у векторній базі Chroma та виконувати пошук із подальшим збагаченням відповідей за допомогою LLM.

## Архітектура

Проект складається з кількох сервісів, що запускаються через `docker compose`:

- **chromadb** – зберігає векторні подання документів.
- **rag-service** – FastAPI‑сервіс для обробки файлів та пошуку по базі.
- **ollama** – контейнер з локальною LLM‑моделлю.
- **llm-service** – проксі до Ollama та точка входу для генерації відповідей.
- **frontend** – React‑інтерфейс для завантаження документів і чату.
- **redis** – опційне кешування запитів.

## Вимоги

- Docker та Docker Compose
- Python 3.12 для локального запуску тестів

## Швидкий старт

```bash
# Клонування репозиторію
git clone <repo-url>
cd rag-system

# Запуск усіх сервісів
docker compose up --build
```

Після запуску сервіси доступні за адресами:

- RAG API: http://localhost:8002
- LLM API: http://localhost:8003
- Frontend: http://localhost:3000

Документи можна завантажувати через `POST /documents/upload`, а пошук здійснювати через `POST /search` у `rag-service`.

## Структура проекту

```
rag-system/
├── docker-compose.yml
├── requirements.txt
├── rag-service/
├── llm-service/
├── frontend/
├── scripts/
└── tests/
```

## Тестування

Виконайте тести перед створенням коміту:

```bash
pytest
```

## Ліцензія

Ліцензійний файл відсутній; використовуйте код на власний розсуд.

