from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserSetting(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    email: Mapped[str] = mapped_column(String(320), nullable=False)
    alert_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # null = 전체 지역, ["한국", "유럽", ...] = 특정 지역만
    region_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    # null = 전체 카테고리
    category_json: Mapped[str | None] = mapped_column(Text, nullable=True)
