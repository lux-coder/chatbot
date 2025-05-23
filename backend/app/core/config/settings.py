from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
from urllib.parse import quote

class Settings(BaseSettings):
    """Application configuration settings.
    
    Attributes:
        POSTGRES_USER: Database username
        POSTGRES_PASSWORD: Database password
        POSTGRES_HOST: Database host
        POSTGRES_PORT: Database port
        POSTGRES_DB: Database name
        SCHEMA_PREFIX: Prefix for tenant schemas
        DB_POOL_SIZE: Maximum number of database connections in the pool
        
        # AI Service Settings
        AI_SERVICE_URL: URL of the AI service
        AI_FALLBACK_ENABLED: Whether to enable fallback to local model
        AI_DEFAULT_MODEL: Default model to use (openai/llama)
        AI_TIMEOUT_SECONDS: Timeout for AI service requests
        AI_MAX_RETRIES: Maximum number of retries for failed requests
        AI_RETRY_DELAY: Delay between retries in seconds
        AI_CACHE_TTL: Cache TTL for AI responses in seconds
        
        # Keycloak Settings
        KEYCLOAK_HOST: Keycloak server hostname
        KEYCLOAK_PORT: Keycloak server port
        KEYCLOAK_REALM: Keycloak realm name
        KEYCLOAK_CLIENT_ID: Client ID for this application
        KEYCLOAK_CLIENT_SECRET: Client secret for this application
        KEYCLOAK_WEBHOOK_SECRET: Secret for verifying webhook signatures
    """
    # Database Settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    
    # Per-tenant settings
    SCHEMA_PREFIX: str = "tenant_"
    
    # Connection pool settings
    DB_POOL_SIZE: int = 20  # Maximum number of connections in the pool

    # AI Service Settings
    AI_SERVICE_URL: str = "http://ai_service:8001"
    AI_FALLBACK_ENABLED: bool = True
    AI_DEFAULT_MODEL: str = "openai"
    AI_TIMEOUT_SECONDS: float = 30.0
    AI_MAX_RETRIES: int = 3
    AI_RETRY_DELAY: float = 1.0
    AI_CACHE_TTL: int = 86400  # 24 hours in seconds
    
    # Redis settings
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str
    
    # Keycloak settings
    KEYCLOAK_HOST: str = "keycloak"
    KEYCLOAK_PORT: int = 8080
    KEYCLOAK_REALM: str = "chatbot"
    KEYCLOAK_CLIENT_ID: str = "chatbot-frontend"
    KEYCLOAK_CLIENT_SECRET: str = ""
    KEYCLOAK_WEBHOOK_SECRET: str = ""  # Secret for verifying webhook signatures
    
    @property
    def postgres_url(self) -> str:
        """Generate the PostgreSQL connection URL."""
        return f"postgres://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def keycloak_url(self) -> str:
        """Generate the Keycloak server URL."""
        return f"http://{self.KEYCLOAK_HOST}:{self.KEYCLOAK_PORT}/realms/{self.KEYCLOAK_REALM}"
    
    @property
    def redis_url(self) -> str:
        """Generate the Redis connection URL."""
        encoded_password = quote(self.REDIS_PASSWORD, safe='')
        return f"redis://:{encoded_password}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings instance."""
    return Settings() 