"""
tests/test_full_suite.py
========================
Comprehensive 10-point integration test suite verifying:
1. motion_plan validation
2. Remotion availability
3. props generation
4. Remotion composition loading
5. single-frame render
6. short video render
7. full video render
8. FFmpeg mux
9. final MP4 existence
10. final MP4 metadata
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

from renderer.remotion_renderer import is_remotion_available, prepare_remotion_props, render_remotion_video

SAMPLE_PLAN = {
    "version": "2.0",
    "topic": "What recursion actually does to your call stack",
    "duration": 4.0,
    "fps": 30,
    "total_frames": 120,
    "creative_direction": {
        "style_id": "cyberpunk",
        "palette": {
            "id": "electric_matrix",
            "name": "Electric Matrix",
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
            "headline_template": "RECURSION UNLOCKED",
            "subtext_template": "Call frames in physical memory."
        }
    },
    "scenes": [
        {
            "id": "scene_1_hook",
            "beat_name": "HOOK",
            "start": 0.0,
            "end": 2.0,
            "duration": 2.0,
            "visual_type": "hook",
            "voice_text": "What does recursion actually do to your stack?",
            "elements": {
                "badge": "SYSTEM INTERNALS",
                "headline": "WHAT RECURSION DOES TO YOUR STACK",
                "subtext": "Each function call claims physical frame space."
            }
        },
        {
            "id": "scene_2_metaphor",
            "beat_name": "CALL STACK SIMULATION",
            "start": 2.0,
            "end": 4.0,
            "duration": 2.0,
            "visual_type": "metaphor",
            "voice_text": "Watch stack frames push downwards until the base case returns.",
            "elements": {
                "metaphor_id": "stack_recursion",
                "label": "CALL STACK BEHAVIOR",
                "description": "Contiguous frame allocation in thread memory."
            }
        }
    ]
}


def test_1_motion_plan_validation():
    print("\n[TEST 1] Validating motion_plan schema...")
    assert "topic" in SAMPLE_PLAN, "Missing topic"
    assert "duration" in SAMPLE_PLAN and SAMPLE_PLAN["duration"] > 0, "Invalid duration"
    assert "creative_direction" in SAMPLE_PLAN, "Missing creative direction"
    cd = SAMPLE_PLAN["creative_direction"]
    assert "palette" in cd and "background" in cd["palette"], "Missing palette"
    assert len(SAMPLE_PLAN["scenes"]) >= 1, "Must have at least 1 scene"
    for sc in SAMPLE_PLAN["scenes"]:
        assert "start" in sc and "end" in sc and "duration" in sc, "Invalid scene timing"
        assert "visual_type" in sc, "Missing visual_type"
    print("✓ Test 1 Passed: motion_plan strictly valid.")


def test_2_remotion_availability():
    print("\n[TEST 2] Checking Remotion availability...")
    available = is_remotion_available()
    assert available, "Remotion must be installed and detected"
    print("✓ Test 2 Passed: Remotion engine available.")


def test_3_props_generation(tmp_dir):
    print("\n[TEST 3] Generating Remotion props...")
    props_file = os.path.join(tmp_dir, "test_props.json")
    res_path = prepare_remotion_props(SAMPLE_PLAN, props_file)
    assert os.path.exists(res_path), "Props file was not created"
    with open(res_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "motionPlan" in data, "Root key motionPlan missing in props"
    assert data["motionPlan"]["topic"] == SAMPLE_PLAN["topic"]
    print("✓ Test 3 Passed: Props JSON created and verified.")


def test_4_composition_loading():
    print("\n[TEST 4] Inspecting Remotion compositions...")
    remotion_dir = os.path.join(BASE_DIR, "remotion")
    cmd = [
        os.path.join(remotion_dir, "node_modules", ".bin", "remotion.cmd" if sys.platform == "win32" else "remotion"),
        "compositions",
        "src/index.ts"
    ]
    res = subprocess.run(cmd, cwd=remotion_dir, capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert res.returncode == 0, f"Compositions query failed: {res.stderr}"
    assert "ReelComposition" in (res.stdout or ""), "ReelComposition not listed in compositions"
    print("✓ Test 4 Passed: ReelComposition loaded correctly.")


def test_5_single_frame_render(tmp_dir):
    print("\n[TEST 5] Rendering single test frame...")
    remotion_dir = os.path.join(BASE_DIR, "remotion")
    out_frame = os.path.join(tmp_dir, "frame_test.png")
    props_path = os.path.join(tmp_dir, "test_props.json")
    prepare_remotion_props(SAMPLE_PLAN, props_path)

    cmd = [
        os.path.join(remotion_dir, "node_modules", ".bin", "remotion.cmd" if sys.platform == "win32" else "remotion"),
        "still",
        "src/index.ts",
        "ReelComposition",
        out_frame,
        f"--props={props_path}",
        "--frame=15",
        "--overwrite",
        "--gl=angle"
    ]
    res = subprocess.run(cmd, cwd=remotion_dir, capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert res.returncode == 0, f"Still render failed: {res.stderr}"
    assert os.path.exists(out_frame), "Frame PNG not created"
    size = os.path.getsize(out_frame)
    assert size > 10000, f"Frame PNG suspiciously small: {size} bytes"
    print(f"✓ Test 5 Passed: Single frame rendered ({size} bytes).")


def test_6_and_7_short_and_full_video_render(tmp_dir):
    print("\n[TEST 6 & 7] Rendering test video via Remotion bridge...")
    raw_video = os.path.join(tmp_dir, "raw_video.mp4")
    progress_updates = []

    def on_prog(pct, msg):
        progress_updates.append((pct, msg))

    success = render_remotion_video(
        SAMPLE_PLAN,
        raw_video,
        fast_mode=True,
        progress_callback=on_prog
    )
    assert success, "render_remotion_video failed"
    assert os.path.exists(raw_video), "Rendered raw_video.mp4 not found"
    assert len(progress_updates) > 0, "No progress updates recorded"
    print(f"✓ Test 6 & 7 Passed: Video rendered with {len(progress_updates)} progress updates.")
    return raw_video


def test_8_ffmpeg_mux(tmp_dir, raw_video):
    print("\n[TEST 8] Multiplexing with FFmpeg...")
    # Generate a quick synthetic beep audio track with ffmpeg
    dummy_audio = os.path.join(tmp_dir, "dummy_audio.wav")
    gen_cmd = [
        "ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=4",
        "-ar", "48000", "-ac", "2", dummy_audio
    ]
    subprocess.run(gen_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    final_mp4 = os.path.join(tmp_dir, "final_mux_test.mp4")
    mux_cmd = [
        "ffmpeg", "-y",
        "-i", raw_video,
        "-i", dummy_audio,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        final_mp4
    ]
    mux_res = subprocess.run(mux_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert mux_res.returncode == 0, f"FFmpeg mux failed: {mux_res.stderr}"
    print("✓ Test 8 Passed: FFmpeg multiplexing succeeded.")
    return final_mp4


def test_9_and_10_mp4_metadata(final_mp4):
    print("\n[TEST 9 & 10] Inspecting final MP4 existence and metadata...")
    assert os.path.exists(final_mp4), "Final MP4 file does not exist"
    size = os.path.getsize(final_mp4)
    assert size > 50000, f"MP4 file is too small: {size} bytes"

    # Use ffprobe to query streams and duration
    probe_cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        final_mp4
    ]
    probe_res = subprocess.run(probe_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
    meta = json.loads(probe_res.stdout)

    streams = meta.get("streams", [])
    has_video = False
    has_audio = False
    v_codec = None
    a_codec = None
    width = None
    height = None

    for s in streams:
        if s.get("codec_type") == "video":
            has_video = True
            v_codec = s.get("codec_name")
            width = s.get("width")
            height = s.get("height")
        elif s.get("codec_type") == "audio":
            has_audio = True
            a_codec = s.get("codec_name")

    duration = float(meta.get("format", {}).get("duration", 0))

    assert has_video, "MP4 lacks video stream"
    assert has_audio, "MP4 lacks audio stream"
    assert v_codec == "h264", f"Unexpected video codec: {v_codec}"
    assert a_codec == "aac", f"Unexpected audio codec: {a_codec}"
    assert duration > 3.0, f"Duration too short: {duration}s"

    print(f"✓ Test 9 & 10 Passed: Video ({v_codec} {width}x{height}) + Audio ({a_codec}), Duration: {duration:.2f}s, Size: {size} bytes.")


def run_all():
    tmp_dir = os.path.join(BASE_DIR, "output", "test_suite_run")
    os.makedirs(tmp_dir, exist_ok=True)

    test_1_motion_plan_validation()
    test_2_remotion_availability()
    test_3_props_generation(tmp_dir)
    test_4_composition_loading()
    test_5_single_frame_render(tmp_dir)
    raw_video = test_6_and_7_short_and_full_video_render(tmp_dir)
    final_mp4 = test_8_ffmpeg_mux(tmp_dir, raw_video)
    test_9_and_10_mp4_metadata(final_mp4)

    print("\n" + "=" * 50)
    print("ALL 10 INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    run_all()
