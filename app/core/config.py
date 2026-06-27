from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/blog"
    app_name: str = "Personal Blog"
    debug: bool = True
    bookmarks_page_password: str | None = None
    scheduler_timezone: str = "Asia/Shanghai"
    bookmark_url_check_enabled: bool = True
    bookmark_url_check_hour: int = 1
    bookmark_url_check_timeout_seconds: float = 15.0
    bookmark_url_check_fail_days: int = 3
    bookmark_url_check_proxy: str | None = None


settings = Settings()
