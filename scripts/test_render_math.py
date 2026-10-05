import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from renderer.deterministic_renderer import render_motion_plan_frame
from agents.creative_director import CreativeDirectorAgent
from agents.script_storyboard_agent import ScriptStoryboardAgent

print("Starting test...", flush=True)
cd_agent = CreativeDirectorAgent()
cd = cd_agent.direct_video("2d to 3d math equation sinc wave", requested_style="cinematic")
print(f"CD created! is_math={cd.get('is_math')}, hook={cd.get('hook', {}).get('headline')}", flush=True)

sb_agent = ScriptStoryboardAgent()
mp = sb_agent.generate_motion_plan("2d to 3d math equation sinc wave", cd, 50.0)
print(f"MP created! Scenes: {[s['visual_type'] for s in mp['scenes']]}", flush=True)

img_hook = render_motion_plan_frame(mp, 2.0, 60, canvas_size=(540, 960))
print(f"Hook frame rendered successfully: {img_hook.size}", flush=True)

img_math = render_motion_plan_frame(mp, 8.0, 240, canvas_size=(540, 960))
print(f"Math 3D frame rendered successfully: {img_math.size}", flush=True)
print("ALL TESTS PASSED!", flush=True)
