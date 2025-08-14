import os
from pathlib import Path

def analyze_services():
    apps_dir = Path("apps")
    services = {}
    
    # Core service categories
    core_services = []
    support_services = []
    feature_services = []
    
    for service_dir in apps_dir.iterdir():
        if service_dir.is_dir():
            service_name = service_dir.name
            has_main = any([
                (service_dir / "main.py").exists(),
                (service_dir / "src" / "main.py").exists()
            ])
            has_railway = (service_dir / "railway.toml").exists()
            has_dockerfile = (service_dir / "Dockerfile").exists()
            has_requirements = (service_dir / "requirements.txt").exists()
            
            # Categorize services
            if service_name in ['api-gateway', 'call-center', 'phone-numbers', 'overview', 'settings']:
                core_services.append(service_name)
            elif service_name in ['ai-brain', 'billing-pro', 'sso-identity', 'enterprise-security']:
                support_services.append(service_name)
            else:
                feature_services.append(service_name)
            
            services[service_name] = {
                'has_main': has_main,
                'has_railway': has_railway,
                'has_dockerfile': has_dockerfile,
                'has_requirements': has_requirements,
                'deployment_ready': has_main and has_railway and has_requirements
            }
    
    print("🏢 VOCELIO MICROSERVICES ANALYSIS")
    print("=" * 50)
    
    print("\n🎯 CORE PLATFORM SERVICES:")
    for service in core_services:
        status = "✅" if services[service]['deployment_ready'] else "❌"
        print(f"  {status} {service}")
    
    print("\n🔧 SUPPORT SERVICES:")
    for service in support_services:
        if service in services:
            status = "✅" if services[service]['deployment_ready'] else "❌"
            print(f"  {status} {service}")
    
    print("\n🚀 FEATURE SERVICES:")
    ready_features = [s for s in feature_services if s in services and services[s]['deployment_ready']]
    not_ready_features = [s for s in feature_services if s in services and not services[s]['deployment_ready']]
    
    print(f"  ✅ Ready: {len(ready_features)} services")
    for service in ready_features[:10]:  # Show first 10
        print(f"    - {service}")
    if len(ready_features) > 10:
        print(f"    ... and {len(ready_features) - 10} more")
    
    print(f"\n  ❌ Need Work: {len(not_ready_features)} services")
    for service in not_ready_features[:5]:  # Show first 5
        print(f"    - {service}")
    if len(not_ready_features) > 5:
        print(f"    ... and {len(not_ready_features) - 5} more")
    
    print(f"\n📊 SUMMARY:")
    print(f"  Total Services: {len(services)}")
    ready_count = sum(1 for s in services.values() if s['deployment_ready'])
    print(f"  Deployment Ready: {ready_count}/{len(services)}")
    print(f"  Success Rate: {ready_count/len(services)*100:.1f}%")
    
    return services

if __name__ == "__main__":
    analyze_services()
