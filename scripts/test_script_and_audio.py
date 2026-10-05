import os
import sys
import json

# Ensure UTF-8 on Windows
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.creative_director import CreativeDirectorAgent
from agents.script_storyboard_agent import ScriptStoryboardAgent

def test():
    cda = CreativeDirectorAgent()
    ssa = ScriptStoryboardAgent()

    for topic in ["Recursion", "Binary Search", "Event Loop"]:
        cd = cda.direct_video(topic)
        print(f"\n{'='*60}\nTopic: {topic}")
        print(f"  Style: {cd['style_id']}")
        print(f"  Voice: {cd['voice']['edge_voice']} (pitch: {cd['voice'].get('pitch')}, rate: {cd['voice'].get('rate')})")
        print(f"  Sound: {cd['dna'].get('sound_profile')}")

        mp = ssa.generate_motion_plan(topic, cd, total_duration=50.0)
        print(f"  Generated {len(mp['scenes'])} scenes:")
        for sc in mp['scenes']:
            print(f"    [{sc['id']}]: {sc['narration']}")

    # Check payoff scene elements
    payoff_elem = mp['scenes'][-1]['elements']
    print("\nPayoff Scene Elements:")
    print(f"  Title: {payoff_elem.get('title')}")
    print(f"  Stat:  {payoff_elem.get('stat')}")
    print(f"  Sub:   {payoff_elem.get('subtitle')}")

if __name__ == "__main__":
    test()
