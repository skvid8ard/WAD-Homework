from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Импортируем стандартный Middleware
from app.controllers import auth

app = FastAPI(
    title="LLM chat",
    description="API для чата с локальной нейросетью",
    version = "v0.3.1"
    )

# Настройка CORS для разрешения запросов с определенных источников
origins = [
    "http://localhost:<port>", # Разрешаем запросы с фронтенда, который работает на этом адресе
    "http://127.0.0.1:<port>"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Разрешаем только указанные источники
    allow_credentials=True, # Разрешаем отправку куки и авторизационных заголовков
    allow_methods=["*"], # Разрешаем все HTTP методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"] # Разрешаем все заголовки
)

app.include_router(auth.router)

@app.get("/health")
async def health_check():
    """Простой эндпоинт для проверки работоспособности сервера. Возвращает статус 'ok' при успешном ответе."""
    return {"status": "ok"}