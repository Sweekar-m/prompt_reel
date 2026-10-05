"""
cli/main.py
===========
Unified CLI Entry Point for REEL STUDIO.
Usage:
    reel
    reel --port 8000
    reel --no-browser
    reel --topic "How recursion works"
    reel --version
"""
import os
import sys
import time
import argparse
import subprocess
import webbrowser
import urllib.request
import urllib.error
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

VERSION = "2.0.0"
DEFAULT_PORT = 5055
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def is_server_running(port: int) -> bool:
    """Checks if the Reel Studio server is healthy on the given port."""
    url = f"http://127.0.0.1:{port}/health"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ReelCLI"})
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("status") == "ok"
    except Exception:
        pass
    return False


def start_server_background(port: int) -> subprocess.Popen:
    """Starts the FastAPI uvicorn server in a background process."""
    cmd = [
        sys.executable,
        "-u",
        "-m",
        "uvicorn",
        "server.app:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--log-level",
        "info"
    ]

    log_file = os.path.join(BASE_DIR, "server.log")
    f_out = open(log_file, "a", encoding="utf-8")

    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP

    proc = subprocess.Popen(
        cmd,
        cwd=BASE_DIR,
        creationflags=creationflags,
        stdout=f_out,
        stderr=f_out,
        stdin=subprocess.DEVNULL,
        close_fds=True
    )
    return proc





def print_banner(url: str):
    print("\n" + "=" * 60)
    print("  REEL STUDIO")
    print("  Local AI Motion Graphics Studio")
    print(f"  URL: {url}")
    print("=" * 60 + "\n")



def create_reel_via_api(port: int, topic: str):
    """Submits a new reel project to the local API."""
    url = f"http://127.0.0.1:{port}/api/reels"
    payload = json.dumps({"topic": topic, "style": "cinematic"}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            reel_id = data.get("reel", {}).get("id")
            print(f"  ✓ Initialized Reel Project '{reel_id}' for topic: \"{topic}\"")
            return reel_id
    except Exception as e:
        print(f"  [!] Note: Could not auto-queue topic via API: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="REEL STUDIO — Local AI Motion Graphics Studio",
        prog="reel"
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to run the studio server on (default: 5055)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser automatically")
    parser.add_argument("--topic", type=str, default=None, help="Pre-load and generate a reel on this topic")
    parser.add_argument("--version", action="store_true", help="Print version and exit")

    args = parser.parse_args()

    if args.version:
        print(f"REEL STUDIO v{VERSION}")
        sys.exit(0)

    port = args.port
    studio_url = f"http://localhost:{port}"

    # 1. Detect if server is running
    running = is_server_running(port)
    if not running:
        print(f"[*] Starting Reel Studio server on port {port}...")
        start_server_background(port)

        # Wait for server to become responsive
        max_wait_sec = 6.0
        start_t = time.time()
        while time.time() - start_t < max_wait_sec:
            if is_server_running(port):
                running = True
                break
            time.sleep(0.3)

        if not running:
            print(f"[!] Warning: Server did not respond within {max_wait_sec}s. Trying to proceed anyway...")

    # 2. Print Studio Banner
    print_banner(studio_url)

    # 3. Handle --topic if specified
    if args.topic:
        reel_id = create_reel_via_api(port, args.topic)
        if reel_id:
            studio_url += f"?topic={urllib.parse.quote(args.topic)}&reel={reel_id}"
        else:
            studio_url += f"?topic={urllib.parse.quote(args.topic)}"

    # 4. Open browser automatically unless requested not to
    if not args.no_browser:
        print(f"[*] Opening browser to {studio_url} ...")
        webbrowser.open(studio_url)
    else:
        print(f"[*] Server running. Access at: {studio_url}")


if __name__ == "__main__":
    main()
