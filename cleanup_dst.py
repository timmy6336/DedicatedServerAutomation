#!/usr/bin/env python3
"""
DST Cleanup Script
Removes Don't Starve Together server files and configuration data.
"""

import os
import shutil
import sys
from pathlib import Path

def remove_directory(path, description):
    """Remove a directory if it exists"""
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            print(f"✅ Removed {description}: {path}")
            return True
        except Exception as e:
            print(f"❌ Failed to remove {description}: {e}")
            return False
    else:
        print(f"ℹ️  {description} not found: {path}")
        return True

def remove_file(path, description):
    """Remove a file if it exists"""
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"✅ Removed {description}: {path}")
            return True
        except Exception as e:
            print(f"❌ Failed to remove {description}: {e}")
            return False
    else:
        print(f"ℹ️  {description} not found: {path}")
        return True

def main():
    print("🧹 DST Cleanup Script")
    print("=" * 50)
    
    # Get user profile
    user_profile = os.environ.get('USERPROFILE', '')
    if not user_profile:
        print("❌ Could not determine user profile directory")
        return False
    
    # Define paths to clean up
    paths_to_clean = [
        # DST Server Installation
        {
            "path": os.path.join(user_profile, "Steam", "steamapps", "common", "Dont Starve Together Dedicated Server"),
            "description": "DST Server Installation",
            "type": "directory"
        },
        
        # DST Configuration directories
        {
            "path": os.path.join(user_profile, "Documents", "Klei", "DoNotStarveTogether", "MyDediServer"),
            "description": "DST MyDediServer Configuration",
            "type": "directory"
        },
        {
            "path": os.path.join(user_profile, "Documents", "Klei", "DoNotStarveTogether", "Cluster_1"),
            "description": "DST Cluster_1 Configuration",
            "type": "directory"
        },
        
        # SteamCMD (if you want to remove it too)
        {
            "path": os.path.join(user_profile, "Steam", "steamapps", "common", "steamcmd"),
            "description": "SteamCMD Installation",
            "type": "directory"
        },
    ]
    
    # Ask for confirmation
    print("\nThe following items will be removed:")
    for item in paths_to_clean:
        if os.path.exists(item["path"]):
            print(f"  - {item['description']}: {item['path']}")
    
    print("\n⚠️  WARNING: This action cannot be undone!")
    response = input("Do you want to continue? (yes/no): ").lower().strip()
    
    if response not in ['yes', 'y']:
        print("❌ Cleanup cancelled.")
        return False
    
    print("\n🧹 Starting cleanup...")
    
    success_count = 0
    total_count = len(paths_to_clean)
    
    # Remove each path
    for item in paths_to_clean:
        if item["type"] == "directory":
            if remove_directory(item["path"], item["description"]):
                success_count += 1
        else:  # file
            if remove_file(item["path"], item["description"]):
                success_count += 1
    
    print("\n📊 Cleanup Summary:")
    print(f"   Successfully processed: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("✅ All DST files and configurations have been removed!")
    else:
        print("⚠️  Some items could not be removed. Check the errors above.")
    
    print("\n💡 Note: You may need to restart Steam or any running processes")
    print("   that might be using these files.")
    
    return success_count == total_count

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Cleanup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
