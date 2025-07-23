import shutil
import os
import subprocess
import urllib.request
import zipfile
import requests
import platform
import subprocess
import miniupnpc
import subprocess
import socket

STEAMCMD_URL = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
# Use standard Steam locations
if platform.system().lower() == 'windows':
    STEAMCMD_DIR = os.path.expandvars(r'%USERPROFILE%\SteamCMD')
    SERVER_DIR = os.path.expandvars(r'%USERPROFILE%\Steam\steamapps\common\Palworld Dedicated Server')
else:
    STEAMCMD_DIR = os.path.expanduser('~/SteamCMD')
    SERVER_DIR = os.path.expanduser('~/Steam/steamapps/common/Palworld Dedicated Server')
PALWORLD_APPID = "2394010"

def download_steamcmd():
    if not os.path.exists(STEAMCMD_DIR):
        os.makedirs(STEAMCMD_DIR)
    steamcmd_zip = os.path.join(STEAMCMD_DIR, 'steamcmd.zip')
    if not os.path.exists(os.path.join(STEAMCMD_DIR, 'steamcmd.exe')):
        print("Downloading SteamCMD...")
        urllib.request.urlretrieve(STEAMCMD_URL, steamcmd_zip)
        with zipfile.ZipFile(steamcmd_zip, 'r') as zip_ref:
            zip_ref.extractall(STEAMCMD_DIR)
        os.remove(steamcmd_zip)
        print("SteamCMD downloaded and extracted.")
    else:
        print("SteamCMD already present.")
    return True

def install_or_update_palworld_server():
    pal_exe = os.path.join(SERVER_DIR, 'PalServer.exe')
    if os.path.exists(pal_exe):
        print("Palworld server already installed. Skipping installation.")
        return True
    print("Installing/updating Palworld Dedicated Server...")
    steamcmd_exe = os.path.join(STEAMCMD_DIR, 'steamcmd.exe')
    if not os.path.exists(steamcmd_exe):
        print("SteamCMD not found! Run download_steamcmd() first.")
        return False
    cmd = [
        steamcmd_exe,
        "+login", "anonymous",
        "+force_install_dir", SERVER_DIR,
        "+app_update", PALWORLD_APPID, "validate",
        "+quit"
    ]
    result = subprocess.run(cmd, shell=True)
    if result.returncode == 0:
        print("Palworld server installed/updated.")
        return True
    else:
        print("Failed to install/update Palworld server.")
        return False

def setup_upnp_port_forwarding():
    """Set up UPnP port forwarding for Palworld server (port 8211)"""
    upnp_success = False
    if miniupnpc:
        try:
            upnp = miniupnpc.UPnP()
            upnp.discoverdelay = 200
            upnp.discover()
            upnp.selectigd()
            local_ip = upnp.lanaddr
            upnp.addportmapping(8211, 'TCP', local_ip, 8211, 'Palworld Server', '')
            upnp.addportmapping(8211, 'UDP', local_ip, 8211, 'Palworld Server', '')
            print(f"UPnP port forwarding set for 8211 TCP/UDP to {local_ip}")
            upnp_success = True
        except Exception as e:
            print(f"UPnP port forwarding failed: {e}")
            upnp_success = False
    else:
        print("miniupnpc not installed. Skipping UPnP port forwarding.")
        upnp_success = False
    
    return upnp_success

def start_palworld_server():
    """Start the Palworld dedicated server"""
    pal_exe = os.path.join(SERVER_DIR, 'PalServer.exe')
    
    if not os.path.exists(pal_exe):
        print(f"PalServer.exe not found in {SERVER_DIR}. Run install_or_update_palworld_server() first.")
        return False
    
    print("Starting Palworld Dedicated Server...")
    try:
        subprocess.Popen([pal_exe], cwd=SERVER_DIR)
        
        # Get public IP for information
        try:
            public_ip = requests.get('https://api.ipify.org').text
            print(f"Server started successfully. Public IP: {public_ip}, Port: 8211")
        except Exception as e:
            print("Server started. Could not retrieve public IP.")
            print(f"Error: {e}")
        
        return True
    except Exception as e:
        print(f"Failed to start Palworld server: {e}")
        return False


# Remove SteamCMD if installed
def uninstall_steamcmd():
    if os.path.exists(STEAMCMD_DIR):
        try:
            shutil.rmtree(STEAMCMD_DIR)
            print(f"SteamCMD uninstalled from {STEAMCMD_DIR}.")
            return True
        except Exception as e:
            print(f"Failed to uninstall SteamCMD: {e}")
            return False
    else:
        print("SteamCMD is not installed.")
        return False

# Remove Palworld Dedicated Server if installed
def uninstall_palworld_server():
    if os.path.exists(SERVER_DIR):
        try:
            shutil.rmtree(SERVER_DIR)
            print(f"Palworld Dedicated Server uninstalled from {SERVER_DIR}.")
            return True
        except Exception as e:
            print(f"Failed to uninstall Palworld server: {e}")
            return False
    else:
        print("Palworld Dedicated Server is not installed.")
        return False

# Remove UPnP port forwarding rule for port 8211 if it exists
def remove_port_forward_rule():
    if miniupnpc:
        try:
            upnp = miniupnpc.UPnP()
            upnp.discoverdelay = 200
            upnp.discover()
            upnp.selectigd()
            local_ip = upnp.lanaddr

            tcp_removed = False
            udp_removed = False

            # Try removing TCP rule - match the addportmapping format
            try:
                tcp_removed = upnp.deleteportmapping(8211, 'TCP', '')
                if tcp_removed:
                    print("UPnP TCP port forwarding rule for 8211 removed.")
                else:
                    print("No UPnP TCP port forwarding rule for 8211 found to remove.")
            except Exception as e:
                if "Invalid Args" in str(e):
                    print("No UPnP TCP port forwarding rule for 8211 found (or router doesn't support removal).")
                    tcp_removed = False
                else:
                    print(f"Failed to remove UPnP TCP port forwarding rule: {e}")
                    tcp_removed = False

            # Try removing UDP rule - match the addportmapping format
            try:
                udp_removed = upnp.deleteportmapping(8211, 'UDP', '')
                if udp_removed:
                    print("UPnP UDP port forwarding rule for 8211 removed.")
                else:
                    print("No UPnP UDP port forwarding rule for 8211 found to remove.")
            except Exception as e:
                if "Invalid Args" in str(e):
                    print("No UPnP UDP port forwarding rule for 8211 found (or router doesn't support removal).")
                    udp_removed = False
                else:
                    print(f"Failed to remove UPnP UDP port forwarding rule: {e}")
                    udp_removed = False

            return tcp_removed or udp_removed
        except Exception as e:
            print(f"Failed to initialize UPnP for removing port forwarding rule: {e}")
            return False
    else:
        print("miniupnpc not installed. Cannot remove UPnP port forwarding rule.")
        return False

if __name__ == "__main__":
    #uninstall_palworld_server()
    #uninstall_steamcmd()
    pass

