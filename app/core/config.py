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


settings = Settings()
