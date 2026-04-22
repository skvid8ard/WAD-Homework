from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import uuid
import jwt
import logging

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.core.redis import redis_client
from app.core.config import settings
from app.services.email_service import generate_verification_code, send_verification_email

logger = logging.getLogger(__name__)

async def register_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Бизнес-логика регистрации пользователя"""
    # Проверяем, существует ли уже пользователь с таким username
    query = select(User).where(
        or_(User.username == user_data.username, User.email == user_data.email)
        )
    result = await db.execute(query)

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username or email already taken / Имя пользователя или email уже занято"
        )

    # Хэшируем пароль
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        is_verified=False
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user) # Подтягивание ID, сгенерированного базой данных

    verification_code = generate_verification_code()

    redis_key = f"verify:{new_user.email}"
    await redis_client.setex(name=redis_key, time=600, value=verification_code)

    await send_verification_email(new_user.email, verification_code)

    return new_user

async def login_user(db: AsyncSession, form_data: OAuth2PasswordRequestForm) -> dict:
    """Бизнес-логика входа и генерации токенов"""

    # Поиск пользователя по username
    query = select(User).where(
        or_(User.username == form_data.username, User.email == form_data.username)
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    # Проверка существования пользователя и верификация пароля
    # Защита от перебора паролей (enum defence)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid username or password / Неверное имя пользователя или пароль"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified, please, verify your email / Email не подтвержден, пожалуйста, подтвердите ваш Email"
        )

    # Генерация токенов
    access_token = create_access_token(subject=user.id)
    # Защита от кражи сессии (session hijackling) путем генерации уникальных JTU (ID токена)
    token_jti = str(uuid.uuid4())
    refresh_token = create_refresh_token(subject=user.id, jti=token_jti)

    # Сохранение refresh token в Redis с TTL (ключ: id пользователя + jti, значение: сам refresh token)
    ttl_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    await redis_client.setex(
        name=f"refresh:{user.id}:{token_jti}",
        time=ttl_seconds,
        value=refresh_token
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_jti": token_jti # Возвращение JTI для последующего использования при обновлении токена
    }

async def refresh_session(refresh_token: str) -> dict:
    """Бизнес-логика обновления access token с помощью старого refresh token.
    Пользователь отдает старый refresh token, который аннулируется, пользователю выдается новая пара refresh + access токенов."""
    try:
        # Дешифровка токена
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except jwt.PyJWTError:
        # Если токен протух или подпись подделана
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token / Refresh токен был истек или недействителен"
        )

    # Извлечение данных
    user_id = payload.get("sub")
    token_jti = payload.get("jti")
    token_type = payload.get("type")

    if token_type != "refresh" or not user_id or not token_jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload / Неверная содержимое refresh токена"
        )

    # Проверка наличия refresh token в Redis (защита от повторного использования токена) и жизни сеанса
    redis_key = f"refresh:{user_id}:{token_jti}"
    stored_token = await redis_client.get(redis_key)

    if not stored_token:
        # Если ключа нет, значит сессия была принудительно завершена (logout)
        # или токен уже был использован для обновления (refresh) и аннулирован (или replay attack)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired or invalid / Refresh токен был истек или недействителен"
        )

    # JWT Rotation: удаление старого refresh token из Redis (аннулирование)
    await redis_client.delete(redis_key)

    # Генерация новой пары токенов
    new_jti = str(uuid.uuid4())
    new_access_token = create_access_token(subject=user_id)
    new_refresh_token = create_refresh_token(subject=user_id, jti=new_jti)

    # Сохранение нового refresh token в Redis
    ttl_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    await redis_client.setex(
        name=f"refresh:{user_id}:{new_jti}",
        time=ttl_seconds,
        value=new_refresh_token
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    }

async def logout_user(user_id: int):
    """
    Инвалидация всех сессий пользователя в Redis.
    В идеале мы должны удалять конкретный JTI, 
    но для простоты удалим все ключи по маске.
    """
    # Поиск всех ключей для данного пользователя и удаление их (инвалидация всех сессий)
    # refresh:14:* - удалит все refresh токены для пользователя с id=14
    cursor = 0
    while True:
        # scan_iter безопаснее keys(), так как не блокирует Redis при большом количестве ключей
        cursor, keys = await redis_client.scan(cursor, match=f"refresh:{user_id}:*")
        if keys:
            await redis_client.delete(*keys)
        if cursor == 0:
            break

async def verify_user_email(db: AsyncSession, email: str, verification_code: str):
    logger.warning(f"DEBUG: Попытка верификации. Email: {email}, Код: {verification_code}")

    """Бизнес-логика верификации email пользователя"""
    redis_key = f"verify:{email}"
    stored_code = await redis_client.get(redis_key)

    logger.warning(f"DEBUG: Код из redis {email}: {stored_code}")

    if not stored_code or stored_code != verification_code:
        logger.error(f"DEBUG: Неверный код верификации для {email}. Ожидалось: {stored_code}, Получено: {verification_code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code / Неверный или истекший код подтверждения Email"
        )

    logger.warning(f"DEBUG: Сравниваем. Из Redis: '{stored_code}' == От юзера: '{verification_code}' ?")

    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found / Пользователь не найден"
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified / Email уже подтвержден"
        )

    user.is_verified = True
    await db.commit()

    await redis_client.delete(redis_key)

    return {"message": "Email successfully verified / Email успешно подтвержден"}

async def resend_verification_code(db: AsyncSession, email:str) -> dict:
    """
    Бизнес-логика повторной отправки кода верификации на email пользователя
    """
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_200_OK, # Возвращаем 200, чтобы не раскрывать информацию о существовании email в системе
            detail="If the email exists, a verification code has been sent / Если email существует, код подтверждения был отправлен"
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified / Email уже подтвержден"
        )

    new_code = generate_verification_code()

    redis_key = f"verify:{email}"
    await redis_client.setex(name=redis_key, time=600, value=new_code)

    await send_verification_email(email, new_code)

    return {"message": "If the email exists, a verification code has been sent / Если email существует, код подтверждения был отправлен"}