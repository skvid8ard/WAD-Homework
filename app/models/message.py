from datetime import datetime
import uuid
from sqlalchemy import String, Text, ForeignKey, DateTime, func, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.base import Base

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
        )
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"))
    # role: 'user' или 'assistant' (модель)
    role: Mapped[str] = mapped_column(String(20))
    # Text используется для длинных сообщений, в отличие от String (VARCHAR)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chat: Mapped["Chat"] = relationship(back_populates="messages")