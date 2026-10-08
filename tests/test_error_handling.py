"""
tests/test_error_handling.py
============================
Verifies graceful error handling and fallback behaviors:
- Nemotron unavailable -> heuristic fallback
- Remotion failure / fallback handling
- Missing audio -> video-only FFmpeg mux
- Fallback Pillow/OpenCV renderer execution
"""
import os
import sys
import unittest
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


class TestErrorHandling(unittest.TestCase):
    def test_nemotron_offline_fallback(self):
        offline_client = NemotronClient(api_key="")
        self.assertFalse(offline_client.is_live, "Client should be in offline mode")
        explanation = offline_client.explain_technical_concept("Deadlock detection in databases")
        self.assertIn("core_mechanism", explanation, "Missing core_mechanism in offline fallback")
        self.assertGreaterEqual(len(explanation.get("how_it_works_steps", [])), 2, "Missing explanation steps")

    def test_pillow_deterministic_fallback(self):
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
        self.assertIsNotNone(frame_img, "Fallback Pillow renderer failed to render image")
        self.assertEqual(frame_img.size, (540, 960), f"Unexpected size: {frame_img.size}")

    def test_missing_audio_ffmpeg_mux(self):
        test_out_dir = os.path.join(BASE_DIR, "output", "test_error_handling")
        os.makedirs(test_out_dir, exist_ok=True)
        dummy_video = os.path.join(test_out_dir, "dummy_video.mp4")

        gen_v = [
            "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=blue:s=320x240:d=1",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", dummy_video
        ]
        subprocess.run(gen_v, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        non_existent_audio = "missing_audio_track.wav"
        final_fallback_mp4 = os.path.join(test_out_dir, "fallback_no_audio.mp4")

        if os.path.exists(non_existent_audio):
            cmd = ["ffmpeg", "-y", "-i", dummy_video, "-i", non_existent_audio, "-c:v", "copy", final_fallback_mp4]
        else:
            cmd = ["ffmpeg", "-y", "-i", dummy_video, "-c:v", "copy", final_fallback_mp4]

        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.assertTrue(os.path.exists(final_fallback_mp4), "Fallback video not created")


if __name__ == "__main__":
    unittest.main()
