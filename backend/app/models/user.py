from tortoise import fields
from datetime import datetime
from typing import Optional
from passlib.hash import bcrypt
from app.models.base import TenantModel


class User(TenantModel):
    """User model for authentication and user management.
    
    Attributes:
        username: Unique username for the user
        email: Unique email address
        hashed_password: Optional bcrypt hashed password (not used with Keycloak)
        first_name: User's first name
        last_name: User's last name
        is_active: Whether the user account is active
        is_superuser: Whether the user has superuser privileges
        last_login: Timestamp of last login
    """
    
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    hashed_password = fields.CharField(max_length=255, null=True)
    first_name = fields.CharField(max_length=50, null=True)
    last_name = fields.CharField(max_length=50, null=True)
    is_superuser = fields.BooleanField(default=False)
    last_login = fields.DatetimeField(null=True)

    class Meta:
        table = "users"
        ordering = ["username"]

    def __str__(self) -> str:
        return f"User(username={self.username})"

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @classmethod
    async def get_by_email(cls, email: str) -> Optional["User"]:
        """Get user by email address."""
        return await cls.get_or_none(email=email, is_active=True)

    @classmethod
    async def get_by_username(cls, username: str) -> Optional["User"]:
        """Get user by username."""
        return await cls.get_or_none(username=username, is_active=True)

    def verify_password(self, password: str) -> bool:
        """Verify if the provided password matches the hashed password."""
        if not self.hashed_password:
            return False
        return bcrypt.verify(password, self.hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.hash(password)

    async def update_last_login(self) -> None:
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        await self.save(update_fields=["last_login"]) 