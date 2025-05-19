import pytest
import pytest_asyncio
from uuid import UUID
from app.models.user import User
from app.repositories.user import UserRepository
from app.core.tenancy import tenant_context


@pytest_asyncio.fixture
async def test_user(test_user_data, tenant_context_manager) -> User:
    """Create a test user."""
    async with tenant_context_manager:
        # Hash the password before creating the user
        user_data = test_user_data.copy()
        user_data["hashed_password"] = User.hash_password(user_data.pop("password"))
        user = await User.create(**user_data)
        return user


@pytest.mark.asyncio
class TestUserModel:
    """Test suite for User model."""

    async def test_create_user(self, test_user_data, tenant_context_manager):
        """Test user creation."""
        async with tenant_context_manager:
            user_data = test_user_data.copy()
            user_data["hashed_password"] = User.hash_password(user_data.pop("password"))
            user = await User.create(**user_data)
            assert user.username == test_user_data["username"]
            assert user.email == test_user_data["email"]
            assert user.verify_password(test_user_data["password"])
            assert user.tenant_id == test_user_data["tenant_id"]

    async def test_get_by_email(self, test_user, test_user_data, tenant_context_manager):
        """Test getting user by email."""
        async with tenant_context_manager:
            found_user = await User.get_by_email(test_user.email)
            assert found_user.id == test_user.id

    async def test_get_by_username(self, test_user, test_user_data, tenant_context_manager):
        """Test getting user by username."""
        async with tenant_context_manager:
            found_user = await User.get_by_username(test_user.username)
            assert found_user.id == test_user.id

    async def test_verify_password(self, test_user, test_user_data, tenant_context_manager):
        """Test password verification."""
        async with tenant_context_manager:
            assert test_user.verify_password(test_user_data["password"])
            assert not test_user.verify_password("wrong_password")

    async def test_full_name(self, test_user, test_user_data, tenant_context_manager):
        """Test full name property."""
        async with tenant_context_manager:
            assert test_user.full_name == f"{test_user.first_name} {test_user.last_name}"
            
            # Test without first/last name
            test_user.first_name = None
            test_user.last_name = None
            assert test_user.full_name == test_user.username

    async def test_soft_delete(self, test_user, test_user_data, tenant_context_manager):
        """Test soft delete functionality."""
        async with tenant_context_manager:
            await test_user.soft_delete()
            assert not test_user.is_active
            
            # Verify user cannot be found after soft delete
            found_user = await User.get_by_email(test_user.email)
            assert found_user is None


@pytest.mark.asyncio
class TestUserRepository:
    """Test suite for UserRepository."""

    async def test_create_user(self, user_repository, test_user_data, tenant_context_manager):
        """Test user creation through repository."""
        async with tenant_context_manager:
            user = await user_repository.create_user(
                username=test_user_data["username"],
                email=test_user_data["email"],
                password=test_user_data["password"],
                first_name=test_user_data["first_name"],
                last_name=test_user_data["last_name"]
            )
            assert user.username == test_user_data["username"]
            assert user.email == test_user_data["email"]
            assert user.verify_password(test_user_data["password"])

    async def test_get_by_email(self, user_repository, test_user, test_user_data, tenant_context_manager):
        """Test getting user by email through repository."""
        async with tenant_context_manager:
            found_user = await user_repository.get_by_email(test_user.email)
            assert found_user.id == test_user.id

    async def test_get_by_username(self, user_repository, test_user, test_user_data, tenant_context_manager):
        """Test getting user by username through repository."""
        async with tenant_context_manager:
            found_user = await user_repository.get_by_username(test_user.username)
            assert found_user.id == test_user.id

    async def test_update_password(self, user_repository, test_user, test_user_data, tenant_context_manager):
        """Test updating user password."""
        async with tenant_context_manager:
            new_password = "new_password123"
            updated_user = await user_repository.update_password(test_user.id, new_password)
            assert updated_user.verify_password(new_password)

    async def test_search_users(self, user_repository, test_user, test_user_data, tenant_context_manager):
        """Test searching users."""
        async with tenant_context_manager:
            # Search by username
            users = await user_repository.search_users(test_user.username)
            assert len(users) == 1
            assert users[0].id == test_user.id

            # Search by email
            users = await user_repository.search_users(test_user.email)
            assert len(users) == 1
            assert users[0].id == test_user.id

            # Search with no results
            users = await user_repository.search_users("nonexistent")
            assert len(users) == 0

    async def test_update_user_profile(self, user_repository, test_user, test_user_data, tenant_context_manager):
        """Test updating user profile."""
        async with tenant_context_manager:
            new_first_name = "Updated"
            new_last_name = "Name"
            new_email = "updated@example.com"

            updated_user = await user_repository.update_user_profile(
                test_user.id,
                first_name=new_first_name,
                last_name=new_last_name,
                email=new_email
            )

            assert updated_user.first_name == new_first_name
            assert updated_user.last_name == new_last_name
            assert updated_user.email == new_email 