# !Тестовый стенд с HTTPS и OAuth!
core-llm.duckdns.org

# Архитектура  
WAD-Homework/
├── .venv/              # Виртуальное окружение Python  
├── ai-models/          # Директория с весами локальных нейросетей (GGUF)  
├── backend/            # Бэкенд (FastAPI)  
│   ├── app/  
│   │  ├── core/           # Настройки, инициализация БД, Redis, безопасность  
│   │  ├── models/         # SQLAlchemy модели (Model)  
│   │  ├── schemas/        # Pydantic модели для валидации ввода/вывода  
│   │  ├── services/       # Бизнес-логика (Service)  
│   │  ├── controllers/    # API Роутеры (Controller)  
│   │  └── main.py         # Точка входа приложения  
│   ├── migrations/     # Файлы миграций базы данных (Alembic)  
│   ├── tests/          # Автоматизированные тесты (pytest)  
│   ├── alembic.ini     # Конфигурация миграций  
│   ├── pytest.ini      # Конфигурация тестов  
│   └── requirements.txt# Зависимости бэкенда  
├── docs/               # Документация проекта  
│   ├── sprints/        # Логи и история спринтов  
│   ├── architecture.md # Справочник архитектуры слоев  
│   ├── SPEC.md         # Спецификация  
│   ├── tech-stack.md   # Технологический стек  
│   └── testing.md      # Инструкции по тестированию  
├── frontend/  
│   ├── src/            # Исходный код React-приложения (FSD архитектура)  
│   ├── index.html      # Главный HTML файл  
│   ├── vite.config.ts  # Конфигурация сборщика Vite  
│   └── package.json    # Зависимости фронтенда  
├── .env                # Единый файл глобальных переменных окружения  
├── .env.example        # Шаблон переменных окружения  
├── .gitignore          # Исключения для Git  
├── CHANGELOG.md        # История изменений проекта  
├── docker-compose.yml  # Инфраструктура (PostgreSQL, Redis)  
└── README.md           # Главный файл документации  

# Деплой с помощью docker-compose
## Получение сертификатов
- Запустить проект с nginx.conf.backup  
- Запустить certbot, получить сертификаты:  
```
docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email твой_почтовый_ящик@gmail.com --agree-tos --no-eff-email -d core-llm.duckdns.org
```
## Запуск проекта
```
docker compose down
```

- Заменить nginx.conf обратно  

```
docker compose up -d --build
```

# Ручной деплой
## Venv  
`python3 -m venv backend/.venv`  
### Linux  
`source backend/.venv/bin/activate`  
### Windows  
`backend\.venv\Scripts\Activate.ps1`

## Установка зависимостей
```
cd backend

CMAKE_ARGS="-DGGML_NATIVE=OFF -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_FMA=OFF -DGGML_F16C=OFF" pip install llama-cpp-python --no-cache-dir --force-reinstall

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
#### Просмотр пользователей
``` bash
docker exec -it wad-homework-postgres-1 psql -U postgres -d chatdb -c"SELECT * FROM users;"
```
#### Просмотр OAuth аккаунтов
``` bash
docker exec -it wad-homework-postgres-1 psql -U postgres -d chatdb -c "SELECT user_id, oauth_name, account_email FROM oauth_accounts;"
```
#### Просмотр чатов
``` bash
docker exec -it wad-homework-postgres-1 psql -U postgres -d chatdb -c "SELECT id, title, created_at FROM chats;"
```
#### Просмотр истории конкретного чата
``` bash
docker exec -it wad-homework-postgres-1 psql -U postgres -d chatdb -c "SELECT role, content FROM messages WHERE chat_id = '<CHAT_ID>' ORDER BY created_at ASC;"
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

### Запуск frontend (из директории frontend)
```
npm install
npm run dev
```