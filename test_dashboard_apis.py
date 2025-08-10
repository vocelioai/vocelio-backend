#!/usr/bin/env python3
"""
🔗 Dashboard API Compliance Test
Tests if backend services provide the APIs your frontend dashboard needs
"""

import requests
import json
from datetime import datetime

class DashboardAPITester:
    """Tests API compliance for dashboard requirements"""
    
    def __init__(self):
        self.services = {
            "overview": "https://overview-production.up.railway.app",
            "agents": "https://agents-production-768d.up.railway.app", 
            "ai-brain": "https://ai-brain-production.up.railway.app",
            "smart-campaigns": "https://smart-campaigns-production.up.railway.app",
            "billing-pro": "https://billing-pro-production.up.railway.app",
            "analytics-pro": "https://analytics-pro-production.up.railway.app",
            "call-center": "https://call-center-production-19af.up.railway.app",
            "voice-lab": "https://voice-lab-production.up.railway.app",
            "team-hub": "https://team-hub-production.up.railway.app"
        }
        
        # Common dashboard API endpoints that should exist
        self.expected_endpoints = [
            "/",           # Root endpoint
            "/health",     # Health check
            "/api/v1/",    # API version 1 (if exists)
            "/docs",       # API documentation
            "/status",     # Service status
        ]
        
        self.results = {}
    
    def test_endpoint(self, service_name: str, base_url: str, endpoint: str) -> dict:
        """Test a specific endpoint"""
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            
            return {
                "status": "available" if response.status_code == 200 else "not_found",
                "status_code": response.status_code,
                "url": url,
                "content_type": response.headers.get("content-type", "unknown")
            }
        except requests.exceptions.Timeout:
            return {"status": "timeout", "url": url}
        except requests.exceptions.ConnectionError:
            return {"status": "connection_error", "url": url}
        except Exception as e:
            return {"status": "error", "error": str(e), "url": url}
    
    def test_service_apis(self, service_name: str, base_url: str) -> dict:
        """Test all expected endpoints for a service"""
        print(f"Testing {service_name:<15} ... ", end="", flush=True)
        
        service_results = {}
        available_count = 0
        
        for endpoint in self.expected_endpoints:
            result = self.test_endpoint(service_name, base_url, endpoint)
            service_results[endpoint] = result
            
            if result["status"] == "available":
                available_count += 1
        
        # Calculate readiness score
        readiness_score = (available_count / len(self.expected_endpoints)) * 100
        
        if readiness_score >= 60:
            print(f"✅ {readiness_score:.0f}% ready")
        elif readiness_score >= 40:
            print(f"🟡 {readiness_score:.0f}% ready")
        else:
            print(f"❌ {readiness_score:.0f}% ready")
        
        return {
            "endpoints": service_results,
            "readiness_score": readiness_score,
            "available_endpoints": available_count,
            "total_endpoints": len(self.expected_endpoints)
        }
    
    def test_all_services(self) -> dict:
        """Test API readiness for all services"""
        print("🔗 Testing Dashboard API Compliance...")
        print("=" * 60)
        
        total_score = 0
        service_count = len(self.services)
        
        for service_name, base_url in self.services.items():
            result = self.test_service_apis(service_name, base_url)
            self.results[service_name] = result
            total_score += result["readiness_score"]
        
        average_score = total_score / service_count if service_count > 0 else 0
        
        print("=" * 60)
        print(f"📊 Overall API Readiness: {average_score:.1f}%")
        
        if average_score >= 80:
            print("🎉 EXCELLENT: Ready for dashboard integration!")
        elif average_score >= 60:
            print("✅ GOOD: Mostly ready, some endpoints need implementation")
        elif average_score >= 40:
            print("🟡 FAIR: Basic functionality, needs API development")
        else:
            print("❌ POOR: Significant API development needed")
        
        return self.results
    
    def generate_api_recommendations(self) -> str:
        """Generate recommendations for API development"""
        if not self.results:
            return "No test results available"
        
        recommendations = f"""
# 🔗 Dashboard API Development Recommendations
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Current API Status
"""
        
        for service_name, result in self.results.items():
            score = result["readiness_score"]
            available = result["available_endpoints"]
            total = result["total_endpoints"]
            
            recommendations += f"\n### {service_name.title()} Service\n"
            recommendations += f"- **Readiness**: {score:.0f}% ({available}/{total} endpoints)\n"
            
            # Show missing endpoints
            missing_endpoints = []
            for endpoint, endpoint_result in result["endpoints"].items():
                if endpoint_result["status"] != "available":
                    missing_endpoints.append(endpoint)
            
            if missing_endpoints:
                recommendations += f"- **Missing**: {', '.join(missing_endpoints)}\n"
            
            recommendations += f"- **Base URL**: {self.services[service_name]}\n"
        
        recommendations += """
## 🎯 Priority Implementations Needed

### 1. API Version Endpoints (/api/v1/)
Most services are missing versioned API endpoints. Add:
```python
@app.get("/api/v1/")
async def api_info():
    return {"version": "1.0.0", "service": "service_name"}
```

### 2. Service Status Endpoints (/status) 
Add operational status beyond health:
```python
@app.get("/status")
async def service_status():
    return {
        "status": "operational",
        "uptime": uptime_seconds,
        "version": "1.0.0",
        "dependencies": dependency_status
    }
```

### 3. API Documentation (/docs)
Ensure all services have FastAPI auto-docs enabled:
```python
app = FastAPI(docs_url="/docs", redoc_url="/redoc")
```

## 🚀 Dashboard Integration Strategy

### Phase 1: Basic Integration (Week 1)
- Use existing health endpoints for service status
- Implement basic service communication
- Add authentication middleware

### Phase 2: API Development (Week 2-3)  
- Add versioned API endpoints to all services
- Implement core business logic endpoints
- Add proper error handling and validation

### Phase 3: Advanced Features (Week 4+)
- Real-time updates via WebSockets
- Advanced analytics endpoints  
- File upload and management APIs

## 📝 Next Steps
1. Choose 3-5 priority services for your dashboard
2. Implement core API endpoints for those services first
3. Build frontend integration for priority services
4. Gradually add remaining services and features
"""
        
        return recommendations

def main():
    """Run API compliance testing"""
    tester = DashboardAPITester()
    results = tester.test_all_services()
    
    # Generate recommendations
    recommendations = tester.generate_api_recommendations()
    with open('API_READINESS_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(recommendations)
    
    print(f"\n📄 Detailed recommendations saved to: API_READINESS_REPORT.md")

if __name__ == "__main__":
    main()
