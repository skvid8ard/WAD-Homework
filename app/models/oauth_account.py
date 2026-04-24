import uuid
from sqlalchemy import String, ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.core.base import Base

class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, 
        primary_key=True, 
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    # Название провайдера (google, github и т.д.)
    oauth_name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    # Уникальный идентификатор пользователя в системе провайдера (например, sub в Google)
    account_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    # Почта, полученная от провайдера (может быть полезна для отображения и поиска)
    account_email: Mapped[str] = mapped_column(String, nullable=False)

    # Связь с пользователем в системе. Один пользователь может иметь несколько OAuth аккаунтов.
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="oauth_accounts")

    # Уникальное ограничение на комбинацию oauth_name и account_id, чтобы один и тот же OAuth аккаунт не мог быть привязан к разным пользователям
    __table_args__ = (
        UniqueConstraint("oauth_name", "account_id", name="uq_oauth_account_id"),
    )