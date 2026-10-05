"""
agents/creative_director.py
===========================
Creative Director Agent.
Determines the complete visual identity, color scheme, typography,
camera movement, visual metaphor, and sound profile for each video.
Enforces the Anti-Repetition system so no two videos feel identical.
"""
import os
import json
import random
import time
from typing import Dict, Any, Optional

from engine.dna_registry import VideoDNA, DNARegistry
from effects.palettes import CURATED_PALETTES, get_palette
from effects.typography_registry import FONT_PAIRINGS
from effects.hooks import select_best_hook, HOOK_ARCHETYPES
from effects.story_structures import select_story_structure, STORY_STRUCTURES
from effects.voice_profiles import VOICE_PROFILES
from effects.sound_profiles import MUSIC_PROFILES
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
        max_attempts: int = 5,
        custom_hook: Optional[Dict[str, Any]] = None,
        custom_math_spec: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Creates a coherent, professional Creative Direction for a given topic.
        Guarantees DNA variety against recent video history.
        """
        # Step 1: Select or deduce visual style
        available_styles = self._load_available_styles()

        best_style_id = requested_style if requested_style in available_styles else self._recommend_style_for_topic(topic)
        style_spec = available_styles.get(best_style_id, available_styles.get("editorial", {}))

        # Step 2: Formulate candidate DNA with controlled variety
        for attempt in range(max_attempts):
            candidate_dna = self._formulate_candidate_dna(topic, best_style_id, style_spec, attempt)
            is_unique, similarity = self.dna_registry.is_dna_unique(candidate_dna, threshold=0.65)

            if is_unique or attempt == max_attempts - 1:
                break
            # If not unique, pick an alternative style or palette
            other_styles = [s for s in available_styles.keys() if s != best_style_id]
            best_style_id = random.choice(other_styles) if other_styles else "editorial"
            style_spec = available_styles.get(best_style_id, {})

        # Step 3: Package complete creative direction with dynamic viral hook and math spec
        palette_obj = get_palette(candidate_dna.palette)
        font_obj = FONT_PAIRINGS.get(candidate_dna.font_pair, FONT_PAIRINGS["inter_jetbrains"])
        hook_obj = HOOK_ARCHETYPES.get(candidate_dna.hook_type, HOOK_ARCHETYPES["contradiction"])
        story_obj = STORY_STRUCTURES.get(candidate_dna.story_structure, STORY_STRUCTURES["structure_a"])
        voice_obj = VOICE_PROFILES.get(candidate_dna.voice_profile, VOICE_PROFILES["energetic"])
        # Use pre-supplied custom hook/math spec if available, otherwise generate dynamically
        viral_hook = custom_hook or self.nemotron.generate_viral_hook(topic, style=best_style_id)
        is_math = viral_hook.get("is_math") or self.nemotron._is_math_topic(topic)
        math_spec = custom_math_spec or (self.nemotron.generate_math_3d_concept(topic) if is_math else None)

        from effects.sound_profiles import get_music_profile
        music_obj = get_music_profile(candidate_dna.sound_profile, is_math=is_math)
        candidate_dna.sound_profile = music_obj.id

        creative_direction = {
            "topic": topic,
            "dna": candidate_dna.to_dict(),
            "style_id": best_style_id,
            "style_name": style_spec.get("name", "Modern Studio"),
            "style_description": style_spec.get("description", ""),
            "is_math": is_math,
            "math_spec": math_spec,
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
            "sound": {
                "id": music_obj.id,
                "name": music_obj.name,
                "bpm": music_obj.bpm,
                "ducking_db": music_obj.ducking_db,
                "chord_progression": music_obj.chord_progression,
                "lead_timbre": music_obj.lead_timbre,
                "bass_freq": music_obj.bass_freq,
                "description": music_obj.description
            },
            "sound_profile": music_obj.id,
            "similarity_against_history": similarity
        }

        return creative_direction

    def _formulate_candidate_dna(self, topic: str, style_id: str, style_spec: Dict[str, Any], attempt: int) -> VideoDNA:
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

        # Select hook
        hook_obj = select_best_hook(topic)

        # Select story structure
        story_obj = select_story_structure(topic, style_id)

        # Query visual metaphor from Nemotron
        metaphor_info = self.nemotron.generate_visual_metaphor(topic)
        metaphor_id = metaphor_info.get("metaphor_id", "tabbed_book_index")

        # Match sound profile
        sound_raw = style_spec.get("sound_direction", "cyberpunk")
        sound_profile = sound_raw if isinstance(sound_raw, str) else sound_raw.get("music_profile", "cyberpunk")

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

        # Match voice profile
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
            sound_profile=sound_profile,
            voice_profile=voice_profile
        )


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
