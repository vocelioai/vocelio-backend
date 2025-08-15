#!/usr/bin/env python3
"""
Railway deployment startup script for Enhanced Compliance Service
Handles Railway environment variables and port configuration
"""

import os
import sys
import uvicorn
from pathlib import Path

def main():
    """Main startup function for Railway deployment"""
    
    # Add project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "src"))
    
    # Get port from Railway environment variable
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Set production environment
    os.environ.setdefault("ENVIRONMENT", "production")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    
    print(f"🔐 Starting Enhanced Compliance Service on {host}:{port}")
    print(f"📊 Service Version: 2.0.0")
    print(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'production')}")
    print(f"📋 Compliance Frameworks: 15+ supported")
    print(f"🔍 Audit Events: 18+ event types")
    
    # Import and run the FastAPI app
    try:
        from src.main import app
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=os.getenv("LOG_LEVEL", "info").lower(),
            access_log=True,
            use_colors=False  # Better for Railway logs
        )
        
    except ImportError:
        # Fallback to main.py in root if src structure doesn't work
        from main import app
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=os.getenv("LOG_LEVEL", "info").lower(),
            access_log=True,
            use_colors=False
        )

if __name__ == "__main__":
    main()
