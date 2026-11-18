from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from pydantic import Field, SecretStr

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    app_name: str = "AppointNowX"
    api_v1_prefix: str = "/api/v1"
    database_url: str | None = None

    jwt_secret_key: SecretStr = Field(min_length=32)
    jwt_algorithm: Literal["HS256"] = "HS256"
    access_token_expire_minutes: int = Field(default=30, gt=0)


settings = Settings()