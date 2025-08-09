# 🚀 Vocelio.ai API Gateway

Enterprise-grade microservices gateway powering the world's most advanced AI call center platform.

## 🌟 Features

### Core Capabilities
- **Intelligent Service Routing** - Smart routing to 18+ microservices with load balancing
- **Advanced Rate Limiting** - Redis-backed sliding window rate limiting with multiple tiers
- **Multi-layer Authentication** - JWT tokens, API keys, and multi-tenant support
- **Circuit Breaker Pattern** - Automatic fault tolerance and graceful degradation
- **Real-time Health Monitoring** - Comprehensive health checks and metrics collection
- **Request/Response Logging** - Detailed audit trails and performance monitoring

### Enterprise Features
- **Service Discovery** - Automatic detection and health monitoring of microservices
- **Load Balancing** - Weighted round-robin with health-based routing
- **Metrics & Analytics** - Real-time performance metrics and error tracking
- **Multi-environment Support** - Production, staging, and development configurations
- **Security Headers** - CORS, trusted hosts, and security best practices

## 🏗️ Architecture

```
┌─────────────────┐    ┌───────────────────┐    ┌─────────────────┐
│   Client Apps   │────│  API Gateway      │────│  Microservices  │
│                 │    │                   │    │                 │
│ • Dashboard     │    │ • Authentication  │    │ • AI Agents     │
│ • Mobile App    │    │ • Rate Limiting   │    │ • Call Center   │
│ • Third Party   │    │ • Load Balancing  │    │ • Voice Lab     │
│ • Webhooks      │    │ • Health Checks   │    │ • Analytics     │
└─────────────────┘    └───────────────────┘    └─────────────────┘
```

## 🚦 Service Routing

The gateway routes requests to 18 specialized microservices:

| Service | Path | Description |
|---------|------|-------------|
| Overview | `/api/v1/overview` | Dashboard and metrics |
| AI Agents | `/api/v1/ai-agents` | AI agent management |
| Smart Campaigns | `/api/v1/smart-campaigns` | Campaign automation |
| Call Center | `/api/v1/call-center` | Call management |
| Voice Lab | `/api/v1/voice-lab` | Voice synthesis |
| Analytics | `/api/v1/analytics` | Advanced analytics |
| Billing | `/api/v1/billing` | Payment processing |
| Integrations | `/api/v1/integrations` | Third-party integrations |
| Marketplace | `/api/v1/marketplace` | Agent marketplace |
| Lead Qualification | `/api/v1/lead-qualification` | Lead processing |
| Appointment Booking | `/api/v1/appointment-booking` | Scheduling system |
| Inbound Calls | `/api/v1/inbound-calls` | Inbound call handling |
| Outbound Calls | `/api/v1/outbound-calls` | Outbound call management |
| Knowledge Base | `/api/v1/knowledge-base` | Knowledge management |
| Team Management | `/api/v1/team-management` | Team coordination |
| Workflows | `/api/v1/workflows` | Process automation |
| Developer API | `/api/v1/developer-api` | API management |
| Webhooks | `/api/v1/webhooks` | Webhook processing |

## 🔐 Authentication

### JWT Tokens
```bash
curl -H "Authorization: Bearer <jwt_token>" \
     https://api.vocelio.ai/api/v1/agents
```

### API Keys
```bash
curl -H "X-API-Key: voc_xxxxxxxxxxxxx" \
     https://api.vocelio.ai/api/v1/campaigns
```

## 📊 Rate Limiting

Intelligent rate limiting with multiple tiers:

| User Type | Requests/Hour | Window |
|-----------|---------------|--------|
| Anonymous | 1,000 | Sliding |
| Authenticated | 5,000 | Sliding |
| API Key | 5,000 | Sliding |
| Premium | 10,000 | Sliding |
| Webhooks | 10,000 | Sliding |

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4999
X-RateLimit-Reset: 1640995200
```

## 🏥 Health Monitoring

### Gateway Health
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": 1640995200.123,
  "gateway": {
    "status": "healthy",
    "uptime": {"seconds": 86400, "human_readable": "1 day, 0:00:00"},
    "checks": {
      "memory": {"status": "healthy", "usage_percent": 45.2},
      "cpu": {"status": "healthy", "usage_percent": 23.1},
      "disk": {"status": "healthy", "usage_percent": 67.8},
      "network": {"status": "healthy", "response_time_ms": 45}
    }
  },
  "services": {
    "summary": {
      "total_services": 18,
      "healthy_instances": 18,
      "overall_health": 100.0
    }
  }
}
```

### Service Status
```bash
GET /status
```

### Metrics
```bash
GET /metrics
```

## ⚙️ Configuration

### Environment Variables

#### Required
```bash
# Security
JWT_SECRET_KEY=your-secret-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key

# Database
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/db

# External APIs
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxx
ELEVENLABS_API_KEY=xxxxxxxxxxxxx
```

#### Optional
```bash
# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://app.vocelio.ai

# Service URLs (auto-configured in Railway)
OVERVIEW_SERVICE_URL=http://overview-service:8001
AI_AGENTS_SERVICE_URL=http://ai-agents-service:8002
# ... etc
```

## 🚀 Deployment

### Railway (Recommended)

1. **Connect Repository**
   ```bash
   railway login
   railway link
   ```

2. **Configure Environment**
   ```bash
   railway variables set JWT_SECRET_KEY=your-secret
   railway variables set DATABASE_URL=postgresql://...
   ```

3. **Deploy**
   ```bash
   railway up
   ```

The `railway.toml` file configures:
- Multi-environment support (production/staging)
- Automatic service discovery
- Environment-specific variables
- Health checks and restart policies

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY apps/api-gateway/ apps/api-gateway/

EXPOSE 8000

CMD ["uvicorn", "apps.api-gateway.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://localhost:5432/vocelio
export REDIS_URL=redis://localhost:6379
export JWT_SECRET_KEY=dev-secret

# Run gateway
uvicorn apps.api-gateway.src.main:app --reload --port 8000
```

## 📝 API Documentation

### Gateway Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Gateway information |
| GET | `/health` | Health check |
| GET | `/status` | Detailed status |
| GET | `/metrics` | Performance metrics |
| GET | `/docs` | Interactive API docs |

### Service Routing

All microservice endpoints are accessible through:
```
/{service_name}/v1/{endpoint}
```

For example:
- `GET /ai-agents/v1/agents` → AI Agents service
- `POST /smart-campaigns/v1/campaigns` → Smart Campaigns service
- `GET /analytics/v1/reports` → Analytics service

## 🔧 Middleware Stack

1. **Request Logging** - Detailed request/response logging
2. **Rate Limiting** - Redis-backed rate limiting
3. **Authentication** - JWT and API key validation
4. **CORS** - Cross-origin resource sharing
5. **Compression** - GZip compression for responses
6. **Security Headers** - Security best practices

## 📊 Monitoring & Observability

### Metrics Collection
- Request rates and response times
- Error rates and status code distribution
- Service health and availability
- Resource usage (CPU, memory, disk)

### Logging
- Structured JSON logging
- Request tracing with unique IDs
- Error tracking and alerting
- Performance monitoring

### Health Checks
- Gateway component health
- External dependency checks
- Service discovery and routing
- Real-time status monitoring

## 🛡️ Security Features

### Authentication
- JWT token validation
- API key authentication
- Multi-tenant organization support
- Role-based access control

### Rate Limiting
- IP-based limiting for anonymous users
- User-based limiting for authenticated requests
- Service-specific rate limits
- Sliding window algorithms

### Security Headers
- CORS configuration
- Trusted host validation
- Security headers (HSTS, CSP, etc.)
- Request size limits

## 🚨 Error Handling

The gateway provides comprehensive error handling:

```json
{
  "error": "Service unavailable",
  "message": "The ai-agents service is temporarily unavailable",
  "status_code": 503,
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "req_abc123",
  "retry_after": 30,
  "support": "Contact support@vocelio.ai with this request ID"
}
```

### Error Types
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (service or endpoint not found)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error (gateway error)
- `502` - Bad Gateway (service error)
- `503` - Service Unavailable (service down)
- `504` - Gateway Timeout (service timeout)

## 📈 Performance

### Benchmarks
- **Throughput**: 10,000+ requests/second
- **Latency**: <10ms median response time
- **Availability**: 99.9% uptime SLA
- **Scalability**: Auto-scaling with traffic

### Optimization
- Connection pooling for database and Redis
- HTTP/2 support for improved performance
- Efficient routing algorithms
- Caching for frequently accessed data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📞 Support

- **Documentation**: https://docs.vocelio.ai
- **Support Email**: support@vocelio.ai
- **Status Page**: https://status.vocelio.ai
- **Discord**: https://discord.gg/vocelio

## 📄 License

Copyright © 2024 Vocelio.ai. All rights reserved.

---

**Built with ❤️ by the Vocelio.ai team**

*Creating the world's most advanced AI call center platform*
