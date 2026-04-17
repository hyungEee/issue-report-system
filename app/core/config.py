from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 앱 기본 설정
    app_name: str = "issue-report-system"
    app_env: str = Field(default="local")
    debug: bool = Field(default=True)

    # 서버
    host: str = "0.0.0.0"
    port: int = 8000

    # DB
    db_user: str
    db_password: str
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str

    # 스케줄러
    scheduler_enabled: bool = True
    scheduler_interval_minutes: int = 30

    # 로깅
    log_level: str = "INFO"

    # 외부 연동
    gnews_api_key: str | None = Field(default=None, alias="GNEWS_API_KEY")
    ai_api_key: str | None = None
    slack_webhook_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()