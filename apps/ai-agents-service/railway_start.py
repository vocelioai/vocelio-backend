#!/usr/bin/env python3
"""
Railway deployment startup script for Enhanced AI Agents Service
Handles Railway environment variables and unified agent platform
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
    
    print(f"🤖 Starting Enhanced AI Agents Service on {host}:{port}")
    print(f"📊 Service Version: 2.0.0")
    print(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'production')}")
    print(f"🛍️ Agent Marketplace: 200+ agents available")
    print(f"🔧 Enhanced Features: Analytics, Performance Tracking, Advanced Management")
    
    # Import and run the FastAPI app - Force src/main.py (Enhanced AI Agents Service)
    try:
        from src.main import app
        print("✅ Using src/main.py (Enhanced AI Agents Service) as entry point")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=os.getenv("LOG_LEVEL", "info").lower(),
            access_log=True,
            use_colors=False  # Better for Railway logs
        )
        
    except ImportError as e:
        print(f"❌ CRITICAL: Enhanced AI Agents Service src/main.py not found: {e}")
        print("❌ DO NOT use root main.py - that's the API Gateway!")
        print("Available files in current directory:")
        import os
        for f in os.listdir("."):
            print(f"  - {f}")
        if os.path.exists("src"):
            print("Files in src directory:")
            for f in os.listdir("src"):
                print(f"  - src/{f}")
        sys.exit(1)

if __name__ == "__main__":
    main()
