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
        
        # AI Service Settings
        AI_SERVICE_URL: URL of the AI service
        AI_FALLBACK_ENABLED: Whether to enable fallback to local model
        AI_DEFAULT_MODEL: Default model to use (openai/llama)
        AI_TIMEOUT_SECONDS: Timeout for AI service requests
        AI_MAX_RETRIES: Maximum number of retries for failed requests
        AI_OPENAI_MODEL: OpenAI model to use
        AI_LLAMA_MODEL_PATH: Path to local Llama model
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

    # AI Service Settings
    AI_SERVICE_URL: str = "http://localhost:8001"
    AI_FALLBACK_ENABLED: bool = True
    AI_DEFAULT_MODEL: str = "openai"
    AI_TIMEOUT_SECONDS: float = 30.0
    AI_MAX_RETRIES: int = 3
    AI_OPENAI_MODEL: str = "gpt-3.5-turbo"
    AI_LLAMA_MODEL_PATH: Optional[str] = None
    
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