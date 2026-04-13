from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Инициализация асинхронного движка
engine = create_async_engine(settings.DATABASE_URL, echo=False) # echo=True для дебага

# Асинхронные сессии
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Базовый класс для всех моделей
Base = declarative_base()

# Dependency для FastAPI (используется в контроллерах)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session