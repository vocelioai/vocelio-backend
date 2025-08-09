# scripts/development/start_phone_numbers.sh
#!/bin/bash

# Start Phone Numbers Service for Development

echo "🚀 Starting Vocelio.ai Phone Numbers Service..."

# Check if .env exists
if [ ! -f "apps/phone-numbers/.env" ]; then
    echo "⚠️  .env file not found. Copying from example..."
    cp apps/phone-numbers/.env.example apps/phone-numbers/.env
    echo "📝 Please edit apps/phone-numbers/.env with your actual credentials"
    exit 1
fi

# Set environment
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Navigate to service directory
cd apps/phone-numbers

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run database migrations
echo "🗄️  Running database migrations..."
python -c "
from sqlalchemy import create_engine
from models.phone_number import Base
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
Base.metadata.create_all(bind=engine)
print('✅ Database tables created')
"

# Start the service
echo "📞 Starting Phone Numbers Service on port 8000..."
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

---

# scripts/deployment/railway_deploy_phone_numbers.sh
#!/bin/bash

# Deploy Phone Numbers Service to Railway

echo "🚀 Deploying Phone Numbers Service to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "npm install -g @railway/cli"
    exit 1
fi

# Login to Railway (if not already logged in)
railway login

# Navigate to phone-numbers service
cd apps/phone-numbers

# Deploy to Railway
echo "📡 Deploying to Railway..."
railway up --service phone-numbers

# Set environment variables (run these manually in Railway dashboard)
echo ""
echo "🔧 Don't forget to set these environment variables in Railway:"
echo "   - DATABASE_URL (from Postgres addon)"
echo "   - TWILIO_ACCOUNT_SID"
echo "   - TWILIO_AUTH_TOKEN" 
echo "   - STRIPE_SECRET_KEY"
echo "   - STRIPE_PUBLISHABLE_KEY"
echo "   - STRIPE_WEBHOOK_SECRET"
echo "   - SECRET_KEY"
echo "   - ALLOWED_HOSTS"
echo ""
echo "✅ Deployment initiated! Check Railway dashboard for status."

---

# scripts/utilities/setup_phone_numbers_service.py
#!/usr/bin/env python3
"""
Setup script for Phone Numbers Service
Creates necessary directories, files, and configurations
"""

import os
import shutil
from pathlib import Path


def create_directory_structure():
    """Create the complete directory structure for phone-numbers service"""
    
    base_dir = Path("apps/phone-numbers")
    
    directories = [
        "src",
        "src/api",
        "src/api/v1",
        "src/api/v1/endpoints",
        "src/services", 
        "src/models",
        "src/schemas",
        "src/core",
        "tests",
        "tests/unit",
        "tests/integration",
        "static",
        "logs"
    ]
    
    for directory in directories:
        dir_path = base_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files for Python packages
        if not directory.startswith("tests") and not directory in ["static", "logs"]:
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                init_file.write_text("# Phone Numbers Service\n")
    
    print("✅ Directory structure created")


def create_config_files():
    """Create configuration files"""
    
    base_dir = Path("apps/phone-numbers")
    
    # Create .env.example if it doesn't exist
    env_example = base_dir / ".env.example"
    if not env_example.exists():
        env_content = """# Phone Numbers Service Configuration
SERVICE_URL=http://localhost:8000
DEBUG=True
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/vocelio_phone_numbers

# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WEBHOOK_URL=https://api.vocelio.ai/phone-numbers/api/v1/webhooks/twilio

# Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Security
SECRET_KEY=your-secret-key
"""
        env_example.write_text(env_content)
    
    # Create .gitignore
    gitignore = base_dir / ".gitignore"
    if not gitignore.exists():
        gitignore_content = """__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

.env
.env.local
.env.development
.env.production

venv/
ENV/
env/
.venv/

.pytest_cache/
.coverage
htmlcov/

logs/
*.log
"""
        gitignore.write_text(gitignore_content)
    
    print("✅ Configuration files created")


def create_startup_script():
    """Create startup script for development"""
    
    script_content = """#!/bin/bash
# Phone Numbers Service Development Startup

echo "📞 Starting Vocelio Phone Numbers Service..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Start the service
cd src && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
    
    script_path = Path("apps/phone-numbers/start.sh")
    script_path.write_text(script_content)
    script_path.chmod(0o755)
    
    print("✅ Startup script created")


def setup_logging():
    """Setup logging configuration"""
    
    logging_config = """
import logging
import sys
from pathlib import Path

# Create logs directory
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "phone_numbers.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Set specific loggers
logging.getLogger("twilio").setLevel(logging.WARNING)
logging.getLogger("stripe").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
"""
    
    config_path = Path("apps/phone-numbers/src/core/logging_config.py")
    config_path.write_text(logging_config)
    
    print("✅ Logging configuration created")


def main():
    """Main setup function"""
    print("🏗️  Setting up Phone Numbers Service...")
    
    create_directory_structure()
    create_config_files()
    create_startup_script()
    setup_logging()
    
    print("\n🎉 Phone Numbers Service setup complete!")
    print("\n📋 Next steps:")
    print("1. Copy .env.example to .env and fill in your credentials")
    print("2. Set up your PostgreSQL database")
    print("3. Configure Twilio account and webhooks")
    print("4. Set up Stripe account and webhooks")
    print("5. Run: cd apps/phone-numbers && ./start.sh")
    print("\n📚 Documentation:")
    print("- Twilio: https://www.twilio.com/docs")
    print("- Stripe: https://stripe.com/docs")
    print("- FastAPI: https://fastapi.tiangolo.com")


if __name__ == "__main__":
    main()

---

# Makefile for Phone Numbers Service
.PHONY: help install dev test lint clean deploy

help: ## Show this help message
	@echo "Vocelio.ai Phone Numbers Service"
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	cd apps/phone-numbers && pip install -r requirements.txt

dev: ## Start development server
	cd apps/phone-numbers && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	cd apps/phone-numbers && python -m pytest tests/ -v --cov=src

lint: ## Run code linting
	cd apps/phone-numbers && flake8 src/ tests/
	cd apps/phone-numbers && black src/ tests/ --check
	cd apps/phone-numbers && isort src/ tests/ --check-only

format: ## Format code
	cd apps/phone-numbers && black src/ tests/
	cd apps/phone-numbers && isort src/ tests/

clean: ## Clean cache and temporary files
	find apps/phone-numbers -type d -name "__pycache__" -exec rm -rf {} +
	find apps/phone-numbers -type f -name "*.pyc" -delete
	rm -rf apps/phone-numbers/.pytest_cache
	rm -rf apps/phone-numbers/.coverage

migrate: ## Run database migrations
	cd apps/phone-numbers && python -c "
from sqlalchemy import create_engine
from models.phone_number import Base
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
Base.metadata.create_all(bind=engine)
print('Database tables created')
"

deploy-railway: ## Deploy to Railway
	cd apps/phone-numbers && railway up

docker-build: ## Build Docker image
	docker build -t vocelio-phone-numbers apps/phone-numbers/

docker-run: ## Run Docker container
	docker run -p 8000:8000 --env-file apps/phone-numbers/.env vocelio-phone-numbers

health-check: ## Check service health
	curl -f http://localhost:8000/health || echo "Service not responding"

logs: ## View service logs
	tail -f apps/phone-numbers/logs/phone_numbers.log