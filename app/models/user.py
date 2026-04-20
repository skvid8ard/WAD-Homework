import uuid
from sqlalchemy import String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
        )
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

    # Связь "один-ко-многим". back_populates указывает на свойство в связанном классе
    chats: Mapped[list["Chat"]] = relationship(back_populates="user")