#!/usr/bin/env python3
"""
Simple DST Cleanup Script
Quickly removes Don't Starve Together server files and configuration.
"""

import os
import shutil

def cleanup_dst():
    """Remove DST server files and configuration"""
    user_profile = os.environ.get('USERPROFILE', '')
    
    # Paths to remove
    dst_server = os.path.join(user_profile, "Steam", "steamapps", "common", "Dont Starve Together Dedicated Server")
    dst_config = os.path.join(user_profile, "Documents", "Klei", "DoNotStarveTogether", "MyDediServer")
    dst_cluster1 = os.path.join(user_profile, "Documents", "Klei", "DoNotStarveTogether", "Cluster_1")
    
    print("🧹 Cleaning up DST files...")
    
    # Remove DST server installation
    if os.path.exists(dst_server):
        try:
            shutil.rmtree(dst_server)
            print(f"✅ Removed DST server: {dst_server}")
        except Exception as e:
            print(f"❌ Failed to remove DST server: {e}")
    
    # Remove DST configurations
    for config_path in [dst_config, dst_cluster1]:
        if os.path.exists(config_path):
            try:
                shutil.rmtree(config_path)
                print(f"✅ Removed DST config: {config_path}")
            except Exception as e:
                print(f"❌ Failed to remove DST config: {e}")
    
    print("✅ DST cleanup completed!")

if __name__ == "__main__":
    cleanup_dst()
