---
name: pydantic-py
description: "Pydantic v2 patterns for data validation, serialization, and settings management. Use when defining API schemas, multi-model patterns (Base/Create/Update/Response), field and model validators, discriminated unions, pydantic-settings for configuration, or ORM integration with from_attributes."
---

# Pydantic Models (Python)

Advanced Pydantic v2 patterns for type-safe data validation and serialization.

## When to Use This Skill

- Designing API request/response schemas
- Multi-model patterns (Base, Create, Update, Response, InDB)
- Custom field and model validators
- Settings management with pydantic-settings
- ORM integration (SQLAlchemy, MongoDB)
- Discriminated unions for polymorphism
- JSON Schema generation

## Prerequisites

```bash
uv add pydantic                    # Core library (v2+)
uv add pydantic-settings           # For BaseSettings (env vars, .env files)
uv add email-validator             # Optional: EmailStr type support
```

## Multi-Model Pattern

Use layered models to separate concerns between API input, output, and database storage:

```python
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field
from pydantic.functional_validators import AfterValidator


def to_camel(s: str) -> str:
    """Convert snake_case to camelCase."""
    parts = s.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class UserBase(BaseModel):
    """Shared properties across all User models."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,  # Accept both snake_case and camelCase
    )

    email: str
    full_name: str | None = None
    is_active: bool = True


class UserCreate(UserBase):
    """Properties for creating a user (input schema)."""

    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    """Properties for updating a user (all optional)."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    email: str | None = None
    full_name: str | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8)


class UserResponse(UserBase):
    """Properties returned to client (output schema)."""

    id: str
    created_at: datetime

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,  # Enable ORM mode
    )


class UserInDB(UserBase):
    """Properties stored in database (internal schema)."""

    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime | None = None
```

### Pattern Benefits

| Model | Purpose | Required Fields |
|-------|---------|-----------------|
| `Base` | Shared validation logic | Core fields |
| `Create` | API input for creation | All required + password |
| `Update` | Partial updates | All optional |
| `Response` | API output | No secrets |
| `InDB` | Database representation | Internal fields |

## Field Validators

Prefer the `Annotated` pattern for reusable validation:

```python
from typing import Annotated

from pydantic import BaseModel, Field, ValidationError
from pydantic.functional_validators import AfterValidator, BeforeValidator


def normalize_email(v: str) -> str:
    """Normalize email to lowercase."""
    return v.lower().strip()


def validate_not_empty(v: str) -> str:
    """Ensure string is not empty after stripping."""
    if not v.strip():
        raise ValueError("Field cannot be empty or whitespace")
    return v


# Reusable annotated types
Email = Annotated[str, BeforeValidator(normalize_email)]
NonEmptyStr = Annotated[str, AfterValidator(validate_not_empty)]


class Contact(BaseModel):
    email: Email
    name: NonEmptyStr = Field(min_length=1, max_length=100)
```

### Decorator Pattern (for complex logic)

```python
from pydantic import BaseModel, field_validator, model_validator


class Order(BaseModel):
    items: list[str]
    quantity: int
    discount_code: str | None = None
    total: float | None = None

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("Order must have at least one item")
        return v

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v

    @model_validator(mode="after")
    def compute_total(self) -> "Order":
        """Compute total after all fields are validated."""
        if self.total is None:
            base_price = len(self.items) * self.quantity * 10.0
            if self.discount_code == "SAVE10":
                base_price *= 0.9
            self.total = base_price
        return self
```

## Model Validators

Use `@model_validator` for cross-field validation:

```python
from pydantic import BaseModel, model_validator


class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime

    @model_validator(mode="after")
    def validate_date_order(self) -> "DateRange":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self) -> "PasswordChange":
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        if self.new_password == self.current_password:
            raise ValueError("New password must be different")
        return self
```

## Settings Management

Use `pydantic-settings` for configuration with environment variables:

```python
from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",  # For nested models: DB__HOST
        case_sensitive=False,
        extra="ignore",  # Ignore unknown env vars
    )

    # Required settings (no default = must be in env)
    database_url: SecretStr
    api_key: SecretStr

    # Optional with defaults
    debug: bool = False
    log_level: str = "INFO"
    max_connections: int = Field(default=10, ge=1, le=100)

    # Nested configuration
    redis_host: str = "localhost"
    redis_port: int = 6379


class DatabaseSettings(BaseSettings):
    """Database-specific settings with prefix."""

    model_config = SettingsConfigDict(
        env_prefix="DB_",  # DB_HOST, DB_PORT, etc.
    )

    host: str = "localhost"
    port: int = 5432
    name: str = "app"
    user: str = "postgres"
    password: SecretStr


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance (singleton pattern)."""
    return Settings()
```

## Discriminated Unions

Use discriminated unions for polymorphic types:

```python
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class CreditCard(BaseModel):
    payment_type: Literal["credit_card"] = "credit_card"
    card_number: str
    expiry: str
    cvv: str


class BankTransfer(BaseModel):
    payment_type: Literal["bank_transfer"] = "bank_transfer"
    account_number: str
    routing_number: str


class PayPal(BaseModel):
    payment_type: Literal["paypal"] = "paypal"
    email: str


# Discriminated union - Pydantic uses payment_type to determine model
PaymentMethod = Annotated[
    Union[CreditCard, BankTransfer, PayPal],
    Field(discriminator="payment_type"),
]


class Checkout(BaseModel):
    order_id: str
    payment: PaymentMethod  # Automatically validated based on payment_type
```

## ORM Integration

Use `from_attributes=True` for SQLAlchemy/ORM objects:

```python
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserORM:
    """SQLAlchemy model (simplified)."""

    def __init__(self, id: int, email: str, created_at: datetime):
        self.id = id
        self.email = email
        self.created_at = created_at


class UserSchema(BaseModel):
    """Pydantic schema that reads from ORM attributes."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    created_at: datetime


# Usage
orm_user = UserORM(id=1, email="user@example.com", created_at=datetime.now())
schema_user = UserSchema.model_validate(orm_user)
```

## Serialization

Control output format with `model_dump` and serializers:

```python
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_serializer


class Event(BaseModel):
    model_config = ConfigDict(
        ser_json_timedelta="float",  # Serialize timedelta as float seconds
    )

    name: str
    timestamp: datetime
    metadata: dict[str, Any] | None = None

    @field_serializer("timestamp")
    def serialize_timestamp(self, v: datetime) -> str:
        return v.isoformat()


event = Event(name="click", timestamp=datetime.now())

# Different serialization modes
event.model_dump()  # Python dict
event.model_dump(mode="json")  # JSON-compatible dict
event.model_dump(exclude_none=True)  # Skip None values
event.model_dump(by_alias=True)  # Use aliases
event.model_dump_json()  # JSON string
```

## Generic Models

Create reusable generic wrappers:

```python
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int
    page: int
    page_size: int

    @property
    def has_next(self) -> bool:
        return self.page * self.page_size < self.total


class User(BaseModel):
    id: int
    name: str


# Usage with concrete type
response: PaginatedResponse[User] = PaginatedResponse(
    items=[User(id=1, name="Alice")],
    total=100,
    page=1,
    page_size=10,
)
```

## ConfigDict Options

Common configuration options:

```python
from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """Model with strict validation."""

    model_config = ConfigDict(
        strict=True,  # No type coercion
        frozen=True,  # Immutable (hashable)
        extra="forbid",  # Error on unknown fields
        validate_default=True,  # Validate default values
        validate_assignment=True,  # Validate on attribute assignment
        use_enum_values=True,  # Serialize enums as values
        str_strip_whitespace=True,  # Strip whitespace from strings
        str_min_length=1,  # Minimum string length
    )

    name: str
    value: int
```

## Anti-Patterns to Avoid

| Don't | Do Instead |
|-------|------------|
| `dict` for data transfer | Typed Pydantic models |
| Manual JSON parsing | `model_validate_json()` |
| `**kwargs` in models | Explicit fields |
| Mutable default values | `Field(default_factory=list)` |
| `Optional[X] = None` everywhere | Only when truly optional |
| `Any` type | Specific types or `TypeVar` |

## References

- [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic Validators](https://docs.pydantic.dev/latest/concepts/validators/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Pydantic Serialization](https://docs.pydantic.dev/latest/concepts/serialization/)
- [Pydantic ConfigDict](https://docs.pydantic.dev/latest/api/config/)
