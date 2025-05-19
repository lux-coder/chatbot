from typing import Optional, List
from uuid import UUID
from app.models.user import User
from app.repositories.base import TenantRepository
from tortoise.expressions import Q
from app.core.tenancy import get_current_tenant


class UserRepository(TenantRepository[User]):
    """Repository for managing User entities."""

    def __init__(self):
        super().__init__(User)

    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        is_superuser: bool = False,
    ) -> User:
        """Create a new user with hashed password."""
        hashed_password = User.hash_password(password)
        return await self.create(
            username=username,
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            is_superuser=is_superuser,
        )

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return await User.get_by_email(email)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return await User.get_by_username(username)

    async def update_password(self, user_id: UUID, new_password: str) -> Optional[User]:
        """Update user's password."""
        user = await self.get_by_id(user_id)
        if user:
            user.hashed_password = User.hash_password(new_password)
            await user.save(update_fields=["hashed_password"])
        return user

    async def search_users(
        self,
        search_term: str,
        limit: int = 10
    ) -> List[User]:
        """Search users by username or email."""
        return await self.model.filter(
            Q(username__icontains=search_term) | Q(email__icontains=search_term),
            tenant_id=get_current_tenant(),
            is_active=True
        ).limit(limit)

    async def update_user_profile(
        self,
        user_id: UUID,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Optional[User]:
        """Update user's profile information."""
        update_data = {}
        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name
        if email is not None:
            update_data["email"] = email

        if update_data:
            return await self.update(user_id, **update_data)
        return await self.get_by_id(user_id) 