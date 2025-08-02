import uuid
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# --- Base Schemas ---

class UserBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    full_name: str | None = Field(None, example="John Doe")

# --- Schemas for API Operations ---

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="a_strong_password")

class UserUpdate(BaseModel):
    full_name: str | None = Field(None, example="John Doe")
    email: EmailStr | None = Field(None, example="user@example.com")

class UserInDBBase(UserBase):
    id: uuid.UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Public Schemas (for API responses) ---

class User(UserInDBBase):
    """
    Public user data.
    """
    pass

class UserInDB(UserInDBBase):
    """
    User data including hashed password (for internal use).
    """
    hashed_password: str
