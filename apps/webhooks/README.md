# Webhooks Service - Vocelio AI Call Center

Comprehensive webhook management and event delivery system for the Vocelio AI Call Center platform.

## Overview

The Webhooks Service provides a powerful, reliable solution for real-time event notifications and integrations with external systems. This service handles the complete webhook lifecycle from event publishing to delivery tracking, retry mechanisms, and comprehensive analytics.

## Key Features

### 🔄 **Event-Driven Architecture**
- **Real-Time Events**: Instant notification of system events
- **Event Publishing**: Programmatic event publishing API
- **Event Filtering**: Advanced filtering based on payload content
- **Event Transformation**: Custom payload transformation and formatting
- **Event Routing**: Intelligent routing to multiple endpoints
- **Event Replay**: Ability to replay failed or missed events

### 🎯 **Webhook Management**
- **Endpoint Configuration**: Flexible webhook endpoint setup
- **Multi-Method Support**: GET, POST, PUT, PATCH, DELETE methods
- **Custom Headers**: Configurable HTTP headers per endpoint
- **Authentication**: Multiple authentication methods (HMAC, JWT, API Key)
- **Rate Limiting**: Per-endpoint rate limiting controls
- **Environment Management**: Development, staging, production environments

### 🔒 **Security & Authentication**
- **HMAC Signatures**: SHA-256 and SHA-1 signature verification
- **JWT Support**: JSON Web Token authentication
- **API Key Authentication**: Simple API key-based auth
- **Custom Headers**: Secure header-based authentication
- **IP Whitelisting**: Restrict delivery to approved IP ranges
- **SSL/TLS Verification**: Ensure secure HTTPS delivery

### 🔄 **Reliable Delivery**
- **Retry Mechanisms**: Configurable retry policies with exponential backoff
- **Dead Letter Queue**: Handle permanently failed deliveries
- **Delivery Tracking**: Comprehensive delivery status monitoring
- **Timeout Handling**: Configurable request timeouts
- **Circuit Breaker**: Automatic endpoint health monitoring
- **Failover Support**: Alternative endpoint configuration

### 📊 **Advanced Analytics**
- **Delivery Metrics**: Success rates, response times, error rates
- **Endpoint Performance**: Per-endpoint analytics and health monitoring
- **Event Analytics**: Event type distribution and performance
- **Error Analysis**: Detailed error breakdown and troubleshooting
- **Trend Analysis**: Historical performance trends and forecasting
- **Real-Time Dashboards**: Live monitoring and alerting

### 🎨 **Template System**
- **Payload Templates**: Jinja2-based payload transformation
- **Header Templates**: Dynamic header generation
- **Event-Specific Templates**: Templates per event type
- **Template Testing**: Built-in template testing and validation
- **Version Control**: Template versioning and rollback
- **Sample Data**: Template testing with sample payloads

## Supported Event Types

### Call Center Events
- `call.started` - Call initiated
- `call.ended` - Call completed
- `call.answered` - Call answered by agent
- `call.missed` - Call missed or abandoned
- `call.transferred` - Call transferred between agents
- `call.recording_available` - Call recording ready

### Lead Management Events
- `lead.created` - New lead created
- `lead.updated` - Lead information updated
- `lead.converted` - Lead successfully converted
- `lead.lost` - Lead marked as lost
- `lead.assigned` - Lead assigned to agent

### Appointment Events
- `appointment.scheduled` - New appointment scheduled
- `appointment.confirmed` - Appointment confirmed by customer
- `appointment.cancelled` - Appointment cancelled
- `appointment.completed` - Appointment completed
- `appointment.rescheduled` - Appointment rescheduled
- `appointment.reminder_sent` - Reminder notification sent

### Agent Events
- `agent.online` - Agent came online
- `agent.offline` - Agent went offline
- `agent.busy` - Agent status changed to busy
- `agent.available` - Agent became available
- `agent.performance_updated` - Agent metrics updated

### Campaign Events
- `campaign.started` - Campaign launched
- `campaign.completed` - Campaign finished
- `campaign.paused` - Campaign paused
- `campaign.performance_updated` - Campaign metrics updated

### Notification Events
- `notification.sent` - Notification dispatched
- `notification.delivered` - Notification delivered
- `notification.clicked` - Notification clicked
- `notification.failed` - Notification delivery failed

### System Events
- `system.health_alert` - System health issue detected
- `system.maintenance` - Maintenance mode activated
- `system.error` - System error occurred
- `system.backup_completed` - Backup operation completed

### Integration Events
- `crm.sync_completed` - CRM synchronization completed
- `crm.sync_failed` - CRM synchronization failed
- `api.rate_limit_exceeded` - API rate limit exceeded
- `api.error` - API error occurred

## API Endpoints

### Webhook Endpoint Management
- `GET /endpoints` - List webhook endpoints with filtering
- `GET /endpoints/{id}` - Get specific webhook endpoint
- `POST /endpoints` - Create new webhook endpoint
- `PUT /endpoints/{id}` - Update existing webhook endpoint
- `DELETE /endpoints/{id}` - Delete webhook endpoint
- `PUT /endpoints/{id}/status` - Update endpoint status
- `POST /endpoints/{id}/test` - Test webhook endpoint

### Webhook Delivery Management
- `GET /deliveries` - List webhook deliveries with filtering
- `GET /deliveries/{id}` - Get specific webhook delivery
- `POST /deliveries/retry/{id}` - Retry failed webhook delivery

### Event Publishing
- `POST /events/publish` - Publish webhook event to trigger deliveries

### Template Management
- `GET /templates` - List webhook templates
- `GET /templates/{id}` - Get specific webhook template
- `POST /templates` - Create new webhook template
- `POST /templates/{id}/test` - Test webhook template

### Analytics
- `GET /analytics/overview` - Comprehensive webhook analytics
- `GET /analytics/trends` - Webhook delivery trends over time

## Authentication Methods

### HMAC SHA-256 Signature
```python
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={expected}" == signature
```

### JWT Authentication
```python
import jwt

def verify_jwt_token(token, secret):
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except jwt.InvalidTokenError:
        return None
```

### API Key Authentication
```http
POST /webhook/endpoint
X-API-Key: your_api_key_here
Content-Type: application/json
```

## Webhook Payload Structure

### Standard Payload Format
```json
{
  "event_type": "lead.created",
  "event_id": "evt_123456789",
  "timestamp": "2025-08-05T17:30:00Z",
  "data": {
    "lead": {
      "id": "lead_123",
      "name": "John Doe",
      "email": "john.doe@example.com",
      "phone": "+1-555-0123",
      "source": "website",
      "score": 85,
      "created_at": "2025-08-05T17:30:00Z"
    },
    "agent": {
      "id": "agent_456",
      "name": "Sarah Johnson",
      "email": "sarah@vocelio.com"
    }
  },
  "metadata": {
    "source_service": "lead_management",
    "version": "1.0",
    "retry_count": 0
  }
}
```

### Call Event Payload
```json
{
  "event_type": "call.ended",
  "event_id": "call_789",
  "timestamp": "2025-08-05T18:00:00Z",
  "data": {
    "call": {
      "id": "call_789",
      "duration": 450,
      "outcome": "completed",
      "recording_url": "https://recordings.vocelio.com/call_789.mp3",
      "started_at": "2025-08-05T17:52:30Z",
      "ended_at": "2025-08-05T18:00:00Z"
    },
    "customer": {
      "id": "customer_456",
      "name": "Jane Smith",
      "phone": "+1-555-0789"
    },
    "agent": {
      "id": "agent_123",
      "name": "Mike Wilson"
    }
  }
}
```

## Filtering and Transformation

### Event Filters
```json
{
  "field_path": "data.lead.score",
  "operator": "greater_than",
  "value": 80,
  "case_sensitive": false
}
```

### Payload Transformation
```json
{
  "enabled": true,
  "template": {
    "crm_lead": {
      "external_id": "{{ data.lead.id }}",
      "contact_name": "{{ data.lead.name }}",
      "email_address": "{{ data.lead.email }}",
      "phone_number": "{{ data.lead.phone }}",
      "lead_score": "{{ data.lead.score }}",
      "assigned_rep": "{{ data.agent.name }}"
    },
    "timestamp": "{{ timestamp }}",
    "source": "vocelio_ai_platform"
  }
}
```

## Retry Configuration

### Exponential Backoff Policy
```json
{
  "enabled": true,
  "max_attempts": 5,
  "initial_delay_seconds": 1,
  "max_delay_seconds": 300,
  "backoff_multiplier": 2.0,
  "retry_on_status_codes": [408, 429, 500, 502, 503, 504]
}
```

### Retry Schedule Example
- Attempt 1: Immediate
- Attempt 2: 1 second delay
- Attempt 3: 2 second delay
- Attempt 4: 4 second delay
- Attempt 5: 8 second delay (final attempt)

## Integration Examples

### CRM Integration
```python
# Create webhook endpoint for CRM sync
webhook_endpoint = {
    "name": "Salesforce Lead Sync",
    "url": "https://api.salesforce.com/webhooks/leads",
    "events": ["lead.created", "lead.updated", "lead.converted"],
    "http_method": "POST",
    "secret": "salesforce_webhook_secret",
    "signature_method": "hmac_sha256",
    "custom_headers": {
        "Authorization": "Bearer sf_token_123",
        "X-Source": "Vocelio"
    },
    "transformation": {
        "enabled": true,
        "template": "salesforce_lead_template"
    }
}
```

### Slack Notifications
```python
# Create Slack notification webhook
slack_webhook = {
    "name": "Slack Alerts",
    "url": "https://hooks.slack.com/services/T123/B456/xyz",
    "events": ["system.health_alert", "system.error"],
    "transformation": {
        "enabled": true,
        "template": {
            "text": "🚨 Alert: {{ event_type }}",
            "attachments": [{
                "color": "danger",
                "fields": [{
                    "title": "Event",
                    "value": "{{ event_type }}",
                    "short": true
                }, {
                    "title": "Time",
                    "value": "{{ timestamp }}",
                    "short": true
                }]
            }]
        }
    }
}
```

### Analytics Dashboard
```python
# Real-time analytics webhook
analytics_webhook = {
    "name": "Analytics Dashboard",
    "url": "https://dashboard.vocelio.com/api/events",
    "events": [
        "call.ended", 
        "lead.converted", 
        "appointment.completed"
    ],
    "rate_limit_per_minute": 100,
    "transformation": {
        "enabled": true,
        "template": {
            "metric_type": "{{ event_type }}",
            "value": 1,
            "timestamp": "{{ timestamp }}",
            "dimensions": {
                "agent_id": "{{ data.agent.id }}",
                "source": "vocelio"
            }
        }
    }
}
```

## Monitoring and Alerting

### Health Monitoring
- **Endpoint Health**: Automatic health checks for webhook endpoints
- **Delivery Success Rate**: Monitor delivery success rates per endpoint
- **Response Time Tracking**: Track webhook response times
- **Error Rate Monitoring**: Alert on high error rates
- **Queue Depth Monitoring**: Monitor pending delivery queue

### Alerting Rules
```json
{
  "delivery_failure_rate": {
    "threshold": 10,
    "period": "5m",
    "action": "alert_operations_team"
  },
  "response_time_degradation": {
    "threshold": 5000,
    "period": "1m",
    "action": "alert_endpoint_owner"
  },
  "queue_backlog": {
    "threshold": 1000,
    "period": "1m",
    "action": "scale_processing_capacity"
  }
}
```

## Error Handling

### Common Error Scenarios
- **Network Timeouts**: Automatic retry with exponential backoff
- **HTTP 5xx Errors**: Retry with circuit breaker pattern
- **Authentication Failures**: Alert endpoint owner
- **Payload Too Large**: Split into smaller chunks
- **Rate Limiting**: Respect retry-after headers
- **Endpoint Unavailable**: Temporary disable with automatic re-enable

### Error Response Format
```json
{
  "error": {
    "code": "DELIVERY_FAILED",
    "message": "Webhook delivery failed after 5 attempts",
    "details": {
      "endpoint_id": "webhook_123",
      "last_attempt": "2025-08-05T18:30:00Z",
      "last_status_code": 500,
      "last_error": "Internal Server Error"
    },
    "retry_after": "2025-08-05T19:00:00Z"
  }
}
```

## Performance Optimization

### Delivery Optimization
- **Batch Processing**: Group deliveries for efficiency
- **Connection Pooling**: Reuse HTTP connections
- **Parallel Processing**: Concurrent delivery processing
- **Queue Management**: Priority-based delivery queues
- **Caching**: Cache endpoint configurations
- **Compression**: Gzip payload compression

### Scaling Configuration
```json
{
  "processing": {
    "max_concurrent_deliveries": 100,
    "batch_size": 50,
    "queue_check_interval": 5,
    "connection_pool_size": 20
  },
  "retry": {
    "max_queue_size": 10000,
    "dead_letter_threshold": 5,
    "cleanup_interval": 3600
  }
}
```

## Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python src/main.py

# Access API documentation
open http://localhost:8019/docs
```

### Testing Webhooks
```bash
# Test webhook endpoint
curl -X POST http://localhost:8019/endpoints/test \
  -H "Content-Type: application/json" \
  -d '{"test": true, "timestamp": "2025-08-05T18:00:00Z"}'

# Publish test event
curl -X POST http://localhost:8019/events/publish \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "lead.created",
    "payload": {
      "lead": {"id": "test_123", "name": "Test Lead"}
    }
  }'
```

## Security Best Practices

### Webhook Security
- **Always use HTTPS**: Ensure encrypted data transmission
- **Verify Signatures**: Validate webhook signatures
- **Implement Timeouts**: Prevent hanging connections
- **Rate Limiting**: Protect against abuse
- **IP Validation**: Verify source IP addresses
- **Secret Rotation**: Regular secret key rotation

### Data Protection
- **PII Handling**: Mask sensitive data in logs
- **Audit Logging**: Track all webhook activities
- **Access Control**: Restrict webhook management access
- **Data Retention**: Implement data retention policies
- **Compliance**: GDPR, CCPA compliance features

---

*Webhooks Service v1.0.0 - Part of the Vocelio AI Call Center Platform*

For technical support or questions, contact the development team.
