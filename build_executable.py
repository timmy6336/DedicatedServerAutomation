#!/usr/bin/env python3
"""
Build script to create executable for Dedicated Server Automation
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🔨 Building Dedicated Server Automation Executable...")
    
    # Get the project directory
    project_dir = Path(__file__).parent
    src_dir = project_dir / "src"
    dist_dir = project_dir / "dist"
    build_dir = project_dir / "build"
    
    # Clean previous builds
    if dist_dir.exists():
        print("🧹 Cleaning previous build...")
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Build command
    main_script = src_dir / "main.py"
    
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window (for GUI app)
        "--name=DedicatedServerAutomation",  # Executable name
        "--icon=icon.ico",              # Icon (if exists)
        "--add-data=src/images;images", # Include images folder
        "--add-data=src/static;static", # Include static files
        "--add-data=src/game_info.json;.",  # Include game info
        "--distpath=dist",              # Output directory
        "--workpath=build",             # Build directory
        "--specpath=.",                 # Spec file location
        "--clean",                      # Clean cache
        str(main_script)
    ]
    
    # Remove icon parameter if icon doesn't exist
    if not (project_dir / "icon.ico").exists():
        pyinstaller_cmd = [cmd for cmd in pyinstaller_cmd if not cmd.startswith("--icon")]
        print("ℹ️ No icon.ico found, building without icon")
    
    print(f"🚀 Running PyInstaller...")
    print(f"Command: {' '.join(pyinstaller_cmd)}")
    
    try:
        # Run PyInstaller
        result = subprocess.run(pyinstaller_cmd, cwd=project_dir, check=True)
        
        if result.returncode == 0:
            executable_path = dist_dir / "DedicatedServerAutomation.exe"
            if executable_path.exists():
                print(f"✅ Build successful!")
                print(f"📁 Executable created at: {executable_path.absolute()}")
                print(f"📊 File size: {executable_path.stat().st_size / (1024*1024):.1f} MB")
                
                # Optional: Create a portable package
                create_portable_package(project_dir, dist_dir)
                
            else:
                print("❌ Build completed but executable not found!")
        else:
            print("❌ Build failed!")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller failed with error: {e}")
        return 1
    except FileNotFoundError:
        print("❌ PyInstaller not found! Please install it with: pip install pyinstaller")
        return 1
    
    return 0

def create_portable_package(project_dir, dist_dir):
    """Create a portable package with the executable and necessary files"""
    print("📦 Creating portable package...")
    
    portable_dir = project_dir / "portable"
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    portable_dir.mkdir()
    
    # Copy executable
    exe_file = dist_dir / "DedicatedServerAutomation.exe"
    if exe_file.exists():
        shutil.copy2(exe_file, portable_dir)
    
    # Copy important files
    files_to_copy = [
        "README.md",
        ".env.example",
        "requirements.txt"
    ]
    
    for file_name in files_to_copy:
        file_path = project_dir / file_name
        if file_path.exists():
            shutil.copy2(file_path, portable_dir)
    
    # Create .env.example if .env exists but .env.example doesn't
    env_file = project_dir / ".env"
    env_example = project_dir / ".env.example"
    if env_file.exists() and not env_example.exists():
        with open(env_file, 'r') as f:
            content = f.read()
        # Remove actual values, keep only keys
        example_content = "\n".join([
            line.split('=')[0] + "=" if '=' in line and not line.strip().startswith('#') else line
            for line in content.split('\n')
        ])
        with open(portable_dir / ".env.example", 'w') as f:
            f.write(example_content)
    
    print(f"✅ Portable package created at: {portable_dir.absolute()}")
    print("💡 You can distribute the entire 'portable' folder")

if __name__ == "__main__":
    sys.exit(main())
