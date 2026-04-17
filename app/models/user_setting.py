from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserSetting(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    slack_webhook_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    alert_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # null = 전체 국가, ["kr", "us", ...] = 특정 국가만
    country_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    # null = 전체 카테고리
    category_json: Mapped[str | None] = mapped_column(Text, nullable=True)
