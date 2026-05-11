"""API routes for items."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter()

DBDep = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=list[schemas.ItemResponse])
def list_items(db: DBDep, skip: int = 0, limit: int = 100):
    """List all items with pagination."""
    return db.query(models.Item).offset(skip).limit(limit).all()


@router.post("/", response_model=schemas.ItemResponse, status_code=201)
def create_item(item: schemas.ItemCreate, db: DBDep):
    """Create a new item."""
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=schemas.ItemResponse)
def get_item(item_id: int, db: DBDep):
    """Get a specific item by ID."""
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=schemas.ItemResponse)
def update_item(item_id: int, update: schemas.ItemUpdate, db: DBDep):
    """Update an item."""
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: DBDep):
    """Delete an item."""
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
