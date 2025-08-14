"""
Update Railway configurations to only redeploy specific services when their code changes
"""
import os
import glob
from pathlib import Path

def update_railway_configs():
    """Update all railway.toml files with service-specific watch paths"""
    
    # Get all railway.toml files
    railway_files = glob.glob("apps/*/railway.toml")
    
    print(f"Found {len(railway_files)} Railway configuration files")
    print("=" * 60)
    
    for railway_file in railway_files:
        # Handle both forward and backward slashes
        service_name = railway_file.replace('\\', '/').split('/')[1]
        watch_path = f"apps/{service_name}/**"
        
        print(f"Updating {service_name}...")
        
        try:
            # Read the current file
            with open(railway_file, 'r') as f:
                content = f.read()
            
            # Check if watchPaths already exists
            if 'watchPaths' in content:
                print(f"  ⚠️  {service_name} already has watchPaths configured")
                continue
            
            # Add watchPaths to the [deploy] section
            if '[deploy]' in content:
                # Find the [deploy] section and add watchPaths
                lines = content.split('\n')
                new_lines = []
                in_deploy_section = False
                watchPaths_added = False
                
                for line in lines:
                    new_lines.append(line)
                    
                    if line.strip() == '[deploy]':
                        in_deploy_section = True
                    elif line.strip().startswith('[') and line.strip() != '[deploy]':
                        if in_deploy_section and not watchPaths_added:
                            # Add watchPaths before the next section
                            new_lines.insert(-1, f'watchPaths = ["{watch_path}"]')
                            watchPaths_added = True
                        in_deploy_section = False
                    elif in_deploy_section and line.strip().startswith('restartPolicyMaxRetries'):
                        # Add watchPaths after restartPolicyMaxRetries
                        new_lines.append(f'watchPaths = ["{watch_path}"]')
                        watchPaths_added = True
                
                # If we're still in deploy section at end of file
                if in_deploy_section and not watchPaths_added:
                    new_lines.append(f'watchPaths = ["{watch_path}"]')
                
                # Write the updated content
                with open(railway_file, 'w') as f:
                    f.write('\n'.join(new_lines))
                
                print(f"  ✅ Added watchPaths = [\"{watch_path}\"] to {service_name}")
            
            else:
                print(f"  ⚠️  No [deploy] section found in {service_name}")
        
        except Exception as e:
            print(f"  ❌ Error updating {service_name}: {e}")
    
    print("\n" + "=" * 60)
    print("Railway configuration update complete!")
    print("\nNow each service will only redeploy when its specific directory changes.")

if __name__ == "__main__":
    # Change to the correct directory
    os.chdir("C:/Users/SNC/OneDrive/Desktop/vocelio-backend")
    update_railway_configs()
