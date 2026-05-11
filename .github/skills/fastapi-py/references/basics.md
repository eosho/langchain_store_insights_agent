# FastAPI Basics

## Path Parameters

```python
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


# Multiple path params
@app.get("/users/{user_id}/items/{item_id}")
def read_user_item(user_id: int, item_id: int):
    return {"user_id": user_id, "item_id": item_id}


# Path with validation
from fastapi import Path


@app.get("/items/{item_id}")
def read_item(item_id: int = Path(..., gt=0, le=1000)):
    return {"item_id": item_id}
```

## Query Parameters

```python
@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    return items[skip : skip + limit]


# Optional query params
@app.get("/items/")
def read_items(q: str | None = None):
    if q:
        return {"q": q}
    return {"items": []}


# Required query params
from fastapi import Query


@app.get("/items/")
def read_items(q: str = Query(..., min_length=3, max_length=50)):
    return {"q": q}


# Multiple values
@app.get("/items/")
def read_items(tags: list[str] = Query(default=[])):
    return {"tags": tags}
```

## Request Body

```python
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: float
    description: str | None = None


@app.post("/items/")
def create_item(item: Item):
    return item


# Multiple body params
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item, user: User):
    return {"item_id": item_id, "item": item, "user": user}
```

## Form Data

```python
from fastapi import Form


@app.post("/login/")
def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}
```

## File Uploads

```python
from fastapi import File, UploadFile


@app.post("/upload/")
async def upload_file(file: UploadFile):
    contents = await file.read()
    return {"filename": file.filename, "size": len(contents)}


# Multiple files
@app.post("/uploads/")
async def upload_files(files: list[UploadFile]):
    return {"filenames": [f.filename for f in files]}
```

## Response Models

```python
class ItemOut(BaseModel):
    name: str
    price: float


@app.post("/items/", response_model=ItemOut)
def create_item(item: Item):
    return item  # Only name and price returned


# Exclude unset fields
@app.get("/items/", response_model=list[ItemOut], response_model_exclude_unset=True)
def read_items():
    return items
```

## Status Codes

```python
from fastapi import status


@app.post("/items/", status_code=status.HTTP_201_CREATED)
def create_item(item: Item):
    return item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    return None
```

## Headers

```python
from fastapi import Header


@app.get("/items/")
def read_items(user_agent: str = Header(default=None)):
    return {"User-Agent": user_agent}


# Response headers
from fastapi import Response


@app.get("/items/")
def read_items(response: Response):
    response.headers["X-Custom-Header"] = "custom-value"
    return {"items": []}
```

## Cookies

```python
from fastapi import Cookie


@app.get("/items/")
def read_items(session_id: str = Cookie(default=None)):
    return {"session_id": session_id}


# Set cookie
@app.post("/login/")
def login(response: Response):
    response.set_cookie(key="session_id", value="abc123")
    return {"message": "logged in"}
```

## Background Tasks

```python
from fastapi import BackgroundTasks


def send_email(email: str, message: str):
    # Simulate sending email
    print(f"Sending email to {email}: {message}")


@app.post("/notify/")
def notify(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email, "Welcome!")
    return {"message": "Notification scheduled"}
```

## Router Organization

```python
# routers/items.py
from fastapi import APIRouter

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/")
def read_items():
    return []


@router.get("/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


# main.py
from fastapi import FastAPI
from routers import items, users

app = FastAPI()
app.include_router(items.router)
app.include_router(users.router)
```
