"""Test database configuration and initialization."""
import asyncio
import logging
from typing import Optional
from tortoise import Tortoise, connections
from app.core.config.test_settings import get_test_settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG level

async def init_test_db(create_schema: bool = True) -> None:
    """Initialize test database with proper error handling and connection management.
    
    Args:
        create_schema: Whether to create database schema. Defaults to True.
    """
    settings = get_test_settings()
    max_retries = 3
    retry_delay = 1  # seconds
    
    logger.debug(f"Attempting to initialize test database with settings: {settings.postgres_url}")
    
    for attempt in range(max_retries):
        try:
            # Close any existing connections
            if Tortoise._inited:
                logger.debug("Closing existing Tortoise connections")
                await Tortoise.close_connections()
            
            # Initialize Tortoise with test configuration
            logger.debug("Initializing Tortoise with config: %s", settings.tortoise_config)
            await Tortoise.init(
                config=settings.tortoise_config,
            )
            
            if create_schema:
                logger.debug("Generating database schema")
                await Tortoise.generate_schemas(safe=True)
            
            # Test the connection
            logger.debug("Testing database connection")
            conn = connections.get("default")
            result = await conn.execute_query("SELECT 1")
            logger.debug(f"Connection test result: {result}")
            
            logger.info("Test database initialized successfully")
            return
            
        except Exception as e:
            logger.error(f"Failed to initialize test database (attempt {attempt + 1}/{max_retries}): {str(e)}")
            logger.debug(f"Error details:", exc_info=True)
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("Max retries reached. Could not initialize test database.")
                raise

async def close_test_db() -> None:
    """Close test database connections with proper cleanup."""
    try:
        if Tortoise._inited:
            await Tortoise.close_connections()
        logger.info("Test database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing test database connections: {str(e)}")
        raise

async def cleanup_test_db() -> None:
    """Clean up test database tables."""
    try:
        if not Tortoise._inited:
            logger.warning("Database not initialized, skipping cleanup")
            return
            
        conn = connections.get("default")
        for model in Tortoise.apps.get("models").values():
            if hasattr(model, "_meta") and not model._meta.abstract:
                table_name = model._meta.db_table or model.__name__.lower()
                await conn.execute_query(f'TRUNCATE TABLE "{table_name}" CASCADE')
        logger.info("Test database tables cleaned up successfully")
    except Exception as e:
        logger.error(f"Error cleaning up test database: {str(e)}")
        raise 