"""
engine/dna_registry.py
======================
Comprehensive Video DNA & Creative Anti-Repetition Registry.
Ensures every video produced possesses a distinct creative identity across:
1. Story DNA: Narrative structure, hook type, pacing, emotional arc, scene count
2. Visual DNA: Visual strategy, composition system, typography, color system, texture, lighting
3. Scene Sequence & Composition Variants: Dynamic scene sequence without rigid templates
4. Audio DNA: Genre, BPM, rhythm architecture, chord progression
5. Closing DNA: Strategy, layout, typography, visual accent
6. Camera & Transition Language: Dynamic camera paths & transition grammars

Evaluates multi-dimensional novelty and weighted anti-repetition against historical productions.
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
    # Generative DNA architecture
    visual_strategy: Optional[str] = None
    story_dna: Optional[Dict[str, Any]] = None
    visual_dna: Optional[Dict[str, Any]] = None
    scene_sequence: Optional[List[str]] = None
    composition_variants: Optional[List[str]] = None
    color_system: Optional[str] = None
    typography_system: Optional[str] = None
    # Sub-systems
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

    def compute_novelty_score(
        self,
        candidate: Any,
        recent_count: int = 10
    ) -> float:
        """
        Calculates weighted novelty score based on anti-repetition rules:
        Base: 100.0
        same story structure recently      -30
        same visual strategy recently      -30
        same scene sequence                -40
        same composition recently          -20
        same camera language               -15
        same transition language           -15
        """
        recent = self.history[-recent_count:] if self.history else []
        if not recent:
            return 100.0

        score = 100.0
        cand_dict = candidate.to_dict() if hasattr(candidate, "to_dict") else candidate

        cand_struct = cand_dict.get("story_structure") or cand_dict.get("story_dna", {}).get("narrative_structure")
        cand_strat = cand_dict.get("visual_strategy") or cand_dict.get("visual_dna", {}).get("visual_strategy")
        cand_seq = cand_dict.get("scene_sequence") or []
        cand_comps = set(cand_dict.get("composition_variants") or [])
        cand_cam = cand_dict.get("camera_language") or cand_dict.get("visual_dna", {}).get("camera_language")
        cand_trans = cand_dict.get("transition_language") or cand_dict.get("visual_dna", {}).get("transition_language")

        # Compare primarily against most recent entries with recency-weighted penalties
        for idx, past in enumerate(reversed(recent)):
            recency_weight = 1.0 if idx == 0 else (0.6 if idx == 1 else 0.3)

            past_struct = past.get("story_structure") or past.get("story_dna", {}).get("narrative_structure")
            past_strat = past.get("visual_strategy") or past.get("visual_dna", {}).get("visual_strategy")
            past_seq = past.get("scene_sequence") or []
            past_comps = set(past.get("composition_variants") or [])
            past_cam = past.get("camera_language") or past.get("visual_dna", {}).get("camera_language")
            past_trans = past.get("transition_language") or past.get("visual_dna", {}).get("transition_language")

            if cand_struct and past_struct and cand_struct == past_struct:
                score -= 30.0 * recency_weight

            if cand_strat and past_strat and cand_strat == past_strat:
                score -= 30.0 * recency_weight

            if cand_seq and past_seq and cand_seq == past_seq:
                score -= 40.0 * recency_weight

            if cand_comps and past_comps and cand_comps.intersection(past_comps):
                shared_ratio = len(cand_comps.intersection(past_comps)) / max(len(cand_comps), 1)
                score -= (20.0 * shared_ratio) * recency_weight

            if cand_cam and past_cam and cand_cam == past_cam:
                score -= 15.0 * recency_weight

            if cand_trans and past_trans and cand_trans == past_trans:
                score -= 15.0 * recency_weight

        return max(0.0, score)

    def compute_similarity_breakdown(
        self,
        dna: Any,
        past: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculates granular similarity scores across key dimensions."""
        dna_dict = dna.to_dict() if hasattr(dna, "to_dict") else dna

        # 1. Visual Similarity (0.0 to 1.0)
        v_matches = 0.0
        v_total = 4.0
        if dna_dict.get("style") == past.get("style") or dna_dict.get("visual_strategy") == past.get("visual_strategy"):
            v_matches += 1.5
        if dna_dict.get("palette") == past.get("palette"):
            v_matches += 1.0
        if dna_dict.get("font_pair") == past.get("font_pair"):
            v_matches += 0.8
        if dna_dict.get("visual_metaphor") == past.get("visual_metaphor"):
            v_matches += 0.7
        visual_sim = min(1.0, v_matches / v_total)

        # 2. Audio Similarity
        past_audio = past.get("audio_dna") or {}
        cur_audio = dna_dict.get("audio_dna") or {}
        a_matches = 0.0
        a_total = 5.0
        cur_genre = cur_audio.get("genre") or dna_dict.get("sound_profile", "")
        past_genre = past_audio.get("genre") or past.get("sound_profile", "")
        if cur_genre and cur_genre == past_genre:
            a_matches += 1.5

        cur_bpm = float(cur_audio.get("bpm") or 124.0)
        past_bpm = float(past_audio.get("bpm") or past.get("bpm") or 124.0)
        if abs(cur_bpm - past_bpm) < 4.0:
            a_matches += 1.0
        elif abs(cur_bpm - past_bpm) < 8.0:
            a_matches += 0.5

        cur_chords = cur_audio.get("chord_progression") or []
        past_chords = past_audio.get("chord_progression") or []
        if cur_chords and past_chords:
            shared_chords = set(cur_chords).intersection(set(past_chords))
            a_matches += (len(shared_chords) / max(len(cur_chords), len(past_chords))) * 1.2

        cur_rhythm = cur_audio.get("rhythm") or ""
        past_rhythm = past_audio.get("rhythm") or ""
        if cur_rhythm and cur_rhythm == past_rhythm:
            a_matches += 0.8

        audio_sim = min(1.0, a_matches / a_total)

        # 3. Closing Similarity
        cur_closing = dna_dict.get("closing_dna") or {}
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

        # 4. Motion & Structural Similarity
        m_matches = 0.0
        m_total = 4.0
        if dna_dict.get("story_structure") == past.get("story_structure"):
            m_matches += 1.5
        if dna_dict.get("scene_sequence") and dna_dict.get("scene_sequence") == past.get("scene_sequence"):
            m_matches += 1.2
        if dna_dict.get("motion_language") == past.get("motion_language"):
            m_matches += 0.7
        if dna_dict.get("camera_language") == past.get("camera_language"):
            m_matches += 0.6
        motion_sim = min(1.0, m_matches / m_total)

        overall = round(
            0.30 * audio_sim +
            0.20 * closing_sim +
            0.25 * visual_sim +
            0.25 * motion_sim,
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
        dna: Any,
        candidate_history: Optional[List[Dict[str, Any]]] = None
    ) -> float:
        history = candidate_history if candidate_history is not None else self.history[-10:]
        if not history:
            return 0.0

        max_sim = 0.0
        for past in history:
            bd = self.compute_similarity_breakdown(dna, past)
            if bd["overall_creative_similarity"] > max_sim:
                max_sim = bd["overall_creative_similarity"]
        return max_sim

    def is_dna_unique(
        self,
        dna: Any,
        threshold: float = 0.60
    ) -> Tuple[bool, float, Dict[str, float]]:
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
        if hasattr(dna, "to_dict"):
            self.history.append(dna.to_dict())
        elif isinstance(dna, dict):
            self.history.append(dna)
        self._save_history()

    register_video = register_dna

    def compute_novelty_score(
        self,
        candidate_structure: Optional[str] = None,
        candidate_strategy: Optional[str] = None,
        candidate_sequence: Optional[List[str]] = None,
        candidate_compositions: Optional[List[str]] = None,
        candidate_camera: Optional[str] = None,
        candidate_transition: Optional[str] = None,
        candidate_dna: Optional[Dict[str, Any]] = None,
        history_window: int = 5
    ) -> float:
        """
        Computes weighted novelty score (0 to 100) comparing a candidate against recent history:
        - same story structure recently:      -30
        - same visual strategy recently:      -30
        - same scene sequence:                -40
        - same composition variants:          -20
        - same camera language:               -15
        - same transition language:           -15
        """
        score = 100.0
        recent = self.history[-history_window:]
        if not recent:
            return 100.0

        struct = candidate_structure or (candidate_dna or {}).get("story_structure")
        strategy = candidate_strategy or (candidate_dna or {}).get("visual_strategy")
        seq = candidate_sequence or (candidate_dna or {}).get("scene_sequence")
        comps = candidate_compositions or (candidate_dna or {}).get("composition_variants")
        cam = candidate_camera or (candidate_dna or {}).get("camera_language")
        trans = candidate_transition or (candidate_dna or {}).get("transition_language")

        for past in reversed(recent):
            if struct and past.get("story_structure") == struct:
                score -= 30.0
                break

        for past in reversed(recent):
            if strategy and past.get("visual_strategy") == strategy:
                score -= 30.0
                break

        for past in reversed(recent):
            past_seq = past.get("scene_sequence")
            if seq and past_seq and list(seq) == list(past_seq):
                score -= 40.0
                break

        for past in reversed(recent):
            past_comps = past.get("composition_variants")
            if comps and past_comps and set(comps).intersection(set(past_comps)):
                score -= 20.0
                break

        for past in reversed(recent):
            if cam and past.get("camera_language") == cam:
                score -= 15.0
                break

        for past in reversed(recent):
            if trans and past.get("transition_language") == trans:
                score -= 15.0
                break

        return max(0.0, min(100.0, score))

    def get_recent_history(self, count: int = 10) -> List[Dict[str, Any]]:
        return self.history[-count:]
