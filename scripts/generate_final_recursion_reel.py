"""
scripts/generate_final_recursion_reel.py
========================================
Executes the complete end-to-end 10-step AI Reel Studio pipeline for:
Topic: "What recursion actually does to your call stack"
Duration: 52 seconds
Resolution: 1080x1920 (9:16 Vertical Mobile Video)
Engine: Remotion Motion Graphics Engine + Neural Voiceover + Procedural Music/SFX + FFmpeg
"""
import os
import sys
import json
import shutil
import asyncio
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from server.services.reel_service import ReelService

TOPIC = "What recursion actually does to your call stack"
DURATION = 52.0
REQUESTED_STYLE = "cyberpunk"


async def main():
    print("=" * 70)
    print("  REEL STUDIO: GENERATING REAL 52-SECOND FINAL MP4")
    print(f"  Topic:    '{TOPIC}'")
    print(f"  Duration: {DURATION}s @ 30 FPS")
    print(f"  Canvas:   1080 x 1920 (9:16 vertical)")
    print("=" * 70)

    service = ReelService()
    project = service.create_project(topic=TOPIC, style=REQUESTED_STYLE, duration=DURATION)
    reel_id = project["id"]
    print(f"\n[*] Created project ID: {reel_id}")

    # Track progress output
    async def progress_listener():
        queue = service.subscribe_progress(reel_id)
        while True:
            msg = await queue.get()
            step = msg.get("step")
            pct = msg.get("pct")
            text = msg.get("msg")
            pct_val = f"{pct:3d}%" if pct is not None else "  --%"
            print(f"  [{pct_val}] (Step {step}) {text}", flush=True)
            if step == 10 or step == -1:
                break

    listener_task = asyncio.create_task(progress_listener())

    # Run the full pipeline in full 1080x1920 mode (fast_mode=False)
    await service.run_full_pipeline(reel_id, fast_mode=False)
    await listener_task

    # Inspect generated project
    updated_project = service.get_project(reel_id)
    assert updated_project["status"] == "completed", f"Pipeline failed: {updated_project.get('error')}"

    video_path = updated_project.get("video_path")
    assert video_path and os.path.exists(video_path), "Final video not created!"

    output_dir = os.path.join(BASE_DIR, "output")
    os.makedirs(output_dir, exist_ok=True)

    final_dest_mp4 = os.path.join(output_dir, "FINAL_REEL_RECURSION.mp4")
    shutil.copy2(video_path, final_dest_mp4)
    print(f"\n✓ Saved final master video to: {final_dest_mp4}")

    # Generate thumbnail frame (at 4.5 seconds - during visual metaphor or hook payoff)
    thumbnail_path = os.path.join(output_dir, "FINAL_REEL_RECURSION_thumbnail.png")
    thumb_cmd = [
        "ffmpeg", "-y",
        "-ss", "00:00:04.500",
        "-i", final_dest_mp4,
        "-vframes", "1",
        "-q:v", "2",
        thumbnail_path
    ]
    subprocess.run(thumb_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"✓ Saved thumbnail to: {thumbnail_path}")

    # Check file sizes
    mp4_size = os.path.getsize(final_dest_mp4)
    thumb_size = os.path.getsize(thumbnail_path)
    print(f"  Final MP4 Size:       {mp4_size:,} bytes ({mp4_size / (1024*1024):.2f} MB)")
    print(f"  Thumbnail Size:       {thumb_size:,} bytes")
    print(f"  Project directory:    {os.path.join(BASE_DIR, 'projects', reel_id)}")
    print("\n" + "=" * 70)
    print("  PRODUCTION VIDEO GENERATION COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
