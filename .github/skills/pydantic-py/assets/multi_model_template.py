"""
Multi-model pattern for API schemas.

This template demonstrates the recommended layered model pattern
for separating API input, output, and database concerns.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


def to_camel(s: str) -> str:
    """Convert snake_case to camelCase for JSON serialization."""
    parts = s.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class {{Entity}}Base(BaseModel):
    """Shared properties across all {{Entity}} models.

    Contains core fields and validation logic inherited by other models.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    is_active: bool = True


class {{Entity}}Create({{Entity}}Base):
    """Properties required when creating a {{Entity}}.

    Used as request body for POST endpoints.
    """

    # Add creation-specific fields here
    # Example: password: str = Field(min_length=8)
    pass


class {{Entity}}Update(BaseModel):
    """Properties for updating a {{Entity}} (all optional).

    Used as request body for PATCH endpoints.
    Inherits from BaseModel (not Base) to make all fields optional.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    is_active: bool | None = None


class {{Entity}}Response({{Entity}}Base):
    """Properties returned to client.

    Used as response model for API endpoints.
    Excludes sensitive fields like passwords.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,  # Enable ORM mode
    )

    id: str
    created_at: datetime
    updated_at: datetime | None = None


class {{Entity}}InDB({{Entity}}Base):
    """Properties stored in database.

    Internal model for database operations.
    May include hashed passwords or other secrets.
    """

    id: str
    created_at: datetime
    updated_at: datetime | None = None
    # Add internal fields here
    # Example: hashed_password: str
