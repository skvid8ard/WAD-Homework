from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import jwt

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User

# Настройка схемы для получения токена из заголовков Authorization
# tokenUrl указывает на эндпоинт, который будет использоваться для получения токена (для кнопки Authorize)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Зависимость для защиты эндпоинтов. 
    Извлекает токен, проверяет подпись, срок годности и ищет пользователя в БД.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials / Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Декодирование токена и извлечение полезной нагрузки (payload)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub") # "sub" - стандартное поле для идентификатора субъекта (пользователя)
        token_type: str = payload.get("type") # "type" - кастомное поле для указания типа токена (access или refresh)

        # Проверка того, что токен является access токеном, а не refresh токеном
        if user_id_str is None or token_type != "access":
            raise credentials_exception

    except jwt.PyJWTError: # Если токен протух или битый
        raise credentials_exception

    # Поиск пользователя в БД по его ID
    query = select(User).where(User.id == uuid.UUID(user_id_str))
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user