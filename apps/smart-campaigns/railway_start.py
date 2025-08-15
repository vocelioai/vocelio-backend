#!/usr/bin/env python3
"""
Railway deployment startup script for Enhanced Smart Campaigns Service v2.0.0
Handles Railway environment variables and campaign management platform
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
    
    print(f"🎯 Starting Enhanced Smart Campaigns Service on {host}:{port}")
    print(f"📊 Service Version: 2.0.0")
    print(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'production')}")
    print(f"📋 Campaign Templates: 89+ available")
    print(f"🧪 A/B Testing: Advanced framework enabled")
    print(f"🚀 AI Optimization: Real-time analytics and insights")
    
    # Import and run the FastAPI app - try src/main.py first for enhanced version
    try:
        from src.main import app
        print("✅ Using enhanced src/main.py as entry point")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=os.getenv("LOG_LEVEL", "info").lower(),
            access_log=True,
            use_colors=False  # Better for Railway logs
        )
        
    except ImportError:
        try:
            # Fallback to main.py in root
            from main import app
            print("✅ Using main.py as entry point")
            
            uvicorn.run(
                app,
                host=host,
                port=port,
                log_level=os.getenv("LOG_LEVEL", "info").lower(),
                access_log=True,
                use_colors=False
            )
        except ImportError as e:
            print(f"❌ Could not import app: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
