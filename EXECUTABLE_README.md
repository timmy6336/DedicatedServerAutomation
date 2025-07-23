# Dedicated Server Automation - Standalone Executable

## 📦 Executable Information

**File:** `DedicatedServerAutomation.exe`  
**Size:** ~40 MB  
**Platform:** Windows 64-bit  
**Dependencies:** All included (no installation required)

## 🚀 How to Use

1. **Download** the `DedicatedServerAutomation.exe` file
2. **Run** the executable directly - no installation needed!
3. **First Time Setup:**
   - The app will create necessary folders automatically
   - Set up your API keys if you want game information (optional)

## 🎮 Supported Games

- **Palworld** - Full dedicated server setup and management
- More games coming soon!

## ⚙️ Features

- **Automatic Server Setup** - Downloads and installs server files
- **UPnP Port Forwarding** - Automatic network configuration
- **Server Status Monitoring** - Real-time server detection
- **Smart Button Logic** - Setup vs Direct Start based on installation status
- **Modern GUI** - Dark theme with fullscreen support

## 🔧 Configuration (Optional)

If you want enhanced game information and images:

1. Create a `.env` file in the same folder as the executable
2. Add your IGDB API credentials:
   ```
   IGDB_CLIENT_ID=your_client_id_here
   IGDB_CLIENT_SECRET=your_client_secret_here
   ```

## 🖥️ System Requirements

- **Windows 10/11** (64-bit)
- **4 GB RAM** minimum
- **Internet connection** for downloading server files
- **Router with UPnP** (optional, for automatic port forwarding)

## 🛠️ Server Management

### If Server Files Are NOT Installed:
- Click **"Start Dedicated Server Setup"** (Blue Button)
- Follow the 3-step installation process:
  1. Install SteamCMD
  2. Download Server Files
  3. Configure & Launch Server

### If Server Files ARE Installed:
- Click **"Start Server"** (Green Button) - Direct server start
- Button becomes disabled when server is running

## 📁 Server Locations

**SteamCMD:** `%USERPROFILE%\SteamCMD\`  
**Palworld Server:** `%USERPROFILE%\Steam\steamapps\common\Palworld Dedicated Server\`

## ⌨️ Keyboard Shortcuts

- **F11** - Toggle Fullscreen
- **Escape** - Exit Fullscreen

## 🐛 Troubleshooting

**Server won't start?**
- Check if Windows Firewall is blocking the server
- Ensure port 8211 (UDP) is available
- Try running as Administrator

**Port forwarding failed?**
- Check if UPnP is enabled on your router
- You can configure port 8211 (UDP) manually on your router
- Server will still work locally without port forwarding

**App won't start?**
- Make sure you have Windows 10/11 64-bit
- Try running as Administrator
- Check if antivirus is blocking the executable

## 📞 Support

For issues or feature requests, please check the project repository or create an issue.

---

**Version:** 1.0.0  
**Build Date:** 2025-01-23  
**Built with:** Python + PyQt5 + PyInstaller
