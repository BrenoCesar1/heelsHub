#!/usr/bin/env python3
"""
Run the complete AI Content Creator system.

Starts:
1. FastAPI server (API endpoints)
2. Link Downloader Bot (Telegram listener)
3. Scheduler (managed by FastAPI)
"""

import os
import sys
import signal
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """Start all services."""
    print("\n" + "="*60)
    print("🚀 AI CONTENT CREATOR - STARTING ALL SERVICES")
    print("="*60)
    
    processes = []
    
    try:
        # Start Link Downloader Bot
        print("\n📱 Starting Link Downloader Bot...")
        bot_process = subprocess.Popen(
            [sys.executable, "bots/link_downloader_bot.py"],
            cwd=project_root
        )
        processes.append(("Link Downloader Bot", bot_process))
        print("✅ Link Downloader Bot started")
        
        # Start FastAPI server
        print("\n🌐 Starting FastAPI server...")
        api_process = subprocess.Popen(
            [
                sys.executable, "-m", "uvicorn",
                "api.main:app",
                "--host", "0.0.0.0",
                "--port", "8070",
                "--reload"
            ],
            cwd=project_root
        )
        processes.append(("FastAPI Server", api_process))
        print("✅ FastAPI server started on http://localhost:8070")
        
        print("\n" + "="*60)
        print("✅ ALL SERVICES RUNNING")
        print("="*60)
        print("\n📚 API Documentation: http://localhost:8070/docs")
        print("🔍 Health Check: http://localhost:8070/health")
        print("📱 Telegram Bot: Listening for video links")
        print("\n💡 Press Ctrl+C to stop all services\n")
        
        # Wait for processes
        for name, process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping all services...")
        
        for name, process in processes:
            print(f"   Stopping {name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        print("✅ All services stopped\n")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
        # Cleanup on error
        for name, process in processes:
            try:
                process.terminate()
            except:
                pass
        
        sys.exit(1)


if __name__ == "__main__":
    main()
