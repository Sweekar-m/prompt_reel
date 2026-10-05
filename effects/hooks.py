"""
effects/hooks.py
================
The 10 Hook Archetype Engine for high-retention short-form video openings.
Generates tailored visual and narrative structures for:
1. QUESTION
2. CONTRADICTION
3. VISUAL_SHOCK
4. COLD_OPEN
5. CODE_FIRST
6. COUNTDOWN
7. MYTH
8. BEFORE_AFTER
9. STORY
10. VISUAL_METAPHOR
"""
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class HookSpec:
    id: str
    name: str
    headline_template: str
    subtext_template: str
    visual_intent: str
    audio_intent: str
    animation_style: str


HOOK_ARCHETYPES: Dict[str, HookSpec] = {
    "question": HookSpec(
        id="question",
        name="The Provocative Question",
        headline_template="WHY DOES THIS CODE RUN 100x FASTER?",
        subtext_template="Most developers have no idea.",
        visual_intent="Show confusing code benchmark with giant glowing speedup number.",
        audio_intent="Tension riser with sudden silence before question punch.",
        animation_style="scale_and_snap"
    ),

    "contradiction": HookSpec(
        id="contradiction",
        name="The Counter-Intuitive Contradiction",
        headline_template="THIS LOOKS SLOW. IT'S ACTUALLY FASTER.",
        subtext_template="Hardware doesn't work the way you think.",
        visual_intent="Split contrast screen: perceived intuition vs computational reality.",
        audio_intent="Low mechanical sub-bass click followed by sharp digital chirp.",
        animation_style="split_reveal"
    ),

    "visual_shock": HookSpec(
        id="visual_shock",
        name="The Visual Shockwave",
        headline_template="THIS IS RECURSION.",
        subtext_template="Watch what happens when memory runs out of space.",
        visual_intent="Tower of memory blocks violently exploding under stack overflow.",
        audio_intent="Heavy distorted bass drop and glass shatter impact.",
        animation_style="shockwave_expand"
    ),

    "cold_open": HookSpec(
        id="cold_open",
        name="The Assertive Cold Open",
        headline_template="YOUR CPU IS LYING TO YOU.",
        subtext_template="Here is what actually happened on line 4.",
        visual_intent="Instant full-bleed bold typography slammed onto the screen in 0.1s.",
        audio_intent="Immediate punchy voiceover starting on frame 1 with zero intro padding.",
        animation_style="hard_impact"
    ),

    "code_first": HookSpec(
        id="code_first",
        name="The Cryptic Code First",
        headline_template="GUESS WHAT THIS CODE DOES.",
        subtext_template="3 lines that break standard assumptions.",
        visual_intent="Curious, elegant code snippet typing out with highlighted mystery operator.",
        audio_intent="Rapid keyboard clatter and mysterious ambient drone.",
        animation_style="typewriter_focus"
    ),

    "countdown": HookSpec(
        id="countdown",
        name="The Kinetic Countdown",
        headline_template="3 CALLS. 2 CALLS. 1 CALL.",
        subtext_template="How the call stack unwinds in 1 millisecond.",
        visual_intent="Rapid numbers 3... 2... 1 flashing in synchronized rhythm.",
        audio_intent="3 rhythmic heartbeat clicks crescendoing into a sub impact.",
        animation_style="rhythmic_counter"
    ),

    "myth": HookSpec(
        id="myth",
        name="The Industry Mythbuster",
        headline_template="EVERYONE EXPLAINS THIS WRONG.",
        subtext_template="Stop memorizing syntax. Understand the architecture.",
        visual_intent="Red strikeout line crossing out conventional tutorial diagram.",
        audio_intent="Buzzer scratch followed by clean authoritative voice statement.",
        animation_style="strike_through"
    ),

    "before_after": HookSpec(
        id="before_after",
        name="The Performance Clash",
        headline_template="1,000,000 CHECKS vs 20 CHECKS.",
        subtext_template="The astronomical power of logarithmic scale.",
        visual_intent="Side-by-side benchmark meter: crawling red bar vs instantaneous green flash.",
        audio_intent="Alarm drone on red side, clean melodic chime on green side.",
        animation_style="dual_meter_race"
    ),

    "story": HookSpec(
        id="story",
        name="The Narrative Dilemma",
        headline_template="YOUR PROGRAM IS TRAPPED.",
        subtext_template="One missing condition just crashed production.",
        visual_intent="Warning dialog box flashing in dark server room aesthetic.",
        audio_intent="Tense cinematic clock ticking with rising synth pulse.",
        animation_style="narrative_pan"
    ),

    "visual_metaphor": HookSpec(
        id="visual_metaphor",
        name="The Tactile Metaphor",
        headline_template="THINK OF MEMORY LIKE THIS.",
        subtext_template="Physical blocks that can only collapse backwards.",
        visual_intent="Immediate 3D isometric physical object interacting on screen.",
        audio_intent="Tactile mechanical snap and wooden block landing impact.",
        animation_style="metaphor_drop"
    ),

    "math_dimension_shift": HookSpec(
        id="math_dimension_shift",
        name="The 2D-to-3D Dimension Shift",
        headline_template="THIS 2D EQUATION LOOKS FLAT. ROTATE THE CAMERA.",
        subtext_template="Watch a single formula evolve into 3D isometric geometry.",
        visual_intent="Glowing 2D mathematical curve smoothly tilting into an orbiting 3D parametric surface mesh.",
        audio_intent="Ethereal harmonic chime swelling into a deep spatial sub-bass sweep as the camera elevates.",
        animation_style="camera_3d_pitch"
    )
}


def select_best_hook(topic: str, difficulty: str = "intermediate") -> HookSpec:
    """Intelligently recommend the best hook archetype based on topic characteristics."""
    t = topic.lower()
    math_words = ["math", "equation", "formula", "2d", "3d", "euler", "sinc", "wave", "fourier", "calculus", "helix", "surface", "paraboloid", "geometry"]
    if any(w in t for w in math_words):
        return HOOK_ARCHETYPES["math_dimension_shift"]
    elif "speed" in t or "fast" in t or "100x" in t or "optimi" in t:
        return HOOK_ARCHETYPES["before_after"]
    elif "recur" in t or "stack" in t or "crash" in t:
        return HOOK_ARCHETYPES["visual_shock"]
    elif "cpu" in t or "hardware" in t or "memory" in t or "lying" in t or "branch" in t:
        return HOOK_ARCHETYPES["cold_open"]
    elif "why" in t or "how" in t:
        return HOOK_ARCHETYPES["question"]
    elif "myth" in t or "wrong" in t or "mistake" in t:
        return HOOK_ARCHETYPES["myth"]
    elif "async" in t or "pointer" in t or "thread" in t:
        return HOOK_ARCHETYPES["visual_metaphor"]
    else:
        return HOOK_ARCHETYPES["contradiction"]
