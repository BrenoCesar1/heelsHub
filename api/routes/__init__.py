"""API route modules."""

from .videos import router as videos_router
from .ideas import router as ideas_router
from .scheduler import router as scheduler_router
from .health import router as health_router

__all__ = [
    'videos_router',
    'ideas_router',
    'scheduler_router',
    'health_router',
]
