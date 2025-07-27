from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, Field


class Settings(BaseSettings):
    database_url: PostgresDsn = Field(alias="DATABASE_URL")
    bot_token: str = Field(alias="DISCORD_BOT_TOKEN")
    debug: bool = Field(default=False)
    redis_url: str = Field(alias="REDIS_URL")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="allow"
    )


settings = Settings()  # pyright: ignore[reportCallIssue]

print(settings.model_dump())
