#!/usr/bin/env python3
"""
Test whitelabel.vocelio.ai domain connectivity
"""
import requests
import ssl
import socket
from datetime import datetime

def test_whitelabel_domain():
    url = "https://whitelabel.vocelio.ai"
    domain = "whitelabel.vocelio.ai"
    
    print("=" * 60)
    print(f"🔍 TESTING WHITE-LABEL DOMAIN: {domain}")
    print("=" * 60)
    print(f"⏰ Test Time: {datetime.now()}")
    print()
    
    # Test 1: DNS Resolution
    try:
        ip = socket.gethostbyname(domain)
        print(f"✅ DNS Resolution: {domain} → {ip}")
    except socket.gaierror as e:
        print(f"❌ DNS Resolution Failed: {e}")
        return
    
    # Test 2: SSL Certificate
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                print(f"✅ SSL Certificate: Valid")
                if cert:
                    print(f"   Certificate Info Available")
    except Exception as e:
        print(f"❌ SSL Test Failed: {e}")
    
    # Test 3: HTTP Connection
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        print(f"✅ HTTP Connection: Status {response.status_code}")
        print(f"   Response Time: {response.elapsed.total_seconds():.2f}s")
        print(f"   Final URL: {response.url}")
        
        if response.status_code == 200:
            print(f"   Content Length: {len(response.text)} bytes")
            print(f"   Content Type: {response.headers.get('content-type', 'Unknown')}")
        
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL Connection Failed: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Failed: {e}")
    except requests.exceptions.Timeout as e:
        print(f"❌ Request Timeout: {e}")
    except Exception as e:
        print(f"❌ HTTP Test Failed: {e}")
    
    # Test 4: Service Health Check
    health_url = f"{url}/health"
    try:
        health_response = requests.get(health_url, timeout=5)
        print(f"✅ Health Check: Status {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"   Health Response: {health_response.text[:200]}")
    except Exception as e:
        print(f"⚠️  Health Check: {e}")
    
    print()
    print("=" * 60)
    print("🎯 WHITE-LABEL DOMAIN TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_whitelabel_domain()
