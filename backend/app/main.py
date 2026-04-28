from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Импортируем стандартный Middleware
from app.controllers import auth, chat 
from app.services.llm_service import LocalLLMService
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Логика при ЗАПУСКЕ сервера ---
    print("🚀 Старт сервера...")
    LocalLLMService.initialize()
    yield

    # --- Логика при ОСТАНОВКЕ сервера ---
    print("🛑 Остановка сервера, очистка ресурсов...")
    # (Опционально) Можно принудительно очистить память
    LocalLLMService._model = None

app = FastAPI(
    title="Core-LLM",
    root_path="/api",
    description="API для чата с локальной нейросетью",
    version = "v0.12.0",
    lifespan=lifespan
    )

# Настройка CORS для разрешения запросов с определенных источников
# origins = [
#     "http://localhost:5173", # Разрешаем запросы с фронтенда, который работает на этом адресе
#     "http://127.0.0.1:5173"
# ]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins, # Разрешаем только указанные источники
    allow_credentials=True, # Разрешаем отправку куки и авторизационных заголовков
    allow_methods=["*"], # Разрешаем все HTTP методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"] # Разрешаем все заголовки
)

app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/health")
async def health_check():
    """Простой эндпоинт для проверки работоспособности сервера. Возвращает статус 'ok' при успешном ответе."""
    return {"status": "ok"}