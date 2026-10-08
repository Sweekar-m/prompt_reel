"""
effects/visual_strategies.py
============================
Visual Strategy Engine.
Provides 18 distinct VisualStrategy blueprints that dictate the visual identity
of a reel: composition system, typography pairing, palette category, camera language,
transition language, motion grammar, texture, lighting, and scene vocabulary.

Every video consumes a coherent VisualStrategy matched directly to its topic and narrative.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from effects.story_structures import TopicAnalysis


@dataclass
class VisualStrategy:
    id: str
    name: str
    category: str
    description: str
    compatible_topic_types: List[str]
    compatible_story_structures: List[str]
    composition_system: str
    palette_category: str
    typography_category: str
    camera_language: str
    transition_language: str
    motion_language: str
    texture: str
    lighting: str
    scene_vocabulary: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


VISUAL_STRATEGIES: Dict[str, VisualStrategy] = {
    # 1. KINETIC TYPOGRAPHY
    "kinetic_typography": VisualStrategy(
        id="kinetic_typography",
        name="Kinetic Typography",
        category="typography",
        description="Massive, commanding typography, rapid text-to-shape transitions, high-contrast monochrome cuts.",
        compatible_topic_types=["philosophical_conceptual", "web_frontend", "language_runtime_internals"],
        compatible_story_structures=["structure_f", "structure_g", "structure_a"],
        composition_system="asymmetric_editorial",
        palette_category="stark_contrast",
        typography_category="bold_grotesk",
        camera_language="snap_transitions",
        transition_language="hard_cut",
        motion_language="snappy_spring",
        texture="clean_vector",
        lighting="high_key_clean",
        scene_vocabulary=["typography", "highlighted_regions", "cards", "timelines"]
    ),

    # 2. EDITORIAL GRID
    "editorial_grid": VisualStrategy(
        id="editorial_grid",
        name="Editorial Swiss Grid",
        category="editorial",
        description="Structured multi-column Swiss grid, disciplined hairline rules, elegant asymmetric negative space.",
        compatible_topic_types=["language_runtime_internals", "operating_systems_lowlevel", "database_storage"],
        compatible_story_structures=["structure_a", "structure_f", "structure_j"],
        composition_system="modular_grid",
        palette_category="warm_editorial",
        typography_category="editorial",
        camera_language="static_editorial",
        transition_language="slide",
        motion_language="precision_linear",
        texture="paper_canvas",
        lighting="ambient_studio",
        scene_vocabulary=["cards", "timelines", "diagrams", "highlighted_regions", "typography"]
    ),

    # 3. CINEMATIC DIAGRAM
    "cinematic_diagram": VisualStrategy(
        id="cinematic_diagram",
        name="Cinematic Diagram",
        category="diagram",
        description="Volumetric diagrams, atmospheric depth haze, slow creeping camera push, illuminated focal paths.",
        compatible_topic_types=["system_architecture", "networking_distributed", "ai_machine_learning"],
        compatible_story_structures=["structure_a", "structure_e", "structure_h", "structure_i"],
        composition_system="spatial_depth",
        palette_category="cinematic_dark",
        typography_category="modern_tech",
        camera_language="slow_push",
        transition_language="zoom",
        motion_language="fluid_orbital",
        texture="depth_glassmorphism",
        lighting="dramatic_spotlight",
        scene_vocabulary=["nodes", "graphs", "flows", "diagrams", "particles", "arrows"]
    ),

    # 4. TECHNICAL BLUEPRINT
    "technical_blueprint": VisualStrategy(
        id="technical_blueprint",
        name="Technical Blueprint",
        category="technical",
        description="CAD coordinate grids, drafting crosshairs, dimension callouts, schematic wireframes.",
        compatible_topic_types=["algorithms_data_structures", "operating_systems_lowlevel", "math_theoretical"],
        compatible_story_structures=["structure_b", "structure_d", "structure_i", "structure_k"],
        composition_system="cad_schematic",
        palette_category="blueprint",
        typography_category="mono_technical",
        camera_language="horizontal_tracking",
        transition_language="directional_wipe",
        motion_language="mechanical_step",
        texture="blueprint_grid",
        lighting="ambient_studio",
        scene_vocabulary=["grids", "diagrams", "paths", "arrows", "counters", "nodes"]
    ),

    # 5. TERMINAL STORY
    "terminal_story": VisualStrategy(
        id="terminal_story",
        name="Terminal Story",
        category="developer",
        description="Dark phosphor CRT terminal trace, raw kernel stderr logs, blinking block cursor, monospace mastery.",
        compatible_topic_types=["operating_systems_lowlevel", "devops_cloud_infra", "security_cryptography"],
        compatible_story_structures=["structure_c", "structure_g", "structure_b"],
        composition_system="terminal_flow",
        palette_category="matrix_terminal",
        typography_category="mono_technical",
        camera_language="snap_transitions",
        transition_language="glitch",
        motion_language="mechanical_step",
        texture="scanline_crt",
        lighting="terminal_phosphor",
        scene_vocabulary=["terminal_traces", "code_execution", "flows", "counters"]
    ),

    # 6. CODE FIRST
    "code_first": VisualStrategy(
        id="code_first",
        name="Code-First Dissection",
        category="developer",
        description="Syntax tokens treated as living physical mechanics, line-by-line runtime execution laser trace.",
        compatible_topic_types=["language_runtime_internals", "web_frontend", "algorithms_data_structures"],
        compatible_story_structures=["structure_a", "structure_c", "structure_g"],
        composition_system="split_execution",
        palette_category="developer_dark",
        typography_category="mono_technical",
        camera_language="depth_zoom",
        transition_language="match_cut",
        motion_language="snappy_spring",
        texture="depth_glassmorphism",
        lighting="dramatic_spotlight",
        scene_vocabulary=["code_execution", "terminal_traces", "comparison_panels", "flows"]
    ),

    # 7. DATA VISUALIZATION
    "data_visualization": VisualStrategy(
        id="data_visualization",
        name="Data Visualization",
        category="data",
        description="Dynamic charts, live latency distribution curves, memory partition arrays, throughput meters.",
        compatible_topic_types=["algorithms_data_structures", "database_storage", "product_engineering"],
        compatible_story_structures=["structure_b", "structure_d", "structure_j"],
        composition_system="metric_breakdown",
        palette_category="clean_analytics",
        typography_category="modern_tech",
        camera_language="horizontal_tracking",
        transition_language="slide",
        motion_language="precision_linear",
        texture="clean_vector",
        lighting="high_key_clean",
        scene_vocabulary=["charts", "counters", "grids", "comparison_panels", "timelines"]
    ),

    # 8. SPLIT SCREEN COMPARISON
    "split_screen_comparison": VisualStrategy(
        id="split_screen_comparison",
        name="Split-Screen Comparison",
        category="comparison",
        description="Dual-channel synchronized showdown: Method A vs Method B side-by-side with diverging telemetry.",
        compatible_topic_types=["web_frontend", "database_storage", "system_architecture", "product_engineering"],
        compatible_story_structures=["structure_j", "structure_f", "structure_h", "structure_c"],
        composition_system="split_comparison",
        palette_category="dual_tone",
        typography_category="bold_grotesk",
        camera_language="vertical_tracking",
        transition_language="directional_wipe",
        motion_language="snappy_spring",
        texture="clean_vector",
        lighting="ambient_studio",
        scene_vocabulary=["comparison_panels", "charts", "counters", "cards", "diagrams"]
    ),

    # 9. MATHEMATICAL 3D
    "mathematical_3d": VisualStrategy(
        id="mathematical_3d",
        name="Mathematical 3D Manifold",
        category="mathematics",
        description="Continuous 3D parametric surfaces, vector flow fields, spatial Euler helices, coordinate rotation.",
        compatible_topic_types=["math_theoretical", "ai_machine_learning"],
        compatible_story_structures=["structure_k", "structure_a", "structure_b"],
        composition_system="isometric_3d",
        palette_category="dark_cosmic",
        typography_category="modern_tech",
        camera_language="orbit",
        transition_language="zoom",
        motion_language="fluid_orbital",
        texture="depth_glassmorphism",
        lighting="cyber_glow",
        scene_vocabulary=["mathematical_surfaces", "3d_objects", "particles", "paths", "graphs"]
    ),

    # 10. SYSTEM ARCHITECTURE
    "system_architecture": VisualStrategy(
        id="system_architecture",
        name="System Architecture & Cloud Topology",
        category="architecture",
        description="High-altitude infrastructure maps, ingress routing, microservice clusters, queue telemetry.",
        compatible_topic_types=["system_architecture", "devops_cloud_infra", "networking_distributed"],
        compatible_story_structures=["structure_i", "structure_h", "structure_e"],
        composition_system="radial_network",
        palette_category="infra_cyan",
        typography_category="modern_tech",
        camera_language="pull_out",
        transition_language="whip",
        motion_language="snappy_spring",
        texture="blueprint_grid",
        lighting="dramatic_spotlight",
        scene_vocabulary=["nodes", "graphs", "flows", "diagrams", "arrows", "cards"]
    ),

    # 11. MAGAZINE EDITORIAL
    "magazine_editorial": VisualStrategy(
        id="magazine_editorial",
        name="Magazine Editorial",
        category="editorial",
        description="Warm serif headline typography, textured cream backgrounds, editorial pull-quotes, refined rhythm.",
        compatible_topic_types=["history_evolution", "philosophical_conceptual", "product_engineering"],
        compatible_story_structures=["structure_a", "structure_l", "structure_h"],
        composition_system="asymmetric_editorial",
        palette_category="warm_editorial",
        typography_category="editorial_serif",
        camera_language="static_editorial",
        transition_language="slide",
        motion_language="drift_inertia",
        texture="paper_canvas",
        lighting="ambient_studio",
        scene_vocabulary=["typography", "cards", "timelines", "highlighted_regions"]
    ),

    # 12. RETRO COMPUTING
    "retro_computing": VisualStrategy(
        id="retro_computing",
        name="Retro Computing",
        category="retro",
        description="Vintage amber/green display, stepped 12fps retro animation, IBM Plex Mono, 80s hardware aesthetic.",
        compatible_topic_types=["history_evolution", "operating_systems_lowlevel", "security_cryptography"],
        compatible_story_structures=["structure_g", "structure_l", "structure_b"],
        composition_system="terminal_flow",
        palette_category="amber_crt",
        typography_category="mono_technical",
        camera_language="snap_transitions",
        transition_language="glitch",
        motion_language="mechanical_step",
        texture="scanline_crt",
        lighting="terminal_phosphor",
        scene_vocabulary=["terminal_traces", "code_execution", "grids", "counters"]
    ),

    # 13. SWISS MINIMAL
    "swiss_minimal": VisualStrategy(
        id="swiss_minimal",
        name="Swiss Minimal",
        category="minimal",
        description="Absolute functional minimalism, maximum negative space, single bold accent color, Helvetica purity.",
        compatible_topic_types=["algorithms_data_structures", "web_frontend", "math_theoretical"],
        compatible_story_structures=["structure_a", "structure_d", "structure_f"],
        composition_system="modular_grid",
        palette_category="stark_contrast",
        typography_category="bold_grotesk",
        camera_language="static_editorial",
        transition_language="hard_cut",
        motion_language="precision_linear",
        texture="clean_vector",
        lighting="high_key_clean",
        scene_vocabulary=["diagrams", "cards", "typography", "highlighted_regions"]
    ),

    # 14. CYBERPUNK
    "cyberpunk": VisualStrategy(
        id="cyberpunk",
        name="Cyberpunk High-Tech",
        category="cinematic",
        description="High-voltage neon primaries, glitch displacement, aggressive whip pans, laser telemetry.",
        compatible_topic_types=["security_cryptography", "ai_machine_learning", "operating_systems_lowlevel"],
        compatible_story_structures=["structure_c", "structure_g", "structure_h"],
        composition_system="spatial_depth",
        palette_category="neon_matrix",
        typography_category="modern_tech",
        camera_language="handheld",
        transition_language="glitch",
        motion_language="snappy_spring",
        texture="neon_glow",
        lighting="cyber_glow",
        scene_vocabulary=["nodes", "flows", "terminal_traces", "particles", "highlighted_regions"]
    ),

    # 15. BRUTALIST
    "brutalist": VisualStrategy(
        id="brutalist",
        name="Brutalist Architecture",
        category="typography",
        description="Monolithic typography, hard borders, raw unpadded blocks, jarring cuts, anti-decorative honesty.",
        compatible_topic_types=["philosophical_conceptual", "web_frontend", "operating_systems_lowlevel"],
        compatible_story_structures=["structure_f", "structure_c", "structure_g"],
        composition_system="asymmetric_editorial",
        palette_category="monochrome_matte",
        typography_category="bold_grotesk",
        camera_language="snap_transitions",
        transition_language="hard_cut",
        motion_language="mechanical_step",
        texture="monochrome_matte",
        lighting="high_key_clean",
        scene_vocabulary=["typography", "cards", "comparison_panels", "timelines"]
    ),

    # 16. DOCUMENTARY
    "documentary": VisualStrategy(
        id="documentary",
        name="Documentary Deep Dive",
        category="editorial",
        description="Slow deliberate tracking, archival chronological timelines, sober authoritative pacing.",
        compatible_topic_types=["history_evolution", "philosophical_conceptual", "system_architecture"],
        compatible_story_structures=["structure_l", "structure_h", "structure_a"],
        composition_system="modular_grid",
        palette_category="warm_editorial",
        typography_category="editorial_serif",
        camera_language="horizontal_tracking",
        transition_language="dissolve",
        motion_language="drift_inertia",
        texture="subtle_film_grain",
        lighting="shadow_depth",
        scene_vocabulary=["timelines", "cards", "diagrams", "highlighted_regions", "typography"]
    ),

    # 17. ABSTRACT MOTION
    "abstract_motion": VisualStrategy(
        id="abstract_motion",
        name="Abstract Kinetic Motion",
        category="abstract",
        description="Organic geometric morphing, fluid orbital curves, synchronized multi-object choreography.",
        compatible_topic_types=["math_theoretical", "ai_machine_learning", "philosophical_conceptual"],
        compatible_story_structures=["structure_e", "structure_k", "structure_a"],
        composition_system="spatial_depth",
        palette_category="dark_cosmic",
        typography_category="modern_tech",
        camera_language="orbit",
        transition_language="morph",
        motion_language="fluid_orbital",
        texture="depth_glassmorphism",
        lighting="dramatic_spotlight",
        scene_vocabulary=["particles", "mathematical_surfaces", "nodes", "flows", "3d_objects"]
    ),

    # 18. PRODUCT DEMO
    "product_demo": VisualStrategy(
        id="product_demo",
        name="Product Engineering UI",
        category="product",
        description="Sleek glassmorphic application UI, live interactive toggles, telemetry badges, production feel.",
        compatible_topic_types=["product_engineering", "web_frontend", "networking_distributed"],
        compatible_story_structures=["structure_j", "structure_d", "structure_e"],
        composition_system="split_execution",
        palette_category="clean_analytics",
        typography_category="modern_tech",
        camera_language="depth_zoom",
        transition_language="mask_reveal",
        motion_language="snappy_spring",
        texture="depth_glassmorphism",
        lighting="ambient_studio",
        scene_vocabulary=["cards", "flows", "comparison_panels", "counters", "highlighted_regions"]
    )
}


def select_visual_strategy(
    topic: str,
    analysis: Optional[TopicAnalysis] = None,
    story_structure_id: Optional[str] = None,
    requested_style: Optional[str] = None,
    recent_strategies: Optional[List[str]] = None
) -> VisualStrategy:
    """
    Selects the most compelling VisualStrategy through multidimensional scoring:
    Category Match + Story Structure Match + Modality Match - Novelty Penalty.
    Ensures every video has an intentional visual identity aligned with its content.
    """
    if analysis is None:
        from effects.story_structures import StoryDirector
        analysis = StoryDirector().analyze_topic(topic)

    recent = recent_strategies or []

    # If requested style matches strategy id directly
    if requested_style and requested_style in VISUAL_STRATEGIES:
        return VISUAL_STRATEGIES[requested_style]

    scores: Dict[str, float] = {}

    for strat_id, strat in VISUAL_STRATEGIES.items():
        score = 10.0

        # Topic category alignment (+35 max)
        if analysis.category in strat.compatible_topic_types:
            score += 35.0

        # Story structure alignment (+25 max)
        if story_structure_id and story_structure_id in strat.compatible_story_structures:
            score += 25.0

        # Modalities bonus (+35 max)
        if analysis.modalities.get("involves_mathematics") and strat_id in ("mathematical_3d", "abstract_motion"):
            score += 35.0
        if analysis.modalities.get("involves_comparison") and strat_id in ("split_screen_comparison", "data_visualization"):
            score += 35.0
        if analysis.modalities.get("involves_history") and strat_id in ("documentary", "magazine_editorial", "retro_computing"):
            score += 35.0
        if analysis.modalities.get("involves_diagrams") and strat_id in ("system_architecture", "cinematic_diagram", "technical_blueprint"):
            score += 30.0
        if analysis.modalities.get("involves_systems") and strat_id in ("technical_blueprint", "system_architecture", "cyberpunk"):
            score += 30.0
        if analysis.modalities.get("involves_data") and strat_id in ("data_visualization", "editorial_grid"):
            score += 25.0
        if analysis.modalities.get("involves_abstract") and strat_id in ("kinetic_typography", "abstract_motion", "swiss_minimal"):
            score += 35.0
        if analysis.modalities.get("involves_code") and strat_id in ("code_first", "terminal_story"):
            score += 25.0

        # Novelty Penalty:
        # -30 if used in the most recent video
        # -15 if used in the 2nd most recent
        # -8 if used in the 3rd most recent
        if recent:
            if len(recent) > 0 and recent[-1] == strat_id:
                score -= 30.0
            if len(recent) > 1 and recent[-2] == strat_id:
                score -= 15.0
            if len(recent) > 2 and recent[-3] == strat_id:
                score -= 8.0

        scores[strat_id] = score

    best_id = max(scores, key=lambda s: scores[s])
    return VISUAL_STRATEGIES[best_id]
