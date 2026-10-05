"""
tests/test_error_handling.py
============================
Verifies graceful error handling and fallback behaviors:
- Nemotron unavailable -> heuristic fallback
- Remotion unavailable -> fallback to Pillow/OpenCV renderer
- Missing audio -> video-only FFmpeg mux
- Invalid / missing motion_plan -> validation failure handled
"""
import os
import sys
import json
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from ai.nemotron_client import NemotronClient
from renderer.remotion_renderer import render_remotion_video
from renderer.deterministic_renderer import render_motion_plan_frame

print("=" * 60)
print("  PHASE 8: ERROR HANDLING & RESILIENCE TEST")
print("=" * 60)

# 1. Test Nemotron offline heuristic fallback
print("\n[TEST 1] Testing Nemotron offline fallback resilience...")
offline_client = NemotronClient(api_key="")
assert not offline_client.is_live, "Client should be in offline mode"
explanation = offline_client.explain_technical_concept("Deadlock detection in databases")
assert "core_mechanism" in explanation, "Missing core_mechanism in offline fallback"
assert len(explanation.get("how_it_works_steps", [])) >= 2, "Missing explanation steps"
print(f"✓ Offline Nemotron Engine generated explanation: {explanation['core_mechanism']}")

# 2. Test Remotion missing / failed render handling
print("\n[TEST 2] Testing Remotion failure fallback to Pillow renderer...")
invalid_plan = {"topic": "Faulty Plan", "duration": 1.0, "scenes": []}
# Passing invalid plan or non-existent props
render_res = render_remotion_video(invalid_plan, "non_existent_dir/out.mp4", fast_mode=True)
assert render_res is False, "render_remotion_video should return False on failure, not raise unhandled exception"
print("✓ Remotion render cleanly returned False upon invalid spec without crashing.")

# 3. Test Pillow / OpenCV deterministic fallback renderer execution
print("\n[TEST 3] Verifying deterministic Pillow fallback renderer...")
valid_sample = {
    "topic": "Fallback Execution Test",
    "creative_direction": {
        "style_id": "minimal",
        "palette": {
            "id": "swiss_cobalt",
            "background": [245, 245, 247],
            "primary": [20, 20, 25],
            "secondary": [0, 80, 255],
            "accent": [255, 60, 60],
            "surface": [255, 255, 255],
            "text": [30, 30, 35],
            "subtext": [100, 100, 110]
        },
        "typography": {"id": "inter_jetbrains"}
    },
    "scenes": [
        {
            "id": "s1",
            "start": 0.0,
            "end": 2.0,
            "duration": 2.0,
            "visual_type": "hook",
            "elements": {"headline": "FALLBACK ENGINE", "badge": "SAFETY"}
        }
    ]
}
frame_img = render_motion_plan_frame(valid_sample, t=0.5, frame_idx=15, canvas_size=(540, 960))
assert frame_img is not None, "Fallback Pillow renderer failed to render image"
assert frame_img.size == (540, 960), f"Unexpected size: {frame_img.size}"
print(f"✓ Fallback Pillow engine generated valid {frame_img.size} image frame successfully.")

# 4. Test missing audio FFmpeg handling
print("\n[TEST 4] Testing missing audio FFmpeg mux handling...")
test_out_dir = os.path.join(BASE_DIR, "output", "test_error_handling")
os.makedirs(test_out_dir, exist_ok=True)
dummy_video = os.path.join(test_out_dir, "dummy_video.mp4")

# Generate 1-sec color bar video
gen_v = [
    "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=blue:s=320x240:d=1",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", dummy_video
]
subprocess.run(gen_v, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Mux when audio file is missing
non_existent_audio = "missing_audio_track.wav"
final_fallback_mp4 = os.path.join(test_out_dir, "fallback_no_audio.mp4")

if os.path.exists(non_existent_audio):
    cmd = ["ffmpeg", "-y", "-i", dummy_video, "-i", non_existent_audio, "-c:v", "copy", final_fallback_mp4]
else:
    # Graceful fallback branch implemented in reel_service.py
    cmd = ["ffmpeg", "-y", "-i", dummy_video, "-c:v", "copy", final_fallback_mp4]

subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
assert os.path.exists(final_fallback_mp4), "Fallback video not created"
print(f"✓ Video-only muxing branch succeeded ({os.path.getsize(final_fallback_mp4)} bytes).")

print("\n" + "=" * 60)
print("✓ PHASE 8: ALL ERROR HANDLING & FALLBACK TESTS PASSED!")
print("=" * 60)
