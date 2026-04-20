import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: str | int) -> str:
    # Генерация access token 
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}

    # Шифрование токена с помощью секретного ключа и алгоритма HS256
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(subject: str | int, jti: str) -> str:
    # Генерация refresh token
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh", "jti": jti}

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_auth_cookie_params() -> dict:
    """
    Параметры для установки куки с refresh токеном.
    Выносится в отдельную функцию для удобства и единообразия при установке и удалении куки.
    """
    return {
        "httponly": True, # Куки недоступна для JavaScript, что защищает от XSS атак
        "secure": settings.ENVIRONMENT == "production", 
        "samesite": "lax", # Куки будет отправляться только при навигации по сайту, что защищает от CSRF атак
        "path": "/auth/refresh" # Куки будет отправляться только на этот эндпоинт, что повышает безопасность
    }