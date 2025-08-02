import uuid
from pydantic import BaseModel, EmailStr, Field

# --- Base User Schemas ---
class UserBase(BaseModel):
    """
    Base user schema with common attributes.
    """
    email: EmailStr
    full_name: str | None = None

# --- Schemas for API Operations ---
class UserCreate(UserBase):
    """
    Schema for creating a new user. Includes the password.
    """
    password: str = Field(min_length=8)

class UserUpdate(UserBase):
    """
    Schema for updating an existing user. All fields are optional.
    """
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = Field(default=None, min_length=8)

# --- Schemas for Database and API Responses ---
class User(UserBase):
    """
    Schema for a user object stored in the database (or in-memory store).
    Includes the hashed password.
    """
    id: uuid.UUID
    hashed_password: str

    model_config = {"from_attributes": True}

class UserPublic(UserBase):
    """
    Schema for returning a user to the client. Excludes the password.
    """
    id: uuid.UUID

    model_config = {"from_attributes": True}
