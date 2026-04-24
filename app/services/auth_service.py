import uuid
import jwt
import logging
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.config import settings

from app.services import user_service, session_service, email_service

logger = logging.getLogger(__name__)

async def register_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Бизнес-логика регистрации пользователя"""
    existing_user = await user_service.get_user_by_login(db, user_data.username) or \
                    await user_service.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username or email already taken / Имя пользователя или email уже занято"
        )

    new_user = await user_service.create_user(db, user_data) # Хэшируем пароль и сохраняем пользователя в БД

    verification_code = email_service.generate_verification_code()
    await session_service.save_otp_code(new_user.email, verification_code)
    await email_service.send_verification_email(new_user.email, verification_code)

    return new_user

async def verify_user_email(db: AsyncSession, email: str, verification_code: str) -> dict:
    logger.warning(f"DEBUG: Попытка верификации. Email: {email}, Код: {verification_code}")

    is_valid = await session_service.verify_and_delete_otp(email, verification_code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code / Неверный или истекший код подтверждения Email"
        )

    user = await user_service.get_user_by_email(db, email)
    if not user:
        logger.error(f"DEBUG: Пользователь с email {email} не найден в БД после успешной проверки кода.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found / Пользователь не найден"
        )
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified / Email уже подтвержден"
        )

    await user_service.mark_user_as_verified(db, user)
    return {"message": "Email successfully verified / Email успешно подтвержден"}

async def login_user(db: AsyncSession, form_data: OAuth2PasswordRequestForm) -> dict:

    # Поиск пользователя по username
    user = await user_service.get_user_by_login(db, form_data.username)
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
    access_token = create_access_token(subject=str(user.id))
    # Защита от кражи сессии (session hijackling) путем генерации уникальных JTU (ID токена)
    token_jti = str(uuid.uuid4())
    refresh_token = create_refresh_token(subject=str(user.id), jti=token_jti)

    # Сохранение refresh token в Redis с TTL (ключ: id пользователя + jti, значение: сам refresh token)
    await session_service.save_refresh_session(str(user.id), token_jti, refresh_token)

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
    user_id, token_jti, token_type = payload.get("sub"), payload.get("jti"), payload.get("type")
    if token_type != "refresh" or not user_id or not token_jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload / Неверная содержимое refresh токена"
        )

    # Проверка наличия refresh token в Redis (защита от повторного использования токена) и жизни сеанса
    is_valid = await session_service.is_session_valid(user_id, token_jti)
        # Если ключа нет, значит сессия была принудительно завершена (logout)
        # или токен уже был использован для обновления (refresh) и аннулирован (или replay attack)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired or invalid / Refresh токен был истек или недействителен"
        )

    # JWT Rotation: удаление старого refresh token из Redis (аннулирование)
    await session_service.delete_refresh_session(user_id, token_jti)

    # Генерация новой пары токенов
    new_jti = str(uuid.uuid4())
    new_access_token = create_access_token(subject=user_id)
    new_refresh_token = create_refresh_token(subject=user_id, jti=new_jti)

    # Сохранение нового refresh token в Redis
    await session_service.save_refresh_session(user_id, new_jti, new_refresh_token)
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
    await session_service.revoke_all_user_sessions(str(user_id))


async def resend_verification_code(db: AsyncSession, email:str) -> dict:
    """
    Бизнес-логика повторной отправки кода верификации на email пользователя
    """
    user = await user_service.get_user_by_email(db, email)
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
    new_code = email_service.generate_verification_code()
    await session_service.save_otp_code(email, new_code)
    await email_service.send_verification_email(email, new_code)

    return {"message": "If the email exists, a verification code has been sent / Если email существует, код подтверждения был отправлен"}