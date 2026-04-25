import logging
from app.core.redis import redis_client
from app.core.config import settings

logger = logging.getLogger(__name__)

# --- РАБОТА С OTP КОДАМИ ---
async def save_otp_code(email: str, code: str, ttl_seconds: int = 600) -> None:
    """
    Сохранение OTP кода в Redis с TTL (время жизни).
    Ключ формируется как "otp:{email}" для удобства поиска.
    """
    redis_key = f"verify:{email}"
    logger.warning(f"DEBUG REDIS [SAVE]: Сохраняем код '{code}' по ключу '{redis_key}'")
    await redis_client.setex(name=redis_key, time=ttl_seconds, value=code)

async def verify_and_delete_otp(email: str, code: str) -> bool:
    """
    Проверка OTP кода из Redis и его удаление после проверки (одноразовый код).
    Возвращает True, если код верный, иначе False.
    """
    redis_key = f"verify:{email}"
    stored_code = await redis_client.get(redis_key)

    logger.warning(f"DEBUG REDIS[VERIFY]: Ищем ключ '{redis_key}'.")
    logger.warning(f"DEBUG REDIS [VERIFY]: Из Redis достали: {repr(stored_code)} (тип: {type(stored_code)})")
    logger.warning(f"DEBUG REDIS [VERIFY]: Юзер прислал: {repr(code)} (тип: {type(code)})")

    if not stored_code:
        logger.error("DEBUG REDIS: Код не найден (вернулся None)!")
        return False

    if isinstance(stored_code, bytes):
        stored_code = stored_code.decode("utf-8")
        logger.warning(f"DEBUG REDIS [VERIFY]: Декодировали байты в строку: '{stored_code}'")

    if stored_code != code:
        logger.error("DEBUG REDIS: Коды не совпадают!")
        return False

    logger.warning("DEBUG REDIS [VERIFY]: Коды совпали! Удаляем ключ.")
    # Код верный, удаляем его из Redis
    await redis_client.delete(redis_key)
    return True

# --- РАБОТА С СЕССИЯМИ И ТОКЕНАМИ JWT ---
async def save_refresh_session(user_id: str, jti: str, refresh_token: str) -> None:
    """
    Сохранение refresh токена в Redis для реализации JWT Rotation и защиты от повторного использования токенов.
    Ключ формируется как "refresh:{user_id}:{jti}" для уникальной идентификации каждой сессии.
    """
    ttl_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    redis_key = f"refresh:{user_id}:{jti}"
    await redis_client.setex(name=redis_key, time=ttl_seconds, value=refresh_token)

async def is_session_valid(user_id: str, jti: str) -> bool:
    """
    Проверка наличия refresh токена в Redis для данного user_id и jti.
    Если токен есть, значит сессия валидная, иначе - нет (возможно, была принудительно завершена или токен уже был использован).
    """
    redis_key = f"refresh:{user_id}:{jti}"
    stored_token = await redis_client.get(redis_key)
    return stored_token is not None

async def delete_refresh_session(user_id: str, jti: str) -> None:
    """
    Удаление refresh токена из Redis, что фактически завершает сеанс пользователя (logout) или аннулирует токен после его использования (JWT Rotation).
    """
    redis_key = f"refresh:{user_id}:{jti}"
    await redis_client.delete(redis_key)

async def revoke_all_user_sessions(user_id: str) -> None:
    """
    Инвалидация всех сессий пользователя в Redis.
    Удаляет все ключи, начинающиеся на "refresh:{user_id}:", что фактически завершает все сеансы пользователя.
    """
    pattern = f"refresh:{user_id}:*"
    cursor = 0
    while True:
        cursor, keys = await redis_client.scan(cursor=cursor, match=pattern)
        if keys:
            await redis_client.delete(*keys)
        if cursor == 0:
            break