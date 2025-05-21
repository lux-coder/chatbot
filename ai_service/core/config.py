"""
AI Service Configuration Settings
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """AI Service settings"""
    
    # OpenAI
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    OPENAI_MODEL: str = Field("gpt-3.5-turbo", description="OpenAI model to use")
    
    # Llama
    MODEL_DIR: str = Field("/models", description="Directory containing Llama model")
    LLAMA_MODEL_PATH: str = Field("llama.cpp", description="Path to Llama model relative to MODEL_DIR")
    
    # Redis (for rate limiting and caching)
    REDIS_URL: str = Field("redis://localhost:6379/1", description="Redis connection string")
    REDIS_HOST: str = Field("localhost", description="Redis host")
    REDIS_PORT: int = Field(6379, description="Redis port")
    REDIS_PASSWORD: Optional[str] = Field(None, description="Redis password")
    
    # Service settings
    HOST: str = Field("0.0.0.0", description="Service host")
    PORT: int = Field(8001, description="Service port")
    WORKERS: int = Field(4, description="Number of worker processes")
    
    # Rate limiting
    RATE_LIMIT_CALLS: int = Field(60, description="Number of calls allowed per window")
    RATE_LIMIT_WINDOW: int = Field(60, description="Window size in seconds")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

def get_settings() -> Settings:
    """Get AI service settings"""
    return Settings() 