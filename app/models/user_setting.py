from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserSetting(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    alert_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    category_json: Mapped[str | None] = mapped_column(Text, nullable=True)
