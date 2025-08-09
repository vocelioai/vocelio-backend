# Voice Lab Service - Requirements.txt

# FastAPI Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
alembic==1.13.1
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Supabase
supabase==2.0.0
postgrest==0.13.0

# HTTP Client
httpx==0.25.2
aiohttp==3.9.1
requests==2.31.0

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
cryptography==41.0.7

# File Handling
python-magic==0.4.27
librosa==0.10.1
soundfile==0.12.1
pydub==0.25.1
mutagen==1.47.0

# Audio Processing
numpy==1.24.4
scipy==1.11.4
librosa==0.10.1
soundfile==0.12.1

# AI/ML Libraries
openai==1.3.7
anthropic==0.7.7
transformers==4.36.0
torch==2.1.1
torchaudio==2.1.1

# Image/Media Processing
pillow==10.1.0
opencv-python==4.8.1.78

# Caching & Queue
redis==5.0.1
celery==5.3.4
kombu==5.3.4

# Data Processing
pandas==2.1.4
openpyxl==3.1.2

# Monitoring & Logging
structlog==23.2.0
prometheus-client==0.19.0
sentry-sdk[fastapi]==1.38.0

# Email
fastapi-mail==1.4.1
jinja2==3.1.2

# Utilities
python-dotenv==1.0.0
click==8.1.7
rich==13.7.0
typer==0.9.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2
factory-boy==3.3.0

# Development
black==23.11.0
isort==5.12.0
flake8==6.1.0
mypy==1.7.1
pre-commit==3.6.0

# Documentation
mkdocs==1.5.3
mkdocs-material==9.4.8

# Railway Deployment
gunicorn==21.2.0
