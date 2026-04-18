from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[int] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[int] = mapped_column(String)

    # Связь "один-ко-многим". back_populates указывает на свойство в связанном классе
    chats: Mapped[list["Chat"]] = relationship(back_populates="user")