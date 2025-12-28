"""Pydantic models for idea management."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class IdeaCreate(BaseModel):
    """Request model for creating a new idea."""
    title: str = Field(
        ...,
        description="Short title for the idea",
        min_length=3,
        max_length=100,
        example="Macaco Influencer da Selva"
    )
    description: str = Field(
        ...,
        description="Detailed description of the video idea",
        min_length=10,
        max_length=1000,
        example="Um macaco da quebrada que é influencer digital e mostra seu dia a dia na selva de forma cômica"
    )
    tags: Optional[list[str]] = Field(
        default=None,
        description="Tags for categorizing the idea",
        example=["comédia", "animais", "selva"]
    )


class IdeaUpdate(BaseModel):
    """Request model for updating an existing idea."""
    title: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=100
    )
    description: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=1000
    )
    tags: Optional[list[str]] = None


class IdeaResponse(BaseModel):
    """Response model for idea operations."""
    id: str = Field(
        ...,
        description="Unique identifier for the idea"
    )
    title: str
    description: str
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    videos_generated: int = Field(
        default=0,
        description="Number of videos generated from this idea"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
