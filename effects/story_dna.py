"""
effects/story_dna.py
====================
Defines StoryDNA and narrative blueprint state.
Encapsulates structural intent, pacing, scene allocation, and emotional progression.
"""
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional


@dataclass
class StoryDNA:
    narrative_structure: str           # e.g. "structure_b"
    structure_name: str                # e.g. "Reverse Engineering"
    topic_category: str                # e.g. "algorithms_data_structures"
    intent: str                        # e.g. "reverse_engineer"
    complexity: str                    # "beginner" | "intermediate" | "advanced"
    emotional_tone: str                # "curious" | "urgent" | "analytical" | "mind_bending"
    hook_type: str                     # "contradiction" | "cold_open" | "question" | ...
    information_density: str           # "minimal" | "balanced" | "dense"
    pacing: str                        # "rapid" | "measured" | "accelerating" | "deliberate"
    reveal_timing: str                 # "early" | "mid" | "late"
    payoff_type: str                   # "metric_speedup" | "mental_model" | "invariant_rule"
    scene_count: int                   # number of beats/scenes
    target_duration: float             # computed video duration in seconds (emerges from script)
    emotional_progression: List[str]   # e.g. ["curiosity", "tension", "insight", "mastery"]
    modalities: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoryDNA":
        valid_keys = {
            "narrative_structure", "structure_name", "topic_category", "intent",
            "complexity", "emotional_tone", "hook_type", "information_density",
            "pacing", "reveal_timing", "payoff_type", "scene_count",
            "target_duration", "emotional_progression", "modalities"
        }
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)
