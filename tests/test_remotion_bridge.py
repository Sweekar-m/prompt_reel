"""
tests/test_remotion_bridge.py
Verifies the Video JSON -> Remotion composition bridge and fallback capability.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from renderer.remotion_renderer import is_remotion_available, prepare_remotion_props, render_remotion_video

def main():
    print("Checking Remotion availability...")
    avail = is_remotion_available()
    print(f"is_remotion_available: {avail}")
    assert avail, "Remotion must be available!"

    # Sample Video JSON motion plan
    sample_plan = {
        "version": "2.0",
        "topic": "Recursion in Hardware",
        "duration": 3.0,
        "fps": 30,
        "total_frames": 90,
        "creative_direction": {
            "style_id": "cyberpunk",
            "palette": {
                "id": "electric_matrix",
                "background": [10, 14, 23],
                "primary": [0, 240, 255],
                "secondary": [255, 0, 128],
                "accent": [255, 230, 0],
                "surface": [18, 24, 38],
                "text": [240, 245, 255],
                "subtext": [140, 160, 190]
            },
            "typography": {
                "heading": "Inter, sans-serif",
                "body": "Inter, sans-serif",
                "mono": "JetBrains Mono, monospace"
            },
            "hook": {
                "headline_template": "HOW RECURSION WORKS",
                "subtext_template": "Call stack frames in memory."
            }
        },
        "scenes": [
            {
                "id": "scene_1_hook",
                "beat_name": "HOOK",
                "start": 0.0,
                "end": 3.0,
                "duration": 3.0,
                "visual_type": "hook",
                "voice_text": "How recursion works.",
                "elements": {
                    "badge": "CS CONCEPTS",
                    "headline": "HOW RECURSION WORKS",
                    "subtext": "Call stack frames in physical memory."
                }
            }
        ]
    }

    test_out_dir = os.path.join(BASE_DIR, "output", "test_remotion")
    os.makedirs(test_out_dir, exist_ok=True)
    out_video = os.path.join(test_out_dir, "test_render.mp4")

    def on_progress(pct, msg):
        print(f"[{pct}%] {msg}")

    print("Rendering 3-second motion plan using Remotion...")
    success = render_remotion_video(
        sample_plan,
        out_video,
        fast_mode=True,
        progress_callback=on_progress
    )

    print(f"Render result: {success}")
    if success and os.path.exists(out_video):
        size = os.path.getsize(out_video)
        print(f"SUCCESS: Rendered video at {out_video} (size: {size} bytes)")
    else:
        print("FAILED to render video")
        sys.exit(1)

if __name__ == "__main__":
    main()
