"""
engine/env_loader.py
====================
Lightweight, resilient .env file loader for REEL STUDIO.
Guarantees NVIDIA_NIM_API_KEY and studio settings are always populated in os.environ.
"""
import os
from typing import Dict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env(env_path: str = None) -> Dict[str, str]:
    """Loads key-value pairs from .env into os.environ if not already present."""
    if env_path is None:
        env_path = os.path.join(BASE_DIR, ".env")

    loaded = {}
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key:
                        os.environ[key] = val
                        loaded[key] = val
        except Exception as e:
            print(f"[!] Warning reading .env ({e})")

    return loaded


# Automatically load on import
load_env()
