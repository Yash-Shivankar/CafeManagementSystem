from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    APP_NAME: str
    DEBUG: bool = True

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Media / File Storage
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    MEDIA_ROOT: Path = BASE_DIR / "media"
    MEDIA_URL: str = "/media/"

    # Load .env automatically
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def create_media_dirs(self) -> None:
        """Ensure media directories exist."""
        self.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.create_media_dirs()
