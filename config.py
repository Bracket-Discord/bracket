from typing import  Optional 
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, Field, RedisDsn


class Settings(BaseSettings):
    database_url: PostgresDsn = Field(alias="DATABASE_URL")
    bot_token: str = Field(alias="DISCORD_BOT_TOKEN")
    debug: bool = Field(default=False)
    redis_url: RedisDsn = Field(alias="REDIS_URL")
    default_brand_color: str = Field(
        default="#7289DA", description="Default brand color for embeds",
        alias="DEFAULT_BRAND_COLOR"
    )
    default_guild_id: Optional[int] = Field(
            alias="DEFAULT_GUILD_ID",
            description="Default guild ID for the bot to operate in",
    )
    owner_ids: list[int] = Field(
        alias="OWNER_IDS",
        description="List of user IDs for bot owners",
        default_factory=list[int]
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="allow"
    )

settings = Settings()  # pyright: ignore[reportCallIssue]

print(settings.model_dump())
