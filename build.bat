@echo off
REM US Phone Number Generator - Automatic Build Script
REM This script automates the EXE building process

echo.
echo ============================================
echo US PHONE NUMBER GENERATOR - Build Script
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [✓] Python found
python --version
echo.

REM Install dependencies
echo [*] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [✓] Dependencies installed
echo.

REM Clean previous builds
if exist dist (
    echo [*] Cleaning previous builds...
    rmdir /s /q dist 2>nul
    rmdir /s /q build 2>nul
    del /q *.spec 2>nul
)

REM Build the EXE
echo [*] Building executable...
echo This may take a minute...
echo.

pyinstaller gui_app.spec

if errorlevel 1 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)

echo.
echo ============================================
echo [✓] BUILD SUCCESSFUL!
echo ============================================
echo.
echo Your EXE is ready:
echo Location: dist\USPhoneNumberGenerator.exe
echo.
echo You can now:
echo 1. Run the EXE directly
echo 2. Share it with others (requires Windows only)
echo 3. Create a shortcut to the EXE on your desktop
echo.
pause
