# apps/voice-marketplace/requirements.txt
# Voice Marketplace Service Dependencies

# FastAPI and web framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Data validation
pydantic==2.5.0
pydantic-settings==2.0.3
email-validator==2.1.0

# HTTP client for inter-service communication
httpx==0.25.2
aiohttp==3.9.1

# Payment processing
stripe==7.9.0

# File storage
boto3==1.34.0
botocore==1.34.0

# Voice processing (if needed)
librosa==0.10.1
soundfile==0.12.1
numpy==1.24.4

# Background tasks
celery==5.3.4
redis==5.0.1

# Monitoring and logging
prometheus-client==0.19.0
structlog==23.2.0
sentry-sdk[fastapi]==1.38.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-mock==3.12.0
httpx==0.25.2

# Development
black==23.11.0
flake8==6.1.0
isort==5.12.0
mypy==1.7.1

# Shared utilities (would be in shared package)
# vocelio-shared==1.0.0


# apps/voice-marketplace/Dockerfile
# Voice Marketplace Service Dockerfile

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8006

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        git \
        libsndfile1 \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules (in real implementation, this would be a package)
COPY ../../shared /app/shared

# Copy application code
COPY src/ /app/

# Create directories for voice samples and temporary files
RUN mkdir -p /app/static/voices /app/tmp

# Create non-root user
RUN adduser --disabled-password --gecos '' vocelio
RUN chown -R vocelio:vocelio /app
USER vocelio

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8006", "--reload"]


# apps/voice-marketplace/railway.toml
# Railway Configuration for Voice Marketplace Service

[build]
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "python -m uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "always"

[env]
# Service Configuration
SERVICE_NAME = "voice-marketplace"
PORT = "8006"
ENVIRONMENT = "production"

# Database (will be provided by Railway)
# DATABASE_URL = "postgresql://..."

# Authentication
# JWT_SECRET_KEY = "your-secret-key"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = "30"

# External APIs
# ELEVENLABS_API_KEY = "your-elevenlabs-key"
# RAMBLE_AI_API_KEY = "your-ramble-ai-key"
PIPER_TTS_URL = "https://piper-tts.railway.app"

# Payment Processing
# STRIPE_SECRET_KEY = "sk_test_..."
# STRIPE_WEBHOOK_SECRET = "whsec_..."

# File Storage
VOICE_SAMPLES_BUCKET = "vocelio-voice-samples"
# AWS_ACCESS_KEY_ID = "your-aws-key"
# AWS_SECRET_ACCESS_KEY = "your-aws-secret"
AWS_REGION = "us-east-1"

# Rate Limiting
RATE_LIMIT_CALLS = "1000"
RATE_LIMIT_PERIOD = "3600"

# CORS
ALLOWED_ORIGINS = "https://app.vocelio.ai,https://vocelio.ai"

# Other Services
API_GATEWAY_URL = "https://api-gateway.railway.app"
BILLING_SERVICE_URL = "https://billing-pro.railway.app"
USER_SERVICE_URL = "https://team-hub.railway.app"
ANALYTICS_SERVICE_URL = "https://analytics-pro.railway.app"

# Monitoring
ENABLE_METRICS = "true"
LOG_LEVEL = "INFO"

[services.voice-marketplace]
source = "."
buildCommand = "pip install -r requirements.txt"
startCommand = "python -m uvicorn main:app --host 0.0.0.0 --port $PORT"


# apps/voice-marketplace/src/tests/test_marketplace.py
"""
Voice Marketplace Service Tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch

from main import app
from core.config import settings
from shared.database.models import Base
from shared.database.client import get_database

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_voice_marketplace.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_database():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_database] = override_get_database

client = TestClient(app)


class TestVoiceMarketplace:
    """Test voice marketplace endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "voice-marketplace"
        assert "voice_tiers" in data
        assert "total_voices" in data
    
    def test_get_voice_tiers(self):
        """Test getting voice tiers"""
        response = client.get("/api/v1/marketplace/tiers")
        assert response.status_code == 200
        
        data = response.json()
        assert "tiers" in data
        assert "total_voices" in data
        
        # Check tier structure
        tiers = data["tiers"]
        expected_tiers = ["standard", "pro", "enterprise", "elite"]
        
        for tier in expected_tiers:
            assert tier in tiers
            assert "name" in tiers[tier]
            assert "price" in tiers[tier]
            assert "voice_count" in tiers[tier]
            assert "features" in tiers[tier]
    
    @patch('services.marketplace_service.MarketplaceService.get_voices')
    def test_get_voices_with_filters(self, mock_get_voices):
        """Test getting voices with filters"""
        # Mock response
        mock_voices = [
            {
                "id": "1",
                "voice_id": "test_voice_1",
                "name": "Test Voice 1",
                "tier": "pro",
                "language": "EN-US",
                "gender": "female",
                "price": 0.18
            }
        ]
        mock_get_voices.return_value = (mock_voices, 1)
        
        response = client.get("/api/v1/marketplace/voices?tier=pro&language=EN")
        assert response.status_code == 200
        
        data = response.json()
        assert "voices" in data
        assert "total" in data
        assert data["total"] == 1
    
    @patch('services.marketplace_service.MarketplaceService.get_voice_by_id')
    def test_get_voice_by_id(self, mock_get_voice):
        """Test getting voice by ID"""
        # Mock response
        mock_voice = {
            "id": "1",
            "voice_id": "test_voice_1",
            "name": "Test Voice 1",
            "tier": "pro",
            "language": "EN-US",
            "gender": "female",
            "price": 0.18,
            "description": "Test voice description",
            "performance": {
                "success_rate": 85.0,
                "avg_duration": 5.5,
                "satisfaction": 4.2
            },
            "rating": 4.5,
            "reviews": 100,
            "samples": 3,
            "tags": ["Professional"],
            "avatar": "👩‍💼",
            "provider": "Test Provider",
            "status": "active",
            "is_featured": False,
            "is_new": False,
            "is_popular": True,
            "created_at": "2025-01-27T10:00:00Z",
            "updated_at": "2025-01-27T10:00:00Z"
        }
        mock_get_voice.return_value = mock_voice
        
        response = client.get("/api/v1/marketplace/voices/test_voice_1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["voice_id"] == "test_voice_1"
        assert data["name"] == "Test Voice 1"
        assert data["tier"] == "pro"
    
    def test_get_voice_not_found(self):
        """Test getting non-existent voice"""
        with patch('services.marketplace_service.MarketplaceService.get_voice_by_id') as mock_get_voice:
            mock_get_voice.return_value = None
            
            response = client.get("/api/v1/marketplace/voices/nonexistent")
            assert response.status_code == 404
    
    @patch('services.marketplace_service.MarketplaceService.get_voice_comparison')
    def test_compare_voices(self, mock_compare):
        """Test voice comparison"""
        mock_comparison = {
            "voices": [
                {
                    "id": "1",
                    "voice_id": "voice_1",
                    "name": "Voice 1",
                    "tier": "pro",
                    "price": 0.18,
                    "quality": 90,
                    "rating": 4.5,
                    "performance": {"success_rate": 85, "avg_duration": 5.5, "satisfaction": 4.2}
                },
                {
                    "id": "2", 
                    "voice_id": "voice_2",
                    "name": "Voice 2",
                    "tier": "enterprise",
                    "price": 0.25,
                    "quality": 95,
                    "rating": 4.8,
                    "performance": {"success_rate": 92, "avg_duration": 6.1, "satisfaction": 4.6}
                }
            ],
            "comparison_matrix": {
                "price_range": {"min": 0.18, "max": 0.25, "avg": 0.215},
                "quality_range": {"min": 90, "max": 95, "avg": 92.5}
            },
            "recommendations": ["Best Value: Voice 1", "Highest Quality: Voice 2"]
        }
        mock_compare.return_value = mock_comparison
        
        response = client.post("/api/v1/marketplace/voices/compare", json={
            "voice_ids": ["voice_1", "voice_2"]
        })
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["voices"]) == 2
        assert "comparison_matrix" in data
        assert "recommendations" in data
    
    def test_compare_voices_invalid_request(self):
        """Test voice comparison with invalid request"""
        response = client.post("/api/v1/marketplace/voices/compare", json={
            "voice_ids": ["voice_1"]  # Only one voice - should require at least 2
        })
        assert response.status_code == 422  # Validation error
    
    def test_search_voices(self):
        """Test voice search"""
        with patch('services.marketplace_service.MarketplaceService.get_voices') as mock_get_voices:
            mock_voices = [
                {
                    "id": "1",
                    "voice_id": "search_voice_1",
                    "name": "Professional Sarah",
                    "tier": "pro",
                    "language": "EN-US",
                    "tags": ["Professional", "Clear"]
                }
            ]
            mock_get_voices.return_value = (mock_voices, 1)
            
            response = client.get("/api/v1/marketplace/search?q=professional")
            assert response.status_code == 200
            
            data = response.json()
            assert "search_results" in data
            assert data["query"] == "professional"
            assert data["total"] == 1
    
    def test_cart_preview(self):
        """Test cart preview functionality"""
        with patch('services.marketplace_service.MarketplaceService.get_voice_by_id') as mock_get_voice:
            mock_voice = Mock()
            mock_voice.voice_id = "test_voice"
            mock_voice.name = "Test Voice"
            mock_voice.tier = "pro"
            mock_voice.price = 0.18
            mock_voice.avatar = "👩‍💼"
            mock_get_voice.return_value = mock_voice
            
            response = client.get("/api/v1/purchases/cart/preview?voice_ids=test_voice")
            assert response.status_code == 200
            
            data = response.json()
            assert "cart" in data
            assert "summary" in data
            assert data["cart"]["total_items"] == 1
    
    def test_get_featured_voices(self):
        """Test getting featured voices"""
        with patch('services.marketplace_service.MarketplaceService.get_voices') as mock_get_voices:
            mock_voices = [
                {
                    "id": "1",
                    "voice_id": "featured_voice_1",
                    "name": "Featured Voice 1",
                    "tier": "elite",
                    "is_featured": True
                }
            ]
            mock_get_voices.return_value = (mock_voices, 1)
            
            response = client.get("/api/v1/marketplace/featured?limit=5")
            assert response.status_code == 200
            
            data = response.json()
            assert "featured_voices" in data
            assert "total" in data


class TestPurchaseEndpoints:
    """Test purchase-related endpoints"""
    
    def setup_method(self):
        """Setup test user authentication"""
        self.mock_user = {
            "id": "test_user_123",
            "email": "test@example.com",
            "name": "Test User"
        }
    
    @patch('shared.auth.dependencies.get_current_user')
    @patch('services.payment_service.PaymentService.create_purchase')
    def test_create_purchase(self, mock_create_purchase, mock_get_user):
        """Test creating a purchase"""
        mock_get_user.return_value = self.mock_user
        mock_create_purchase.return_value = {
            "purchase": {
                "id": "purchase_123",
                "user_id": "test_user_123",
                "total_amount": 0.36,
                "status": "pending",
                "items": []
            },
            "payment_intent": {
                "id": "pi_123",
                "client_secret": "pi_123_secret"
            }
        }
        
        response = client.post("/api/v1/purchases", json={
            "voice_ids": ["voice_1", "voice_2"],
            "payment_method": "stripe"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "purchase" in data
        assert "payment_intent" in data
        assert data["next_action"] == "complete_payment"
    
    @patch('shared.auth.dependencies.get_current_user')
    def test_create_purchase_unauthorized(self, mock_get_user):
        """Test creating purchase without authentication"""
        mock_get_user.side_effect = Exception("Authentication required")
        
        response = client.post("/api/v1/purchases", json={
            "voice_ids": ["voice_1"],
            "payment_method": "stripe"
        })
        assert response.status_code == 500  # Would be 401 with proper auth middleware
    
    @patch('shared.auth.dependencies.get_current_user')
    @patch('services.payment_service.PaymentService.get_user_purchases')
    def test_get_user_purchases(self, mock_get_purchases, mock_get_user):
        """Test getting user's purchase history"""
        mock_get_user.return_value = self.mock_user
        mock_get_purchases.return_value = {
            "purchases": [],
            "total": 0,
            "page": 1,
            "page_size": 20,
            "total_pages": 0
        }
        
        response = client.get("/api/v1/purchases")
        assert response.status_code == 200
        
        data = response.json()
        assert "purchases" in data
        assert "total" in data
        assert "page" in data


class TestReviewEndpoints:
    """Test review-related endpoints"""
    
    def setup_method(self):
        """Setup test user authentication"""
        self.mock_user = {
            "id": "test_user_123", 
            "email": "test@example.com",
            "name": "Test User"
        }
    
    @patch('shared.auth.dependencies.get_current_user')
    @patch('services.review_service.ReviewService.create_review')
    def test_create_review(self, mock_create_review, mock_get_user):
        """Test creating a review"""
        mock_get_user.return_value = self.mock_user
        mock_create_review.return_value = {
            "id": "review_123",
            "voice_id": "voice_123",
            "user_id": "test_user_123",
            "rating": 5,
            "title": "Great voice!",
            "content": "This voice works perfectly for our sales calls.",
            "is_verified": True,
            "created_at": "2025-01-27T10:00:00Z"
        }
        
        response = client.post("/api/v1/reviews", json={
            "voice_id": "voice_123",
            "rating": 5,
            "title": "Great voice!",
            "content": "This voice works perfectly for our sales calls.",
            "use_case": "Sales calls",
            "industry": "Technology"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["rating"] == 5
        assert data["title"] == "Great voice!"
        assert data["is_verified"] == True
    
    @patch('services.review_service.ReviewService.get_voice_reviews')
    def test_get_voice_reviews(self, mock_get_reviews):
        """Test getting reviews for a voice"""
        mock_get_reviews.return_value = {
            "reviews": [
                {
                    "id": "review_1",
                    "rating": 5,
                    "title": "Excellent",
                    "content": "Great voice quality",
                    "created_at": "2025-01-27T10:00:00Z"
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 20,
            "total_pages": 1,
            "average_rating": 5.0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 1}
        }
        
        response = client.get("/api/v1/reviews/voice/voice_123")
        assert response.status_code == 200
        
        data = response.json()
        assert "reviews" in data
        assert "average_rating" in data
        assert "rating_distribution" in data
        assert data["total"] == 1


class TestIntegrationScenarios:
    """Test complete user scenarios"""
    
    def setup_method(self):
        """Setup for integration tests"""
        self.mock_user = {
            "id": "integration_user_123",
            "email": "integration@example.com", 
            "name": "Integration User"
        }
    
    @patch('shared.auth.dependencies.get_current_user')
    @patch('services.marketplace_service.MarketplaceService.get_voices')
    @patch('services.payment_service.PaymentService.create_purchase')
    def test_complete_purchase_flow(self, mock_create_purchase, mock_get_voices, mock_get_user):
        """Test complete purchase flow from browsing to buying"""
        mock_get_user.return_value = self.mock_user
        
        # 1. Browse voices
        mock_voices = [
            {
                "id": "1",
                "voice_id": "integration_voice_1",
                "name": "Integration Voice 1",
                "tier": "pro",
                "price": 0.18
            }
        ]
        mock_get_voices.return_value = (mock_voices, 1)
        
        browse_response = client.get("/api/v1/marketplace/voices?tier=pro")
        assert browse_response.status_code == 200
        
        # 2. Preview cart
        with patch('services.marketplace_service.MarketplaceService.get_voice_by_id') as mock_get_voice:
            mock_voice = Mock()
            mock_voice.voice_id = "integration_voice_1"
            mock_voice.name = "Integration Voice 1" 
            mock_voice.tier = "pro"
            mock_voice.price = 0.18
            mock_voice.avatar = "🎤"
            mock_get_voice.return_value = mock_voice
            
            cart_response = client.get("/api/v1/purchases/cart/preview?voice_ids=integration_voice_1")
            assert cart_response.status_code == 200
        
        # 3. Create purchase
        mock_create_purchase.return_value = {
            "purchase": {
                "id": "integration_purchase_123",
                "user_id": "integration_user_123",
                "total_amount": 0.18,
                "status": "pending"
            },
            "payment_intent": {
                "id": "pi_integration_123",
                "client_secret": "pi_integration_123_secret"
            }
        }
        
        purchase_response = client.post("/api/v1/purchases", json={
            "voice_ids": ["integration_voice_1"],
            "payment_method": "stripe"
        })
        assert purchase_response.status_code == 200
        
        purchase_data = purchase_response.json()
        assert "purchase" in purchase_data
        assert "payment_intent" in purchase_data


if __name__ == "__main__":
    pytest.main([__file__])


# apps/voice-marketplace/.env.example
# Voice Marketplace Service Environment Variables

# Basic Configuration
SERVICE_NAME=voice-marketplace
DEBUG=false
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8006

# Database
DATABASE_URL=postgresql://user:password@localhost/vocelio_voice_marketplace
DATABASE_POOL_SIZE=20

# Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
ELEVENLABS_API_KEY=your-elevenlabs-api-key
RAMBLE_AI_API_KEY=your-ramble-ai-api-key
PIPER_TTS_URL=http://localhost:8010

# Payment Processing
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_stripe_webhook_secret

# File Storage
VOICE_SAMPLES_BUCKET=vocelio-voice-samples
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1

# Rate Limiting
RATE_LIMIT_CALLS=1000
RATE_LIMIT_PERIOD=3600

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Other Microservices
API_GATEWAY_URL=http://localhost:8000
BILLING_SERVICE_URL=http://localhost:8008
USER_SERVICE_URL=http://localhost:8009
ANALYTICS_SERVICE_URL=http://localhost:8007

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=8016
LOG_LEVEL=INFO

# Redis (for caching and background tasks)
REDIS_URL=redis://localhost:6379/0


# apps/voice-marketplace/README.md
# 🎭 Vocelio Voice Marketplace Service

The Voice Marketplace is a comprehensive microservice that manages the world's largest AI voice collection with 65+ premium voices across 4 quality tiers.

## 🌟 Features

### 🎙️ Voice Management
- **4-Tier System**: Standard ($0.08/min) → Pro ($0.18/min) → Enterprise ($0.25/min) → Elite ($0.35/min)
- **65+ Premium Voices** across multiple languages and styles
- **Advanced Filtering**: By tier, language, gender, style, rating, and price
- **Voice Comparison**: Side-by-side comparison of up to 4 voices
- **Performance Metrics**: Success rates, satisfaction scores, and usage analytics

### 🛒 Purchase System
- **Shopping Cart**: Preview costs and voice selections
- **Stripe Integration**: Secure payment processing
- **Usage Tracking**: Monitor voice usage and billing
- **Instant Activation**: Voices available immediately after purchase

### ⭐ Review System
- **User Reviews**: Rate and review purchased voices
- **Verified Purchases**: Mark reviews from actual purchasers
- **Helpfulness Voting**: Community-driven review quality
- **Rating Analytics**: Comprehensive rating distribution

### 🔍 Search & Discovery
- **Advanced Search**: Find voices by name, description, or tags
- **Featured Voices**: Curated premium voice selections
- **Trending Analysis**: Popular voices based on purchase activity
- **Category Organization**: Organized by use case and industry

## 🏗️ Architecture

### Database Models
- **VoiceListing**: Core voice information and metadata
- **Purchase/PurchaseItem**: Purchase orders and voice acquisitions
- **Review**: User reviews and ratings
- **Category**: Voice organization and filtering

### Services
- **MarketplaceService**: Voice browsing, filtering, and comparison
- **PaymentService**: Purchase processing and Stripe integration
- **ReviewService**: Review management and analytics
- **CategoryService**: Category and organization management

### API Endpoints
```
GET    /marketplace/voices          # Get filtered voices
GET    /marketplace/voices/{id}     # Get voice details
POST   /marketplace/voices/compare  # Compare voices
GET    /marketplace/tiers           # Get tier information
GET    /marketplace/stats           # Marketplace analytics
POST   /purchases                   # Create purchase
GET    /purchases                   # Get purchase history
POST   /reviews                     # Create review
GET    /reviews/voice/{id}          # Get voice reviews
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Stripe Account
- AWS S3 (for voice samples)

### Installation

1. **Clone and Setup**
```bash
cd apps/voice-marketplace
pip install -r requirements.txt
```

2. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Database Setup**
```bash
# Create database
createdb vocelio_voice_marketplace

# Run migrations
alembic upgrade head
```

4. **Start Service**
```bash
python -m uvicorn main:app --reload --port 8006
```

### Docker Deployment
```bash
# Build image
docker build -t vocelio-voice-marketplace .

# Run container
docker run -p 8006:8006 --env-file .env vocelio-voice-marketplace
```

### Railway Deployment
```bash
# Deploy to Railway
railway up

# Set environment variables
railway variables:set DATABASE_URL=postgresql://...
railway variables:set STRIPE_SECRET_KEY=sk_...
```

## 📊 Voice Tier System

### Standard Tier ($0.08/min)
- **8 Premium Voices**
- **Languages**: English, Spanish
- **Provider**: Piper TTS
- **Use Case**: Appointment setting, cold calling
- **Features**: Natural HD voice, basic emotions, fast response

### Pro Tier ($0.18/min) - Most Popular
- **12 Elite Voices**
- **Languages**: 15+ languages
- **Provider**: Ramble.AI
- **Use Case**: Sales calls, client follow-ups
- **Features**: Natural flow, advanced emotions, low latency

### Enterprise Tier ($0.25/min)
- **18 Custom Voices**
- **Languages**: 100+ languages
- **Provider**: ElevenLabs + Custom
- **Use Case**: Branded campaigns, agencies
- **Features**: Voice cloning, persona control, analytics

### Elite Tier ($0.35/min)
- **25+ Ultra Voices**
- **Languages**: 70+ languages
- **Provider**: ElevenLabs Premium
- **Use Case**: VIP clients, high-stakes calls
- **Features**: Ultra-realistic, emotional tags, real-time optimization

## 🔧 Configuration

### Key Environment Variables
```bash
# Service
PORT=8006
DATABASE_URL=postgresql://...

# Authentication
JWT_SECRET_KEY=your-secret-key

# Payment
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Voice Providers
ELEVENLABS_API_KEY=your-key
RAMBLE_AI_API_KEY=your-key

# Storage
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
VOICE_SAMPLES_BUCKET=vocelio-voices
```

## 🧪 Testing

### Run Tests
```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests/test_integration.py

# Load tests
pytest tests/test_load.py -v
```

### Test Coverage
```bash
pytest --cov=src tests/
```

## 📈 Monitoring

### Health Checks
- **Endpoint**: `GET /health`
- **Metrics**: `GET /metrics`
- **Database**: Connection and query performance
- **External APIs**: ElevenLabs, Stripe availability

### Key Metrics
- Voice browsing and search performance
- Purchase conversion rates
- Payment processing success
- Review submission rates
- Voice provider API response times

## 🔒 Security

### Authentication
- JWT-based authentication
- User session management
- Role-based access control

### Payment Security
- PCI DSS compliant (via Stripe)
- Secure payment intent handling
- Webhook signature verification

### Data Protection
- Encrypted sensitive data
- Secure API communication
- Rate limiting and DDoS protection

## 🤝 Integration

### Frontend Integration
```javascript
// Get voices with filters
const voices = await fetch('/api/v1/marketplace/voices?tier=pro&language=EN');

// Create purchase
const purchase = await fetch('/api/v1/purchases', {
  method: 'POST',
  body: JSON.stringify({
    voice_ids: ['voice_1', 'voice_2'],
    payment_method: 'stripe'
  })
});
```

### Service Communication
- **Billing Service**: Purchase notifications
- **Analytics Service**: Usage tracking
- **User Service**: Authentication and profiles
- **Call Service**: Voice activation and usage

## 📚 API Documentation

### Voice Endpoints
- Browse and filter voices
- Get detailed voice information
- Compare multiple voices
- Search voices by criteria

### Purchase Endpoints
- Create and manage purchases
- Process payments via Stripe
- Track usage and billing
- Purchase history

### Review Endpoints
- Create and update reviews
- Get voice reviews
- Vote on review helpfulness
- Review analytics

## 🚀 Deployment

### Production Checklist
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Stripe webhooks configured
- [ ] AWS S3 bucket setup
- [ ] SSL certificates installed
- [ ] Monitoring configured
- [ ] Backup strategy implemented

### Scaling Considerations
- Database connection pooling
- Redis caching for voice metadata
- CDN for voice samples
- Load balancing for high traffic
- Background job processing

## 📞 Support

For technical support or questions:
- **Documentation**: [docs.vocelio.ai](https://docs.vocelio.ai)
- **API Reference**: [api.vocelio.ai/voice-marketplace](https://api.vocelio.ai/voice-marketplace)
- **GitHub Issues**: [github.com/vocelio/issues](https://github.com/vocelio/issues)
- **Discord**: [discord.gg/vocelio](https://discord.gg/vocelio)

---

**Vocelio Voice Marketplace** - Powering the world's best AI call center platform with premium voice technology 🎭🚀