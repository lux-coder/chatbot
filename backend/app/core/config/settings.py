from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration settings.
    
    Attributes:
        POSTGRES_USER: Database username
        POSTGRES_PASSWORD: Database password
        POSTGRES_HOST: Database host
        POSTGRES_PORT: Database port
        POSTGRES_DB: Database name
        SCHEMA_PREFIX: Prefix for tenant schemas
        DB_POOL_SIZE: Connection pool size
        DB_POOL_MAX_OVERFLOW: Maximum number of connections that can be created beyond pool size
    """
    # Database Settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    
    # Per-tenant settings
    SCHEMA_PREFIX: str = "tenant_"
    
    # Connection pool settings
    DB_POOL_SIZE: int = 20
    DB_POOL_MAX_OVERFLOW: int = 10
    
    @property
    def postgres_url(self) -> str:
        """Generate the PostgreSQL connection URL."""
        return f"postgres://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings instance."""
    return Settings() 