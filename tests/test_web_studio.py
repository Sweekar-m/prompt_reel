"""
tests/test_web_studio.py
========================
Verifies CLI command execution, FastAPI server endpoints,
HTML dashboard accessibility, project management, and video streaming.
"""
import os
import sys
import json
import urllib.request
import urllib.error
import subprocess
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 5055
BASE_URL = f"http://127.0.0.1:{PORT}"

print("=" * 60)
print("  PHASE 7: WEB STUDIO & CLI AUTOMATED TEST")
print("=" * 60)

# 1. Test CLI main.py --version
print("\n[TEST 1] Testing 'reel --version' CLI invocation...")
cli_path = os.path.join(BASE_DIR, "cli", "main.py")
ver_res = subprocess.run([sys.executable, cli_path, "--version"], capture_output=True, text=True, encoding="utf-8", errors="replace")
assert ver_res.returncode == 0, f"CLI version failed: {ver_res.stderr}"
assert "REEL STUDIO" in ver_res.stdout, f"Unexpected version output: {ver_res.stdout}"
print(f"✓ CLI Version Command: {ver_res.stdout.strip()}")

# 2. Check if server is running or start it in background
def check_health():
    try:
        req = urllib.request.Request(f"{BASE_URL}/health", headers={"User-Agent": "ReelTest"})
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("status") == "ok"
    except Exception:
        pass
    return False

server_proc = None
if not check_health():
    print(f"\n[*] Starting Reel Studio server on port {PORT}...")
    server_cmd = [
        sys.executable, "-u", "-m", "uvicorn", "server.app:app",
        "--host", "127.0.0.1", "--port", str(PORT), "--log-level", "warning"
    ]
    server_proc = subprocess.Popen(server_cmd, cwd=BASE_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2.5)

assert check_health(), f"Server not responding on {BASE_URL}/health"
print("✓ Web Studio Server is healthy.")

# 3. Test Dashboard HTML (GET /)
print("\n[TEST 3] Loading Web Studio Dashboard HTML...")
req_home = urllib.request.Request(f"{BASE_URL}/", headers={"User-Agent": "ReelTest"})
with urllib.request.urlopen(req_home, timeout=3.0) as resp:
    assert resp.status == 200, f"Failed to load dashboard: {resp.status}"
    html_content = resp.read().decode("utf-8", errors="replace")
    assert "<html" in html_content.lower(), "Response does not contain HTML"
    assert "reel" in html_content.lower() or "studio" in html_content.lower(), "Dashboard title missing"
print(f"✓ Dashboard HTML successfully served ({len(html_content):,} bytes).")

# 4. Test List Projects (GET /api/reels)
print("\n[TEST 4] Querying Reel Projects via API...")
req_list = urllib.request.Request(f"{BASE_URL}/api/reels", headers={"User-Agent": "ReelTest"})
with urllib.request.urlopen(req_list, timeout=3.0) as resp:
    assert resp.status == 200
    data = json.loads(resp.read().decode("utf-8"))
    assert data.get("status") == "success"
    reels = data.get("reels", [])
    print(f"✓ Retrieved {len(reels)} projects.")
    has_target = any(r.get("id") == "82190f3d" for r in reels)
    assert has_target, "Target recursion project 82190f3d not in project list"

# 5. Test Single Project Details (GET /api/reels/82190f3d)
print("\n[TEST 5] Inspecting project 82190f3d details...")
req_proj = urllib.request.Request(f"{BASE_URL}/api/reels/82190f3d", headers={"User-Agent": "ReelTest"})
with urllib.request.urlopen(req_proj, timeout=3.0) as resp:
    assert resp.status == 200
    proj_data = json.loads(resp.read().decode("utf-8")).get("reel", {})
    assert proj_data.get("id") == "82190f3d"
    assert proj_data.get("status") == "completed"
    assert proj_data.get("has_video") is True
print(f"✓ Project details verified: Topic='{proj_data.get('topic')}', Status='{proj_data.get('status')}'.")

# 6. Test Video Streaming (GET /api/reels/82190f3d/video)
print("\n[TEST 6] Streaming Video via API...")
req_video = urllib.request.Request(f"{BASE_URL}/api/reels/82190f3d/video", headers={"User-Agent": "ReelTest"})
with urllib.request.urlopen(req_video, timeout=5.0) as resp:
    assert resp.status == 200 or resp.status == 206
    c_type = resp.headers.get("Content-Type", "")
    assert "video/mp4" in c_type, f"Unexpected Content-Type: {c_type}"
    chunk = resp.read(1024 * 64) # Read 64 KB
    assert len(chunk) > 0, "Video stream empty"
print(f"✓ Video streaming endpoint active: Content-Type={c_type}, received header chunk.")

# 7. Test Create Project Draft (POST /api/reels)
print("\n[TEST 7] Creating draft project via API...")
payload = json.dumps({"topic": "API Test Reel", "style": "cyberpunk", "duration": 30.0}).encode("utf-8")
req_create = urllib.request.Request(f"{BASE_URL}/api/reels", data=payload, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req_create, timeout=3.0) as resp:
    assert resp.status == 200
    c_data = json.loads(resp.read().decode("utf-8"))
    assert c_data.get("status") == "success"
    new_id = c_data.get("reel", {}).get("id")
    assert new_id is not None
print(f"✓ Created new draft project: {new_id}")

print("\n" + "=" * 60)
print("✓ PHASE 7 WEB STUDIO & CLI AUDIT PASSED: ALL ENDPOINTS VERIFIED!")
print("=" * 60)

if server_proc:
    server_proc.terminate()
