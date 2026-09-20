from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    DEBUG: bool = True
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    POSTGRES_DRIVER: Literal["psycopg", "psycopg2"] = "psycopg"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    MEDIA_URL_EXPIRE_SECONDS: int = 300

    CORS_ORIGINS: str = "http://localhost:5173"

    LOGIN_RATE_LIMIT_ATTEMPTS: int = 5
    LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = 300

    REFRESH_COOKIE_NAME: str = "caelum_refresh"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    TIMEZONE: str = "Asia/Kolkata"

    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    MEDIA_ROOT: Path = BASE_DIR / "media"
    MEDIA_URL: str = "/media/"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql+{self.POSTGRES_DRIVER}://"
            f"{quote_plus(self.POSTGRES_USER)}:{quote_plus(self.POSTGRES_PASSWORD)}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def cors_origins(self) -> list[str]:
        """CORS_ORIGINS parsed into a list. Never returns ['*'] — wildcard
        origins are incompatible with allow_credentials=True."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    def create_media_dirs(self) -> None:
        """Ensure media directories exist."""
        self.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.create_media_dirs()
