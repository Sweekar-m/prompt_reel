"""
effects/motion_templates.py
===========================
Comprehensive Motion System & Template Architecture for Prompt Reel.
Defines genuinely distinct visual motion paradigms inspired by top motion studios
and references (e.g. Jitter, Moonb, OneTake).

A template is NOT just "palette + font + background".
A template defines:
- scene grammar (how ideas are structured visually)
- layout grammar (centered, left-weighted, split, diagonal, asymmetric, edge-anchored, full-bleed, stacked)
- object grammar (geometric shapes, path lines, UI elements, data tokens, 3D meshes, dimensional blocks)
- motion grammar (snappy spring, fluid decay, mechanical step, continuous drift, elastic overshoot)
- camera grammar (push, pull, pan, orbit, tilt, rotate, whip, track, follow, drift, zoom-through, depth planes, still)
- typography grammar (word-by-word reveal, tracking expand, kinetic displacement, line split, mask reveal, text-to-shape)
- transition grammar (element morph, line-to-path, UI-collapse, camera-dive, spatial wipe)
- timing grammar (pacing rhythm, rapid bursts vs stillness holds)
- background behavior (structural grid, blueprint grid, fracture planes, clean canvas, OS workspace)
- visual density & contrast rules
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class MotionTemplateSpec:
    id: str
    name: str
    category: str               # "kinetic_type", "product_ui", "technical", "spatial_3d", "abstract", "minimal", "data_viz", "cinematic"
    tagline: str
    description: str

    # Grammar specifications
    composition_styles: List[str]   # ["asymmetric_left", "full_bleed", "split_contrast", ...]
    primary_object_types: List[str] # ["massive_type", "bezier_path", "ui_window", "spatial_node", ...]
    motion_grammar: Dict[str, Any]  # default curves, spring stiffness, overshoot allowance
    camera_grammar: Dict[str, Any]  # allowed moves, default camera style, depth range
    typography_grammar: Dict[str, Any] # tracking, line splitting, word stagger, case
    transition_grammar: List[str]   # preferred carry primitives: ["morph", "expand", "travel", ...]
    timing_grammar: Dict[str, Any]  # rhythm pattern: rapid_burst -> long_hold -> dramatic_pause
    background_style: str           # "blueprint_grid", "swiss_ruler", "monochrome_planes", "clean_canvas", "os_workspace", ...
    lighting_depth: str             # "flat_high_contrast", "isometric_depth", "cinematic_directional", "subtle_ambient"
    visual_density: str             # "high_technical", "stark_minimal", "dense_kinetic", "balanced_ui"

    # Color and typography defaults
    preferred_fonts: Dict[str, str]
    compatible_audio_genres: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


MOTION_TEMPLATES: Dict[str, MotionTemplateSpec] = {
    # ── 1. KINETIC EDITORIAL ──────────────────────────────────────────────────
    "kinetic_editorial": MotionTemplateSpec(
        id="kinetic_editorial",
        name="Kinetic Editorial",
        category="kinetic_type",
        tagline="Bold high-fashion editorial typography with asymmetric grid cuts",
        description="Massive, authoritative typography commanding the canvas, paired with hairline dividing rules, word collisions, and elegant editorial pace.",
        composition_styles=["asymmetric_left", "edge_anchored", "full_bleed", "stacked"],
        primary_object_types=["massive_type", "hairline_divider", "editorial_column", "word_mask"],
        motion_grammar={
            "enter_primitive": "masked_reveal",
            "move_primitive": "drift",
            "transform_primitive": "object_to_text",
            "impact_primitive": "flash",
            "spring_config": {"mass": 0.85, "damping": 16, "stiffness": 190},
            "motion_blur_default": 0.25,
        },
        camera_grammar={
            "style": "pan_and_drift",
            "allowed_moves": ["pan", "push", "still", "drift"],
            "depth_range": [0, 200],
            "stillness_ratio": 0.35, # Uses intentional stillness holds
        },
        typography_grammar={
            "mode": "word_by_word",
            "stagger_frames": 3,
            "tracking_expand": True,
            "max_font_size": 96,
            "line_split": True,
            "case": "uppercase",
        },
        transition_grammar=["text_to_object", "masked_reveal", "collapse", "line_to_path"],
        timing_grammar={
            "beat_style": "rapid_burst_then_hold",
            "burst_duration_sec": 1.4,
            "hold_duration_sec": 2.2,
        },
        background_style="swiss_ruler",
        lighting_depth="flat_high_contrast",
        visual_density="dense_kinetic",
        preferred_fonts={"heading": "Outfit, sans-serif", "mono": "JetBrains Mono, monospace"},
        compatible_audio_genres=["minimal_electronic", "documentary", "organic_percussion", "modern_corporate"],
    ),

    # ── 2. DYNAMIC PRODUCT UI ─────────────────────────────────────────────────
    "dynamic_product_ui": MotionTemplateSpec(
        id="dynamic_product_ui",
        name="Dynamic Product UI",
        category="product_ui",
        tagline="Living software interface with floating panels, cursor ripples, and data states",
        description="Treats the concept as an exquisite modern software operating system. Cards, inspectors, terminal drawers, and telemetry meters seamlessly interact.",
        composition_styles=["centered", "split_contrast", "docked_bottom", "layered_planes"],
        primary_object_types=["ui_window", "telemetry_pill", "cursor_target", "data_table", "inspect_panel"],
        motion_grammar={
            "enter_primitive": "spring",
            "move_primitive": "follow",
            "transform_primitive": "card_to_screen",
            "impact_primitive": "ripple",
            "spring_config": {"mass": 0.7, "damping": 13, "stiffness": 160},
            "motion_blur_default": 0.15,
        },
        camera_grammar={
            "style": "track_and_zoom",
            "allowed_moves": ["track", "push", "depth_planes", "pan"],
            "depth_range": [-200, 350],
            "stillness_ratio": 0.2,
        },
        typography_grammar={
            "mode": "type_on",
            "stagger_frames": 1.5,
            "tracking_expand": False,
            "max_font_size": 64,
            "line_split": False,
            "case": "normal",
        },
        transition_grammar=["card_to_screen", "expand", "reshape", "morph"],
        timing_grammar={
            "beat_style": "smooth_fluid_continuity",
            "burst_duration_sec": 1.8,
            "hold_duration_sec": 1.6,
        },
        background_style="os_workspace",
        lighting_depth="subtle_ambient",
        visual_density="balanced_ui",
        preferred_fonts={"heading": "Inter, sans-serif", "mono": "JetBrains Mono, monospace"},
        compatible_audio_genres=["energetic_tech", "modern_corporate", "lofi_technology", "glitch_electronic"],
    ),

    # ── 3. BRUTALIST TYPOGRAPHY ───────────────────────────────────────────────
    "brutalist_typography": MotionTemplateSpec(
        id="brutalist_typography",
        name="Brutalist Typography",
        category="kinetic_type",
        tagline="Aggressive high-contrast geometry with mechanical snaps and giant glyphs",
        description="Raw, structural, uncompromising graphic design. Monospaced headers, thick structural dividing rules, harsh kinetic velocity, and zero decorative fluff.",
        composition_styles=["asymmetric_left", "full_bleed", "diagonal", "stacked"],
        primary_object_types=["monolithic_block", "glyph_cluster", "structural_divider", "raw_badge"],
        motion_grammar={
            "enter_primitive": "slide",
            "move_primitive": "acceleration",
            "transform_primitive": "split",
            "impact_primitive": "shake",
            "spring_config": {"mass": 1.2, "damping": 18, "stiffness": 260},
            "motion_blur_default": 0.45,
        },
        camera_grammar={
            "style": "whip_and_lock",
            "allowed_moves": ["whip", "rotate", "push", "still"],
            "depth_range": [0, 100],
            "stillness_ratio": 0.4,
        },
        typography_grammar={
            "mode": "kinetic_displacement",
            "stagger_frames": 2,
            "tracking_expand": True,
            "max_font_size": 110,
            "line_split": True,
            "case": "uppercase",
        },
        transition_grammar=["split", "shoot", "collapse", "wipe"],
        timing_grammar={
            "beat_style": "aggressive_staccato",
            "burst_duration_sec": 0.8,
            "hold_duration_sec": 2.5,
        },
        background_style="monochrome_planes",
        lighting_depth="flat_high_contrast",
        visual_density="high_technical",
        preferred_fonts={"heading": "JetBrains Mono, monospace", "mono": "JetBrains Mono, monospace"},
        compatible_audio_genres=["dark_pulse", "high_energy_digital", "industrial_crunch", "dark_tech"],
    ),

    # ── 4. FLUID ABSTRACT ─────────────────────────────────────────────────────
    "fluid_abstract": MotionTemplateSpec(
        id="fluid_abstract",
        name="Fluid Abstract",
        category="abstract",
        tagline="Organic liquid vectors, harmonic bezier curves, and flowing geometry",
        description="Mathematical beauty rendered through organic physics. Continuous bezier paths inflate, morph into data networks, and dissolve gracefully.",
        composition_styles=["radial", "centered", "diagonal", "panoramic"],
        primary_object_types=["liquid_blob", "bezier_wave", "gradient_portal", "particle_fountain"],
        motion_grammar={
            "enter_primitive": "elastic",
            "move_primitive": "drift",
            "transform_primitive": "morph",
            "impact_primitive": "ripple",
            "spring_config": {"mass": 1.3, "damping": 10, "stiffness": 110},
            "motion_blur_default": 0.2,
        },
        camera_grammar={
            "style": "orbital_drift",
            "allowed_moves": ["orbit", "drift", "pull", "track"],
            "depth_range": [-300, 300],
            "stillness_ratio": 0.15,
        },
        typography_grammar={
            "mode": "character_tracking",
            "stagger_frames": 4,
            "tracking_expand": True,
            "max_font_size": 72,
            "line_split": False,
            "case": "normal",
        },
        transition_grammar=["morph", "merge", "expand", "dissolve"],
        timing_grammar={
            "beat_style": "gentle_undulating_waves",
            "burst_duration_sec": 2.2,
            "hold_duration_sec": 1.8,
        },
        background_style="clean_canvas",
        lighting_depth="subtle_ambient",
        visual_density="stark_minimal",
        preferred_fonts={"heading": "Outfit, sans-serif", "mono": "Inter, sans-serif"},
        compatible_audio_genres=["futuristic_ambient", "atmospheric_space", "minimal_piano_electro", "synthwave"],
    ),

    # ── 5. TECHNICAL BLUEPRINT ────────────────────────────────────────────────
    "technical_blueprint": MotionTemplateSpec(
        id="technical_blueprint",
        name="Technical Blueprint",
        category="technical",
        tagline="Precision CAD schematic grids, orthographic dimensions, and vector trace lines",
        description="Engineering excellence captured in architectural vector drawings. Dimension callouts, dynamic stroke paths, node connections, and exact technical tolerances.",
        composition_styles=["asymmetric_left", "split_contrast", "edge_anchored", "layered_planes"],
        primary_object_types=["blueprint_schematic", "dimension_leader", "sub_node", "trace_circuit", "cad_crosshair"],
        motion_grammar={
            "enter_primitive": "path_reveal",
            "move_primitive": "follow",
            "transform_primitive": "line_to_path",
            "impact_primitive": "displacement",
            "spring_config": {"mass": 0.9, "damping": 15, "stiffness": 180},
            "motion_blur_default": 0.1,
        },
        camera_grammar={
            "style": "orthographic_pan",
            "allowed_moves": ["pan", "push", "track", "still"],
            "depth_range": [0, 150],
            "stillness_ratio": 0.3,
        },
        typography_grammar={
            "mode": "type_on",
            "stagger_frames": 2,
            "tracking_expand": True,
            "max_font_size": 58,
            "line_split": False,
            "case": "uppercase",
        },
        transition_grammar=["line_to_path", "expand", "masked_reveal", "collapse"],
        timing_grammar={
            "beat_style": "measured_construction_steps",
            "burst_duration_sec": 1.5,
            "hold_duration_sec": 2.0,
        },
        background_style="blueprint_grid",
        lighting_depth="flat_high_contrast",
        visual_density="high_technical",
        preferred_fonts={"heading": "JetBrains Mono, monospace", "mono": "JetBrains Mono, monospace"},
        compatible_audio_genres=["fast_rhythmic_math", "dark_tech", "glitch_electronic", "lofi_technology"],
    ),

    # ── 6. 3D SPATIAL EXPLAINER ───────────────────────────────────────────────
    "spatial_3d_explainer": MotionTemplateSpec(
        id="spatial_3d_explainer",
        name="3D Spatial Explainer",
        category="spatial_3d",
        tagline="Volumetric isometric geometry traversing multi-plane 3D camera coordinates",
        description="True spatial motion design. Isometric blocks, parametric mathematical surfaces, orbital continuous camera trajectories, and layered Z-depth planes.",
        composition_styles=["spatial_depth", "centered", "diagonal", "layered_planes"],
        primary_object_types=["spatial_mesh", "isometric_cube_cluster", "depth_layer_planes", "orbital_beacon"],
        motion_grammar={
            "enter_primitive": "depth_push",
            "move_primitive": "orbit",
            "transform_primitive": "rotate_to_next",
            "impact_primitive": "shake",
            "spring_config": {"mass": 1.1, "damping": 14, "stiffness": 150},
            "motion_blur_default": 0.35,
        },
        camera_grammar={
            "style": "full_3d_orbital_flight",
            "allowed_moves": ["orbit", "depth_planes", "tilt", "rotate", "push", "whip"],
            "depth_range": [-800, 600],
            "stillness_ratio": 0.15,
        },
        typography_grammar={
            "mode": "kinetic_displacement",
            "stagger_frames": 3,
            "tracking_expand": True,
            "max_font_size": 76,
            "line_split": True,
            "case": "uppercase",
        },
        transition_grammar=["rotate_to_next", "camera_pass_through", "pull_away", "expand"],
        timing_grammar={
            "beat_style": "dynamic_rollercoaster_traversal",
            "burst_duration_sec": 2.0,
            "hold_duration_sec": 1.5,
        },
        background_style="spatial_depth_grid",
        lighting_depth="isometric_depth",
        visual_density="balanced_ui",
        preferred_fonts={"heading": "Outfit, sans-serif", "mono": "JetBrains Mono, monospace"},
        compatible_audio_genres=["cinematic_electronic", "orchestral_hybrid", "deep_bass_drone", "fast_rhythmic_math"],
    ),

    # ── 7. MINIMAL SWISS MOTION ───────────────────────────────────────────────
    "minimal_swiss": MotionTemplateSpec(
        id="minimal_swiss",
        name="Minimal Swiss Motion",
        category="minimal",
        tagline="Disciplined 12-column Swiss grid, stark negative space, and intentional pauses",
        description="Timeless modernist design philosophy. Pure typography, disciplined geometric tokens, razor-sharp alignment, and maximum visual impact through restraint.",
        composition_styles=["asymmetric_left", "edge_anchored", "stacked", "split_contrast"],
        primary_object_types=["swiss_type_block", "minimal_token", "column_ruler", "stark_accent"],
        motion_grammar={
            "enter_primitive": "clip_reveal",
            "move_primitive": "deceleration",
            "transform_primitive": "reshape",
            "impact_primitive": "flash",
            "spring_config": {"mass": 0.8, "damping": 18, "stiffness": 210},
            "motion_blur_default": 0.05,
        },
        camera_grammar={
            "style": "disciplined_horizontal_steps",
            "allowed_moves": ["pan", "still", "push"],
            "depth_range": [0, 50],
            "stillness_ratio": 0.45,
        },
        typography_grammar={
            "mode": "mask_reveal",
            "stagger_frames": 2,
            "tracking_expand": False,
            "max_font_size": 84,
            "line_split": True,
            "case": "normal",
        },
        transition_grammar=["wipe", "masked_reveal", "collapse", "reshape"],
        timing_grammar={
            "beat_style": "meditative_precision_snaps",
            "burst_duration_sec": 1.0,
            "hold_duration_sec": 2.8,
        },
        background_style="swiss_ruler",
        lighting_depth="flat_high_contrast",
        visual_density="stark_minimal",
        preferred_fonts={"heading": "Inter, sans-serif", "mono": "JetBrains Mono, monospace"},
        compatible_audio_genres=["minimal_electronic", "documentary", "organic_percussion", "modern_corporate"],
    ),

    # ── 8. DATA STORY ─────────────────────────────────────────────────────────
    "data_story": MotionTemplateSpec(
        id="data_story",
        name="Data Story",
        category="data_viz",
        tagline="Flowing statistical graphs, expanding numerical meters, and comparative telemetry",
        description="Transforms computational logic into persuasive graphical metrics. Real-time counter streams, dynamic area partitions, and clear before/after metrics.",
        composition_styles=["split_contrast", "centered", "stacked", "radial"],
        primary_object_types=["numerical_meter", "bar_hierarchy", "flow_stream", "stat_callout"],
        motion_grammar={
            "enter_primitive": "overshoot",
            "move_primitive": "acceleration",
            "transform_primitive": "split",
            "impact_primitive": "displacement",
            "spring_config": {"mass": 0.9, "damping": 14, "stiffness": 170},
            "motion_blur_default": 0.18,
        },
        camera_grammar={
            "style": "stat_punch_and_track",
            "allowed_moves": ["push", "track", "pan", "still"],
            "depth_range": [-100, 200],
            "stillness_ratio": 0.25,
        },
        typography_grammar={
            "mode": "word_by_word",
            "stagger_frames": 2,
            "tracking_expand": True,
            "max_font_size": 68,
            "line_split": True,
            "case": "uppercase",
        },
        transition_grammar=["split", "merge", "expand", "collapse"],
        timing_grammar={
            "beat_style": "rapid_count_then_stabilize",
            "burst_duration_sec": 1.6,
            "hold_duration_sec": 1.9,
        },
        background_style="clean_canvas",
        lighting_depth="subtle_ambient",
        visual_density="high_technical",
        preferred_fonts={"heading": "Outfit, sans-serif", "mono": "JetBrains Mono, monospace"},
        compatible_audio_genres=["modern_corporate", "energetic_tech", "high_energy_digital", "glitch_electronic"],
    ),

    # ── 9. TERMINAL MOTION ───────────────────────────────────────────────────
    "terminal_motion": MotionTemplateSpec(
        id="terminal_motion",
        name="Terminal Motion",
        category="technical",
        tagline="High-velocity CLI cascades, memory register hex maps, and system pipe streams",
        description="For hardcore developers. Glowing monochrome phosphor, micro-second syntax highlights, pipe operators chaining data, and real compiler outputs.",
        composition_styles=["full_bleed", "asymmetric_left", "stacked", "centered"],
        primary_object_types=["terminal_buffer", "memory_hex_strip", "pipeline_operator", "cursor_stream"],
        motion_grammar={
            "enter_primitive": "type_on",
            "move_primitive": "deceleration",
            "transform_primitive": "line_to_path",
            "impact_primitive": "flash",
            "spring_config": {"mass": 0.7, "damping": 16, "stiffness": 220},
            "motion_blur_default": 0.12,
        },
        camera_grammar={
            "style": "micro_step_down",
            "allowed_moves": ["pan", "push", "still"],
            "depth_range": [0, 100],
            "stillness_ratio": 0.35,
        },
        typography_grammar={
            "mode": "type_on",
            "stagger_frames": 1,
            "tracking_expand": False,
            "max_font_size": 52,
            "line_split": False,
            "case": "normal",
        },
        transition_grammar=["shoot", "line_to_path", "masked_reveal", "collapse"],
        timing_grammar={
            "beat_style": "rapid_command_execution",
            "burst_duration_sec": 1.2,
            "hold_duration_sec": 2.2,
        },
        background_style="terminal_workspace",
        lighting_depth="flat_high_contrast",
        visual_density="high_technical",
        preferred_fonts={"heading": "JetBrains Mono, monospace", "mono": "JetBrains Mono, monospace"},
        compatible_audio_genres=["dark_tech", "glitch_electronic", "fast_rhythmic_math", "lofi_technology"],
    ),

    # ── 10. CINEMATIC OBJECT FILM ─────────────────────────────────────────────
    "cinematic_object": MotionTemplateSpec(
        id="cinematic_object",
        name="Cinematic Object Film",
        category="cinematic",
        tagline="Macro depth-of-field, dramatic directional shadows, and tactile weighted physics",
        description="Premium Apple-grade product film aesthetic. The technical concept behaves like a mastercrafted hardware sculpture under dramatic moving spotlights.",
        composition_styles=["centered", "diagonal", "spatial_depth", "asymmetric_left"],
        primary_object_types=["hero_sculpture", "specular_edge", "shadow_plane", "monolith_artifact"],
        motion_grammar={
            "enter_primitive": "blur_reveal",
            "move_primitive": "depth_push",
            "transform_primitive": "morph",
            "impact_primitive": "shake",
            "spring_config": {"mass": 1.4, "damping": 12, "stiffness": 130},
            "motion_blur_default": 0.4,
        },
        camera_grammar={
            "style": "slow_macro_cinematic_travel",
            "allowed_moves": ["push", "orbit", "tilt", "pull", "track"],
            "depth_range": [-500, 500],
            "stillness_ratio": 0.25,
        },
        typography_grammar={
            "mode": "character_tracking",
            "stagger_frames": 3,
            "tracking_expand": True,
            "max_font_size": 78,
            "line_split": True,
            "case": "uppercase",
        },
        transition_grammar=["camera_pass_through", "pull_away", "morph", "expand"],
        timing_grammar={
            "beat_style": "dramatic_crescendo_arc",
            "burst_duration_sec": 2.5,
            "hold_duration_sec": 2.0,
        },
        background_style="clean_canvas",
        lighting_depth="cinematic_directional",
        visual_density="balanced_ui",
        preferred_fonts={"heading": "Outfit, sans-serif", "mono": "Inter, sans-serif"},
        compatible_audio_genres=["cinematic_electronic", "orchestral_hybrid", "deep_bass_drone", "atmospheric_space"],
    ),
}


def get_motion_template(template_id: str) -> MotionTemplateSpec:
    return MOTION_TEMPLATES.get(template_id, MOTION_TEMPLATES["kinetic_editorial"])


def list_motion_templates() -> List[MotionTemplateSpec]:
    return list(MOTION_TEMPLATES.values())


def select_best_template_for_topic(topic: str, requested_style: Optional[str] = None) -> MotionTemplateSpec:
    """Intelligently matches a topic and conceptual goal to the optimal motion template."""
    if requested_style and requested_style in MOTION_TEMPLATES:
        return MOTION_TEMPLATES[requested_style]

    t = topic.lower()
    if any(k in t for k in ["docker", "container", "cloud", "layer", "pod", "kubernetes"]):
        return MOTION_TEMPLATES["spatial_3d_explainer"]
    elif any(k in t for k in ["binary search", "search", "partition", "sort", "algorithm", "tree", "graph"]):
        return MOTION_TEMPLATES["technical_blueprint"]
    elif any(k in t for k in ["api", "rest", "http", "network", "client", "server", "json"]):
        return MOTION_TEMPLATES["dynamic_product_ui"]
    elif any(k in t for k in ["oop", "object", "class", "inherit", "polymorph", "architecture"]):
        return MOTION_TEMPLATES["kinetic_editorial"]
    elif any(k in t for k in ["if", "else", "branch", "logic", "switch", "boolean"]):
        return MOTION_TEMPLATES["brutalist_typography"]
    elif any(k in t for k in ["math", "formula", "geometry", "sinc", "vector", "3d"]):
        return MOTION_TEMPLATES["spatial_3d_explainer"]
    elif any(k in t for k in ["memory", "hardware", "cpu", "assembly", "register", "cache"]):
        return MOTION_TEMPLATES["terminal_motion"]
    elif any(k in t for k in ["data", "benchmark", "performance", "throughput", "latency"]):
        return MOTION_TEMPLATES["data_story"]
    else:
        return MOTION_TEMPLATES["kinetic_editorial"]
