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
                "pool_size": 20,
                "max_overflow": 10,
            },
        }
    },
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
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
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_POOL_MAX_OVERFLOW,
    })
    
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

async def close_database_connection() -> None:
    """Close the database connection."""
    await Tortoise.close_connections() 