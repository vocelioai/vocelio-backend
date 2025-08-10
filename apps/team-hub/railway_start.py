#!/usr/bin/env python3
"""
Railway startup script for Vocelio.ai services
Handles PORT environment variable properly for Railway deployment
Updated: Fix PyJWT import conflict by removing python-jose
"""
import os
import sys
import subprocess

def get_port():
    """Get port from environment variable with fallback"""
    return os.environ.get('PORT', '8000')

def get_app_module():
    """Determine the app module based on service structure"""
    if os.path.exists('src/main.py'):
        return 'src.main:app'
    elif os.path.exists('main_test.py'):
        return 'main_test:app'
    elif os.path.exists('src/main_test.py'):
        return 'src.main_test:app'
    else:
        # Fallback
        return 'main:app'

def main():
    """Start uvicorn with proper configuration"""
    port = get_port()
    app_module = get_app_module()
    
    # Set PYTHONPATH to current directory
    os.environ['PYTHONPATH'] = '.'
    
    print(f"🚀 Starting Vocelio.ai service on port {port}")
    print(f"📦 App module: {app_module}")
    print(f"🐍 Python path: {os.environ.get('PYTHONPATH', 'not set')}")
    
    # Build uvicorn command
    cmd = [
        sys.executable, '-m', 'uvicorn',
        app_module,
        '--host', '0.0.0.0',
        '--port', port,
        '--workers', '1'
    ]
    
    print(f"🔧 Command: {' '.join(cmd)}")
    
    # Execute uvicorn
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting service: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
