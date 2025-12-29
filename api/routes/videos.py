"""Video generation endpoints."""

import uuid
import asyncio
from typing import Dict
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime

from api.models.video import (
    VideoGenerationRequest,
    VideoGenerationResponse,
    VideoTaskStatus,
    VideoStatus
)
from services.video_generation.video_generation_service import VideoGenerationService
from storage.ideas_storage import IdeasStorage

router = APIRouter(prefix="/api/videos", tags=["Videos"])

# In-memory task storage (consider Redis for production)
_tasks: Dict[str, VideoTaskStatus] = {}

# Service instances (lazy initialization to avoid errors when env vars are missing)
_video_service: VideoGenerationService = None
_ideas_storage: IdeasStorage = None


def _get_video_service() -> VideoGenerationService:
    """Get or create video service instance (lazy initialization)."""
    global _video_service
    if _video_service is None:
        _video_service = VideoGenerationService()
    return _video_service


def _get_ideas_storage() -> IdeasStorage:
    """Get or create ideas storage instance (lazy initialization)."""
    global _ideas_storage
    if _ideas_storage is None:
        _ideas_storage = IdeasStorage()
    return _ideas_storage


async def _generate_video_task(
    task_id: str,
    user_idea: str,
    send_to_telegram: bool,
    post_to_tiktok: bool,
    idea_id: str = None
):
    """Background task for video generation."""
    try:
        # Update status: generating script
        _tasks[task_id].status = VideoStatus.GENERATING_SCRIPT
        _tasks[task_id].progress = 25
        _tasks[task_id].message = "Generating AI script..."
        
        # Generate video (blocking call in thread pool)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            _get_video_service().generate_video,
            user_idea,
            send_to_telegram,
            post_to_tiktok,
            None
        )
        
        # Update task with results
        _tasks[task_id].status = VideoStatus.COMPLETED
        _tasks[task_id].progress = 100
        _tasks[task_id].message = "Video generation completed successfully"
        _tasks[task_id].video_path = result.get('video_path')
        
        # Increment idea counter if using saved idea
        if idea_id:
            _get_ideas_storage().increment_video_count(idea_id)
            
    except Exception as e:
        _tasks[task_id].status = VideoStatus.FAILED
        _tasks[task_id].progress = 0
        _tasks[task_id].message = "Video generation failed"
        _tasks[task_id].error = str(e)


@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a video from user idea or saved idea.
    
    The video generation happens asynchronously in the background.
    Use the returned task_id to check progress via GET /api/videos/status/{task_id}
    
    Args:
        request: Video generation request with user idea or idea_id
        
    Returns:
        Task information with task_id for tracking progress
    """
    # Validate request
    if not request.user_idea and not request.idea_id:
        raise HTTPException(
            status_code=400,
            detail="Either user_idea or idea_id must be provided"
        )
    
    # Get idea from storage if idea_id is provided
    user_idea = request.user_idea
    if request.idea_id:
        idea = _get_ideas_storage().get(request.idea_id)
        if not idea:
            raise HTTPException(
                status_code=404,
                detail=f"Idea with id {request.idea_id} not found"
            )
        user_idea = idea['description']
    
    # Create task
    task_id = str(uuid.uuid4())
    _tasks[task_id] = VideoTaskStatus(
        task_id=task_id,
        status=VideoStatus.PENDING,
        progress=0,
        message="Video generation queued"
    )
    
    # Start background task
    background_tasks.add_task(
        _generate_video_task,
        task_id,
        user_idea,
        request.send_to_telegram,
        request.post_to_tiktok,
        request.idea_id
    )
    
    return VideoGenerationResponse(
        task_id=task_id,
        status=VideoStatus.PENDING,
        message="Video generation started. Use task_id to check progress."
    )


@router.get("/status/{task_id}", response_model=VideoTaskStatus)
async def get_video_status(task_id: str):
    """
    Check the status of a video generation task.
    
    Args:
        task_id: Task identifier returned from /generate endpoint
        
    Returns:
        Current task status including progress and results
    """
    if task_id not in _tasks:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )
    
    return _tasks[task_id]


@router.get("/tasks")
async def list_tasks():
    """
    List all video generation tasks.
    
    Returns:
        List of all tasks with their current status
    """
    return {
        "total": len(_tasks),
        "tasks": list(_tasks.values())
    }


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """
    Delete a video generation task from history.
    
    Args:
        task_id: Task identifier
        
    Returns:
        Success message
    """
    if task_id not in _tasks:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )
    
    del _tasks[task_id]
    return {"message": f"Task {task_id} deleted successfully"}
