import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_user_by_login(db: AsyncSession, login: str) -> User | None:
    """
    Поиск пользователя по его username или email.
    """
    query = select(User).where(
        or_(User.username == login, User.email == login)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user_data: UserCreate, is_verified: bool = False) -> User:
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        is_verified=is_verified
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user) # Подтягивание ID, сгенерированного базой данных
    return new_user

async def mark_user_as_verified(db: AsyncSession, user: User):
    user.is_verified = True
    await db.commit()