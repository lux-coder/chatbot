"""
AI Service Settings Module
"""

from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """AI Service settings"""
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Llama
    MODEL_DIR: str = "/models"
    LLAMA_MODEL_PATH: str = "llama.cpp"
    
    # Redis (for rate limiting and caching)
    REDIS_URL: str = "redis://redis:6379/1"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    
    # Service settings
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    WORKERS: int = 4
    
    # Rate limiting
    RATE_LIMIT_CALLS: int = 60
    RATE_LIMIT_WINDOW: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings() 