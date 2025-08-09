@echo off
REM 🌍 Vocelio.ai Overview Service Startup Script for Windows

echo 🚀 Starting Vocelio.ai Overview Service...
echo ==================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file from example...
    copy .env.example .env
    echo ⚠️  Please configure your .env file with proper credentials
)

REM Start the service
echo 🌟 Starting Overview Service on port 8001...
python main.py

pause
