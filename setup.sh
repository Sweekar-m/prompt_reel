#!/usr/bin/env bash
set -e

echo "========================================================"
echo "  REEL STUDIO - Automated 1-Click Environment Setup"
echo "========================================================"

# 1. Check Python
if command -v python3 &>/dev/null; then
    PY_CMD="python3"
elif command -v python &>/dev/null; then
    PY_CMD="python"
else
    echo "[ERROR] Python 3.10+ is required but not found in PATH."
    exit 1
fi

echo "[*] Using Python: $PY_CMD"
echo "[*] Installing Python dependencies..."
$PY_CMD -m pip install -r requirements.txt

# 2. Check Node.js and npm
if ! command -v node &>/dev/null; then
    echo "[ERROR] Node.js is required for Remotion motion graphics engine."
    echo "Please install Node.js (v18+) from https://nodejs.org"
    exit 1
fi

echo "[*] Installing Remotion Node dependencies..."
cd remotion
npm install
cd ..

# 3. Setup .env file
if [ ! -f .env ]; then
    echo "[*] Creating .env from .env.example..."
    cp .env.example .env
    echo "[i] Created .env configuration file."
else
    echo "[i] Existing .env file found."
fi

echo ""
echo "========================================================"
echo "  SUCCESS! Reel Studio is ready to use!"
echo "========================================================"
echo ""
echo "  To add your AI Key (Optional):"
echo "    Open .env and set: NVIDIA_NIM_API_KEY=your_key_here"
echo ""
echo "  To start Reel Studio:"
echo "    $PY_CMD generate_reel.py"
echo ""
echo "========================================================"
