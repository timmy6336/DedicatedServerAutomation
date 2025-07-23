import os
import subprocess
import sys
import urllib.request
import zipfile
import requests
import platform
import subprocess
import miniupnpc
import subprocess

STEAMCMD_URL = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
STEAMCMD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../steamcmd'))
SERVER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../palworld_server'))
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

def start_palworld_server():
    pal_exe = os.path.join(SERVER_DIR, 'PalServer.exe')
    # Attempt UPnP port forwarding for 8211
    upnp_success = False
    if miniupnpc:
        try:
            upnp = miniupnpc.UPnP()
            upnp.discoverdelay = 200
            upnp.discover()
            upnp.selectigd()
            local_ip = upnp.lanaddr
            upnp.addportmapping(8211, 'TCP', local_ip, 8211, 'Palworld Server', '')
            print(f"UPnP port forwarding set for 8211 TCP/UDP to {local_ip}")
            upnp_success = True
        except Exception as e:
            print(f"UPnP port forwarding failed: {e}")
    else:
        print("miniupnpc not installed. Skipping UPnP port forwarding.")
    if not os.path.exists(pal_exe):
        print(f"PalServer.exe not found in {SERVER_DIR}. Run install_or_update_palworld_server() first.")
        return
    print("Starting Palworld Dedicated Server...")
    subprocess.Popen([pal_exe], cwd=SERVER_DIR)
    # Get public IP
    try:
        public_ip = requests.get('https://api.ipify.org').text
        # Check if public IP is pingable
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        ping_cmd = ['ping', param, '1', public_ip]
        ping_result = subprocess.run(ping_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if ping_result.returncode == 0:
            print(f"Server started. Public IP {public_ip} is pingable. You can now connect to {public_ip}:8211 in Palworld.")
        else:
            print(f"Server started. Public IP {public_ip} is NOT pingable. Check your network/firewall settings.")
    except Exception as e:
        print("Server started. Could not retrieve or ping public IP.")
        print(f"Error: {e}")

if __name__ == "__main__":
    download_steamcmd()
    if install_or_update_palworld_server():
        start_palworld_server()
