from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_setting import UserSetting


class UserSettingRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, user_setting: UserSetting) -> UserSetting:
        self.db.add(user_setting)
        self.db.flush()
        return user_setting

    def find_by_user_id(self, user_id: int) -> UserSetting | None:
        stmt = select(UserSetting).where(UserSetting.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def find_all(self) -> list[UserSetting]:
        stmt = select(UserSetting)
        return list(self.db.execute(stmt).scalars().all())

    def upsert(
        self,
        user_id: int,
        slack_webhook_url: str,
        alert_enabled: bool = True,
        country_json: str | None = None,
        category_json: str | None = None,
    ) -> UserSetting:
        user_setting = self.find_by_user_id(user_id)

        if user_setting is None:
            user_setting = UserSetting(
                user_id=user_id,
                slack_webhook_url=slack_webhook_url,
                alert_enabled=alert_enabled,
                country_json=country_json,
                category_json=category_json,
            )
            self.db.add(user_setting)
        else:
            user_setting.slack_webhook_url = slack_webhook_url
            user_setting.alert_enabled = alert_enabled
            user_setting.country_json = country_json
            user_setting.category_json = category_json

        self.db.flush()
        return user_setting

    def update_webhook_url(self, user_id: int, slack_webhook_url: str) -> UserSetting | None:
        user_setting = self.find_by_user_id(user_id)
        if user_setting is None:
            return None

        user_setting.slack_webhook_url = slack_webhook_url
        self.db.flush()
        return user_setting
