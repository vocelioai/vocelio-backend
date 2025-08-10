#!/usr/bin/env python3
"""
🎯 Quick Railway Environment Variables Commands Generator
Generates Railway CLI commands to set all environment variables
"""

def generate_railway_commands():
    """Generate Railway CLI commands for environment variables"""
    
    # Safe variables that can be set automatically
    safe_variables = {
        "ENVIRONMENT": "production",
        "PORT": "8000", 
        "DEBUG": "false",
        "JWT_ALGORITHM": "HS256",
        "JWT_EXPIRE_MINUTES": "1440",
        "OPENAI_MODEL": "gpt-4o-mini",
        "CORS_ORIGINS": "https://*.railway.app,https://*.vocelio.ai",
        "ALLOWED_ORIGINS": "https://*.railway.app,https://*.vocelio.ai", 
        "ALLOWED_HOSTS": "*",
        "TEAM_HUB_SERVICE_URL": "https://team-hub-production.up.railway.app",
        "OVERVIEW_SERVICE_URL": "https://overview-production.up.railway.app",
        "AI_AGENTS_SERVICE_URL": "https://ai-agents-service-production.up.railway.app",
        "SMART_CAMPAIGNS_SERVICE_URL": "https://smart-campaigns-production.up.railway.app",
        "PHONE_NUMBERS_SERVICE_URL": "https://phone-numbers-production.up.railway.app",
        "ANALYTICS_SERVICE_URL": "https://analytics-pro-production.up.railway.app",
        "RATE_LIMIT_REQUESTS": "1000",
        "RATE_LIMIT_WINDOW": "3600",
        "PROMETHEUS_ENABLED": "true",
        "PROMETHEUS_PORT": "9090",
        "DEFAULT_FROM_EMAIL": "support@vocelio.ai"
    }
    
    # Variables that need your actual values
    secret_variables = {
        "JWT_SECRET_KEY": "your_jwt_secret_here",
        "SECRET_KEY": "your_secret_key_here", 
        "DATABASE_URL": "your_database_url_here",
        "SUPABASE_URL": "your_supabase_url_here",
        "SUPABASE_KEY": "your_supabase_key_here",
        "OPENAI_API_KEY": "your_openai_key_here",
        "ANTHROPIC_API_KEY": "your_anthropic_key_here",
        "ELEVENLABS_API_KEY": "your_elevenlabs_key_here",
        "TWILIO_ACCOUNT_SID": "your_twilio_sid_here",
        "TWILIO_AUTH_TOKEN": "your_twilio_token_here",
        "STRIPE_SECRET_KEY": "your_stripe_secret_here",
        "STRIPE_WEBHOOK_SECRET": "your_stripe_webhook_secret_here",
        "STRIPE_PUBLISHABLE_KEY": "your_stripe_publishable_key_here"
    }
    
    commands = []
    
    print("🚀 Railway Environment Variables Setup")
    print("="*50)
    
    print("\n📋 STEP 1: Install Railway CLI (if not installed)")
    print("npm install -g @railway/cli")
    print("railway login")
    
    print("\n🎯 STEP 2: Set Safe Variables (Copy & Paste These Commands)")
    print("-" * 50)
    
    for key, value in safe_variables.items():
        command = f'railway variables set {key}="{value}"'
        commands.append(command)
        print(command)
    
    print("\n🔐 STEP 3: Set Secret Variables (Replace with your actual values)")
    print("-" * 50)
    
    for key, placeholder in secret_variables.items():
        command = f'railway variables set {key}="{placeholder}"'
        print(f"# {command}")
    
    print("\n💡 STEP 4: Alternative - Set All Safe Variables at Once")
    print("-" * 50)
    
    # Create a single PowerShell command for Windows
    powershell_commands = " ; ".join([f'railway variables set {k}="{v}"' for k, v in safe_variables.items()])
    print(f"# PowerShell (Windows):")
    print(f"{powershell_commands}")
    
    print("\n✅ STEP 5: Verify Variables Set")
    print("-" * 50)
    print("railway variables")
    
    print(f"\n📊 Summary:")
    print(f"✅ {len(safe_variables)} safe variables ready to set")
    print(f"🔐 {len(secret_variables)} secret variables need your values")
    print(f"🎯 Total: {len(safe_variables) + len(secret_variables)} environment variables")
    
    return commands

def save_commands_to_file(commands):
    """Save commands to a file for easy execution"""
    with open('railway_commands.sh', 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Railway Environment Variables Setup\n")
        f.write("# Generated automatically for Vocelio.ai\n\n")
        f.write("echo '🚀 Setting Railway Environment Variables...'\n\n")
        
        for cmd in commands:
            f.write(f"{cmd}\n")
        
        f.write("\necho '✅ Safe variables set! Now set your secret variables manually.'\n")
    
    print(f"\n📄 Commands saved to: railway_commands.sh")
    print("Make executable with: chmod +x railway_commands.sh")

if __name__ == "__main__":
    commands = generate_railway_commands()
    save_commands_to_file(commands)
