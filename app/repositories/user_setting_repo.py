from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.user_setting import UserSetting


class UserSettingRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_email(self, email: str) -> UserSetting | None:
        stmt = select(UserSetting).where(UserSetting.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def find_all(self) -> list[UserSetting]:
        stmt = select(UserSetting)
        return list(self.db.execute(stmt).scalars().all())

    def upsert(
        self,
        email: str,
        alert_enabled: bool = True,
        category_json: str | None = None,
    ) -> UserSetting:
        user_setting = self.find_by_email(email)

        if user_setting is None:
            user_setting = UserSetting(
                email=email,
                alert_enabled=alert_enabled,
                category_json=category_json,
            )
            self.db.add(user_setting)
        else:
            user_setting.alert_enabled = alert_enabled
            user_setting.category_json = category_json

        self.db.flush()
        return user_setting

    def delete_by_email(self, email: str) -> bool:
        stmt = delete(UserSetting).where(UserSetting.email == email)
        result = self.db.execute(stmt)
        self.db.flush()
        return result.rowcount > 0

