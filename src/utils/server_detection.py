import psutil
import socket
import requests
import subprocess
import platform

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Create a socket connection to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Connect to a remote address (doesn't actually send data)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        return "Unable to determine"

def get_public_ip():
    """Get the public IP address"""
    try:
        # Try multiple services in case one is down
        services = [
            "https://api.ipify.org",
            "https://httpbin.org/ip",
            "https://ipinfo.io/ip"
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    if "ipify" in service:
                        return response.text.strip()
                    elif "httpbin" in service:
                        return response.json()["origin"]
                    elif "ipinfo" in service:
                        return response.text.strip()
            except:
                continue
        
        return "Unable to determine"
    except Exception:
        return "Unable to determine"

def is_palworld_server_running():
    """Check if Palworld dedicated server is running"""
    try:
        # Look for Palworld server processes
        palworld_processes = [
            "PalServer.exe",
            "PalServer-Win64-Test-Cmd.exe",
            "PalServer-Win64-Shipping-Cmd.exe"
        ]
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                process_name = proc.info['name']
                if process_name and any(palworld_proc.lower() in process_name.lower() for palworld_proc in palworld_processes):
                    return True
                    
                # Also check command line for Palworld server
                cmdline = proc.info['cmdline']
                if cmdline and any('palworld' in cmd.lower() and 'server' in cmd.lower() for cmd in cmdline):
                    return True
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        return False
    except Exception:
        return False

def get_palworld_server_port():
    """Get the port that Palworld server is running on (default 8211)"""
    try:
        # Check if port 8211 is in use (default Palworld port)
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == 8211 and conn.status == psutil.CONN_LISTEN:
                return 8211
        
        # If not found, return default
        return 8211
    except Exception:
        return 8211

def get_server_status_info(game_name):
    """Get comprehensive server status information for a game"""
    game_name_lower = game_name.lower()
    
    status_info = {
        'is_running': False,
        'local_ip': get_local_ip(),
        'public_ip': get_public_ip(),
        'port': None,
        'connection_string': None
    }
    
    if game_name_lower == "palworld":
        status_info['is_running'] = is_palworld_server_running()
        if status_info['is_running']:
            status_info['port'] = get_palworld_server_port()
            if status_info['local_ip'] != "Unable to determine":
                status_info['connection_string'] = f"{status_info['local_ip']}:{status_info['port']}"
    
    return status_info
