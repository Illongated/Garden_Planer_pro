from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, validates
from app.models.base import Base

class User(Base):
    """User model."""
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise ValueError("Email cannot be empty.")
        if '@' not in email:
            raise ValueError("Invalid email address format.")
        return email.lower()

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
