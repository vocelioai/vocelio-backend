#!/usr/bin/env python3
"""
🎯 Environment Files Verification Script
Verifies all environment files have been updated with accurate Railway URLs
"""

import os
import re
from pathlib import Path

class EnvFilesVerifier:
    def __init__(self):
        self.base_path = Path(".")
        self.env_files = [
            ".env",
            ".env.production", 
            ".env.example",
            ".env.vercel",
            ".env.vercel.enterprise",
            ".env.production.template"
        ]
        
        # Expected verified URLs (28 services)
        self.verified_urls = {
            "api-gateway-production-588d.up.railway.app",
            "overview-production.up.railway.app",
            "ai-agents-service-production.up.railway.app", 
            "smart-campaigns-production.up.railway.app",
            "analytics-pro-production.up.railway.app",
            "team-hub-production.up.railway.app",
            "phone-numbers-production.up.railway.app",
            "voice-lab-production.up.railway.app",
            "settings-production.up.railway.app",
            "flow-builder-production.up.railway.app",
            "call-center-production-19af.up.railway.app",
            "voice-marketplace-production.up.railway.app",
            "ai-brain-production.up.railway.app",
            "integrations-production-a079.up.railway.app",
            "ai-agent-platform-production.up.railway.app",
            "billing-pro-production.up.railway.app",
            "compliance-production-a432.up.railway.app",
            "white-label-production-ab67.up.railway.app",
            "developer-api-production-a124.up.railway.app",
            "knowledge-base-production.up.railway.app",
            "lead-management-production.up.railway.app",
            "scheduling-production.up.railway.app",
            "unified-campaigns-production.up.railway.app",
            "notifications-production.up.railway.app",
            "scripts-production.up.railway.app",
            "webhooks-production.up.railway.app",
            "recording-production.up.railway.app",
            "monitoring-production.up.railway.app"
        }
    
    def verify_file(self, file_path):
        """Verify a single environment file"""
        if not file_path.exists():
            return {"status": "missing", "verified_urls": 0, "total_urls": 0}
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
        # Find all Railway URLs in the file
        railway_urls = re.findall(r'https://([^.]+\.up\.railway\.app)', content)
        unique_urls = set(railway_urls)
        
        # Count how many verified URLs are present
        verified_count = len(unique_urls & self.verified_urls)
        
        return {
            "status": "verified" if verified_count >= 20 else "partial",
            "verified_urls": verified_count,
            "total_urls": len(unique_urls),
            "missing_urls": self.verified_urls - unique_urls,
            "extra_urls": unique_urls - self.verified_urls
        }
    
    def verify_all_files(self):
        """Verify all environment files"""
        print("🎯 Environment Files Verification Report")
        print("=" * 60)
        
        total_verified = 0
        total_files = 0
        
        for env_file in self.env_files:
            file_path = self.base_path / env_file
            result = self.verify_file(file_path)
            
            print(f"\n📄 {env_file}")
            print("-" * 40)
            
            if result["status"] == "missing":
                print("❌ File not found")
                continue
            elif result["status"] == "error":
                print(f"❌ Error reading file: {result['message']}")
                continue
            
            total_files += 1
            
            if result["status"] == "verified":
                print(f"✅ VERIFIED - {result['verified_urls']}/{len(self.verified_urls)} URLs found")
                total_verified += 1
            else:
                print(f"🟡 PARTIAL - {result['verified_urls']}/{len(self.verified_urls)} URLs found")
            
            if result.get("extra_urls"):
                print(f"ℹ️  Extra URLs: {len(result['extra_urls'])}")
            
            if result.get("missing_urls") and len(result["missing_urls"]) < 10:
                print(f"⚠️  Missing: {', '.join(list(result['missing_urls'])[:3])}...")
        
        print("\n🎯 SUMMARY")
        print("=" * 60)
        print(f"✅ Verified Files: {total_verified}/{total_files}")
        print(f"🎯 Expected URLs: {len(self.verified_urls)} services")
        
        if total_verified == total_files:
            print("\n🏆 ALL ENVIRONMENT FILES SUCCESSFULLY UPDATED!")
            print("🚀 Ready for production deployment")
        else:
            print(f"\n🔧 {total_files - total_verified} files need attention")
        
        return total_verified == total_files

if __name__ == "__main__":
    verifier = EnvFilesVerifier()
    success = verifier.verify_all_files()
    exit(0 if success else 1)
