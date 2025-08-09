# Railway Deployment Guide

## Services Deployed
- api-gateway (port 8000)
- overview-service (port 8001)
- ai-agents-service (port 8002)
- smart-campaigns-service (port 8003)
- Postgres (Railway plugin)
- Redis (Railway plugin)

## 1. Pre-Deployment Checklist
- [ ] Remove real secrets from `.env` (use `.env.example`)
- [ ] Commit & push sanitized repo to GitHub
- [ ] Rotate any keys already committed historically
- [ ] Confirm Dockerfiles build locally (`docker compose up --build`)

## 2. Create Railway Project
1. New Project → Deploy from GitHub → select repository
2. Add services one by one choosing the proper subdirectory:
   - `apps/api-gateway`
   - `apps/overview-service`
   - `apps/ai-agents-service`
   - `apps/smart-campaigns-service`
3. Add Postgres plugin
4. Add Redis plugin

## 3. Configure Environment Variables (each service)
| Variable | Example | Notes |
|----------|---------|-------|
| ENVIRONMENT | production | |
| DATABASE_URL | (Railway Postgres URL) | Provided by plugin |
| REDIS_URL | (Railway Redis URL) | Provided by plugin |
| JWT_SECRET_KEY | generate_new_long_random | Use a secret generator |
| OVERVIEW_SERVICE_URL | http://overview-service:8001 | Internal DNS |
| AI_AGENTS_SERVICE_URL | http://ai-agents-service:8002 | |
| SMART_CAMPAIGNS_SERVICE_URL | http://smart-campaigns-service:8003 | |
| OPENAI_API_KEY | (rotated) | Optional |
| SENTRY_DSN | (if used) | Optional |

Tip: Set shared variables via Railway variables UI and link to multiple services.

## 4. Health Checks
Set health path:
- api-gateway: `/health`
- other services: `/health`

## 5. Deployment Order
Railway will auto-build in parallel. Gateway depends on services; if startup race occurs, gateway has internal wait script.

## 6. Scaling
- Start with min 1 instance each
- Enable auto scaling only after validating stability

## 7. Logs & Monitoring
- Use Railway Logs tab per service
- Optionally add Sentry DSN & Prometheus exporter in future

## 8. Post-Deployment Smoke Test
```bash
curl -s $GATEWAY_URL/health
curl -s $GATEWAY_URL/health/detailed | head
curl -s $GATEWAY_URL/api/overview-service/health
```

## 9. Future Enhancements
- Add more microservices progressively (adjust SERVICES map)
- Introduce centralized tracing (OpenTelemetry)
- Add rate limiting with Redis backend tuning

## 10. Troubleshooting
| Symptom | Cause | Fix |
|---------|-------|-----|
| 502 from gateway | Service not healthy | Check service logs, health endpoint |
| 504 timeout | Upstream slow | Increase timeout or optimize upstream |
| Circuit breaker open | Consecutive failures | Investigate upstream errors, then restart |

---
Generated: 2025-08-09
