@echo off
echo ===================================================
echo   Building Vortex BitTorrent Client for Windows
echo ===================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8+ and check 'Add Python to PATH'.
    pause
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment.
    pause
    exit /b 1
)

:: Activate virtual environment and install dependencies
echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies.
    pause
    exit /b 1
)

:: Generate logo.ico if it doesn't exist
if not exist resources\logo.ico (
    echo Generating logo.ico...
    python -c "from PIL import Image; Image.open('resources/logo.png').save('resources/logo.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])"
)

:: Build the executables using PyInstaller
echo Building executables...
pyinstaller --clean vortex.spec
if %errorlevel% neq 0 (
    echo Error: PyInstaller build failed.
    pause
    exit /b 1
)

echo.
echo ===================================================
echo   Build Successful!
echo   Executables are located in the 'dist' directory:
echo     - dist\Vortex.exe      (Windowed GUI)
echo     - dist\Vortex-CLI.exe  (Console CLI)
echo ===================================================
echo.
pause
