#!/usr/bin/env python3
"""
White-Label Service Status Check
"""
import requests
import socket
from datetime import datetime

def check_whitelabel_status():
    print("=" * 60)
    print("🔍 WHITE-LABEL SERVICE STATUS CHECK")
    print("=" * 60)
    print(f"⏰ Check Time: {datetime.now()}")
    print()
    
    # Test URLs
    urls_to_test = [
        "https://ttn13i41.up.railway.app/",
        "https://ttn13i41.up.railway.app/health",
        "https://ttn13i41.up.railway.app/docs",
        "https://ttn13i41.up.railway.app/api/v1/health",
        "https://whitelabel.vocelio.ai/",
        "https://whitelabel.vocelio.ai/health"
    ]
    
    for url in urls_to_test:
        try:
            print(f"🔗 Testing: {url}")
            response = requests.get(url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                print(f"   ✅ Status: {response.status_code} - SUCCESS")
                print(f"   📄 Content Length: {len(response.text)} bytes")
            else:
                print(f"   ❌ Status: {response.status_code}")
                print(f"   📄 Response: {response.text[:100]}")
                
        except requests.exceptions.ConnectionError as e:
            print(f"   ❌ Connection Failed: Unable to connect")
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout: Request timed out")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print()
    
    # DNS Check
    print("🌐 DNS Resolution Check:")
    try:
        ip = socket.gethostbyname("whitelabel.vocelio.ai")
        print(f"   ✅ whitelabel.vocelio.ai → {ip}")
    except socket.gaierror:
        print(f"   ❌ whitelabel.vocelio.ai → DNS not resolving")
    
    try:
        ip = socket.gethostbyname("ttn13i41.up.railway.app")
        print(f"   ✅ ttn13i41.up.railway.app → {ip}")
    except socket.gaierror:
        print(f"   ❌ ttn13i41.up.railway.app → DNS not resolving")
    
    print()
    print("=" * 60)
    print("📋 RECOMMENDED ACTIONS:")
    print("=" * 60)
    print("1. Update DNS CNAME: whitelabel → ttn13i41.up.railway.app")
    print("2. Verify Railway service deployment")
    print("3. Check Railway service logs")
    print("4. Test again in 10-30 minutes after DNS update")
    print("=" * 60)

if __name__ == "__main__":
    check_whitelabel_status()
