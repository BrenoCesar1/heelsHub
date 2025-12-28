"""
FastAPI main application.

REST API for AI-powered video generation and management.
"""

import schedule
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import (
    health_router,
    videos_router,
    ideas_router,
    scheduler_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown tasks including scheduler initialization.
    """
    # Startup
    print("\n" + "="*60)
    print("🚀 AI CONTENT CREATOR API - Starting Up")
    print("="*60)
    
    # Start scheduler polling task
    async def run_scheduler():
        while True:
            schedule.run_pending()
            await asyncio.sleep(1)
    
    scheduler_task = asyncio.create_task(run_scheduler())
    
    print("✅ API is ready")
    print("📚 Documentation: http://localhost:8070/docs")
    print("="*60 + "\n")
    
    yield
    
    # Shutdown
    print("\n🛑 Shutting down API...")
    scheduler_task.cancel()
    print("✅ Shutdown complete\n")


# Create FastAPI app
app = FastAPI(
    title="AI Content Creator API",
    description=(
        "REST API for AI-powered video generation and management.\n\n"
        "Features:\n"
        "- Generate videos from user ideas\n"
        "- Save and manage video ideas\n"
        "- Schedule automatic video generation\n"
        "- Integrate with Telegram and TikTok"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)
app.include_router(videos_router)
app.include_router(ideas_router)
app.include_router(scheduler_router)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8070,
        reload=True,
        log_level="info"
    )
