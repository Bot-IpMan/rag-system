# RAG System Project Structure

```
rag-system/
├── docker-compose.yml
├── README.md
├── .env
├── .gitignore
├── requirements.txt
│
├── rag-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI додаток
│   │   ├── config.py               # Конфігурація
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── document.py         # Pydantic моделі
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── document_processor.py  # Обробка документів
│   │   │   ├── embeddings.py       # Векторизація
│   │   │   └── rag_engine.py       # Основна RAG логіка
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── documents.py    # API для документів
│   │   │   │   └── search.py       # API для пошуку
│   │   │   └── dependencies.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py
│
├── llm-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py                 # Ollama інтеграція
│       ├── config.py
│       └── models/
│           └── llm.py
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── src/
│   │   ├── App.js
│   │   ├── components/
│   │   │   ├── DocumentUpload.js
│   │   │   ├── SearchInterface.js
│   │   │   └── ChatInterface.js
│   │   └── services/
│   │       └── api.js
│   └── public/
│       └── index.html
│
├── data/
│   ├── documents/              # Вхідні документи
│   ├── processed/             # Оброблені дані
│   └── vector_db/            # ChromaDB storage
│
├── scripts/
│   ├── setup.sh              # Скрипт ініціалізації
│   ├── load_documents.py     # Завантаження документів
│   └── health_check.py       # Перевірка здоров'я системи
│
└── tests/
    ├── __init__.py
    ├── test_document_processor.py
    ├── test_rag_engine.py
    └── test_api.py
```