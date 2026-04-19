"""User model for FastAPI Users with Beanie."""

from beanie import Document
from fastapi_users_db_beanie import BeanieBaseUser, ObjectIDIDMixin
from pydantic import Field, AliasChoices
from pymongo.collation import Collation


class User(BeanieBaseUser, ObjectIDIDMixin, Document):
    """User document model for MongoDB with FastAPI Users integration.
    
    Extends BeanieBaseUser with:
    - id: ObjectId (from ObjectIDIDMixin)
    - email: str (unique, required)
    - hashed_password: str (required)
    - is_active: bool (default True)
    - is_superuser: bool (default False)
    - is_verified: bool (default False)
    
    Custom fields:
    - username: str (non-unique, full name)
    """

    username: str = Field(
        ...,
        description="Full name of the user",
        validation_alias=AliasChoices("username", "name"),
        serialization_alias="username",
    )

    class Settings:
        """Beanie document settings."""
        collection = "users"
        email_collation = Collation(locale="en", strength=2)
        indexes = [
            ("email", "unique"),  # Unique index on email
            "username",  # For sorting/filtering by username
        ]
