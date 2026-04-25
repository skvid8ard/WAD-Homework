import redis.asyncio as redis
from app.core.config import settings

# Глобальный пул соединений
redis_client = redis.from_url(
    settings.REDIS_URL, 
    encoding="utf-8", 
    decode_responses=True # Автоматически декодирует байты в строки
)

async def get_redis():
    yield redis_client