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

## Тестирование API
### Запуск бд и redis
```
docker compose up -d redis postgres
```
### Запуск сервера uvicorn (для тестов)
```
uvicorn app.main:app --reload
```
### Интерактивная документация (Swagger)
После запуска сервера перейти по адресу: [http://localhost:8000/docs](http://localhost:8000/docs)
Здесь можно протестировать все эндпоинты в интерактивном режиме.

### Тестирование через Терминал (cURL)
```bash
curl -X 'POST' \
  'http://localhost:8000/auth/register' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "testuser",
  "password": "StrongPassword123!"
}'
```

### Проверка в бд (пример)
``` bash
docker exec -it wad-homework-postgres-1 psql -U postgres -d chatdb -c"SELECT * FROM users;"
```

### Проверка refresh-токенов в redis
```
docker exec -it wad-redis redis-cli -a <redis_password> KEYS "refresh:*"
```

## Запуск проекта и миграции
```
docker compose up -d  
```

Генерация новой миграции:
```
alembic revision --autogenerate -m "Initial with UUID"
```

Накат актуальной структуры базы данных:  
```
alembic upgrade head
```