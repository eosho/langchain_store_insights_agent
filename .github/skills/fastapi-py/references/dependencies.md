# Dependency Injection

## Basic Dependencies

```python
from fastapi import Depends


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/items/")
def read_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

## Typed Dependencies with Annotated (Recommended)

```python
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

# Define reusable dependency types
DBDep = Annotated[Session, Depends(get_db)]
UserDep = Annotated[User, Depends(get_current_user)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


@app.get("/items/")
def read_items(db: DBDep, user: UserDep):
    return db.query(Item).filter(Item.owner_id == user.id).all()


@app.post("/items/")
def create_item(item: ItemCreate, db: DBDep, user: UserDep):
    return crud.create_item(db, item, user.id)
```

## Class-Based Dependencies

```python
class Paginator:
    def __init__(self, skip: int = 0, limit: int = 10):
        self.skip = skip
        self.limit = limit


@app.get("/items/")
def read_items(pagination: Paginator = Depends()):
    return items[pagination.skip : pagination.skip + pagination.limit]


# With validation
class PaginatorWithMax:
    def __init__(self, skip: int = 0, limit: int = Query(default=10, le=100)):
        self.skip = skip
        self.limit = limit
```

## Dependency with Parameters

```python
def get_item_by_id(item_id: int, db: DBDep) -> Item:
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")
    return item


ItemDep = Annotated[Item, Depends(get_item_by_id)]


@app.get("/items/{item_id}")
def read_item(item: ItemDep):
    return item


@app.put("/items/{item_id}")
def update_item(item: ItemDep, update: ItemUpdate, db: DBDep):
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    return item
```

## Dependency Factories

```python
def get_repository(model: type[Base]):
    """Factory that returns a dependency for any model."""

    def dependency(db: DBDep):
        return Repository(model, db)

    return dependency


ItemRepoDep = Annotated[Repository[Item], Depends(get_repository(Item))]
UserRepoDep = Annotated[Repository[User], Depends(get_repository(User))]


@app.get("/items/")
def read_items(repo: ItemRepoDep):
    return repo.get_all()
```

## Chained Dependencies

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(db: DBDep, token: str = Depends(oauth2_scheme)) -> User:
    user = authenticate_token(db, token)
    if not user:
        raise HTTPException(401, "Invalid token")
    return user


def get_current_active_user(user: UserDep) -> User:
    if not user.is_active:
        raise HTTPException(400, "Inactive user")
    return user


ActiveUserDep = Annotated[User, Depends(get_current_active_user)]


@app.get("/users/me")
def read_current_user(user: ActiveUserDep):
    return user
```

## Global Dependencies

```python
# Apply to all routes in app
app = FastAPI(dependencies=[Depends(verify_api_key)])


# Apply to all routes in router
router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_current_user)],
)


# Apply to specific route
@app.get("/admin/", dependencies=[Depends(require_admin)])
def admin_only():
    return {"area": "admin"}
```

## Dependency Overrides (Testing)

```python
# In tests
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return User(id=1, username="testuser", role="admin")


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# Run tests...

# Clean up
app.dependency_overrides.clear()
```

## Context Manager Dependencies

```python
from contextlib import asynccontextmanager


@asynccontextmanager
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db():
    async with get_async_db() as db:
        yield db
```

## Dependencies with Cleanup

```python
def get_http_client():
    """Dependency that cleans up after request."""
    client = httpx.Client()
    try:
        yield client
    finally:
        client.close()


HTTPClientDep = Annotated[httpx.Client, Depends(get_http_client)]


@app.get("/external/")
def call_external(client: HTTPClientDep):
    response = client.get("https://api.example.com/data")
    return response.json()
```

## Best Practices

- **Use `Annotated`** — Makes dependencies reusable and type-safe
- **Yield for cleanup** — Use generators for resources that need cleanup
- **Single responsibility** — Each dependency does one thing
- **Chain appropriately** — Build complex deps from simple ones
- **Test with overrides** — Use `dependency_overrides` in tests
- **Avoid side effects** — Dependencies should be predictable
