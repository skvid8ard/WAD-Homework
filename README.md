# Архитектура  
backend/  
├── app/  
│   ├── core/           # Настройки, инициализация БД, Redis, безопасность  
│   ├── models/         # SQLAlchemy модели (Model)  
│   ├── schemas/        # Pydantic модели для валидации ввода/вывода  
│   ├── services/       # Бизнес-логика (Service)  
│   ├── controllers/    # API Роутеры (Controller)  
│   └── main.py         # Точка входа приложения  
├── .env                # Переменные окружения  
└── requirements.txt  

# Деплой
## Venv  
`python3 -m venv .venv`  
### Linux  
`source .venv/bin/activate`  
### Windows  
`.\venv\Scripts\Activate.ps1`

## Установка зависимостей
```
pip install -r requirements.txt  
```

## Генерация секретов для .env  
```
openssl rand --hex 32
```  

## .env  
```
PROJECT_NAME="Local LLM Chat"
DATABASE_URL="postgresql+asyncpg://postgres:<pass>@localhost:5432/chatdb"
REDIS_URL="redis://:<pass>@localhost:6379/0"

# JWT Settings
SECRET_KEY="<pass>"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# DBs
REDIS_PASSWORD="<pass>"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="<pass>"
POSTGRES_DB="chatdb"

# GitHub OAuth
GITHUB_CLIENT_ID="your_github_client_id"
GITHUB_CLIENT_SECRET="your_github_client_secret"
```

```
docker compose up -d  
```