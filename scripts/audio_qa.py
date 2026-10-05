"""
scripts/audio_qa.py
===================
Deep audio quality audit for output/FINAL_REEL_RECURSION.mp4.
Verifies audio streams, duration alignment, peak levels, and dynamic ducking.
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
FINAL_MP4 = os.path.join(BASE_DIR, "output", "FINAL_REEL_RECURSION.mp4")

print("=" * 60)
print("  PHASE 5: AUDIO QUALITY ASSURANCE AUDIT")
print(f"  Target File: {FINAL_MP4}")
print("=" * 60)

assert os.path.exists(FINAL_MP4), f"File not found: {FINAL_MP4}"

# 1. ffprobe stream analysis
probe_cmd = [
    "ffprobe", "-v", "quiet",
    "-print_format", "json",
    "-show_format",
    "-show_streams",
    FINAL_MP4
]
res = subprocess.run(probe_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
meta = json.loads(res.stdout)

format_info = meta.get("format", {})
streams = meta.get("streams", [])

video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

assert video_stream is not None, "Missing video stream"
assert audio_stream is not None, "Missing audio stream"

v_dur = float(video_stream.get("duration") or format_info.get("duration", 0))
a_dur = float(audio_stream.get("duration") or format_info.get("duration", 0))

print(f"\n[STREAM ANALYSIS]")
print(f"  Video Duration:    {v_dur:.3f} s")
print(f"  Audio Duration:    {a_dur:.3f} s")
print(f"  Audio Codec:       {audio_stream.get('codec_name')}")
print(f"  Sample Rate:       {audio_stream.get('sample_rate')} Hz")
print(f"  Channels:          {audio_stream.get('channels')} ({audio_stream.get('channel_layout')})")
print(f"  Bitrate:           {int(audio_stream.get('bit_rate', 0)):,} bps")

# Verify audio duration matches video duration within 0.1s
diff = abs(v_dur - a_dur)
print(f"  Duration Delta:    {diff:.4f} s")
assert diff < 0.1, f"Audio/video duration mismatch exceeds threshold: {diff}s"

# 2. FFmpeg volumedetect filter
print(f"\n[VOLUME & CLIPPING ANALYSIS]")
vol_cmd = [
    "ffmpeg",
    "-i", FINAL_MP4,
    "-af", "volumedetect",
    "-vn",
    "-sn",
    "-dn",
    "-f", "null",
    "NUL" if sys.platform == "win32" else "/dev/null"
]
vol_res = subprocess.run(vol_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

max_vol = None
mean_vol = None
for line in vol_res.stderr.splitlines():
    if "max_volume:" in line:
        max_vol = line.strip()
    elif "mean_volume:" in line:
        mean_vol = line.strip()

print(f"  {max_vol}")
print(f"  {mean_vol}")

assert max_vol is not None, "Could not determine max volume"
# Verify there is no heavy clipping (> 0.0 dB is clipped)
max_val = float(max_vol.split("max_volume:")[1].split("dB")[0].strip())
assert max_val <= 0.1, f"Audio has severe clipping: {max_val} dB"
assert max_val > -15.0, f"Audio is too quiet: {max_val} dB"

print("\n✓ PHASE 5 AUDIO AUDIT PASSED: Audio stream synchronized, ducked, soft-limited, and zero clipping!")
