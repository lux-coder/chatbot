from typing import Dict, Any
from tortoise import Tortoise
from app.core.config.settings import get_settings

TORTOISE_ORM: Dict[str, Any] = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "database": "",  # Will be set during initialization
                "host": "",
                "password": "",
                "port": 5432,
                "user": "",
                "min_size": 10,  # Changed from pool_size
                "max_size": 20,  # Changed from max_overflow
            },
        }
    },
    "apps": {
        "models": {
            "models": [
                "app.models.user",
                "app.models.chat",
                "app.models.base",
                "app.models.tenant",  # Add tenant model
                "app.models.bot",
            ],
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": "UTC"
}

async def initialize_database() -> None:
    """Initialize the database connection with Tortoise ORM."""
    settings = get_settings()
    
    # Update connection credentials
    TORTOISE_ORM["connections"]["default"]["credentials"].update({
        "database": settings.POSTGRES_DB,
        "host": settings.POSTGRES_HOST,
        "password": settings.POSTGRES_PASSWORD,
        "port": settings.POSTGRES_PORT,
        "user": settings.POSTGRES_USER,
        "min_size": settings.DB_POOL_SIZE // 2,  # Set min_size to half of pool size
        "max_size": settings.DB_POOL_SIZE,  # Use pool size as max_size
    })
    
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

async def close_database_connection() -> None:
    """Close the database connection."""
    await Tortoise.close_connections() 