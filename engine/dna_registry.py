"""
engine/dna_registry.py
======================
Comprehensive Video DNA & Creative Anti-Repetition Registry.
Ensures every video produced possesses a distinct creative identity across:
1. Audio DNA: Genre, BPM, rhythm architecture, chord progression, instrument palette, energy curve
2. Closing DNA: Strategy (12 distinct patterns), layout, camera motion, typography, visual accent
3. Visual DNA: Style, palette, typography pairing, visual metaphor
4. Motion DNA: Motion language, camera language, transition language, carry primitives
5. Hook DNA: Archetype, opening animation style, badge, voice cadence

Evaluates multi-dimensional similarity against historical productions and enforces
creative regeneration when similarity exceeds safe thresholds.
"""
import os
import json
import time
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional, Tuple

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
    # Upgraded DNA sub-systems
    audio_dna: Optional[Dict[str, Any]] = None
    closing_dna: Optional[Dict[str, Any]] = None
    motion_dna: Optional[Dict[str, Any]] = None
    hook_dna: Optional[Dict[str, Any]] = None
    creative_seed: int = 42
    audio_seed: int = 42
    closing_seed: int = 42

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

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history

    def compute_similarity_breakdown(
        self,
        dna: VideoDNA,
        past: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculates granular similarity scores across 4 key dimensions:
        - audio_similarity (genre, BPM, chord progression, rhythm, instruments)
        - visual_similarity (style, palette, font_pair, visual metaphor)
        - closing_similarity (closing strategy, layout, camera motion)
        - motion_similarity (camera language, transition language, motion language)
        """
        # 1. Visual Similarity (0.0 to 1.0)
        v_matches = 0
        v_total = 4
        if getattr(dna, "style", None) == past.get("style"):
            v_matches += 1.5
        if getattr(dna, "palette", None) == past.get("palette"):
            v_matches += 1.0
        if getattr(dna, "font_pair", None) == past.get("font_pair"):
            v_matches += 0.8
        if getattr(dna, "visual_metaphor", None) == past.get("visual_metaphor"):
            v_matches += 0.7
        visual_sim = min(1.0, v_matches / v_total)

        # 2. Audio Similarity (0.0 to 1.0)
        past_audio = past.get("audio_dna") or {}
        cur_audio = getattr(dna, "audio_dna", None) or {}
        a_matches = 0.0
        a_total = 5.0

        cur_genre = cur_audio.get("genre") or getattr(dna, "sound_profile", "")
        past_genre = past_audio.get("genre") or past.get("sound_profile", "")
        if cur_genre and cur_genre == past_genre:
            a_matches += 1.5

        # BPM proximity check: if BPMs are within 4 BPM, penalize heavily
        cur_bpm = float(cur_audio.get("bpm") or 124.0)
        past_bpm = float(past_audio.get("bpm") or past.get("bpm") or 124.0)
        if abs(cur_bpm - past_bpm) < 4.0:
            a_matches += 1.0
        elif abs(cur_bpm - past_bpm) < 8.0:
            a_matches += 0.5

        # Chord progression similarity
        cur_chords = cur_audio.get("chord_progression") or []
        past_chords = past_audio.get("chord_progression") or []
        if cur_chords and past_chords:
            shared_chords = set(cur_chords).intersection(set(past_chords))
            a_matches += (len(shared_chords) / max(len(cur_chords), len(past_chords))) * 1.2
        elif cur_genre == past_genre:
            a_matches += 0.5

        # Rhythm similarity
        cur_rhythm = cur_audio.get("rhythm") or ""
        past_rhythm = past_audio.get("rhythm") or ""
        if cur_rhythm and cur_rhythm == past_rhythm:
            a_matches += 0.8

        audio_sim = min(1.0, a_matches / a_total)

        # 3. Closing Similarity (0.0 to 1.0)
        cur_closing = getattr(dna, "closing_dna", None) or {}
        past_closing = past.get("closing_dna") or {}
        c_matches = 0.0
        c_total = 3.0

        cur_strat = cur_closing.get("strategy_id")
        past_strat = past_closing.get("strategy_id")
        if cur_strat and cur_strat == past_strat:
            c_matches += 1.5

        if cur_closing.get("layout") and cur_closing.get("layout") == past_closing.get("layout"):
            c_matches += 0.8

        if cur_closing.get("camera_motion") and cur_closing.get("camera_motion") == past_closing.get("camera_motion"):
            c_matches += 0.7

        closing_sim = min(1.0, c_matches / c_total) if (cur_strat or past_strat) else (1.0 if not cur_strat and not past_strat else 0.4)

        # 4. Motion & Pacing Similarity (0.0 to 1.0)
        m_matches = 0.0
        m_total = 3.0
        if getattr(dna, "story_structure", None) == past.get("story_structure"):
            m_matches += 1.2
        if getattr(dna, "motion_language", None) == past.get("motion_language"):
            m_matches += 0.9
        if getattr(dna, "camera_language", None) == past.get("camera_language"):
            m_matches += 0.9
        motion_sim = min(1.0, m_matches / m_total)

        # Overall composite similarity
        # Audio (30%), Closing (25%), Visual (25%), Motion (20%)
        overall = round(
            0.30 * audio_sim +
            0.25 * closing_sim +
            0.25 * visual_sim +
            0.20 * motion_sim,
            2
        )

        return {
            "overall_creative_similarity": overall,
            "audio_similarity": round(audio_sim, 2),
            "visual_similarity": round(visual_sim, 2),
            "closing_similarity": round(closing_sim, 2),
            "motion_similarity": round(motion_sim, 2)
        }

    def compute_similarity(
        self,
        dna: VideoDNA,
        candidate_history: Optional[List[Dict[str, Any]]] = None
    ) -> float:
        """
        Compute maximum similarity score (0.0 to 1.0) against recent video DNA history.
        Evaluates audio, visual, closing, and motion dimensions.
        """
        history = candidate_history if candidate_history is not None else self.history[-10:]
        if not history:
            return 0.0

        max_sim = 0.0
        for past in history:
            breakdown = self.compute_similarity_breakdown(dna, past)
            if breakdown["overall_creative_similarity"] > max_sim:
                max_sim = breakdown["overall_creative_similarity"]

        return max_sim

    def is_dna_unique(
        self,
        dna: VideoDNA,
        threshold: float = 0.60
    ) -> Tuple[bool, float, Dict[str, float]]:
        """
        Verifies if candidate DNA is creatively distinct from recent history.
        Returns (is_unique, highest_similarity, worst_breakdown).
        """
        history = self.history[-10:]
        if not history:
            return (True, 0.0, {
                "overall_creative_similarity": 0.0,
                "audio_similarity": 0.0,
                "visual_similarity": 0.0,
                "closing_similarity": 0.0,
                "motion_similarity": 0.0
            })

        worst_breakdown = {
            "overall_creative_similarity": 0.0,
            "audio_similarity": 0.0,
            "visual_similarity": 0.0,
            "closing_similarity": 0.0,
            "motion_similarity": 0.0
        }
        max_sim = 0.0

        for past in history:
            bd = self.compute_similarity_breakdown(dna, past)
            if bd["overall_creative_similarity"] > max_sim:
                max_sim = bd["overall_creative_similarity"]
                worst_breakdown = bd

        is_unique = max_sim <= threshold
        return (is_unique, max_sim, worst_breakdown)

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
