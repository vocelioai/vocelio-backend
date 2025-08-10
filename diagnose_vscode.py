#!/usr/bin/env python3
"""
🔍 VS Code Problem Diagnostic
Quick check to identify what's causing 2000+ problems
"""

import os
from pathlib import Path

def count_files_by_type():
    """Count files by extension"""
    root = Path(".")
    file_counts = {}
    
    for file_path in root.rglob("*"):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext:
                file_counts[ext] = file_counts.get(ext, 0) + 1
    
    print("📊 File counts by extension:")
    for ext, count in sorted(file_counts.items()):
        print(f"  {ext}: {count}")

def check_python_files():
    """Check Python files for common issues"""
    root = Path(".")
    python_files = list(root.rglob("*.py"))
    
    print(f"\n🐍 Found {len(python_files)} Python files:")
    
    for py_file in python_files[:10]:  # Show first 10
        relative_path = py_file.relative_to(root)
        print(f"  {relative_path}")
    
    if len(python_files) > 10:
        print(f"  ... and {len(python_files) - 10} more")

def check_problematic_dirs():
    """Check for directories that might cause issues"""
    root = Path(".")
    problematic = [
        "node_modules", ".venv", "build", "dist", 
        "__pycache__", ".git", "vocelio-dashboard"
    ]
    
    print(f"\n🚨 Checking for problematic directories:")
    
    for prob_dir in problematic:
        paths = list(root.rglob(prob_dir))
        if paths:
            print(f"  {prob_dir}: {len(paths)} found")
            for path in paths[:3]:  # Show first 3
                print(f"    - {path}")
        else:
            print(f"  {prob_dir}: ✅ not found")

if __name__ == "__main__":
    print("🔍 VS Code Problem Diagnostic")
    print("=" * 40)
    
    count_files_by_type()
    check_python_files()
    check_problematic_dirs()
    
    print("\n💡 Next steps:")
    print("1. Make sure Python interpreter is set to .venv")
    print("2. Reload VS Code window")
    print("3. Check VS Code Output > Python for specific errors")
