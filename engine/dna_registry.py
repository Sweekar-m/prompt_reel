"""
engine/dna_registry.py
======================
Video DNA and Anti-Repetition System.
Ensures every video produced has a distinct creative fingerprint across:
- style, palette, font_pair, hook_type, story_structure,
- motion_language, camera_language, transition_language,
- visual_metaphor, sound_profile, voice_profile.
Tracks historical DNA and guarantees controlled variety.
"""
import os
import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional

DNA_HISTORY_PATH = os.path.join(os.path.dirname(__file__), "..", "dna_history.json")


@dataclass
class VideoDNA:
    id: str
    topic: str
    timestamp: float
    style: str
    palette: str
    font_pair: str
    hook_type: str
    story_structure: str
    motion_language: str
    camera_language: str
    transition_language: str
    visual_metaphor: str
    sound_profile: str
    voice_profile: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DNARegistry:
    def __init__(self, history_file: str = DNA_HISTORY_PATH):
        self.history_file = history_file
        self.history: List[Dict[str, Any]] = self._load_history()

    def _load_history(self) -> List[Dict[str, Any]]:
        if os.path.isfile(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
            except Exception:
                pass
        return []

    def _save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history[-100:], f, indent=4)  # Retain last 100
        except Exception as e:
            print(f"[!] Warning: Could not save DNA history: {e}")

    def compute_similarity(self, dna: VideoDNA, candidate_history: Optional[List[Dict[str, Any]]] = None) -> float:
        """
        Compute similarity score (0.0 to 1.0) against recent video DNA history.
        Weights identical dimensions heavily.
        """
        history = candidate_history if candidate_history is not None else self.history[-10:]
        if not history:
            return 0.0

        weights = {
            "style": 0.20,
            "palette": 0.15,
            "font_pair": 0.10,
            "hook_type": 0.10,
            "story_structure": 0.10,
            "visual_metaphor": 0.15,
            "sound_profile": 0.10,
            "voice_profile": 0.10,
        }

        max_sim = 0.0
        for past in history:
            sim = 0.0
            for key, weight in weights.items():
                if getattr(dna, key, None) == past.get(key):
                    sim += weight
            if sim > max_sim:
                max_sim = sim

        return round(max_sim, 2)

    def is_dna_unique(self, dna: VideoDNA, threshold: float = 0.65) -> Tuple[bool, float]:
        """Verify if candidate DNA is distinct enough from recent history."""
        sim = self.compute_similarity(dna)
        return (sim <= threshold, sim)

    def register_dna(self, dna: Any, *args, **kwargs):
        """Append verified DNA to history and persist."""
        if hasattr(dna, "to_dict"):
            self.history.append(dna.to_dict())
        elif isinstance(dna, dict):
            self.history.append(dna)
        self._save_history()

    register_video = register_dna

    def get_recent_history(self, count: int = 10) -> List[Dict[str, Any]]:
        return self.history[-count:]
