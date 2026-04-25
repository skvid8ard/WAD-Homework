import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import Chat
from app.schemas.chat import ChatCreate
from app.models.message import Message

async def create_chat(db: AsyncSession, user_id: uuid.UUID, chat_in: ChatCreate) -> Chat:
    """Создает новый чат в базе данных."""
    new_chat = Chat(
        user_id=user_id,
        title=chat_in.title
    )
    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat)
    return new_chat

async def get_user_chats(db: AsyncSession, user_id: uuid.UUID) -> list[Chat]:
    """Возвращает список чатов пользователя, отсортированный от новых к старым."""
    query = select(Chat).where(
        Chat.user_id == user_id
    ).order_by(Chat.created_at.desc())
    
    result = await db.execute(query)
    # scalars().all() извлекает список объектов из ответа SQLAlchemy
    return list(result.scalars().all())

async def get_chat_by_id(db: AsyncSession, chat_id: uuid.UUID, user_id: uuid.UUID) -> Chat | None:
    """Ищет чат и проверяет, что он принадлежит пользователю (защита от IDOR)"""
    query = select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_chat_messages(db: AsyncSession, chat_id: uuid.UUID) -> list[Message]:
    """Возвращает историю сообщений чата (от старых к новым)"""
    # Здесь order_by(asc), чтобы чат читался сверху вниз, как в мессенджерах
    query = select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at.asc())
    result = await db.execute(query)
    return list(result.scalars().all())

async def add_message(db: AsyncSession, chat_id: uuid.UUID, role: str, content: str) -> Message:
    """Сохраняет одно сообщение в БД"""
    new_msg = Message(
        chat_id=chat_id,
        role=role,
        content=content
    )
    db.add(new_msg)
    await db.commit()
    await db.refresh(new_msg)
    return new_msg