"""
effects/story_structures.py
===========================
Narrative Story Structure Engine.
Provides 8 distinct structural blueprints to prevent formulaic storytelling:
- STRUCTURE_A: Hook -> Mystery -> Reveal -> Explanation -> Payoff
- STRUCTURE_B: Result -> Reverse Engineering -> Explanation -> Reveal
- STRUCTURE_C: Problem -> Failure -> Debugging -> Solution
- STRUCTURE_D: Question -> Experiment -> Observation -> Explanation
- STRUCTURE_E: Visual Metaphor -> Technical Mapping -> Code -> Conclusion
- STRUCTURE_F: Myth -> Contradiction -> Proof -> Explanation
- STRUCTURE_G: Cold Open -> Rapid Breakdown -> Deep Dive -> Final Insight
- STRUCTURE_H: Story -> Conflict -> Technical Explanation -> Resolution
"""
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class StoryBeat:
    name: str
    duration_ratio: float  # Fraction of total duration (sums to 1.0)
    intent: str
    visual_type: str       # "hook", "metaphor", "code", "benchmark", "diagram", "split", "payoff"


@dataclass
class StoryStructure:
    id: str
    name: str
    description: str
    beats: List[StoryBeat]

    def compute_timeline(self, total_duration: float = 50.0) -> List[Dict[str, Any]]:
        """Calculate start and end seconds for each beat."""
        timeline = []
        current_time = 0.0
        for b in self.beats:
            dur = round(total_duration * b.duration_ratio, 2)
            end_t = min(round(current_time + dur, 2), total_duration)
            timeline.append({
                "beat": b.name,
                "start": current_time,
                "end": end_t,
                "duration": round(end_t - current_time, 2),
                "intent": b.intent,
                "visual_type": b.visual_type
            })
            current_time = end_t
        return timeline


STORY_STRUCTURES: Dict[str, StoryStructure] = {
    # STRUCTURE_A: Hook -> Mystery -> Reveal -> Explanation -> Payoff
    "structure_a": StoryStructure(
        id="structure_a",
        name="Mystery & Reveal",
        description="Creates an intriguing puzzle before delivering an aha-moment breakdown.",
        beats=[
            StoryBeat("Hook", 0.08, "Provoke curiosity with an unexpected question", "hook"),
            StoryBeat("Mystery", 0.16, "Present the puzzling behavior or counter-intuitive code", "code"),
            StoryBeat("Reveal", 0.22, "Show the underlying mechanism in action", "metaphor"),
            StoryBeat("Explanation", 0.34, "Step-by-step breakdown of how it works", "diagram"),
            StoryBeat("Payoff", 0.20, "Before/after benchmark and definitive principle", "payoff")
        ]
    ),

    # STRUCTURE_B: Result -> Reverse Engineering -> Explanation -> Reveal
    "structure_b": StoryStructure(
        id="structure_b",
        name="Reverse Engineering",
        description="Starts with the astounding end result, then tears apart the engine piece by piece.",
        beats=[
            StoryBeat("Result", 0.10, "Show impossible benchmark: 1 billion items found in 20 steps", "benchmark"),
            StoryBeat("Disassembly", 0.25, "Strip away the surface to expose the core math", "diagram"),
            StoryBeat("Explanation", 0.35, "Trace the binary division logic line by line", "code"),
            StoryBeat("Synthesis", 0.30, "Reassemble the pattern into a reusable mental model", "payoff")
        ]
    ),

    # STRUCTURE_C: Problem -> Failure -> Debugging -> Solution
    "structure_c": StoryStructure(
        id="structure_c",
        name="The Bug & The Fix",
        description="A relatable engineering crisis: stack overflow or memory leak, followed by the surgical fix.",
        beats=[
            StoryBeat("Problem", 0.10, "Production failure or fatal crash warning", "hook"),
            StoryBeat("Failure", 0.22, "Visualizing exactly why memory or CPU collapsed", "metaphor"),
            StoryBeat("Debugging", 0.34, "Pinpointing the offending instruction", "code"),
            StoryBeat("Solution", 0.34, "Applying the correct pattern with zero crash guarantee", "payoff")
        ]
    ),

    # STRUCTURE_D: Question -> Experiment -> Observation -> Explanation
    "structure_d": StoryStructure(
        id="structure_d",
        name="The Empirical Lab",
        description="Scientific testing approach: hypothesis, benchmark experiment, and empirical proof.",
        beats=[
            StoryBeat("Hypothesis", 0.10, "Can we run this in O(1) space instead of O(N)?", "hook"),
            StoryBeat("Experiment", 0.24, "Run both algorithms against 10 million test cases", "split"),
            StoryBeat("Observation", 0.32, "Watch the live memory and time counters diverge", "benchmark"),
            StoryBeat("Law", 0.34, "State the formal computational law governing the result", "payoff")
        ]
    ),

    # STRUCTURE_E: Visual Metaphor -> Technical Mapping -> Code -> Conclusion
    "structure_e": StoryStructure(
        id="structure_e",
        name="Metaphor-First Mental Model",
        description="Grounds the concept immediately in physical objects before showing a single line of code.",
        beats=[
            StoryBeat("Metaphor_Hook", 0.12, "Show physical blocks stacking or janitor sweeping", "metaphor"),
            StoryBeat("Mapping", 0.26, "Map physical objects directly to RAM and CPU registers", "diagram"),
            StoryBeat("Code_Proof", 0.36, "Show how 3 lines of code implement the exact physical machine", "code"),
            StoryBeat("Mastery", 0.26, "Lock in the visual intuition forever", "payoff")
        ]
    ),

    # STRUCTURE_F: Myth -> Contradiction -> Proof -> Explanation
    "structure_f": StoryStructure(
        id="structure_f",
        name="Mythbuster",
        description="Destroys a common textbook myth and replaces it with real engineering truth.",
        beats=[
            StoryBeat("The_Myth", 0.10, "What 90% of beginners and tutorials teach", "hook"),
            StoryBeat("Contradiction", 0.22, "Prove where the conventional wisdom fails completely", "split"),
            StoryBeat("Proof", 0.36, "Demonstrate the real hardware or compiler behavior", "diagram"),
            StoryBeat("New_Standard", 0.32, "The true mental model used by senior engineers", "payoff")
        ]
    ),

    # STRUCTURE_G: Cold Open -> Rapid Breakdown -> Deep Dive -> Final Insight
    "structure_g": StoryStructure(
        id="structure_g",
        name="Speedrun Masterclass",
        description="Fast-paced, high-density technical briefing with zero fluff.",
        beats=[
            StoryBeat("Cold_Open", 0.08, "Immediate core statement on frame 1", "hook"),
            StoryBeat("Rapid_Breakdown", 0.22, "3 instant takeaways in 10 seconds", "diagram"),
            StoryBeat("Deep_Dive", 0.45, "Detailed dissection of the critical invariant", "code"),
            StoryBeat("Final_Insight", 0.25, "Architectural rule of thumb", "payoff")
        ]
    ),

    # STRUCTURE_H: Story -> Conflict -> Technical Explanation -> Resolution
    "structure_h": StoryStructure(
        id="structure_h",
        name="Engineering Narrative",
        description="Narrative journey through a classic computer science dilemma and its triumphant resolution.",
        beats=[
            StoryBeat("Scenario", 0.12, "Setting the scene: scaling to 100,000 requests/sec", "hook"),
            StoryBeat("Bottleneck", 0.24, "The architectural bottleneck threatening the system", "split"),
            StoryBeat("Breakthrough", 0.36, "The algorithmic breakthrough that unlocked scale", "code"),
            StoryBeat("Resolution", 0.28, "System operating smoothly at scale", "payoff")
        ]
    )
}


def select_story_structure(topic: str, style_id: str = "editorial") -> StoryStructure:
    """Select the most compelling narrative structure for the topic and visual style."""
    t = topic.lower()
    if "myth" in t or "wrong" in t:
        return STORY_STRUCTURES["structure_f"]
    elif "bug" in t or "crash" in t or "error" in t:
        return STORY_STRUCTURES["structure_c"]
    elif "metaphor" in t or "visual" in t or "pointer" in t or "async" in t:
        return STORY_STRUCTURES["structure_e"]
    elif "binary" in t or "search" in t or "speed" in t or "fast" in t:
        return STORY_STRUCTURES["structure_b"]
    elif style_id in ["terminal", "brutalist"]:
        return STORY_STRUCTURES["structure_g"]
    else:
        return STORY_STRUCTURES["structure_a"]
