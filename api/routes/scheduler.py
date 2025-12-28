"""Scheduler management endpoints."""

from fastapi import APIRouter, HTTPException
from typing import Optional
import schedule
from datetime import datetime

from api.models.scheduler import SchedulerConfig, SchedulerStatus, ScheduleTime
from storage.scheduler_storage import SchedulerStorage
from storage.ideas_storage import IdeasStorage
from services.video_generation.video_generation_service import VideoGenerationService

router = APIRouter(prefix="/api/scheduler", tags=["Scheduler"])

# Storage and service instances
_scheduler_storage = SchedulerStorage()
_ideas_storage = IdeasStorage()
_video_service = VideoGenerationService()

# Scheduler state
_scheduler_running = False


def _scheduled_video_generation():
    """Function called by scheduler to generate videos."""
    print("\n🕐 SCHEDULER: Running scheduled video generation")
    
    try:
        config = _scheduler_storage.get_config()
        
        # Determine what idea to use
        user_idea = None
        if config.get('use_saved_ideas'):
            if config.get('idea_id'):
                # Use specific idea
                idea = _ideas_storage.get(config['idea_id'])
                if idea:
                    user_idea = idea['description']
                    _ideas_storage.increment_video_count(config['idea_id'])
            else:
                # Use random idea
                idea = _ideas_storage.get_random()
                if idea:
                    user_idea = idea['description']
                    _ideas_storage.increment_video_count(idea['id'])
        
        # Generate video
        result = _video_service.generate_video(
            user_idea=user_idea,
            send_to_telegram=True,
            post_to_tiktok=True
        )
        
        # Record successful run
        _scheduler_storage.record_run()
        
        print(f"✅ SCHEDULER: Video generated successfully")
        print(f"   Video: {result.get('video_path')}")
        print(f"   Telegram: {result.get('telegram_sent')}")
        print(f"   TikTok: {result.get('tiktok_posted')}")
        
    except Exception as e:
        print(f"❌ SCHEDULER: Video generation failed: {e}")


def _apply_schedule(config: dict):
    """Apply schedule configuration to schedule library."""
    global _scheduler_running
    
    # Clear existing schedule
    schedule.clear()
    
    if not config.get('enabled', True):
        _scheduler_running = False
        return
    
    # Schedule jobs
    for time_str in config.get('schedule_times', []):
        schedule.every().day.at(time_str).do(_scheduled_video_generation)
        print(f"📅 Scheduled video generation at {time_str}")
    
    _scheduler_running = True


@router.post("/configure", response_model=SchedulerStatus)
async def configure_scheduler(config: SchedulerConfig):
    """
    Configure scheduler settings.
    
    Set schedule times, enable/disable scheduler, and configure
    whether to use saved ideas.
    
    Args:
        config: Scheduler configuration
        
    Returns:
        Updated scheduler status
    """
    # Convert ScheduleTime objects to strings
    time_strings = [t.to_time_string() for t in config.schedule_times]
    
    # Update storage
    updated_config = _scheduler_storage.update_config(
        enabled=config.enabled,
        schedule_times=time_strings,
        use_saved_ideas=config.use_saved_ideas,
        idea_id=config.idea_id
    )
    
    # Apply to scheduler
    _apply_schedule(updated_config)
    
    return await get_scheduler_status()


@router.get("/status", response_model=SchedulerStatus)
async def get_scheduler_status():
    """
    Get current scheduler status.
    
    Returns information about scheduler state, schedule times,
    and generation statistics.
    
    Returns:
        Scheduler status with all configuration and stats
    """
    config = _scheduler_storage.get_config()
    
    # Get next run time from schedule library
    next_run = None
    if _scheduler_running and schedule.jobs:
        next_job = min(schedule.jobs, key=lambda j: j.next_run)
        next_run = next_job.next_run.isoformat() if next_job.next_run else None
    
    return SchedulerStatus(
        enabled=config.get('enabled', True),
        running=_scheduler_running,
        schedule_times=config.get('schedule_times', []),
        next_run=next_run,
        last_run=_scheduler_storage.get_last_run(),
        total_videos_generated=_scheduler_storage.get_total_videos(),
        use_saved_ideas=config.get('use_saved_ideas', False),
        current_idea_id=config.get('idea_id')
    )


@router.post("/start")
async def start_scheduler():
    """
    Start the scheduler with current configuration.
    
    Applies saved configuration and begins scheduling video generation.
    
    Returns:
        Success message with scheduler status
    """
    config = _scheduler_storage.get_config()
    _apply_schedule(config)
    
    return {
        "message": "Scheduler started successfully",
        "status": await get_scheduler_status()
    }


@router.post("/stop")
async def stop_scheduler():
    """
    Stop the scheduler.
    
    Clears all scheduled jobs and stops automatic video generation.
    
    Returns:
        Success message
    """
    global _scheduler_running
    
    schedule.clear()
    _scheduler_running = False
    
    return {
        "message": "Scheduler stopped successfully",
        "status": await get_scheduler_status()
    }


@router.post("/run-now")
async def run_now():
    """
    Trigger an immediate video generation (bypassing schedule).
    
    Useful for testing scheduler configuration.
    
    Returns:
        Success message
    """
    try:
        _scheduled_video_generation()
        return {
            "message": "Video generation triggered successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Video generation failed: {str(e)}"
        )


# Initialize scheduler on startup
@router.on_event("startup")
async def startup_scheduler():
    """Load and apply scheduler configuration on API startup."""
    print("\n🚀 Initializing scheduler...")
    config = _scheduler_storage.get_config()
    _apply_schedule(config)
    print("✅ Scheduler initialized")
