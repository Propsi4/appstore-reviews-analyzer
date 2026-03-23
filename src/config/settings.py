"""Configuration settings for the Appstore Reviews Analyzer."""

# Thirdparty imports
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)


class APIConfig(BaseSettings):
    """API settings."""

    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, ge=1, le=65535, description="API port")
    reload: bool = Field(default=False, description="Enable reload")


class PostgreSQLConfig(BaseSettings):
    """PostgreSQL database settings."""

    host: str = Field(..., description="PostgreSQL database host")
    port: int = Field(default=5432, ge=1, le=65535, description="PostgreSQL database port")
    database: str = Field(..., description="PostgreSQL database name")
    user: str = Field(..., description="PostgreSQL database user")
    password: str = Field(..., description="PostgreSQL database password")
    ssl_mode: str = Field(default="prefer", description="PostgreSQL SSL mode")
    schema: str = Field(default="public", description="PostgreSQL schema name")

    def get_postgres_connection_string(self, async_driver: bool = False) -> str:
        """
        Generate PostgreSQL connection string.

        Args:
            async_driver: If True, returns asyncpg connection string, otherwise psycopg2

        Returns:
            Database connection string
        """
        driver = "postgresql+asyncpg" if async_driver else "postgresql+psycopg2"

        conn_string = f"{driver}://{self.user}:{self.password}" f"@{self.host}:{self.port}/{self.database}"

        if self.ssl_mode != "disable":
            conn_string += f"?sslmode={self.ssl_mode}"

        return conn_string


class GeminiConfig(BaseSettings):
    """Gemini API settings."""

    api_key: str = Field(..., description="Gemini API key for analysis")
    model: str = Field(default="gemini-3.1-flash-lite", description="Gemini model name")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = Field(default="Appstore Reviews Analyzer", description="Application name")
    APP_VERSION: str = Field(default="0.1.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Enable debug mode")

    api: APIConfig = Field(default_factory=APIConfig)
    gemini: GeminiConfig = Field(default_factory=GeminiConfig)
    postgres: PostgreSQLConfig = Field(default_factory=PostgreSQLConfig)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
    )


# Global settings instance
settings = Settings()
