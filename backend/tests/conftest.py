"""Test configuration and fixtures."""
import asyncio
import pytest
import pytest_asyncio
import asyncpg
from typing import AsyncGenerator, Dict
from uuid import UUID, uuid4
from tortoise import Tortoise
from app.core.config.test_settings import get_test_settings
from app.core.tenancy import tenant_context
from .database_test import init_test_db, close_test_db, cleanup_test_db

# Event Loop Fixture
@pytest.fixture(scope="session")
def event_loop():
    """Create and configure event loop for tests."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

# Database Initialization
@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_tests():
    """Initialize test database and cleanup after all tests."""
    settings = get_test_settings()
    
    # Connect to default database to create test database
    conn = await asyncpg.connect(
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database="postgres"  # Connect to default database first
    )
    
    try:
        # Terminate all connections to the test database if it exists
        await conn.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{settings.POSTGRES_DB}'
            AND pid <> pg_backend_pid();
        """)
        
        # Drop test database if it exists and create a new one
        await conn.execute(f'DROP DATABASE IF EXISTS {settings.POSTGRES_DB}')
        await conn.execute(f'CREATE DATABASE {settings.POSTGRES_DB}')
    finally:
        await conn.close()

    try:
        # Initialize Tortoise with test database
        await Tortoise.init(
            config=settings.tortoise_config
        )
        
        # Generate schemas for all models
        await Tortoise.generate_schemas(safe=True)
        
        yield
    finally:
        await Tortoise.close_connections()
        
        # Connect to default database to drop test database
        conn = await asyncpg.connect(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database="postgres"
        )
        
        try:
            # Terminate all connections to the test database
            await conn.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{settings.POSTGRES_DB}'
                AND pid <> pg_backend_pid();
            """)
            
            await conn.execute(f'DROP DATABASE IF EXISTS {settings.POSTGRES_DB}')
        finally:
            await conn.close()

@pytest_asyncio.fixture(autouse=True)
async def cleanup_after_test():
    """Clean up database after each test."""
    yield
    if Tortoise._inited:
        # Clean all tables after each test
        conn = Tortoise.get_connection("default")
        for model in Tortoise.apps.get("models").values():
            if hasattr(model, "_meta") and not model._meta.abstract:
                await conn.execute_query(f'TRUNCATE TABLE "{model._meta.db_table}" CASCADE')

# Test Data Fixtures
@pytest_asyncio.fixture
async def test_tenant_id() -> UUID:
    """Create a test tenant ID."""
    return uuid4()

@pytest_asyncio.fixture
async def test_user_data(test_tenant_id) -> Dict:
    """Create test user data."""
    unique_id = uuid4().hex[:8]
    return {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "tenant_id": test_tenant_id
    }

@pytest_asyncio.fixture
async def user_repository():
    """Create a user repository instance."""
    from app.repositories.user import UserRepository
    return UserRepository()

@pytest_asyncio.fixture
async def test_conversation_data(test_tenant_id) -> Dict:
    """Create test conversation data."""
    return {
        "title": "Test Conversation",
        "tenant_id": test_tenant_id
    }

@pytest_asyncio.fixture
async def test_message_data(test_tenant_id) -> Dict:
    """Create test message data."""
    return {
        "content": "Hello, this is a test message",
        "role": "user",
        "metadata": {"test_key": "test_value"},
        "tenant_id": test_tenant_id
    }

@pytest_asyncio.fixture
async def test_user(test_user_data):
    """Create a test user."""
    from app.models.user import User
    # Set tenant context
    token = tenant_context.set(test_user_data["tenant_id"])
    try:
        # Hash the password before creating the user
        user_data = test_user_data.copy()
        user_data["hashed_password"] = User.hash_password(user_data.pop("password"))
        user = await User.create(**user_data)
        return user
    finally:
        tenant_context.reset(token)

@pytest_asyncio.fixture
async def tenant_context_manager(test_tenant_id):
    """Create a tenant context manager for tests."""
    from app.core.tenancy import tenant_context

    class TenantContextManager:
        async def __aenter__(self):
            self.token = tenant_context.set(test_tenant_id)
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            tenant_context.reset(self.token)

    return TenantContextManager()

@pytest_asyncio.fixture
async def conversation_repository():
    """Create a conversation repository instance."""
    from app.repositories.chat import ConversationRepository
    return ConversationRepository()

@pytest_asyncio.fixture
async def message_repository():
    """Create a message repository instance."""
    from app.repositories.chat import MessageRepository
    return MessageRepository()

@pytest_asyncio.fixture
async def chat_repository():
    """Create a chat repository instance."""
    from app.repositories.chat import ChatRepository
    return ChatRepository()
