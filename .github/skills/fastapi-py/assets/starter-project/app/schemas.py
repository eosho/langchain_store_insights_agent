"""Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    """Shared properties."""

    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    """Properties for creating an item."""

    pass


class ItemUpdate(BaseModel):
    """Properties for updating an item (all optional)."""

    title: str | None = None
    description: str | None = None


class ItemResponse(ItemBase):
    """Properties exposed in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
