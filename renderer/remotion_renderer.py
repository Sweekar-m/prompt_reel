"""
renderer/remotion_renderer.py
=============================
Bridge between Video JSON (motion_plan) and Remotion Motion Graphics Engine.
Translates motion_plan specifications into Remotion composition props, executes
Remotion CLI rendering, monitors progress, and handles errors with fallback support.
"""
import os
import sys
import json
import shutil
import subprocess
import re
from typing import Dict, Any, Optional, Callable

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOTION_DIR = os.path.join(BASE_DIR, "remotion")


def is_remotion_available() -> bool:
    """Checks if Node, npx, and the Remotion project are installed and ready."""
    try:
        # Check node
        node_res = subprocess.run(["node", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        if node_res.returncode != 0:
            return False

        # Check Remotion project directory and node_modules
        if not os.path.exists(REMOTION_DIR):
            return False

        remotion_mod = os.path.join(REMOTION_DIR, "node_modules", "remotion")
        if not os.path.exists(remotion_mod):
            return False

        return True
    except Exception:
        return False


def prepare_remotion_props(motion_plan: Dict[str, Any], output_props_path: str) -> str:
    """
    Serializes motion_plan into the Remotion ReelCompositionProps schema:
    { "motionPlan": { ... } }
    """
    props = {
        "motionPlan": motion_plan
    }
    os.makedirs(os.path.dirname(os.path.abspath(output_props_path)), exist_ok=True)
    with open(output_props_path, "w", encoding="utf-8") as f:
        json.dump(props, f, indent=2, ensure_ascii=False)

    return output_props_path


def render_remotion_video(
    motion_plan: Dict[str, Any],
    output_mp4_path: str,
    fast_mode: bool = False,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> bool:
    """
    Executes Remotion CLI to render the motion graphics video directly
    from the Video JSON motion_plan.

    Returns True if rendering succeeded, False if it failed.
    """
    if not is_remotion_available():
        return False

    output_mp4_path = os.path.abspath(output_mp4_path)
    project_dir = os.path.dirname(output_mp4_path)
    props_path = os.path.join(project_dir, "remotion_props.json")
    prepare_remotion_props(motion_plan, props_path)

    # Remotion composition ID
    comp_id = "ReelComposition"
    entry_file = "src/index.ts"

    # Scale for fast mode (540x960) vs production (1080x1920)
    scale = "0.5" if fast_mode else "1"

    # Dynamic concurrency based on CPU count (defaults to 4 on 8-core machines)
    cpu_cores = os.cpu_count() or 4
    concurrency = str(max(2, min(4, cpu_cores // 2)))

    # Resolve remotion binary: prefer local node_modules/.bin/remotion.cmd
    local_bin = os.path.join(REMOTION_DIR, "node_modules", ".bin", "remotion.cmd" if sys.platform == "win32" else "remotion")
    base_args = [
        "render",
        entry_file,
        comp_id,
        output_mp4_path,
        f"--props={props_path}",
        f"--scale={scale}",
        f"--concurrency={concurrency}",
        "--overwrite",
        "--gl=angle"
    ]

    if os.path.exists(local_bin):
        cmd = [local_bin, *base_args]
    else:
        npx_cmd = "npx.cmd" if sys.platform == "win32" else "npx"
        cmd = [npx_cmd, "remotion", *base_args]

    try:
        process = subprocess.Popen(
            cmd,
            cwd=REMOTION_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            universal_newlines=True
        )

        frame_progress_re = re.compile(r"Rendered\s+(\d+)/(\d+)")
        bundle_progress_re = re.compile(r"Bundling\s+(\d+)%")

        last_lines = []
        for line in process.stdout:
            line_str = line.strip()
            if not line_str:
                continue
            last_lines.append(line_str)
            if len(last_lines) > 20:
                last_lines.pop(0)

            # Check for actual frame rendering progress
            frame_match = frame_progress_re.search(line_str)
            if frame_match and progress_callback:
                cur = int(frame_match.group(1))
                tot = int(frame_match.group(2))
                pct = int((cur / max(1, tot)) * 100)
                mapped_pct = 85 + int(pct * 0.10)
                progress_callback(mapped_pct, f"Remotion rendering: frame {cur}/{tot} ({pct}%)")
            else:
                bundle_match = bundle_progress_re.search(line_str)
                if bundle_match and progress_callback:
                    bpct = int(bundle_match.group(1))
                    mapped_pct = 75 + int(bpct * 0.08)
                    progress_callback(mapped_pct, f"Bundling Webpack assets: {bpct}%")

        process.wait()
        exists = os.path.exists(output_mp4_path)
        print(f"[RemotionRenderer] Process finished with exit code {process.returncode}. Target exists: {exists}", flush=True)
        if process.returncode != 0 or not exists:
            print("[RemotionRenderer] Last lines from Remotion output:\n" + "\n".join(last_lines), flush=True)

        return process.returncode == 0 and exists
    except Exception as e:
        print(f"[RemotionRenderer] Error executing Remotion render: {e}", file=sys.stderr, flush=True)
        return False
