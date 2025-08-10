# Vocelio Backend - Microservices Architecture

🚀 **Comprehensive FastAPI microservices platform for AI-powered voice solutions**

## 🏗️ Architecture Overview

Vocelio Backend consists of 18 microservices orchestrated through an API Gateway, providing a complete enterprise voice AI platform.

### Services Included

| Service | Port | Description |
|---------|------|-------------|
| **api-gateway** | 8000 | Central routing, authentication, load balancing |
| **overview** | 8001 | Dashboard and system overview |
| **ai-agents** | 8002 | AI agent management and conversation flow |
| **smart-campaigns** | 8003 | Campaign management and automation |
| **analytics-pro** | 8004 | Advanced analytics and reporting |
| **team-hub** | 8005 | Team collaboration and management |
| **phone-numbers** | 8006 | Phone number provisioning and management |
| **voice-lab** | 8007 | Voice synthesis and customization |
| **settings** | 8008 | User preferences and configuration |
| **flow-builder** | 8009 | Visual conversation flow designer |
| **call-center** | 8010 | Call queue and management |
| **integrations** | 8011 | Third-party integrations (CRM, tools) |
| **voice-marketplace** | 8012 | Voice model marketplace |
| **billing-pro** | 8013 | Payment processing and subscriptions |
| **developer-api** | 8014 | API keys, webhooks, SDK tools |
| **agent-store** | 8015 | AI agent marketplace |
| **compliance** | 8016 | GDPR, telecom regulations, audit trails |
| **white-label** | 8017 | Brand customization and templates |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for Railway CLI)
- Git
- PostgreSQL (or use managed database)
- Redis (for caching)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/vocelioai/vocelio-backend.git
   cd vocelio-backend
   ```

2. **Install dependencies for each service**
   ```bash
   # Install Python dependencies for all services
   for service in apps/*/; do
       echo "Installing dependencies for $(basename $service)..."
       cd "$service"
       pip install -r requirements.txt
       cd ../..
   done
   ```

3. **Configure environment variables**
   ```bash
   # Copy example environment files
   cp .env.example .env
   
   # Edit .env with your configuration
   nano .env
   ```

4. **Start all services**
   ```bash
   # Start all services in development mode
   python launch_services.py
   
   # Or start specific services
   python launch_services.py api-gateway overview ai-agents
   ```

5. **Run health checks**
   ```bash
   # Quick health check
   python health_check.py
   
   # Comprehensive test suite
   python test_microservices.py
   ```

### 🌐 Railway Deployment

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy to Railway**
   ```bash
   # Deploy all services
   python deploy_railway.py
   
   # Deploy specific services
   python deploy_railway.py api-gateway billing-pro
   ```

3. **Configure environment variables in Railway dashboard**
   - `DATABASE_URL` - PostgreSQL connection string
   - `REDIS_URL` - Redis connection string
   - `JWT_SECRET_KEY` - JWT signing secret
   - `OPENAI_API_KEY` - OpenAI API key
   - `SUPABASE_URL` - Supabase project URL
   - `SUPABASE_ANON_KEY` - Supabase anonymous key

## 📊 Testing & Monitoring

### Health Checks
```bash
# Basic connectivity test
python health_check.py

# Comprehensive API testing
python test_microservices.py

# Test specific services
python test_microservices.py api-gateway billing-pro
```

### Service Monitoring
- All services expose `/health` endpoints
- Structured logging with correlation IDs
- Metrics collection ready for Prometheus
- Distributed tracing support

## 🔐 Security Features

- **JWT-based authentication** with role-based access control
- **API key management** for external integrations
- **Rate limiting** and request throttling
- **CORS configuration** for web clients
- **Input validation** with Pydantic schemas
- **SQL injection protection** with SQLAlchemy
- **Compliance tools** for GDPR, telecom regulations

## 🏢 Enterprise Features

### Billing & Payments
- Subscription management (Stripe/PayPal integration)
- Usage-based billing and metering
- Invoice generation and payment tracking
- Revenue analytics and reporting

### White-Label Solutions
- Custom branding and themes
- Domain customization
- Template management
- Asset optimization

### Compliance & Governance
- GDPR data management
- Audit trail logging
- Telecom regulation compliance
- Automated compliance reporting

### Developer Tools
- SDK generation (Python, JavaScript, Go)
- API documentation
- Webhook management
- Testing utilities

## 🔧 Configuration

### Service Configuration
Each service has its own `railway.toml` and `requirements.txt`:

```toml
# apps/service-name/railway.toml
[build]
provider = "nixpacks"

[build.env]
PYTHON_VERSION = "3.11"

[start]
cmd = "sh -c 'python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${UVICORN_WORKERS:-2}'"
```

### API Gateway Routing
The API Gateway automatically routes requests to appropriate services:

```
/api/v1/proxy/{service}/{path} → http://service:port/{path}
```

### Database Schema
- Shared database with service-specific schemas
- Database migrations in `shared/database/migrations/`
- Connection pooling and async operations
- Read/write replica support

## 📈 Scaling & Performance

### Horizontal Scaling
- Stateless service design
- Load balancing through API Gateway
- Redis for session management
- Database connection pooling

### Performance Optimizations
- Async/await throughout
- Connection pooling
- Response caching
- Image optimization
- CDN integration ready

### Monitoring & Observability
- Structured logging with correlation IDs
- Health check endpoints
- Metrics exposure for Prometheus
- Distributed tracing ready

## 🛠️ Development Tools

### Code Quality
- Type hints throughout
- Pydantic for data validation
- SQLAlchemy for database ORM
- Black for code formatting
- mypy for static type checking

### Testing
- Comprehensive test suite
- Health check automation
- Load testing capabilities
- Integration test framework

### CI/CD
- GitHub Actions workflows
- Automated testing
- Railway deployment
- Environment promotion

## 📚 API Documentation

Each service exposes interactive API documentation:
- **Swagger UI**: `http://service:port/docs`
- **ReDoc**: `http://service:port/redoc`
- **OpenAPI spec**: `http://service:port/openapi.json`

### Key API Endpoints

#### API Gateway (`localhost:8000`)
- `GET /health` - Gateway health check
- `GET /api/v1/gateway/status` - Service status
- `GET /api/v1/gateway/services` - Available services
- `POST /api/v1/proxy/{service}/{path}` - Service proxy

#### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh
- `GET /api/v1/auth/me` - Current user info

#### Billing (`localhost:8013`)
- `GET /api/v1/billing/usage` - Usage metrics
- `POST /api/v1/subscriptions` - Create subscription
- `GET /api/v1/invoices` - List invoices

## 🔄 Data Flow

```mermaid
graph TD
    A[Client] --> B[API Gateway]
    B --> C[Auth Service]
    B --> D[Business Services]
    D --> E[Database]
    D --> F[External APIs]
    D --> G[Message Queue]
```

## 📋 Environment Variables

### Required Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port

# Authentication
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...

# Payment Processing
STRIPE_PUBLISHABLE_KEY=pk_...
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Storage
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=vocelio-storage
```

## 🆘 Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Check what's using a port
   netstat -ano | findstr :8000
   
   # Kill process if needed
   taskkill /PID <pid> /F
   ```

2. **Service won't start**
   ```bash
   # Check logs
   python launch_services.py service-name
   
   # Verify dependencies
   cd apps/service-name
   pip install -r requirements.txt
   ```

3. **Database connection issues**
   - Verify DATABASE_URL in environment
   - Check database server is running
   - Confirm network connectivity

4. **Authentication failures**
   - Verify JWT_SECRET_KEY is set
   - Check token expiration
   - Validate user permissions

### Support

- 📧 Email: support@vocelio.ai
- 📖 Documentation: [docs.vocelio.ai](https://docs.vocelio.ai)
- 🐛 Issues: [GitHub Issues](https://github.com/vocelioai/vocelio-backend/issues)

## 📄 License

Copyright © 2024 Vocelio AI. All rights reserved.

---

Built with ❤️ by the Vocelio team
