"""
agents/creative_director.py
===========================
Creative Director Agent.
Determines the complete visual identity, color scheme, typography,
camera movement, visual metaphor, Audio DNA, and Closing Strategy for each video.
Enforces the Creative Anti-Repetition system so every production possesses an
original, professional creative identity.
"""
import os
import json
import random
import time
import hashlib
from typing import Dict, Any, Optional, List

from engine.dna_registry import VideoDNA, DNARegistry
from effects.palettes import CURATED_PALETTES, get_palette
from effects.typography_registry import FONT_PAIRINGS
from effects.hooks import select_best_hook, HOOK_ARCHETYPES
from effects.story_structures import select_story_structure, STORY_STRUCTURES
from effects.voice_profiles import VOICE_PROFILES
from effects.audio_dna import generate_audio_dna, AudioDNA, compute_audio_seed
from effects.closing_strategies import select_closing_strategy, ClosingDNA
from ai.nemotron_client import NemotronClient

STYLES_DIR = os.path.join(os.path.dirname(__file__), "..", "styles")


class CreativeDirectorAgent:
    def __init__(self, nemotron_client: Optional[NemotronClient] = None, dna_registry: Optional[DNARegistry] = None):
        self.nemotron = nemotron_client or NemotronClient()
        self.dna_registry = dna_registry or DNARegistry()

    def direct_video(
        self,
        topic: str,
        script_summary: str = "",
        requested_style: Optional[str] = None,
        duration_sec: float = 50.0,
        max_attempts: int = 6,
        custom_hook: Optional[Dict[str, Any]] = None,
        custom_math_spec: Optional[Dict[str, Any]] = None,
        project_id: str = "proj_default",
        requested_genre: Optional[str] = None,
        requested_bpm: Optional[float] = None,
        requested_closing_strategy: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates a coherent, professional Creative Direction for a given topic.
        Guarantees DNA variety across Audio, Closing, Visual, and Motion against history.
        """
        # Step 1: Select or deduce visual style
        available_styles = self._load_available_styles()

        best_style_id = requested_style if requested_style in available_styles else self._recommend_style_for_topic(topic)
        style_spec = available_styles.get(best_style_id, available_styles.get("editorial", {}))

        # Step 2: Formulate candidate DNA with controlled variety and anti-repetition check
        best_candidate = None
        best_similarity = 1.0
        best_breakdown = {}

        for attempt in range(max_attempts):
            candidate_dna = self._formulate_candidate_dna(
                topic=topic,
                style_id=best_style_id,
                style_spec=style_spec,
                attempt=attempt,
                duration_sec=duration_sec,
                project_id=project_id,
                custom_hook=custom_hook,
                requested_genre=requested_genre,
                requested_bpm=requested_bpm,
                requested_closing_strategy=requested_closing_strategy
            )

            is_unique, similarity, breakdown = self.dna_registry.is_dna_unique(candidate_dna, threshold=0.60)

            if similarity < best_similarity:
                best_similarity = similarity
                best_candidate = candidate_dna
                best_breakdown = breakdown

            if is_unique:
                best_candidate = candidate_dna
                best_similarity = similarity
                best_breakdown = breakdown
                break

            # If repetitive, vary the style or palette across attempts
            other_styles = [s for s in available_styles.keys() if s != best_style_id]
            if other_styles and attempt >= 2 and not requested_style:
                best_style_id = other_styles[attempt % len(other_styles)]
                style_spec = available_styles.get(best_style_id, {})

        candidate_dna = best_candidate or self._formulate_candidate_dna(
            topic, best_style_id, style_spec, 0, duration_sec, project_id, custom_hook
        )

        # Step 3: Package complete creative direction
        palette_obj = get_palette(candidate_dna.palette)
        font_obj = FONT_PAIRINGS.get(candidate_dna.font_pair, FONT_PAIRINGS["inter_jetbrains"])
        hook_obj = HOOK_ARCHETYPES.get(candidate_dna.hook_type, HOOK_ARCHETYPES["contradiction"])
        story_obj = STORY_STRUCTURES.get(candidate_dna.story_structure, STORY_STRUCTURES["structure_a"])
        voice_obj = VOICE_PROFILES.get(candidate_dna.voice_profile, VOICE_PROFILES["energetic"])

        viral_hook = custom_hook or self.nemotron.generate_viral_hook(topic, style=best_style_id)
        is_math = viral_hook.get("is_math") or self.nemotron._is_math_topic(topic)
        math_spec = custom_math_spec or (self.nemotron.generate_math_3d_concept(topic) if is_math else None)

        audio_dna_dict = candidate_dna.audio_dna or {}
        closing_dna_dict = candidate_dna.closing_dna or {}

        creative_direction = {
            "topic": topic,
            "dna": candidate_dna.to_dict(),
            "style_id": best_style_id,
            "style_name": style_spec.get("name", "Modern Studio"),
            "style_description": style_spec.get("description", ""),
            "is_math": is_math,
            "math_spec": math_spec,
            "creative_seed": candidate_dna.creative_seed,
            "audio_seed": candidate_dna.audio_seed,
            "closing_seed": candidate_dna.closing_seed,
            "palette": {
                "id": palette_obj.id,
                "name": palette_obj.name,
                "is_dark": palette_obj.is_dark,
                "background": list(palette_obj.background),
                "primary": list(palette_obj.primary),
                "secondary": list(palette_obj.secondary),
                "accent": list(palette_obj.accent),
                "text": list(palette_obj.text),
                "subtext": list(palette_obj.subtext),
                "surface": list(palette_obj.surface),
            },
            "typography": {
                "id": font_obj.id,
                "name": font_obj.name,
                "category": font_obj.category,
                "description": font_obj.description,
                "heading": "Inter, 'Segoe UI', system-ui, sans-serif",
                "body": "Inter, 'Segoe UI', system-ui, sans-serif",
                "mono": "'JetBrains Mono', Consolas, 'Courier New', monospace",
            },
            "hook": {
                "id": hook_obj.id,
                "name": hook_obj.name,
                "headline": viral_hook.get("headline", hook_obj.headline_template),
                "subtext": viral_hook.get("subtext", hook_obj.subtext_template),
                "badge": viral_hook.get("badge", topic.upper()),
                "opening_voice": viral_hook.get("opening_voice", ""),
                "headline_template": viral_hook.get("headline", hook_obj.headline_template),
                "subtext_template": viral_hook.get("subtext", hook_obj.subtext_template),
                "animation_style": viral_hook.get("animation_style", hook_obj.animation_style)
            },
            "story_structure": {
                "id": story_obj.id,
                "name": story_obj.name,
                "timeline": story_obj.compute_timeline(duration_sec)
            },
            "visual_metaphor": "math_3d" if is_math else candidate_dna.visual_metaphor,
            "camera_language": "camera_3d_pitch" if is_math else candidate_dna.camera_language,
            "transition_language": candidate_dna.transition_language,
            "motion_language": candidate_dna.motion_language,
            "voice": {
                "id": voice_obj.id,
                "name": voice_obj.name,
                "edge_voice": voice_obj.edge_voice,
                "rate": voice_obj.rate,
                "pitch": voice_obj.pitch
            },
            # Complete Audio DNA integration
            "audio_dna": audio_dna_dict,
            "sound": {
                "id": audio_dna_dict.get("genre", "cinematic_electronic"),
                "name": audio_dna_dict.get("genre_name", "Cinematic Electronic"),
                "bpm": audio_dna_dict.get("bpm", 120.0),
                "mood": audio_dna_dict.get("mood", "tension"),
                "rhythm": audio_dna_dict.get("rhythm", "four_on_floor"),
                "chord_progression": audio_dna_dict.get("chord_progression", ["Dm", "Bb", "Gm", "A"]),
                "instrument_palette": audio_dna_dict.get("instrument_palette", []),
                "energy_curve": audio_dna_dict.get("energy_curve", []),
                "ducking_db": -12.0
            },
            "sound_profile": audio_dna_dict.get("genre", "cinematic_electronic"),
            # Complete Closing DNA integration
            "closing_dna": closing_dna_dict,
            "closing": {
                "strategy_id": closing_dna_dict.get("strategy_id", "kinetic_statement"),
                "strategy_name": closing_dna_dict.get("strategy_name", "Kinetic Statement"),
                "layout": closing_dna_dict.get("layout", "kinetic_words"),
                "camera_motion": closing_dna_dict.get("camera_motion", "whip_freeze"),
                "typography_style": closing_dna_dict.get("typography_style", "massive_stacked"),
                "visual_accent": closing_dna_dict.get("visual_accent", "clean_glow"),
                "headline": closing_dna_dict.get("headline", topic.upper()),
                "secondary_text": closing_dna_dict.get("secondary_text", ""),
                "stat_callout": closing_dna_dict.get("stat_callout", "10X INSIGHT"),
                "callback_ref": closing_dna_dict.get("callback_ref"),
                "action_label": closing_dna_dict.get("action_label")
            },
            "similarity_against_history": best_similarity,
            "similarity_breakdown": best_breakdown
        }

        return creative_direction

    def _formulate_candidate_dna(
        self,
        topic: str,
        style_id: str,
        style_spec: Dict[str, Any],
        attempt: int,
        duration_sec: float = 50.0,
        project_id: str = "proj_default",
        custom_hook: Optional[Dict[str, Any]] = None,
        requested_genre: Optional[str] = None,
        requested_bpm: Optional[float] = None,
        requested_closing_strategy: Optional[str] = None
    ) -> VideoDNA:
        """Formulates an integrated VideoDNA candidate containing Audio and Closing DNA."""
        salt = f"attempt_{attempt}_{int(time.time()) % 1000}"

        # Seeds
        creative_seed = int(hashlib.sha256(f"{project_id}_{topic}_{style_id}_{salt}".encode()).hexdigest()[:8], 16)
        audio_seed = compute_audio_seed(project_id, topic, style_id, salt)
        closing_seed = int(hashlib.sha256(f"closing_{project_id}_{topic}_{salt}".encode()).hexdigest()[:8], 16)

        # Match palette to style
        style_to_palette_map = {
            "editorial": ["cream_terracotta", "charcoal_gold"],
            "cyberpunk": ["electric_matrix", "aurora_violet"],
            "minimal": ["swiss_cobalt", "electric_matrix"],
            "brutalist": ["terminal_matrix", "stark_noir"],
            "terminal": ["terminal_matrix"],
            "neo_futuristic": ["aurora_violet", "navy_coral"],
            "swiss_grid": ["swiss_cobalt", "stark_noir"],
            "cinematic": ["charcoal_gold", "burgundy_velvet"],
            "retro_computing": ["terminal_matrix"],
            "monochrome": ["stark_noir"],
            "holographic": ["aurora_violet", "electric_matrix"],
            "paper_technical": ["cream_terracotta"],
            "luxury_tech": ["charcoal_gold"],
            "blueprint": ["blueprint_cyan"],
            "glass_ui": ["navy_coral", "electric_matrix"]
        }
        possible_palettes = style_to_palette_map.get(style_id, ["electric_matrix"])
        selected_palette = possible_palettes[attempt % len(possible_palettes)]

        # Match fonts to style
        style_to_font_map = {
            "editorial": "space_grotesk_ibm",
            "cyberpunk": "inter_jetbrains",
            "minimal": "dm_sans_jetbrains",
            "brutalist": "archivo_ibm",
            "terminal": "space_grotesk_ibm",
            "neo_futuristic": "inter_jetbrains",
            "swiss_grid": "manrope_source",
            "cinematic": "playfair_inter",
            "retro_computing": "space_grotesk_ibm",
            "monochrome": "archivo_ibm",
            "holographic": "bebas_inter",
            "paper_technical": "manrope_source",
            "luxury_tech": "playfair_inter",
            "blueprint": "manrope_source",
            "glass_ui": "dm_sans_jetbrains"
        }
        selected_font = style_to_font_map.get(style_id, "inter_jetbrains")

        # Select hook & story structure
        hook_obj = select_best_hook(topic)
        story_obj = select_story_structure(topic, style_id)

        # Query visual metaphor from Nemotron
        metaphor_info = self.nemotron.generate_visual_metaphor(topic)
        metaphor_id = metaphor_info.get("metaphor_id", "tabbed_book_index")

        # Generate True Audio DNA (not static sound profile string!)
        audio_dna = generate_audio_dna(
            topic=topic,
            style_id=style_id,
            duration_sec=duration_sec,
            project_id=project_id,
            requested_genre=requested_genre,
            requested_bpm=requested_bpm,
            seed_salt=salt
        )

        # Generate True Closing DNA (12 distinct closing strategies)
        hook_data = custom_hook or {"headline": hook_obj.headline_template}
        closing_dna = select_closing_strategy(
            topic=topic,
            hook_data=hook_data,
            style_id=style_id,
            story_structure_id=story_obj.id,
            seed_salt=f"{salt}_{requested_closing_strategy or ''}"
        )

        anim_raw = style_spec.get("animation_vocabulary", style_spec.get("motion_language", "smooth_rise"))
        motion_language = anim_raw if isinstance(anim_raw, str) else anim_raw.get("entry", "smooth_rise")

        cam_raw = style_spec.get("camera", style_spec.get("camera_behavior", "dynamic_drift"))
        camera_language = cam_raw if isinstance(cam_raw, str) else cam_raw.get("style", "dynamic_drift")

        trans_raw = style_spec.get("transitions", "hard_cut")
        if isinstance(trans_raw, str):
            transition_language = trans_raw
        elif isinstance(trans_raw, dict):
            transition_language = trans_raw.get("preferred", ["hard_cut"])[0]
        elif isinstance(trans_raw, list) and trans_raw:
            transition_language = trans_raw[0]
        else:
            transition_language = "hard_cut"

        style_to_voice = {
            "editorial": "documentary",
            "cyberpunk": "energetic",
            "minimal": "calm",
            "brutalist": "fast_explainer",
            "terminal": "dramatic",
            "cinematic": "deep_cinematic",
            "neo_futuristic": "young_technical",
            "swiss_grid": "conversational"
        }
        voice_profile = style_to_voice.get(style_id, "energetic")

        dna_id = f"dna_{int(time.time())}_{random.randint(100, 999)}"

        return VideoDNA(
            id=dna_id,
            topic=topic,
            timestamp=time.time(),
            style=style_id,
            palette=selected_palette,
            font_pair=selected_font,
            hook_type=hook_obj.id,
            story_structure=story_obj.id,
            motion_language=motion_language,
            camera_language=camera_language,
            transition_language=transition_language,
            visual_metaphor=metaphor_id,
            sound_profile=audio_dna.genre,
            voice_profile=voice_profile,
            audio_dna=audio_dna.to_dict(),
            closing_dna=closing_dna.to_dict(),
            creative_seed=creative_seed,
            audio_seed=audio_seed,
            closing_seed=closing_seed
        )

    def regenerate_audio_dna(
        self,
        topic_or_cd: Any,
        cd_or_topic: Any = None,
        requested_genre: Optional[str] = None,
        requested_bpm: Optional[float] = None,
        salt: str = ""
    ) -> Dict[str, Any]:
        """Regenerates ONLY the Audio DNA with a fresh seed while preserving visual direction."""
        if isinstance(topic_or_cd, dict):
            current_cd = topic_or_cd
            topic = cd_or_topic or current_cd.get("topic", "Coding Topic")
        else:
            topic = str(topic_or_cd)
            current_cd = cd_or_topic if isinstance(cd_or_topic, dict) else {}

        style_id = current_cd.get("style_id", "cinematic")
        seed_salt = salt or f"regen_audio_{int(time.time() * 1000)}"

        new_audio = generate_audio_dna(
            topic=topic,
            style_id=style_id,
            duration_sec=current_cd.get("story_structure", {}).get("timeline", [{}])[-1].get("end", 50.0),
            project_id="regen_audio",
            requested_genre=requested_genre,
            requested_bpm=requested_bpm,
            seed_salt=seed_salt
        )
        audio_dict = new_audio.to_dict()
        current_cd["audio_dna"] = audio_dict
        current_cd["sound"] = {
            "id": new_audio.genre,
            "name": new_audio.genre_name,
            "bpm": new_audio.bpm,
            "mood": new_audio.mood,
            "rhythm": new_audio.rhythm,
            "chord_progression": new_audio.chord_progression,
            "instrument_palette": new_audio.instrument_palette,
            "energy_curve": new_audio.energy_curve,
            "ducking_db": -12.0
        }
        current_cd["sound_profile"] = new_audio.genre
        current_cd["audio_seed"] = new_audio.variation_seed
        if "dna" in current_cd and isinstance(current_cd["dna"], dict):
            current_cd["dna"]["audio_dna"] = audio_dict
            current_cd["dna"]["sound_profile"] = new_audio.genre
            current_cd["dna"]["audio_seed"] = new_audio.variation_seed

        return audio_dict

    def regenerate_closing_dna(
        self,
        topic_or_cd: Any,
        cd_or_topic: Any = None,
        requested_strategy: Optional[str] = None,
        salt: str = ""
    ) -> Dict[str, Any]:
        """Regenerates ONLY the Closing Strategy with a fresh seed while preserving other dimensions."""
        if isinstance(topic_or_cd, dict):
            current_cd = topic_or_cd
            topic = cd_or_topic or current_cd.get("topic", "Coding Topic")
        else:
            topic = str(topic_or_cd)
            current_cd = cd_or_topic if isinstance(cd_or_topic, dict) else {}

        style_id = current_cd.get("style_id", "editorial")
        story_id = current_cd.get("story_structure", {}).get("id", "structure_a")
        seed_salt = salt or f"regen_closer_{int(time.time() * 1000)}"

        new_closing = select_closing_strategy(
            topic=topic,
            hook_data=current_cd.get("hook", {}),
            style_id=style_id,
            story_structure_id=story_id,
            seed_salt=f"{seed_salt}_{requested_strategy or ''}"
        )
        closing_dict = new_closing.to_dict()
        current_cd["closing_dna"] = closing_dict
        current_cd["closing"] = {
            "strategy_id": new_closing.strategy_id,
            "strategy_name": new_closing.strategy_name,
            "layout": new_closing.layout,
            "camera_motion": new_closing.camera_motion,
            "typography_style": new_closing.typography_style,
            "visual_accent": new_closing.visual_accent,
            "headline": new_closing.headline,
            "secondary_text": new_closing.secondary_text,
            "stat_callout": new_closing.stat_callout,
            "callback_ref": new_closing.callback_ref,
            "action_label": new_closing.action_label
        }
        current_cd["closing_seed"] = new_closing.variation_seed
        if "dna" in current_cd and isinstance(current_cd["dna"], dict):
            current_cd["dna"]["closing_dna"] = closing_dict
            current_cd["dna"]["closing_seed"] = new_closing.variation_seed

        return closing_dict

    def _recommend_style_for_topic(self, topic: str) -> str:
        t = topic.lower()
        if "hardware" in t or "cpu" in t or "terminal" in t or "assembl" in t:
            return "terminal"
        elif "history" in t or "why" in t or "deep dive" in t:
            return "editorial"
        elif "ai" in t or "attention" in t or "neural" in t or "hologram" in t:
            return "neo_futuristic"
        elif "clean" in t or "refactor" in t or "architecture" in t:
            return "swiss_grid"
        elif "speed" in t or "fast" in t or "100x" in t or "crash" in t:
            return "brutalist"
        elif "blueprint" in t or "struct" in t or "memory" in t:
            return "blueprint"
        elif "glass" in t or "spatial" in t:
            return "glass_ui"
        elif "cinematic" in t or "math" in t:
            return "cinematic"
        else:
            return "cyberpunk"

    def _load_available_styles(self) -> Dict[str, Any]:
        styles = {}
        if os.path.isdir(STYLES_DIR):
            for fname in os.listdir(STYLES_DIR):
                if fname.endswith(".json"):
                    p = os.path.join(STYLES_DIR, fname)
                    try:
                        with open(p, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            styles[data["id"]] = data
                    except Exception:
                        pass
        return styles
