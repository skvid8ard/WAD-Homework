from datetime import datetime
import uuid
from sqlalchemy import String, ForeignKey, DateTime, func, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.base import Base

class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
        )
    # ondelete="CASCADE" на уровне БД: удалили юзера -> удалились его чаты
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))

    # server_default=func.now() заставляет саму БД (Postgres) подставлять время при INSERT.
    # Это надежнее, чем генерировать время в Python, так как защищает от рассинхронизации часов на серверах.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="chats")
    messages: Mapped[list["Message"]] = relationship(back_populates="chat")