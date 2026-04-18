from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings

# Инициализация асинхронного движка
engine = create_async_engine(settings.DATABASE_URL, echo=False) # echo=True для дебага

# Асинхронные сессии
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Dependency для FastAPI (используется в контроллерах)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session