# RAG System

Скелет системи Retrieval-Augmented Generation (RAG), що дозволяє завантажувати документи, індексувати їх у векторній базі Chroma та виконувати пошук із подальшим збагаченням відповідей за допомогою LLM.

## Архітектура

Проект складається з кількох сервісів, що запускаються через `docker compose`:

- **rag-service** – FastAPI‑сервіс з вбудованою ChromaDB для обробки файлів та пошуку.
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
├── rag-service/
├── llm-service/
├── frontend/
├── scripts/
└── tests/

# 📁 Структура RAG System проекту та розміщення файлів

## 🏗️ Повна структура директорій

```
rag-system/
├── 📄 docker-compose.yml                    # ← ЗАМІНИТИ виправленою версією
├── 📄 README.md                             # ← Існуючий файл
├── 📄 .env                                  # ← СТВОРИТИ (опціонально)
├── 📄 .gitignore                            # ← СТВОРИТИ
│
├── 📂 scripts/
│   ├── 📄 startup.sh                        # ← Існуючий файл
│   ├── 📄 diagnose.py                       # ← Існуючий файл
│   ├── 📄 setup.sh                          # ← Існуючий файл
│   ├── 📄 health_check.py                   # ← Існуючий неповний файл
│   └── 📄 load_documents.py                 # ← Порожній файл
│
├── 📂 rag-service/
│   ├── 📄 Dockerfile                        # ← ЗАМІНИТИ виправленою версією
│   ├── 📄 requirements.txt                  # ← Існуючий файл
│   └── 📂 app/
│       ├── 📄 __init__.py                   # ← Існуючий порожній файл
│       ├── 📄 main.py                       # ← Існуючий файл
│       ├── 📄 config.py                     # ← Існуючий файл
│       ├── 📂 core/
│       │   ├── 📄 __init__.py               # ← Існуючий порожній файл
│       │   ├── 📄 document_processor.py     # ← Існуючий файл
│       │   ├── 📄 rag_engine.py            # ← Існуючий файл
│       │   └── 📄 embeddings.py            # ← Порожній файл
│       ├── 📂 models/
│       │   ├── 📄 __init__.py              # ← Існуючий файл з кодом
│       │   └── 📄 document.py              # ← Існуючий файл
│       ├── 📂 api/
│       │   ├── 📄 __init__.py              # ← Порожній файл
│       │   ├── 📄 dependencies.py          # ← Порожній файл
│       │   └── 📂 routes/
│       │       ├── 📄 __init__.py          # ← Порожній файл
│       │       ├── 📄 documents.py         # ← Порожній файл
│       │       └── 📄 search.py            # ← Порожній файл
│       └── 📂 utils/
│           ├── 📄 __init__.py              # ← Порожній файл
│           └── 📄 helpers.py               # ← Порожній файл
│
├── 📂 llm-service/
│   ├── 📄 Dockerfile                        # ← Існуючий файл
│   ├── 📄 requirements.txt                  # ← Існуючий файл
│   └── 📂 app/
│       ├── 📄 main.py                       # ← Існуючий файл
│       ├── 📄 config.py                     # ← Порожній файл
│       └── 📂 models/
│           └── 📄 llm.py                    # ← Порожній файл
│
├── 📂 frontend/
│   ├── 📄 Dockerfile                        # ← Існуючий файл
│   ├── 📄 package.json                      # ← Існуючий файл
│   ├── 📂 public/
│   │   └── 📄 index.html                    # ← Існуючий файл
│   └── 📂 src/
│       ├── 📄 App.js                        # ← Існуючий файл
│       ├── 📄 App.css                       # ← Існуючий файл
│       ├── 📂 components/                   # ← Директорія існує
│       │   ├── 📄 ChatInterface.js          # ← Порожній файл
│       │   ├── 📄 DocumentUpload.js         # ← Порожній файл
│       │   └── 📄 SearchInterface.js        # ← Порожній файл
│       └── 📂 services/
│           └── 📄 api.js                    # ← Порожній файл
│
├── 📂 tests/                                # ← Директорія для тестів
│   ├── 📄 __init__.py                       # ← Порожній файл
│   ├── 📄 test_api.py                       # ← Порожній файл
│   ├── 📄 test_document_processor.py        # ← Порожній файл
│   └── 📄 test_rag_engine.py               # ← Порожній файл
│
└── 📂 data/                                 # ← СТВОРИТИ директорію
    ├── 📂 uploads/                          # ← СТВОРИТИ підпапку
    ├── 📂 processed/                        # ← СТВОРИТИ підпапку
    └── 📂 vector_db/                        # ← СТВОРИТИ підпапку
```

## 🔧 Що потрібно зробити:

### 1. Замінити існуючі файли:

**📄 docker-compose.yml** (корінь проекту)
```bash
# Замінити весь вміст файлу виправленою версією
cp docker-compose.yml docker-compose.yml.backup  # резервна копія
# Вставити новий вміст з artifact "docker_compose_fixed"
```

**📄 rag-service/Dockerfile**
```bash
# Замінити існуючий Dockerfile
cp rag-service/Dockerfile rag-service/Dockerfile.backup
# Вставити новий вміст з artifact "rag_dockerfile_fixed"
```

### 2. Створити нові файли:

**📄 scripts/startup.sh**
```bash
chmod +x scripts/startup.sh
```

**📄 scripts/diagnose.py**
```bash
chmod +x scripts/diagnose.py
```

**📄 .env** (корінь проекту)
```bash
# Створити файл з налаштуваннями при потребі
touch .env
```

**📄 .gitignore** (корінь проекту)
```bash
# Створити файл для ігнорування файлів Git
touch .gitignore
```

### 3. Створити директорії:

```bash
# Створити необхідні директорії
mkdir -p data/uploads
mkdir -p data/processed  
mkdir -p data/vector_db
mkdir -p ~/.cache/huggingface
```

## 🚀 Покрокова інструкція запуску:

### Крок 1: Запуск системи
```bash
# Запуск усіх сервісів
docker compose up --build

# Діагностика проблем
python3 scripts/diagnose.py
```

## 📝 Додаткові файли для створення:

### 📄 .env (корінь проекту)
```env
# Налаштування для RAG системи
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
OLLAMA_BASE_URL=http://ollama:11434
DEFAULT_MODEL=llama3.1:8b
```

### 📄 .gitignore (корінь проекту)
```gitignore
# Дані
data/uploads/*
data/processed/*
data/vector_db/*
!data/.gitkeep

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.venv/
venv/

# Docker
.docker/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Логи
*.log
logs/

# Тимчасові файли
.DS_Store
Thumbs.db

# Node modules (для frontend)
node_modules/
npm-debug.log*
```

## 🎯 Пріоритет дій для виправлення:

1. **Високий пріоритет:**
   - ✅ Замінити `docker-compose.yml`
   - ✅ Замінити `rag-service/Dockerfile`
2. **Середній пріоритет:**
   - ✅ Створити `scripts/startup.sh`
   - ✅ Створити `scripts/diagnose.py`
   - ✅ Створити директорії `data/`

3. **Низький пріоритет:**
   - Створити `.env` та `.gitignore`
   - Заповнити порожні файли в `tests/`

Після виконання цих кроків система повинна працювати коректно! 🎉

```


## Тестування

Виконайте тести перед створенням коміту:

```bash
pytest
```

## Ліцензія

Ліцензійний файл відсутній; використовуйте код на власний розсуд.

