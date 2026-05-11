"""SQLAlchemy ORM models."""

from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class Item(Base):
    """Item database model."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
