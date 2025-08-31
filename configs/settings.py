from functools import cached_property
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, Field, RedisDsn


class DiscordSettings(BaseSettings):
    client_id: str = Field(alias="DISCORD_CLIENT_ID")
    client_secret: str = Field(alias="DISCORD_CLIENT_SECRET")
    bot_token: str = Field(alias="DISCORD_BOT_TOKEN")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="allow"
    )


class Settings(BaseSettings):
    discord: DiscordSettings = DiscordSettings()  # pyright: ignore[reportCallIssue]
    environment: str = Field(default="production", alias="ENVIRONMENT")
    jwt_secret: str = Field(alias="JWT_SECRET_KEY")
    database_url: PostgresDsn = Field(alias="DATABASE_URL")
    debug: bool = Field(default=False)
    redis_url: RedisDsn = Field(alias="REDIS_URL")
    default_brand_color_str: str = Field(
        default="#7289DA",
        description="Default brand color for embeds",
        alias="DEFAULT_BRAND_COLOR",
    )
    default_guild_id: Optional[int] = Field(
        alias="DEFAULT_GUILD_ID",
        description="Default guild ID for the bot to operate in",
    )
    owner_ids: list[int] = Field(
        alias="OWNER_IDS",
        description="List of user IDs for bot owners",
        default_factory=list[int],
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="allow"
    )

    @cached_property
    def default_brand_color(self) -> int:
        return int(self.default_brand_color_str.lstrip("#"), 16)
