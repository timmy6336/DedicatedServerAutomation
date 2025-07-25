@echo off
echo Building Dedicated Server Automation Executable...

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Clean previous builds
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM Build the executable
echo Running PyInstaller...
pyinstaller --onefile --windowed --name=DedicatedServerAutomation --add-data="src/images;images" --add-data="src/static;static" --add-data="src/game_info.json;." --clean src/main.py

if exist "dist\DedicatedServerAutomation.exe" (
    echo.
    echo ✅ Build successful!
    echo 📁 Executable created at: dist\DedicatedServerAutomation.exe
    
    REM Get file size
    for %%A in (dist\DedicatedServerAutomation.exe) do echo 📊 File size: %%~zA bytes
    
    echo.
    echo 🚀 You can now run: dist\DedicatedServerAutomation.exe
    echo 💡 The executable includes all dependencies and can run on other Windows machines
) else (
    echo ❌ Build failed! Check the output above for errors.
)

pause
