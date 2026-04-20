from fastapi import APIRouter, Depends, Response, HTTPException, status, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services import auth_service
from app.core.dependencies import get_current_user
from app.models.user import User
from app.core.security import get_auth_cookie_params
from app.core.config import settings

# Объявление роутера с настройками "по умолчанию" для всех его методов
router = APIRouter(
    prefix="/auth", # Все URL в этом методе будут начинаться с /auth
    tags=["Authentication"] # В Swagger UI эти методы будут сгруппированы под одним тегом
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Эндпоинт для регистрации нового пользователя. Принимает данные пользователя, проверяет их и сохраняет в базе данных. Возвращает данные нового пользователя (без пароля) в формате UserResponse."""
    return await auth_service.register_user(db, user_data)

@router.post("/login")
async def login(
    user_data: UserCreate,
    response: Response, # Позволяет устанавливать HTTP заголовки в ответе
    db: AsyncSession = Depends(get_db)
):
    """Эндпоинт для входа пользователя. Принимает данные пользователя, проверяет их и при успешной аутентификации генерирует access и refresh токены. Устанавливает refresh токен в HTTP-only куки и возвращает access токен в теле ответа."""
    tokens = await auth_service.login_user(db, user_data)

    # Установка токенов в HTTP-only куки для безопасности
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        **get_auth_cookie_params() # Получение параметров для установки куки из отдельной функции
    )
    return {
        "access_token": tokens["access_token"],
        "token_type": "bearer"
    }

@router.post("/refresh")
async def refresh_token(
    response: Response,
    # FastAPI автоматически достанет токен из куки "refresh_token"
    refresh_token: str | None = Cookie(default=None)
):
    """Эндпоинт для обновления access токена с помощью refresh токена и ротации токенов. Проверяет валидность refresh токена, генерирует новый access токен и устанавливает его в куки. Возвращает новый access токен в теле ответа."""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Refresh token missing / Отсутствует refresh токен"
        )

    # Использование метода refresh_session из auth_service для проверки и генерации нового access токена
    new_tokens = await auth_service.refresh_session(refresh_token)

    # Установка нового refresh токена в куки
    response.set_cookie(
        key="refresh_token",
        value=new_tokens["refresh_token"],
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        **get_auth_cookie_params()
    )

    return {
        "access_token": new_tokens["access_token"],
        "token_type": "bearer"
    }
   
@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user) # Логаут пользователя, который делает запрос (получаем из access токена)
    ):
    """Эндпоинт для выхода пользователя (logout). Инвалидирует все сессии пользователя в Redis и удаляет refresh токен из куки, что фактически завершает сеанс пользователя."""

    # Вызов метода logout_user из auth_service для инвалидации всех сессий пользователя в Redis
    await auth_service.logout_user(current_user.id)

    # Удаление refresh токена из куки, что фактически завершает сеанс пользователя (logout)
    response.delete_cookie(
        key="refresh_token",
        path="/auth/refresh",
        httponly=True,
        samesite="lax"
    )

    return {"detail": "Successfully logged out / Успешный выход из системы"}
