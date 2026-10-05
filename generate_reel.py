"""
generate_reel.py
================
Root entry point for REEL STUDIO.
Allows running CLI commands or launching the studio from the root directory.

Usage:
    python generate_reel.py
    python generate_reel.py --topic "How Garbage Collection Works in Java"
    python generate_reel.py --port 5055
    python generate_reel.py --no-browser
"""
import sys
import os

# Add root directory to sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from cli.main import main

if __name__ == "__main__":
    main()
