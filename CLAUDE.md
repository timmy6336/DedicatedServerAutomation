# DedicatedServerAutomation

A PyQt5 desktop GUI app for managing Palworld dedicated game servers. Automates downloading, installing, configuring, and running a Palworld server via SteamCMD.

## Project Structure
src/
├── main.py # Entry point
├── hello_app.py # Main window (two-panel layout: game list left, details right)
├── game.py # Game data model (loads from game_info.json)
├── game_info.json # Palworld metadata
├── game_details_page.py # Server control panel UI
├── styles.py # Dark theme constants and reusable styles
├── setup_windows/
│ ├── base_setup_window.py # Abstract multi-step install wizard with worker threads
│ └── palworld_setup_window.py # 3-step Palworld setup wizard
├── scripts/
│ └── palworld_server_startup_script.py # SteamCMD download, Palworld install, server launch, UPnP
├── utils/
│ └── server_detection.py # Process detection, local/public IP discovery
└── static/
├── games_list.py # Hardcoded game list (currently just Palworld)
└── extract_game_info.py # Data extraction utility

## Tech Stack
- **Python 3 + PyQt5** — GUI framework
- **psutil** — process monitoring
- **miniupnpc** — UPnP port forwarding
- **requests** — HTTP/IP detection
- **python-dotenv** — env var management
- **PyInstaller** — builds Windows executable
## Key Behaviors
- Server status polled every 10 seconds via QTimer
- Long operations (SteamCMD install, Palworld download) run in worker threads to keep UI responsive
- Palworld server runs on port **8211** (TCP + UDP)
- UPnP port forwarding attempted automatically, fails gracefully
- Public IP fetched from ipify/httpbin/ipinfo with fallbacks
- SteamCMD installed to `%LOCALAPPDATA%\DedicatedServerAutomation\SteamCMD` (Windows)
- Palworld server installed via AppID **2394010**
## Current Limitations
- Only Palworld is implemented; game list is hardcoded in `static/games_list.py`
- No persistent configuration storage
- Windows-primary (paths use `os.path.expandvars` for `%LOCALAPPDATA%`)
## Running Locally
```bash
pip install -r requirements.txt
python src/main.py
