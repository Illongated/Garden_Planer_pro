from datetime import datetime
from sqlalchemy import DateTime, func, Integer
from sqlalchemy.orm import as_declarative, Mapped, mapped_column, declared_attr

@as_declarative()
class Base:
    """Base class for all SQLAlchemy models."""
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        import re
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        # Simple pluralization
        if name.endswith('y'):
            return name[:-1] + 'ies'
        elif name.endswith('s'):
            return name + 'es'
        else:
            return name + 's'
