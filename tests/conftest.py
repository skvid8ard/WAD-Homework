import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app as fastapi_app
from app.core.base import Base
from app.core.database import get_db
import app.models

# 1. Настройка тестового движка
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# 2. ОПРЕДЕЛЯЕМ функцию-заменитель (Dependency)
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

# 3. РЕГИСТРИРУЕМ её (теперь Python знает имя override_get_db)
fastapi_app.dependency_overrides[get_db] = override_get_db

# 4. Фикстуры для тестов
@pytest_asyncio.fixture(scope="session", autouse=True) # autouse=True важен!
async def setup_db():
    """Создает таблицы перед тестами и удаляет после"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client():
    """Асинхронный клиент для запросов"""
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), 
        base_url="http://test"
    ) as ac:
        yield ac