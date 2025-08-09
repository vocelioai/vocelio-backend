# 📊 Vocelio.ai Smart Campaigns Service

Enterprise-grade campaign management and optimization service that powers 89+ smart campaigns with AI-driven optimization, A/B testing, and comprehensive performance analytics.

## 🚀 Features

### Smart Campaign Management
- **89+ Campaign Types** - Comprehensive campaign templates
- **AI-Powered Optimization** - Machine learning optimization engine
- **Real-Time Performance** - Live campaign metrics and analytics
- **A/B Testing Platform** - Advanced multivariate testing capabilities

### Campaign Types
- **Outbound Calls** - Direct sales and lead generation
- **Lead Nurturing** - Automated follow-up sequences
- **Appointment Setting** - Calendar booking optimization
- **Customer Retention** - Loyalty and retention campaigns
- **Survey Collection** - Feedback and data collection
- **Sales Follow-up** - Post-purchase engagement
- **Event Promotion** - Event marketing and registration
- **Product Launch** - New product introduction campaigns

### Industry Coverage
- ☀️ **Solar Energy** - Residential and commercial solar campaigns
- 🏥 **Insurance** - Life, health, and property insurance
- 🏠 **Real Estate** - Property sales and investment campaigns
- ⚕️ **Healthcare** - Medical services and telehealth
- 💰 **Financial** - Investment and financial planning
- 🚗 **Automotive** - Vehicle sales and services
- 📚 **Education** - Online courses and educational services
- 🛍️ **Retail** - E-commerce and product campaigns
- 💻 **Technology** - Software and SaaS campaigns

### Advanced Analytics
- **Revenue Attribution** - Direct campaign revenue tracking
- **Conversion Analytics** - Multi-funnel conversion analysis
- **ROI Optimization** - Return on investment maximization
- **Customer Journey** - Complete customer interaction mapping

## 🎯 Optimization Goals

- **Maximize Revenue** - Focus on revenue generation
- **Maximize Conversions** - Optimize for conversion rates
- **Minimize Cost** - Cost-efficient campaign management
- **Improve Quality** - Enhance customer satisfaction
- **Increase Reach** - Expand audience engagement

## 🛠 Technical Stack

- **FastAPI** - High-performance async API framework
- **PostgreSQL** - Enterprise-grade campaign data storage
- **Redis** - Real-time caching and performance optimization
- **Pydantic** - Data validation and serialization
- **Machine Learning** - AI-powered optimization algorithms

## 🚦 API Endpoints

### Core Campaign Management
- `GET /` - Service health check
- `GET /health` - Service health status
- `GET /campaigns` - List campaigns with advanced filtering
- `GET /campaigns/{campaign_id}` - Get specific campaign details
- `POST /campaigns` - Create new smart campaign
- `PUT /campaigns/{campaign_id}` - Update campaign configuration
- `DELETE /campaigns/{campaign_id}` - Delete campaign

### Performance & Analytics
- `GET /campaigns/{campaign_id}/performance` - Campaign performance metrics
- `POST /campaigns/{campaign_id}/optimize` - Trigger AI optimization
- `GET /analytics` - Comprehensive campaign analytics

### A/B Testing
- `POST /campaigns/{campaign_id}/ab-test` - Create A/B test
- `GET /campaigns/{campaign_id}/ab-tests` - List campaign A/B tests

### Industry Management
- `GET /industries/{industry}/campaigns` - Campaigns by industry
- `GET /industries` - Industry performance breakdown

### Campaign Types
- `GET /types` - Available campaign types
- `GET /types/{campaign_type}/campaigns` - Campaigns by type

### Batch Operations
- `POST /campaigns/batch/start` - Start multiple campaigns
- `POST /campaigns/batch/pause` - Pause multiple campaigns

## 🔧 Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start Service**
   ```bash
   python main.py
   ```

## 🌐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_HOST` | PostgreSQL host | localhost |
| `DATABASE_PORT` | PostgreSQL port | 5432 |
| `REDIS_HOST` | Redis host | localhost |
| `REDIS_PORT` | Redis port | 6379 |
| `SERVICE_PORT` | Service port | 8003 |
| `DEFAULT_DAILY_CALL_LIMIT` | Default daily call limit | 1000 |
| `AI_OPTIMIZATION_ENABLED` | Enable AI optimization | true |

## 📊 Campaign Models

### Smart Campaign
```json
{
  "id": "uuid",
  "name": "Solar Power Revolution 2025",
  "description": "High-converting solar energy campaign",
  "campaign_type": "outbound_calls",
  "industry": "solar",
  "status": "active",
  "optimization_goal": "maximize_revenue",
  "total_calls": 25847,
  "successful_calls": 8956,
  "conversion_rate": 34.7,
  "revenue_generated": 12300000,
  "cost_per_acquisition": 150.25,
  "roi_percentage": 285.7,
  "target_audience_size": 150000,
  "daily_call_limit": 2000,
  "ai_agent_ids": ["agent_solar_1", "agent_solar_2"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Campaign Performance
```json
{
  "campaign_id": "uuid",
  "calls_today": 350,
  "calls_this_week": 1850,
  "calls_this_month": 8200,
  "revenue_today": 65000,
  "revenue_this_week": 320000,
  "revenue_this_month": 1250000,
  "conversion_rate": 34.7,
  "success_rate": 89.2,
  "avg_call_duration": 6.8,
  "cost_per_lead": 125.50,
  "roi_percentage": 285.7,
  "customer_satisfaction": 9.2,
  "peak_performance_hours": [10, 11, 14, 15, 16, 19, 20]
}
```

## 🎛 Campaign Configuration

### Create Campaign Request
```json
{
  "name": "Premium Insurance Outreach",
  "description": "High-value insurance prospects",
  "campaign_type": "lead_nurturing",
  "industry": "insurance",
  "optimization_goal": "maximize_conversions",
  "target_audience_size": 95000,
  "daily_call_limit": 1500,
  "ai_agent_ids": ["agent_insurance_1"],
  "script_template": "Insurance script template...",
  "start_date": "2024-02-01T09:00:00Z",
  "end_date": "2024-03-31T18:00:00Z"
}
```

### A/B Test Configuration
```json
{
  "test_name": "Voice Optimization Test",
  "variant_a_config": {
    "voice_type": "professional_david",
    "script_variant": "formal_approach"
  },
  "variant_b_config": {
    "voice_type": "confident_mike",
    "script_variant": "confident_approach"
  },
  "traffic_split": 50.0,
  "duration_days": 14
}
```

## 🔄 Data Flow

1. **Campaign Creation** - Configure campaign parameters and target audience
2. **AI Agent Assignment** - Assign optimized AI agents to campaigns
3. **Real-Time Execution** - Execute campaigns with live performance tracking
4. **Performance Analysis** - Continuous performance monitoring and analysis
5. **AI Optimization** - Automatic performance improvements and recommendations
6. **A/B Testing** - Scientific testing of campaign variations
7. **Results Analysis** - Comprehensive reporting and insights

## 🎯 Performance Metrics

- **Conversion Rate** - Percentage of successful campaign outcomes
- **Revenue Attribution** - Direct revenue generated by campaigns
- **ROI Percentage** - Return on investment calculation
- **Cost Per Acquisition** - Average cost to acquire a customer
- **Customer Satisfaction** - Customer feedback and satisfaction scores
- **Call Efficiency** - Average call duration and success rate
- **Peak Performance Analysis** - Optimal timing and performance windows

## 🤖 AI Optimization Engine

### Optimization Types
- **Voice Optimization** - AI-powered voice selection and tuning
- **Timing Optimization** - Optimal call timing and scheduling
- **Audience Refinement** - ML-based audience targeting
- **Script Enhancement** - Dynamic script optimization
- **Performance Tuning** - Real-time performance adjustments

### Optimization Results
```json
{
  "campaign_id": "uuid",
  "optimization_type": "ai_powered_optimization",
  "improvements": {
    "conversion_rate_improvement": 6.2,
    "revenue_increase": 185000,
    "cost_reduction": 15.7
  },
  "estimated_monthly_impact": 650000,
  "confidence_score": 92.5
}
```

## 🔒 Security

- **Input Validation** - Comprehensive data validation
- **API Authentication** - JWT token-based authentication
- **Campaign Access Control** - User-based campaign permissions
- **Data Encryption** - Encrypted campaign data storage

## 📈 Monitoring

- **Health Endpoints** - Service status monitoring
- **Performance Metrics** - Campaign performance tracking
- **Error Tracking** - Exception and error monitoring
- **Resource Usage** - System resource monitoring

## 🚀 Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8003"]
```

### Railway Deployment
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

## 🔧 Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start with hot reload
python main.py

# API Documentation
open http://localhost:8003/docs
```

### Testing
```bash
# Run integration tests
python test_integration.py

# Performance testing
python test_performance.py
```

## 📚 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc

## 🤝 Integration Examples

### Frontend Integration
```javascript
// Get all campaigns
const campaigns = await fetch('http://localhost:8003/campaigns').then(r => r.json());

// Create new campaign
const newCampaign = await fetch('http://localhost:8003/campaigns', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: "Solar Revolution 2025",
    description: "High-converting solar campaign",
    campaign_type: "outbound_calls",
    industry: "solar",
    optimization_goal: "maximize_revenue",
    target_audience_size: 150000,
    daily_call_limit: 2000
  })
}).then(r => r.json());

// Optimize campaign
const optimization = await fetch(`http://localhost:8003/campaigns/${campaignId}/optimize`, {
  method: 'POST'
}).then(r => r.json());
```

### Backend Integration
```python
import httpx

# Get campaign analytics
async with httpx.AsyncClient() as client:
    response = await client.get('http://localhost:8003/analytics')
    analytics = response.json()
    
    # Create A/B test
    ab_test = await client.post(f'http://localhost:8003/campaigns/{campaign_id}/ab-test', json={
        "test_name": "Voice Optimization",
        "variant_a_config": {"voice_type": "professional_david"},
        "variant_b_config": {"voice_type": "confident_mike"},
        "traffic_split": 50.0,
        "duration_days": 14
    })
```

## 📊 Dashboard Integration

This service powers the Smart Campaigns dashboard section with:

- **89 Active Campaigns** - Real-time campaign monitoring
- **AI Optimization Insights** - Intelligent recommendations
- **Performance Analytics** - Revenue and conversion tracking
- **A/B Testing Results** - Scientific campaign optimization
- **Industry Breakdown** - Performance by industry analysis

## 🎯 Next Steps

- **Advanced ML Models** - Predictive campaign performance
- **Real-Time Personalization** - Dynamic campaign customization
- **Advanced Segmentation** - AI-powered audience segmentation
- **Behavioral Triggers** - Event-driven campaign automation
- **Cross-Campaign Analytics** - Multi-campaign performance analysis

---

**Service Port**: 8003  
**Status**: ✅ Production Ready  
**Version**: 1.0.0
