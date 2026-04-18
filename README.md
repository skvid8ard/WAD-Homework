# Архитектура  
backend/  
├── app/  
│   ├── core/           # Настройки, инициализация БД, Redis, безопасность  
│   ├── models/         # SQLAlchemy модели (Model)  
│   ├── schemas/        # Pydantic модели для валидации ввода/вывода  
│   ├── services/       # Бизнес-логика (Service)  
│   ├── controllers/    # API Роутеры (Controller)  
│   └── main.py         # Точка входа приложения  
├── migrations/         # Файлы миграций базы данных (Alembic)  
├── docs/               # Документация и логи спринтов  
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

## Настройка окружения
### Генерация секретов для .env
```
openssl rand --hex 32
```  

### Создание .env  
Скопировать `.env` из `.env.example` и заменить все инсерты сгенерированными секретами.  

## Запуск проекта и миграции
```
docker compose up -d  
```

Накат актуальной структуры базы данных:  
```
alembic upgrade head
```
