import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.user import User
from app.models.oauth_account import OAuthAccount
from app.schemas.user import UserCreate
from app.schemas.oauth import OAuthUserData
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

async def get_oauth_account(db: AsyncSession, oauth_name: str, account_id: str) -> OAuthAccount | None:
    """
    Поиск привязанных OAuth аккаунтов в базе
    """
    query = select(OAuthAccount).where(
        OAuthAccount.oauth_name == oauth_name,
        OAuthAccount.account_id == account_id
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_oauth_account(db: AsyncSession, user_id: uuid.UUID, oauth_data: OAuthUserData) -> OAuthAccount:
    """
    Создание записи о привязке соцсети к пользователю
    """
    oauth_acc = OAuthAccount(
        oauth_name=oauth_data.provider,
        account_id=oauth_data.account_id,
        account_email=oauth_data.email,
        user_id=user_id
    )
    db.add(oauth_acc)
    await db.commit()    
    return oauth_acc

async def create_user_from_oauth(db: AsyncSession, email: str) -> User:
    """
    Создание пользователя без пароля со статусом email verified
    """
    base_username = email.split("@")[0]
    
    # Добавление короткого случайного хеша из uuid для избежания коллизий
    unique_suffix = str(uuid.uuid4())[:6]
    username = f"{base_username}_{unique_suffix}"

    new_user = User(
        email=email,
        username=username,
        hashed_password=None,
        is_verified=True
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user