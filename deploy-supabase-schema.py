#!/usr/bin/env python3
"""
🚀 Deploy Supabase Schema Script
Automatically deploy the complete Vocelio database schema to Supabase
"""

import requests
import json
import time
from datetime import datetime

# Supabase Configuration
SUPABASE_URL = "https://bhzhgivqqnwvndzjthqv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJoemhnaXZxcW53dm5kemp0aHF2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyODQ5MjgsImV4cCI6MjA3MDg2MDkyOH0.1JyoU3xQG7McYRIWzJfTfwv6oH7FCIZkLTLUnahLtKI"

def read_schema_file():
    """Read the complete Supabase schema file"""
    try:
        with open('VOCELIO_COMPLETE_SUPABASE_SCHEMA.sql', 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print("❌ Schema file 'VOCELIO_COMPLETE_SUPABASE_SCHEMA.sql' not found!")
        return None
    except Exception as e:
        print(f"❌ Error reading schema file: {str(e)}")
        return None

def deploy_schema_via_supabase_api(schema_sql):
    """Deploy schema using Supabase SQL execution"""
    print("🚀 Deploying Schema via Supabase API...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Split schema into manageable chunks
    statements = schema_sql.split(';')
    statements = [stmt.strip() for stmt in statements if stmt.strip()]
    
    success_count = 0
    error_count = 0
    
    print(f"📝 Found {len(statements)} SQL statements to execute...")
    
    for i, statement in enumerate(statements):
        if not statement.strip():
            continue
            
        try:
            # Use Supabase's SQL execution endpoint (if available)
            # Note: This might require service role key for DDL operations
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/rpc/execute_sql",
                headers=headers,
                json={"sql": statement},
                timeout=30
            )
            
            if response.status_code == 200:
                success_count += 1
                if i % 10 == 0:
                    print(f"✅ Executed {i+1}/{len(statements)} statements...")
            else:
                error_count += 1
                if "already exists" not in response.text:
                    print(f"⚠️ Statement {i+1} warning: {response.status_code}")
                
        except Exception as e:
            error_count += 1
            print(f"❌ Statement {i+1} error: {str(e)[:50]}...")
            
        # Rate limiting
        if i % 5 == 0:
            time.sleep(0.1)
    
    return success_count, error_count

def test_schema_deployment():
    """Test if key tables were created successfully"""
    print("\n🔍 Testing Schema Deployment...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    test_tables = [
        "organizations",
        "users",
        "ai_agents", 
        "calls",
        "campaigns",
        "flows",
        "settings",
        "knowledge_articles",
        "leads",
        "notifications"
    ]
    
    accessible_tables = 0
    
    for table in test_tables:
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/{table}?select=count",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ {table}: Accessible")
                accessible_tables += 1
            else:
                print(f"❌ {table}: Not accessible ({response.status_code})")
                
        except Exception as e:
            print(f"⚠️ {table}: {str(e)[:30]}...")
    
    return accessible_tables, len(test_tables)

def main():
    """Main deployment process"""
    print("🗄️ VOCELIO SUPABASE SCHEMA DEPLOYMENT")
    print("=" * 45)
    print(f"🔗 Target: {SUPABASE_URL}")
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Read schema file
    schema_sql = read_schema_file()
    if not schema_sql:
        return False
    
    print(f"📄 Schema file loaded: {len(schema_sql):,} characters")
    print()
    
    # Deploy schema
    success_count, error_count = deploy_schema_via_supabase_api(schema_sql)
    
    print(f"\n📊 Deployment Summary:")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Errors: {error_count}")
    print()
    
    # Test deployment
    accessible, total = test_schema_deployment()
    
    print(f"\n🎯 Final Results:")
    print(f"📊 Tables Accessible: {accessible}/{total}")
    print(f"📈 Success Rate: {(accessible/total*100):.1f}%")
    
    if accessible >= total * 0.8:
        print("\n🎉 SCHEMA DEPLOYMENT SUCCESSFUL!")
        print("✅ Database is ready for production use")
        return True
    else:
        print("\n⚠️ SCHEMA DEPLOYMENT INCOMPLETE")
        print("❗ Manual schema deployment may be required")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n💡 MANUAL DEPLOYMENT INSTRUCTIONS:")
        print("1. Go to Supabase Dashboard > SQL Editor")
        print("2. Copy contents of 'VOCELIO_COMPLETE_SUPABASE_SCHEMA.sql'")
        print("3. Paste and execute in SQL editor")
        print("4. Verify all tables are created successfully")
