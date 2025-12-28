"""Pydantic models for video generation."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class VideoStatus(str, Enum):
    """Video generation status."""
    PENDING = "pending"
    GENERATING_SCRIPT = "generating_script"
    GENERATING_VIDEO = "generating_video"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoGenerationRequest(BaseModel):
    """Request model for video generation."""
    user_idea: str = Field(
        ...,
        description="User's video idea that will be enhanced by AI",
        min_length=10,
        max_length=500,
        example="Um macaco da quebrada que é influencer e mostra seu dia dia na selva"
    )
    send_to_telegram: bool = Field(
        default=True,
        description="Whether to send the video to Telegram"
    )
    post_to_tiktok: bool = Field(
        default=True,
        description="Whether to post the video to TikTok"
    )
    idea_id: Optional[str] = Field(
        default=None,
        description="ID of a saved idea to generate video from"
    )


class VideoGenerationResponse(BaseModel):
    """Response model for video generation."""
    task_id: str = Field(
        ...,
        description="Unique task identifier for tracking generation progress"
    )
    status: VideoStatus = Field(
        ...,
        description="Current status of video generation"
    )
    message: str = Field(
        ...,
        description="Human-readable status message"
    )
    video_path: Optional[str] = Field(
        default=None,
        description="Path to generated video file (when completed)"
    )
    telegram_sent: Optional[bool] = Field(
        default=None,
        description="Whether video was sent to Telegram"
    )
    tiktok_posted: Optional[bool] = Field(
        default=None,
        description="Whether video was posted to TikTok"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if generation failed"
    )


class VideoTaskStatus(BaseModel):
    """Model for checking video task status."""
    task_id: str
    status: VideoStatus
    progress: int = Field(ge=0, le=100, description="Progress percentage")
    message: str
    video_path: Optional[str] = None
    error: Optional[str] = None
