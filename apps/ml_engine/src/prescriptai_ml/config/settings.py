from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database connection settings loaded from environment variables."""

    # model_config = SettingsConfigDict(
    #     env_file=".env",
    #     env_file_encoding="utf-8",
    #     extra="ignore",
    # )

    postgres_user: str = Field(default="prescriptai_user", alias="POSTGRES_USER")
    postgres_password: str = Field(default="prescriptai_password", alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="prescriptai_db", alias="POSTGRES_DB")
    postgres_host: str = Field(default="postgres", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")

    @property
    def connection_url(self) -> str:
        """Construct the SQLAlchemy connection string."""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache(maxsize=1)
def get_db_settings() -> DatabaseSettings:
    """Return a cached singleton instance of the database settings."""
    return DatabaseSettings()