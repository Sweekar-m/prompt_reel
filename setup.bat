@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo   REEL STUDIO - Automated 1-Click Environment Setup
echo ========================================================

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py -3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python 3.10+ is required but not found in PATH.
        echo Please install Python from https://python.org and re-run setup.
        pause
        exit /b 1
    )
    set PY_CMD=py -3
) else (
    set PY_CMD=python
)

echo [*] Using Python: %PY_CMD%
echo [*] Installing Python dependencies...
%PY_CMD% -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies.
    pause
    exit /b 1
)

:: 2. Check Node.js and npm
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is required for Remotion motion graphics engine.
    echo Please install Node.js (v18+) from https://nodejs.org and re-run setup.
    pause
    exit /b 1
)

echo [*] Installing Remotion Node dependencies...
pushd remotion
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Remotion npm dependencies.
    popd
    pause
    exit /b 1
)
popd

:: 3. Setup .env file
if not exist .env (
    echo [*] Creating .env from .env.example...
    copy .env.example .env >nul
    echo [i] Created .env configuration file.
) else (
    echo [i] Existing .env file found.
)

echo.
echo ========================================================
echo   SUCCESS! Reel Studio is ready to use!
echo ========================================================
echo.
echo  To add your AI Key (Optional):
echo    Open .env and set: NVIDIA_NIM_API_KEY=your_key_here
echo    (Note: Reel Studio runs seamlessly offline even without a key!)
echo.
echo  To start Reel Studio:
echo    .\reel.bat
echo    - or -
echo    python generate_reel.py
echo.
echo ========================================================
