# Pydantic Models for FastAPI

## Basic Schema Pattern

```python
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    """Shared attributes for all Item schemas."""

    title: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    price: float = Field(..., gt=0)


class ItemCreate(ItemBase):
    """Schema for creating items (no id, no timestamps)."""

    pass


class ItemUpdate(BaseModel):
    """Schema for updating items (all fields optional)."""

    title: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)


class ItemResponse(ItemBase):
    """Schema for API responses (includes id, timestamps)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    owner_id: int
```

## Field Validation

```python
from pydantic import BaseModel, EmailStr, Field, field_validator


class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    age: int = Field(..., ge=0, le=120)
    password: str = Field(..., min_length=8)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("must be alphanumeric")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("must contain uppercase")
        if not any(c.isdigit() for c in v):
            raise ValueError("must contain digit")
        return v
```

## Model Validators

```python
from pydantic import BaseModel, model_validator


class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime

    @model_validator(mode="after")
    def validate_dates(self) -> "DateRange":
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")
        return self
```

## Nested Models

```python
class Address(BaseModel):
    street: str
    city: str
    country: str
    zip_code: str


class Company(BaseModel):
    name: str
    address: Address


class UserWithCompany(BaseModel):
    username: str
    email: EmailStr
    company: Company | None = None
```

## Generic Response Wrapper

```python
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    has_next: bool


# Usage
@app.get("/items/", response_model=PaginatedResponse[ItemResponse])
def list_items(page: int = 1, page_size: int = 10):
    return PaginatedResponse(
        items=items,
        total=100,
        page=page,
        page_size=page_size,
        has_next=page * page_size < 100,
    )
```

## ORM Integration

```python
from pydantic import BaseModel, ConfigDict


class UserFromORM(BaseModel):
    """Schema that can be created from SQLAlchemy model."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    created_at: datetime


# Usage with SQLAlchemy
@app.get("/users/{user_id}", response_model=UserFromORM)
def get_user(user_id: int, db: DBDep):
    user = db.query(User).filter(User.id == user_id).first()
    return user  # Pydantic converts ORM object automatically
```

## Discriminated Unions

```python
from typing import Literal

from pydantic import BaseModel


class EmailNotification(BaseModel):
    type: Literal["email"]
    email: str
    subject: str


class SMSNotification(BaseModel):
    type: Literal["sms"]
    phone: str
    message: str


Notification = EmailNotification | SMSNotification


@app.post("/notify/")
def send_notification(notification: Notification):
    match notification:
        case EmailNotification():
            return {"sent_to": notification.email}
        case SMSNotification():
            return {"sent_to": notification.phone}
```

## Custom JSON Serialization

```python
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class Price(BaseModel):
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
        }
    )

    amount: Decimal
    currency: str
    updated_at: datetime
```

## Computed Fields

```python
from pydantic import BaseModel, computed_field


class Rectangle(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height
```

## Best Practices

- **Separate schemas**: `Base`, `Create`, `Update`, `Response`, `InDB`
- **Use `from_attributes=True`** for ORM integration
- **Validate at boundaries** — Input schemas should be strict
- **Response schemas control output** — Never leak internal fields
- **Use `Field()` for metadata** — descriptions, examples, constraints
- **Prefer `model_validator` over `@root_validator`** — Pydantic v2 pattern
