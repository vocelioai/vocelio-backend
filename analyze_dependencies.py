#!/usr/bin/env python3
"""
🔍 Vocelio.ai Dependency Analysis Tool
Comprehensive dependency checking and analysis across all services

This tool:
- Scans all requirements.txt files
- Checks for version conflicts
- Identifies missing dependencies
- Validates compatibility
- Generates consolidated requirements
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class DependencyAnalyzer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.all_requirements: Dict[str, List[str]] = {}
        self.package_versions: Dict[str, Set[str]] = defaultdict(set)
        self.conflicts: List[Tuple[str, List[str]]] = []
        
    def find_requirements_files(self) -> List[Path]:
        """Find all requirements.txt files"""
        requirements_files = []
        
        # Search for requirements.txt files
        for file_path in self.root_path.rglob("requirements.txt"):
            requirements_files.append(file_path)
        
        return sorted(requirements_files)
    
    def parse_requirement(self, line: str) -> Tuple[str, str]:
        """Parse a requirement line and extract package name and version"""
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            return "", ""
        
        # Handle different version specifications
        patterns = [
            r'^([a-zA-Z0-9_-]+)\[([^\]]+)\]==(.+)$',  # package[extras]==version
            r'^([a-zA-Z0-9_-]+)==(.+)$',              # package==version
            r'^([a-zA-Z0-9_-]+)>=(.+)$',              # package>=version
            r'^([a-zA-Z0-9_-]+)<=(.+)$',              # package<=version
            r'^([a-zA-Z0-9_-]+)>(.+)$',               # package>version
            r'^([a-zA-Z0-9_-]+)<(.+)$',               # package<version
            r'^([a-zA-Z0-9_-]+)~=(.+)$',              # package~=version
            r'^([a-zA-Z0-9_-]+)\[([^\]]+)\]$',        # package[extras]
            r'^([a-zA-Z0-9_-]+)$',                    # package (no version)
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                if len(match.groups()) >= 2:
                    if '[' in match.group(1):
                        # Handle extras
                        package_name = match.group(1).split('[')[0]
                        version = match.group(3) if len(match.groups()) >= 3 else match.group(2)
                    else:
                        package_name = match.group(1)
                        version = match.group(2) if len(match.groups()) >= 2 else "latest"
                    return package_name.lower(), version
                else:
                    return match.group(1).lower(), "latest"
        
        return "", ""
    
    def load_requirements(self, file_path: Path) -> List[str]:
        """Load requirements from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            requirements = []
            for line in lines:
                package, version = self.parse_requirement(line)
                if package:
                    requirements.append(f"{package}=={version}")
                    self.package_versions[package].add(version)
            
            return requirements
            
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return []
    
    def analyze_all_requirements(self):
        """Analyze all requirements files"""
        print("🔍 Scanning for requirements.txt files...")
        
        requirements_files = self.find_requirements_files()
        
        if not requirements_files:
            print("❌ No requirements.txt files found!")
            return
        
        print(f"📄 Found {len(requirements_files)} requirements files:")
        
        for file_path in requirements_files:
            relative_path = file_path.relative_to(self.root_path)
            print(f"  📄 {relative_path}")
            
            requirements = self.load_requirements(file_path)
            self.all_requirements[str(relative_path)] = requirements
    
    def detect_conflicts(self):
        """Detect version conflicts between services"""
        print("\n🔍 Checking for version conflicts...")
        
        conflicts = []
        
        for package, versions in self.package_versions.items():
            if len(versions) > 1 and "latest" not in versions:
                # Check if versions are actually different
                unique_versions = set()
                for version in versions:
                    # Remove comparison operators for conflict detection
                    clean_version = re.sub(r'^[><=~!]+', '', version)
                    unique_versions.add(clean_version)
                
                if len(unique_versions) > 1:
                    conflicts.append((package, list(versions)))
        
        if conflicts:
            print(f"⚠️  Found {len(conflicts)} version conflicts:")
            for package, versions in conflicts:
                print(f"  ❌ {package}: {', '.join(versions)}")
        else:
            print("✅ No version conflicts detected!")
        
        self.conflicts = conflicts
        return conflicts
    
    def generate_consolidated_requirements(self) -> Dict[str, str]:
        """Generate consolidated requirements with latest versions"""
        print("\n📦 Generating consolidated requirements...")
        
        consolidated = {}
        
        for package, versions in self.package_versions.items():
            if "latest" in versions:
                consolidated[package] = "latest"
            else:
                # Use the highest version (assuming semantic versioning)
                try:
                    from packaging import version
                    sorted_versions = sorted(versions, key=lambda x: version.parse(re.sub(r'^[><=~!]+', '', x)), reverse=True)
                    consolidated[package] = sorted_versions[0]
                except:
                    # Fallback to last version if packaging module not available
                    consolidated[package] = list(versions)[-1]
        
        return consolidated
    
    def check_missing_dependencies(self):
        """Check for commonly missing dependencies"""
        print("\n🔍 Checking for missing dependencies...")
        
        # Common dependencies that should be present
        essential_packages = {
            'fastapi': 'Web framework',
            'uvicorn': 'ASGI server',
            'pydantic': 'Data validation',
            'python-dotenv': 'Environment variables',
            'httpx': 'HTTP client',
            'asyncpg': 'PostgreSQL driver',
            'redis': 'Redis client'
        }
        
        missing = []
        for package, description in essential_packages.items():
            if package not in self.package_versions:
                missing.append((package, description))
        
        if missing:
            print(f"⚠️  Missing essential dependencies:")
            for package, description in missing:
                print(f"  ❌ {package}: {description}")
        else:
            print("✅ All essential dependencies present!")
        
        return missing
    
    def check_security_vulnerabilities(self):
        """Check for known security vulnerabilities (basic check)"""
        print("\n🔒 Checking for potential security issues...")
        
        # Known vulnerable versions (this would normally come from a security database)
        vulnerable_packages = {
            'requests': ['2.25.0', '2.25.1'],  # Example
            'urllib3': ['1.25.8', '1.25.9'],   # Example
            'pillow': ['8.1.0', '8.1.1'],      # Example
        }
        
        vulnerabilities = []
        for package, versions in self.package_versions.items():
            if package in vulnerable_packages:
                for version in versions:
                    clean_version = re.sub(r'^[><=~!]+', '', version)
                    if clean_version in vulnerable_packages[package]:
                        vulnerabilities.append((package, clean_version))
        
        if vulnerabilities:
            print(f"⚠️  Potential security vulnerabilities:")
            for package, version in vulnerabilities:
                print(f"  🔓 {package}=={version}")
        else:
            print("✅ No known vulnerabilities detected!")
        
        return vulnerabilities
    
    def generate_service_matrix(self):
        """Generate a matrix showing which packages are used by which services"""
        print("\n📊 Service-Package Matrix:")
        print("=" * 80)
        
        # Get all unique packages
        all_packages = sorted(self.package_versions.keys())
        
        # Get all services
        services = []
        for file_path in self.all_requirements.keys():
            if 'apps/' in file_path:
                service_name = file_path.split('apps/')[1].split('/')[0]
                services.append(service_name)
            elif file_path == 'requirements.txt':
                services.append('root')
        
        services = sorted(set(services))
        
        # Print header
        print(f"{'Package':<25} | {' | '.join(f'{s:<15}' for s in services)}")
        print("-" * (25 + 3 * len(services) + 15 * len(services)))
        
        # Print each package
        for package in all_packages[:20]:  # Limit to first 20 for readability
            row = f"{package:<25} |"
            for service in services:
                # Check if this service uses this package
                service_file = None
                for file_path, requirements in self.all_requirements.items():
                    if service in file_path or (service == 'root' and file_path == 'requirements.txt'):
                        service_file = file_path
                        break
                
                if service_file and any(package in req for req in self.all_requirements[service_file]):
                    row += f" {'✅':<15} |"
                else:
                    row += f" {'❌':<15} |"
            
            print(row)
    
    def generate_recommendations(self):
        """Generate recommendations for dependency management"""
        print("\n💡 Recommendations:")
        print("=" * 50)
        
        recommendations = []
        
        # Check for conflicts
        if self.conflicts:
            recommendations.append("🔧 Resolve version conflicts by standardizing package versions")
        
        # Check for redundant packages
        core_packages = len([p for p in self.package_versions.keys() 
                           if p in ['fastapi', 'uvicorn', 'pydantic', 'asyncpg', 'redis']])
        if core_packages == 5:
            recommendations.append("✅ Core FastAPI stack properly configured")
        
        # Development recommendations
        dev_packages = ['pytest', 'black', 'isort', 'mypy']
        missing_dev = [p for p in dev_packages if p not in self.package_versions]
        if missing_dev:
            recommendations.append(f"📝 Consider adding development tools: {', '.join(missing_dev)}")
        
        # Production recommendations
        prod_packages = ['gunicorn', 'sentry-sdk', 'prometheus-client']
        missing_prod = [p for p in prod_packages if p not in self.package_versions]
        if missing_prod:
            recommendations.append(f"🚀 Consider adding production tools: {', '.join(missing_prod)}")
        
        # Security recommendations
        recommendations.append("🔒 Regularly update dependencies for security patches")
        recommendations.append("🔍 Use dependabot or similar for automated security updates")
        
        for i, recommendation in enumerate(recommendations, 1):
            print(f"{i}. {recommendation}")
    
    def save_consolidated_requirements(self, output_path: str):
        """Save consolidated requirements to a file"""
        consolidated = self.generate_consolidated_requirements()
        
        output_file = Path(output_path) / "consolidated_requirements.txt"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# Vocelio.ai - Consolidated Requirements\n")
                f.write("# Generated automatically from all service requirements\n\n")
                
                for package, version in sorted(consolidated.items()):
                    if version == "latest":
                        f.write(f"{package}\n")
                    else:
                        f.write(f"{package}=={version}\n")
            
            print(f"\n💾 Consolidated requirements saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ Error saving consolidated requirements: {e}")
    
    def run_full_analysis(self):
        """Run complete dependency analysis"""
        print("🚀 Starting Vocelio.ai Dependency Analysis")
        print("=" * 60)
        
        # Analyze all requirements
        self.analyze_all_requirements()
        
        # Detect conflicts
        self.detect_conflicts()
        
        # Check missing dependencies
        self.check_missing_dependencies()
        
        # Security check
        self.check_security_vulnerabilities()
        
        # Generate matrix
        self.generate_service_matrix()
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Save consolidated requirements
        self.save_consolidated_requirements(str(self.root_path))
        
        print("\n" + "=" * 60)
        print("✅ Dependency analysis complete!")

def main():
    """Main function"""
    root_path = r"c:\Users\SNC\OneDrive\Desktop\vocelio-backend"
    
    analyzer = DependencyAnalyzer(root_path)
    analyzer.run_full_analysis()

if __name__ == "__main__":
    main()
