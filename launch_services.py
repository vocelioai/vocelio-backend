#!/usr/bin/env python3
"""
Service launcher for Vocelio microservices.
Starts all services in development mode for testing.
"""

import subprocess
import sys
import time
import signal
import threading
from pathlib import Path

class ServiceLauncher:
    def __init__(self):
        self.services = {
            "api-gateway": {"port": 8000, "path": "apps/api-gateway"},
            "overview": {"port": 8001, "path": "apps/overview"},
            "ai-agents": {"port": 8002, "path": "apps/ai-agents"},
            "smart-campaigns": {"port": 8003, "path": "apps/smart-campaigns"},
            "analytics-pro": {"port": 8004, "path": "apps/analytics-pro"},
            "team-hub": {"port": 8005, "path": "apps/team-hub"},
            "phone-numbers": {"port": 8006, "path": "apps/phone-numbers"},
            "voice-lab": {"port": 8007, "path": "apps/voice-lab"},
            "settings": {"port": 8008, "path": "apps/settings"},
            "flow-builder": {"port": 8009, "path": "apps/flow-builder"},
            "call-center": {"port": 8010, "path": "apps/call-center"},
            "integrations": {"port": 8011, "path": "apps/integrations"},
            "voice-marketplace": {"port": 8012, "path": "apps/voice-marketplace"},
            "billing-pro": {"port": 8013, "path": "apps/billing-pro"},
            "developer-api": {"port": 8014, "path": "apps/developer-api"},
            "agent-store": {"port": 8015, "path": "apps/agent-store"},
            "compliance": {"port": 8016, "path": "apps/compliance"},
            "white-label": {"port": 8017, "path": "apps/white-label"}
        }
        self.processes = {}
        self.running = True

    def start_service(self, name: str, config: dict):
        """Start a single service."""
        service_path = Path(config["path"])
        port = config["port"]
        
        if not service_path.exists():
            print(f"❌ Service path not found: {service_path}")
            return None
        
        main_file = service_path / "src" / "main.py"
        if not main_file.exists():
            print(f"❌ Main file not found: {main_file}")
            return None
        
        cmd = [
            sys.executable, "-m", "uvicorn",
            "src.main:app",
            "--host", "0.0.0.0",
            "--port", str(port),
            "--reload",
            "--reload-dir", "src",
            "--log-level", "info"
        ]
        
        try:
            print(f"🚀 Starting {name} on port {port}...")
            process = subprocess.Popen(
                cmd,
                cwd=service_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Start log monitoring in background
            threading.Thread(
                target=self.monitor_logs,
                args=(name, process),
                daemon=True
            ).start()
            
            return process
            
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            return None

    def monitor_logs(self, name: str, process: subprocess.Popen):
        """Monitor service logs."""
        while self.running and process.poll() is None:
            try:
                line = process.stdout.readline()
                if line:
                    print(f"[{name}] {line.strip()}")
            except:
                break

    def start_all_services(self, service_filter=None):
        """Start all services or filtered subset."""
        services_to_start = self.services
        if service_filter:
            services_to_start = {k: v for k, v in self.services.items() if k in service_filter}
        
        print(f"🔥 Starting {len(services_to_start)} services...")
        print("=" * 50)
        
        for name, config in services_to_start.items():
            process = self.start_service(name, config)
            if process:
                self.processes[name] = process
                time.sleep(1)  # Stagger starts
        
        print("\n✅ All services started!")
        print("=" * 50)
        self.print_service_status()
        
        return len(self.processes)

    def print_service_status(self):
        """Print status of all services."""
        print("\n📊 SERVICE STATUS:")
        print("-" * 50)
        for name, config in self.services.items():
            if name in self.processes:
                process = self.processes[name]
                status = "🟢 RUNNING" if process.poll() is None else "🔴 STOPPED"
                print(f"{name:<20} Port {config['port']:<5} {status}")
            else:
                print(f"{name:<20} Port {config['port']:<5} 🔴 NOT STARTED")

    def stop_all_services(self):
        """Stop all running services."""
        print("\n🛑 Stopping all services...")
        self.running = False
        
        for name, process in self.processes.items():
            try:
                print(f"Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Force killing {name}...")
                process.kill()
            except Exception as e:
                print(f"Error stopping {name}: {e}")
        
        self.processes.clear()
        print("✅ All services stopped")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n📡 Received signal {signum}")
        self.stop_all_services()
        sys.exit(0)

def main():
    """Main launcher execution."""
    launcher = ServiceLauncher()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, launcher.signal_handler)
    signal.signal(signal.SIGTERM, launcher.signal_handler)
    
    # Check for service filter
    service_filter = None
    if len(sys.argv) > 1:
        service_filter = sys.argv[1:]
        print(f"Starting filtered services: {', '.join(service_filter)}")
    
    try:
        started_count = launcher.start_all_services(service_filter)
        
        if started_count == 0:
            print("❌ No services started successfully")
            sys.exit(1)
        
        print(f"\n🎉 {started_count} services running!")
        print("Press Ctrl+C to stop all services")
        print("=" * 50)
        
        # Keep main thread alive
        while launcher.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        launcher.stop_all_services()
    except Exception as e:
        print(f"❌ Launcher error: {e}")
        launcher.stop_all_services()
        sys.exit(1)

if __name__ == "__main__":
    main()
