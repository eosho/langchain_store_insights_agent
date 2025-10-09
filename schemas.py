from __future__ import annotations

from typing import Optional, Literal, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import date as Date


class Insight(BaseModel):
    """Model representing a store insight or recommendation."""

    id: str = Field(..., description="Unique ID for the insight/recommendation")
    store_id: Optional[str] = Field(None, description="Store identifier")
    type: Optional[Literal["insight", "recommendation"]] = None
    title: Optional[str] = None
    text: Optional[str] = Field(None, description="Insight body text")
    score: Optional[float] = None
    ts: Optional[str] = Field(None, description="ISO8601 timestamp from source")


class InsightListResponse(BaseModel):
    """Response model for listing insights/recommendations."""

    items: List[Insight]


class ErrorResponse(BaseModel):
    """Standard error response model."""

    detail: str


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for chat endpoints."""

    question: str = Field(..., description="User's question about store insights")


class ChatResponse(BaseModel):
    """Response model for non-streaming chat endpoint."""

    answer: str = Field(..., description="Generated answer from the LLM")
    sources: List[Dict[str, Any]] = Field(
        default_factory=list, description="Source insights used"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
