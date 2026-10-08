"""
effects/visual_dna.py
=====================
Defines VisualDNA for Prompt Reel.
Encapsulates the complete cohesive visual identity of a single video production.
Ensures internal consistency within one reel while creating distinct visual identities
across different reels.
"""
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional
from effects.visual_strategies import VisualStrategy
from effects.palettes import get_palette, CURATED_PALETTES
from effects.typography_registry import get_font_pairing


@dataclass
class VisualDNA:
    visual_strategy: str               # e.g. "technical_blueprint"
    strategy_name: str                 # e.g. "Technical Blueprint"
    composition_system: str            # e.g. "cad_schematic" | "modular_grid" | "split_comparison"
    typography: Dict[str, Any]         # {"heading": ..., "body": ..., "mono": ..., "font_pair_id": ...}
    color_system: Dict[str, Any]       # {"palette_id": ..., "background": [...], "primary": [...], ...}
    spacing_system: str                # "compact_technical" | "generous_editorial" | "stark_minimal" | "balanced"
    camera_language: str               # "slow_push" | "horizontal_tracking" | "orbit" | "snap_transitions" | ...
    transition_language: str           # "whip" | "directional_wipe" | "zoom" | "hard_cut" | "glitch" | ...
    motion_language: str               # "snappy_spring" | "fluid_orbital" | "mechanical_step" | "precision_linear"
    scene_vocabulary: List[str]        # ["nodes", "flows", "diagrams", "arrows", "counters"]
    texture: str                       # "clean_vector" | "blueprint_grid" | "depth_glassmorphism" | "scanline_crt"
    lighting: str                      # "ambient_studio" | "dramatic_spotlight" | "cyber_glow" | "high_key_clean"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VisualDNA":
        valid_keys = {
            "visual_strategy", "strategy_name", "composition_system", "typography",
            "color_system", "spacing_system", "camera_language", "transition_language",
            "motion_language", "scene_vocabulary", "texture", "lighting"
        }
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


def build_visual_dna(
    strategy: Any,
    palette_id: Optional[Any] = None,
    font_pair_id: Optional[str] = None
) -> VisualDNA:
    """
    Builds a coherent VisualDNA instance honoring the specified VisualStrategy.
    Resolves matching palette, typography, spacing, and texture tokens.
    """
    if isinstance(strategy, str) and isinstance(palette_id, VisualStrategy):
        strategy, palette_id = palette_id, None
    elif isinstance(strategy, str):
        from effects.visual_strategies import VISUAL_STRATEGIES, select_visual_strategy
        if strategy in VISUAL_STRATEGIES:
            strategy = VISUAL_STRATEGIES[strategy]
        else:
            strategy = select_visual_strategy(strategy)

    # 1. Palette resolution
    if not palette_id or not isinstance(palette_id, str):
        # Pick palette aligned with strategy category
        if strategy.palette_category == "blueprint":
            palette_id = "blueprint_cyan"
        elif strategy.palette_category == "matrix_terminal":
            palette_id = "terminal_matrix"
        elif strategy.palette_category == "amber_crt":
            palette_id = "amber_crt" if "amber_crt" in CURATED_PALETTES else "terminal_matrix"
        elif strategy.palette_category == "warm_editorial":
            palette_id = "cream_terracotta"
        elif strategy.palette_category == "stark_contrast":
            palette_id = "stark_noir"
        elif strategy.palette_category == "neon_matrix":
            palette_id = "electric_matrix"
        elif strategy.palette_category == "dark_cosmic":
            palette_id = "aurora_violet"
        elif strategy.palette_category == "clean_analytics":
            palette_id = "swiss_cobalt"
        elif strategy.palette_category == "infra_cyan":
            palette_id = "blueprint_cyan"
        elif strategy.palette_category == "dual_tone":
            palette_id = "navy_coral"
        else:
            palette_id = "charcoal_gold"

    pal_obj = get_palette(palette_id)
    color_system = {
        "palette_id": pal_obj.id,
        "name": pal_obj.name,
        "is_dark": pal_obj.is_dark,
        "background": list(pal_obj.background),
        "primary": list(pal_obj.primary),
        "secondary": list(pal_obj.secondary),
        "accent": list(pal_obj.accent),
        "surface": list(pal_obj.surface),
        "text": list(pal_obj.text),
        "subtext": list(pal_obj.subtext),
    }

    # 2. Typography resolution
    if not font_pair_id:
        if strategy.typography_category == "mono_technical":
            font_pair_id = "space_grotesk_ibm"
        elif strategy.typography_category == "editorial_serif":
            font_pair_id = "playfair_inter"
        elif strategy.typography_category == "bold_grotesk":
            font_pair_id = "bebas_inter"
        elif strategy.typography_category == "editorial":
            font_pair_id = "manrope_source"
        else:
            font_pair_id = "inter_jetbrains"

    font_obj = get_font_pairing(font_pair_id)
    heading_cand = font_obj.heading_font_candidates[0] if getattr(font_obj, "heading_font_candidates", None) else "Inter"
    h_name = heading_cand.split(".")[0].replace("-Bold", "").replace("bd", "").replace("b", "")
    body_cand = font_obj.body_font_candidates[0] if getattr(font_obj, "body_font_candidates", None) else "Inter"
    b_name = body_cand.split(".")[0].replace("-Regular", "")
    mono_cand = font_obj.mono_font_candidates[0] if getattr(font_obj, "mono_font_candidates", None) else "JetBrainsMono"
    m_name = mono_cand.split(".")[0].replace("-Regular", "")

    typography_system = {
        "font_pair_id": font_obj.id,
        "name": font_obj.name,
        "heading": f"{h_name}, sans-serif",
        "body": f"{b_name}, sans-serif",
        "mono": f"{m_name}, monospace",
    }

    # 3. Spacing system resolution
    if strategy.category in ("technical", "developer", "data"):
        spacing = "compact_technical"
    elif strategy.category in ("editorial", "retro"):
        spacing = "generous_editorial"
    elif strategy.category == "minimal":
        spacing = "stark_minimal"
    else:
        spacing = "balanced"

    return VisualDNA(
        visual_strategy=strategy.id,
        strategy_name=strategy.name,
        composition_system=strategy.composition_system,
        typography=typography_system,
        color_system=color_system,
        spacing_system=spacing,
        camera_language=strategy.camera_language,
        transition_language=strategy.transition_language,
        motion_language=strategy.motion_language,
        scene_vocabulary=strategy.scene_vocabulary,
        texture=strategy.texture,
        lighting=strategy.lighting,
    )
