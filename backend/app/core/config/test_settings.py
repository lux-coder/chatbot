"""Test configuration settings."""
from pydantic import BaseModel
from typing import Optional
from functools import lru_cache


class TestSettings(BaseModel):
    """Test configuration settings.
    
    This class provides test-specific configuration,
    including database settings, connection pools, and tenant configuration.
    """
    # Database Settings
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "test_chatbot_db"
    
    # Test-specific settings
    DB_POOL_MIN_SIZE: int = 5
    DB_POOL_MAX_SIZE: int = 15
    DB_COMMAND_TIMEOUT: int = 30
    
    # Per-tenant settings
    SCHEMA_PREFIX: str = "test_tenant_"
    
    @property
    def postgres_url(self) -> str:
        """Generate the PostgreSQL connection URL for tests."""
        return f"postgres://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def tortoise_config(self) -> dict:
        """Generate Tortoise ORM configuration for tests."""
        return {
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "database": self.POSTGRES_DB,
                        "host": self.POSTGRES_HOST,
                        "password": self.POSTGRES_PASSWORD,
                        "port": self.POSTGRES_PORT,
                        "user": self.POSTGRES_USER,
                        "minsize": self.DB_POOL_MIN_SIZE,
                        "maxsize": self.DB_POOL_MAX_SIZE,
                        "command_timeout": self.DB_COMMAND_TIMEOUT,
                    },
                }
            },
            "apps": {
                "models": {
                    "models": [
                        "app.models.user",
                        "app.models.base",
                        "app.models.chat"
                    ],
                    "default_connection": "default",
                }
            },
            "use_tz": True,
            "timezone": "UTC"
        }


@lru_cache()
def get_test_settings() -> TestSettings:
    """Get cached test settings instance."""
    return TestSettings() 