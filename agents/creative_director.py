"""
agents/creative_director.py
===========================
Creative Director Agent for Prompt Reel.
Synthesizes topic semantics, StoryDNA, VisualDNA, Audio DNA, and Closing Strategy.
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
from effects.typography_registry import FONT_PAIRINGS, get_font_pairing
from effects.hooks import select_best_hook, HOOK_ARCHETYPES
from effects.story_structures import StoryDirector, StoryStructure, STORY_STRUCTURES, TopicAnalysis
from effects.story_dna import StoryDNA
from effects.visual_strategies import select_visual_strategy, VisualStrategy, VISUAL_STRATEGIES
from effects.visual_dna import build_visual_dna, VisualDNA
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
        Guarantees DNA variety across StoryDNA, VisualDNA, Audio, and Closing against history.
        """
        # Step 1: Semantic Topic Analysis
        topic_analysis = StoryDirector.analyze_topic(topic)

        # Step 2: Query recent history for anti-repetition tracking
        recent_history = self.dna_registry.get_recent_history(10)
        recent_structures = [
            h.get("story_structure") or h.get("story_dna", {}).get("narrative_structure")
            for h in recent_history if h.get("story_structure") or h.get("story_dna")
        ]
        recent_strategies = [
            h.get("visual_strategy") or h.get("visual_dna", {}).get("visual_strategy")
            for h in recent_history if h.get("visual_strategy") or h.get("visual_dna")
        ]

        # Step 3: Natural duration calculation
        # If duration is default 50.0, allow duration to emerge naturally based on complexity
        if duration_sec == 50.0:
            if topic_analysis.intent == "rapid_takeaway":
                duration_sec = 30.0
            elif topic_analysis.complexity == "advanced":
                duration_sec = 55.0
            elif topic_analysis.complexity == "beginner":
                duration_sec = 42.0

        # Step 4: Narrative structure selection
        story_obj = StoryDirector.select_structure(
            topic,
            analysis=topic_analysis,
            recent_structures=recent_structures
        )

        # Step 5: Visual Strategy selection
        visual_strategy = select_visual_strategy(
            topic,
            analysis=topic_analysis,
            story_structure_id=story_obj.id,
            requested_style=requested_style,
            recent_strategies=recent_strategies
        )

        # Step 6: Formulate candidate DNA with novelty optimization
        best_candidate: Optional[VideoDNA] = None
        best_similarity = 1.0
        best_novelty_score = -1.0
        best_breakdown: Dict[str, float] = {}

        for attempt in range(max_attempts):
            candidate_dna = self._formulate_candidate_dna(
                topic=topic,
                topic_analysis=topic_analysis,
                story_obj=story_obj,
                visual_strategy=visual_strategy,
                attempt=attempt,
                duration_sec=duration_sec,
                project_id=project_id,
                custom_hook=custom_hook,
                requested_genre=requested_genre,
                requested_bpm=requested_bpm,
                requested_closing_strategy=requested_closing_strategy
            )

            is_unique, similarity, breakdown = self.dna_registry.is_dna_unique(candidate_dna, threshold=0.60)
            novelty = self.dna_registry.compute_novelty_score(candidate_dna)

            if novelty > best_novelty_score:
                best_novelty_score = novelty
                best_similarity = similarity
                best_candidate = candidate_dna
                best_breakdown = breakdown

            if is_unique and novelty >= 65.0:
                best_candidate = candidate_dna
                best_similarity = similarity
                best_breakdown = breakdown
                break

            # If repetitive on first attempts, alternate visual strategy
            if attempt >= 2 and not requested_style:
                alt_strats = [s for s in VISUAL_STRATEGIES.keys() if s != visual_strategy.id]
                visual_strategy = VISUAL_STRATEGIES[alt_strats[attempt % len(alt_strats)]]

        candidate_dna = best_candidate or self._formulate_candidate_dna(
            topic, topic_analysis, story_obj, visual_strategy, 0, duration_sec, project_id, custom_hook
        )

        # Step 7: Build StoryDNA & VisualDNA objects
        hook_obj = HOOK_ARCHETYPES.get(candidate_dna.hook_type, HOOK_ARCHETYPES["contradiction"])
        viral_hook = custom_hook or self.nemotron.generate_viral_hook(topic, style=visual_strategy.id)
        is_math = bool(viral_hook.get("is_math") or topic_analysis.modalities.get("involves_mathematics") or self.nemotron._is_math_topic(topic))
        math_spec = custom_math_spec or (self.nemotron.generate_math_3d_concept(topic) if is_math else None)

        story_dna = StoryDNA(
            narrative_structure=story_obj.id,
            structure_name=story_obj.name,
            topic_category=topic_analysis.category,
            intent=topic_analysis.intent,
            complexity=topic_analysis.complexity,
            emotional_tone=topic_analysis.emotional_tone,
            hook_type=hook_obj.id,
            information_density="dense" if visual_strategy.category in ("technical", "developer", "data") else "balanced",
            pacing=story_obj.pacing_profile,
            reveal_timing="mid",
            payoff_type="invariant_rule",
            scene_count=len(story_obj.beats),
            target_duration=duration_sec,
            emotional_progression=["curiosity", "tension", "insight", "mastery"],
            modalities=topic_analysis.modalities
        )

        visual_dna = build_visual_dna(
            strategy=visual_strategy,
            palette_id=candidate_dna.palette,
            font_pair_id=candidate_dna.font_pair
        )

        # Update candidate DNA with structured models
        candidate_dna.story_dna = story_dna.to_dict()
        candidate_dna.visual_dna = visual_dna.to_dict()
        candidate_dna.visual_strategy = visual_strategy.id
        candidate_dna.scene_sequence = [b.visual_type for b in story_obj.beats]

        palette_obj = get_palette(candidate_dna.palette)
        font_obj = FONT_PAIRINGS.get(candidate_dna.font_pair, FONT_PAIRINGS["inter_jetbrains"])
        voice_obj = VOICE_PROFILES.get(candidate_dna.voice_profile, VOICE_PROFILES["energetic"])

        audio_dna_dict = candidate_dna.audio_dna or {}
        closing_dna_dict = candidate_dna.closing_dna or {}

        creative_direction = {
            "topic": topic,
            "dna": candidate_dna.to_dict(),
            "story_dna": story_dna.to_dict(),
            "visual_dna": visual_dna.to_dict(),
            "visual_strategy_id": visual_strategy.id,
            "visual_strategy": visual_strategy.to_dict(),
            "style_id": visual_strategy.id,
            "style_name": visual_strategy.name,
            "style_description": visual_strategy.description,
            "is_math": is_math,
            "math_spec": math_spec,
            "creative_seed": candidate_dna.creative_seed,
            "audio_seed": candidate_dna.audio_seed,
            "closing_seed": candidate_dna.closing_seed,
            "palette": visual_dna.color_system,
            "typography": visual_dna.typography,
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
            "camera_language": visual_dna.camera_language,
            "transition_language": visual_dna.transition_language,
            "motion_language": visual_dna.motion_language,
            "voice": {
                "id": voice_obj.id,
                "name": voice_obj.name,
                "edge_voice": voice_obj.edge_voice,
                "rate": voice_obj.rate,
                "pitch": voice_obj.pitch
            },
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
            "similarity_breakdown": best_breakdown,
            "novelty_score": best_novelty_score
        }

        return creative_direction

    def _formulate_candidate_dna(
        self,
        topic: str,
        topic_analysis: TopicAnalysis,
        story_obj: StoryStructure,
        visual_strategy: VisualStrategy,
        attempt: int,
        duration_sec: float = 50.0,
        project_id: str = "proj_default",
        custom_hook: Optional[Dict[str, Any]] = None,
        requested_genre: Optional[str] = None,
        requested_bpm: Optional[float] = None,
        requested_closing_strategy: Optional[str] = None
    ) -> VideoDNA:
        """Formulates an integrated VideoDNA candidate containing StoryDNA and VisualDNA."""
        salt = f"attempt_{attempt}_{int(time.time()) % 1000}"

        # Seeds
        creative_seed = int(hashlib.sha256(f"{project_id}_{topic}_{visual_strategy.id}_{salt}".encode()).hexdigest()[:8], 16)
        audio_seed = compute_audio_seed(project_id, topic, visual_strategy.id, salt)
        closing_seed = int(hashlib.sha256(f"closing_{project_id}_{topic}_{salt}".encode()).hexdigest()[:8], 16)

        # Palette selection based on VisualStrategy
        strat_palettes = {
            "blueprint": ["blueprint_cyan"],
            "matrix_terminal": ["terminal_matrix"],
            "amber_crt": ["terminal_matrix"],
            "warm_editorial": ["cream_terracotta", "charcoal_gold"],
            "stark_contrast": ["stark_noir", "swiss_cobalt"],
            "neon_matrix": ["electric_matrix", "aurora_violet"],
            "dark_cosmic": ["aurora_violet", "charcoal_gold"],
            "clean_analytics": ["swiss_cobalt", "navy_coral"],
            "infra_cyan": ["blueprint_cyan", "electric_matrix"],
            "dual_tone": ["navy_coral", "charcoal_gold"],
            "monochrome_matte": ["stark_noir"]
        }
        possible_palettes = strat_palettes.get(visual_strategy.palette_category, ["charcoal_gold", "electric_matrix"])
        selected_palette = possible_palettes[attempt % len(possible_palettes)]

        # Font selection based on VisualStrategy
        strat_fonts = {
            "mono_technical": "space_grotesk_ibm",
            "editorial_serif": "playfair_inter",
            "bold_grotesk": "bebas_inter",
            "editorial": "manrope_source",
            "modern_tech": "inter_jetbrains"
        }
        selected_font = strat_fonts.get(visual_strategy.typography_category, "inter_jetbrains")

        hook_obj = select_best_hook(topic)
        metaphor_info = self.nemotron.generate_visual_metaphor(topic)
        metaphor_id = metaphor_info.get("metaphor_id", visual_strategy.id)

        # Generate Audio DNA aligned to Visual Strategy
        audio_dna = generate_audio_dna(
            topic=topic,
            style_id=visual_strategy.id,
            duration_sec=duration_sec,
            project_id=project_id,
            requested_genre=requested_genre,
            requested_bpm=requested_bpm,
            seed_salt=salt
        )

        # Generate Closing DNA
        hook_data = custom_hook or {"headline": hook_obj.headline_template}
        closing_dna = select_closing_strategy(
            topic=topic,
            hook_data=hook_data,
            style_id=visual_strategy.id,
            story_structure_id=story_obj.id,
            seed_salt=f"{salt}_{requested_closing_strategy or ''}"
        )

        strategy_to_voice = {
            "kinetic_typography": "energetic",
            "editorial_grid": "documentary",
            "cinematic_diagram": "deep_cinematic",
            "technical_blueprint": "fast_explainer",
            "terminal_story": "dramatic",
            "code_first": "young_technical",
            "data_visualization": "conversational",
            "split_screen_comparison": "energetic",
            "mathematical_3d": "deep_cinematic",
            "system_architecture": "documentary",
            "magazine_editorial": "documentary",
            "retro_computing": "dramatic",
            "swiss_minimal": "calm",
            "cyberpunk": "energetic",
            "brutalist": "fast_explainer",
            "documentary": "documentary",
            "abstract_motion": "deep_cinematic",
            "product_demo": "conversational"
        }
        voice_profile = strategy_to_voice.get(visual_strategy.id, "energetic")
        dna_id = f"dna_{int(time.time())}_{random.randint(100, 999)}"

        return VideoDNA(
            id=dna_id,
            topic=topic,
            timestamp=time.time(),
            style=visual_strategy.id,
            palette=selected_palette,
            font_pair=selected_font,
            hook_type=hook_obj.id,
            story_structure=story_obj.id,
            motion_language=visual_strategy.motion_language,
            camera_language=visual_strategy.camera_language,
            transition_language=visual_strategy.transition_language,
            visual_metaphor=metaphor_id,
            sound_profile=audio_dna.genre,
            voice_profile=voice_profile,
            visual_strategy=visual_strategy.id,
            audio_dna=audio_dna.to_dict(),
            closing_dna=closing_dna.to_dict(),
            creative_seed=creative_seed,
            audio_seed=audio_seed,
            closing_seed=closing_seed
        )

    def _load_available_styles(self) -> Dict[str, Any]:
        """Loads legacy styles for fallback compatibility."""
        styles = {}
        if os.path.exists(STYLES_DIR):
            for fname in os.listdir(STYLES_DIR):
                if fname.endswith(".json"):
                    sid = fname[:-5]
                    try:
                        with open(os.path.join(STYLES_DIR, fname), "r", encoding="utf-8") as f:
                            styles[sid] = json.load(f)
                    except Exception:
                        pass
        return styles

    def _recommend_style_for_topic(self, topic: str) -> str:
        analysis = StoryDirector.analyze_topic(topic)
        strat = select_visual_strategy(topic, analysis, "structure_a")
        return strat.id

    def regenerate_audio_dna(self, topic: str, cd: Dict[str, Any], salt: str = "reroll") -> Dict[str, Any]:
        from effects.audio_dna import generate_audio_dna
        style_id = cd.get("visual_strategy_id") or cd.get("style_id", "cyberpunk")
        return generate_audio_dna(
            topic=topic,
            style_id=style_id,
            duration_sec=50.0,
            seed_salt=salt
        ).to_dict()

    def regenerate_closing_strategy(self, topic: str, cd: Dict[str, Any], salt: str = "reroll") -> Dict[str, Any]:
        from effects.closing_strategies import select_closing_strategy
        style_id = cd.get("visual_strategy_id") or cd.get("style_id", "cyberpunk")
        hook_data = cd.get("hook", {})
        return select_closing_strategy(
            topic=topic,
            hook_data=hook_data,
            style_id=style_id,
            seed_salt=salt
        ).to_dict()

    regenerate_closing_dna = regenerate_closing_strategy
