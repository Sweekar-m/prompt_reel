"""
agents/shot_designer_agent.py
=============================
Shot Designer Agent for Prompt Reel.
Operates between Storyboard Assembly and the Render Engine.

Mandate:
- Eliminates "animated presentation slides" and monotonous centered card layouts.
- Decides HOW every idea is visualized as a professional motion-graphics film.
- Produces rich VisualRecipes with varied compositions, 3D camera travel, motion primitives,
  typography behaviors, depth planes, and continuous visual carries.
- Content-Aware Generative Variety: Infers visual metaphors from topic semantics rather
  than keyword hardcoding.
- Assigns data-driven composition variants across Hook, Code, Diagram, Metaphor, and Payoff beats.
"""
import hashlib
from typing import Dict, Any, List, Optional
from effects.story_structures import StoryDirector, TopicAnalysis
from effects.visual_strategies import VISUAL_STRATEGIES, VisualStrategy
from effects.visual_dna import VisualDNA, build_visual_dna
from effects.motion_templates import (
    get_motion_template,
    select_best_template_for_topic,
    MotionTemplateSpec,
    MOTION_TEMPLATES
)
from effects.motion_primitives import (
    ALL_MOTION_PRIMITIVES,
    ENTER_PRIMITIVES,
    MOVE_PRIMITIVES,
    TRANSFORM_PRIMITIVES,
    IMPACT_PRIMITIVES,
    EXIT_PRIMITIVES
)
from effects.visual_recipes import (
    VisualRecipe,
    CameraWaypoint,
    CameraTrajectory,
    VisualPrimitivesConfig,
    TypographyBehaviorConfig,
    SubjectLayer,
    CarryRelationship
)


class ShotDesignerAgent:
    def __init__(self):
        pass

    def design_shots_for_motion_plan(
        self,
        motion_plan: Dict[str, Any],
        requested_template_id: Optional[str] = None,
        creative_dir: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enhances motion plan by generating rich, renderable Visual Recipes and
        dynamic composition variants for every beat in the storyboard.
        """
        topic = motion_plan.get("topic", "Software Architecture")
        creative_dir = creative_dir or motion_plan.get("creative_direction", {})
        scenes = motion_plan.get("scenes", [])
        total_duration = motion_plan.get("duration", 50.0)

        # 1. Resolve Topic Analysis and VisualDNA
        analysis = StoryDirector.analyze_topic(topic)
        visual_dna_dict = creative_dir.get("visual_dna") or motion_plan.get("visual_dna") or {}
        strat_id = visual_dna_dict.get("visual_strategy") or creative_dir.get("visual_strategy_id") or "cinematic_diagram"
        visual_strategy = VISUAL_STRATEGIES.get(strat_id, VISUAL_STRATEGIES["cinematic_diagram"])

        # Resolve Motion Template matching the strategy
        template_id = requested_template_id or creative_dir.get("motion_template_id")
        if not template_id:
            template = select_best_template_for_topic(topic, requested_style=strat_id)
        else:
            template = get_motion_template(template_id)

        creative_dir["motion_template"] = template.to_dict()
        creative_dir["motion_template_id"] = template.id

        # 2. Continuous Camera Trajectory Accumulator
        curr_cam = CameraWaypoint(x=0.0, y=0.0, z=0.0, pitch=0.0, yaw=0.0, roll=0.0, scale=1.0)

        # 3. Design each beat as an expressive motion shot
        designed_scenes = []
        composition_variants_used = []
        num_scenes = len(scenes)

        for idx, scene in enumerate(scenes):
            recipe, curr_cam, comp_variant = self._design_scene_recipe(
                scene=scene,
                idx=idx,
                num_scenes=num_scenes,
                topic=topic,
                analysis=analysis,
                strategy=visual_strategy,
                template=template,
                curr_cam=curr_cam,
                tech_summary=motion_plan.get("technical_summary", {}),
                code_assets=motion_plan.get("code_assets", {})
            )
            scene["visual_recipe"] = recipe.to_dict()
            scene["visual_recipe_obj"] = recipe
            scene["composition_variant"] = comp_variant
            composition_variants_used.append(comp_variant)
            designed_scenes.append(scene)

        motion_plan["scenes"] = designed_scenes
        motion_plan["composition_variants"] = composition_variants_used
        motion_plan["shot_designer_version"] = "4.0"
        motion_plan["motion_template"] = template.to_dict()

        # Update creative direction & DNA with used compositions
        if "dna" in creative_dir and isinstance(creative_dir["dna"], dict):
            creative_dir["dna"]["composition_variants"] = composition_variants_used

        return motion_plan

    def _design_scene_recipe(
        self,
        scene: Dict[str, Any],
        idx: int,
        num_scenes: int,
        topic: str,
        analysis: TopicAnalysis,
        strategy: VisualStrategy,
        template: MotionTemplateSpec,
        curr_cam: CameraWaypoint,
        tech_summary: Dict[str, Any],
        code_assets: Dict[str, Any]
    ) -> tuple[VisualRecipe, CameraWaypoint, str]:
        """Designs a customized VisualRecipe & selects dynamic composition variant for a beat."""
        v_type = scene.get("visual_type", "metaphor")
        beat_name = scene.get("beat_name", f"beat_{idx+1}")
        start_t = float(scene.get("start", 0.0))
        end_t = float(scene.get("end", start_t + 5.0))
        dur_t = float(scene.get("duration", end_t - start_t))
        elems = scene.get("elements", {})

        # ── 1. Dynamic Composition Selection ──────────────────────────────────
        comp_variant = self._select_composition_variant(v_type, strategy, idx, analysis)

        possible_comps = template.composition_styles
        comp_style = possible_comps[idx % len(possible_comps)]

        if comp_style == "asymmetric_left":
            anchor = {"x_pct": 14, "y_pct": 46, "align": "left"}
        elif comp_style == "asymmetric_right":
            anchor = {"x_pct": 74, "y_pct": 48, "align": "right"}
        elif comp_style == "split_contrast":
            anchor = {"x_pct": 50, "y_pct": 50, "align": "split"}
        elif comp_style == "edge_anchored":
            anchor = {"x_pct": 10, "y_pct": 78, "align": "left"}
        elif comp_style == "full_bleed":
            anchor = {"x_pct": 50, "y_pct": 50, "align": "full"}
        elif comp_style == "stacked":
            anchor = {"x_pct": 20, "y_pct": 35, "align": "left"}
        elif comp_style == "spatial_depth":
            anchor = {"x_pct": 50, "y_pct": 52, "align": "center"}
        else:
            anchor = {"x_pct": 50, "y_pct": 50, "align": "center"}

        # ── 2. Dynamic Camera Trajectory based on Visual Strategy ─────────────
        cam_start = CameraWaypoint(
            x=curr_cam.x,
            y=curr_cam.y,
            z=curr_cam.z,
            pitch=curr_cam.pitch,
            yaw=curr_cam.yaw,
            roll=curr_cam.roll,
            scale=curr_cam.scale
        )

        cam_mode = strategy.camera_language
        if cam_mode == "static_editorial":
            cam_end = CameraWaypoint(x=cam_start.x, y=cam_start.y, z=cam_start.z, pitch=cam_start.pitch, yaw=cam_start.yaw, roll=cam_start.roll, scale=cam_start.scale)
            blur_intensity = 0.0
            move_style = "still"
        elif cam_mode == "slow_push":
            cam_end = CameraWaypoint(x=cam_start.x + (15 if idx % 2 == 0 else -15), y=cam_start.y - 10, z=cam_start.z + 140, pitch=cam_start.pitch + 2.0, yaw=cam_start.yaw, roll=cam_start.roll, scale=cam_start.scale * 1.06)
            blur_intensity = 0.12
            move_style = "push"
        elif cam_mode == "fast_push":
            cam_end = CameraWaypoint(x=cam_start.x, y=cam_start.y - 20, z=cam_start.z + 280, pitch=cam_start.pitch + 3.5, yaw=cam_start.yaw, roll=cam_start.roll, scale=cam_start.scale * 1.14)
            blur_intensity = 0.35
            move_style = "push"
        elif cam_mode == "pull_out":
            cam_end = CameraWaypoint(x=cam_start.x, y=cam_start.y + 15, z=cam_start.z - 160, pitch=cam_start.pitch - 2.0, yaw=cam_start.yaw, roll=cam_start.roll, scale=cam_start.scale * 0.94)
            blur_intensity = 0.15
            move_style = "pull"
        elif cam_mode == "horizontal_tracking":
            delta_x = 90 if idx % 2 == 0 else -90
            cam_end = CameraWaypoint(x=cam_start.x + delta_x, y=cam_start.y, z=cam_start.z, pitch=cam_start.pitch, yaw=cam_start.yaw + (3.0 if delta_x > 0 else -3.0), roll=cam_start.roll, scale=cam_start.scale)
            blur_intensity = 0.22
            move_style = "pan"
        elif cam_mode == "vertical_tracking":
            delta_y = -70 if idx % 2 == 0 else 70
            cam_end = CameraWaypoint(x=cam_start.x, y=cam_start.y + delta_y, z=cam_start.z, pitch=cam_start.pitch + (2.5 if delta_y < 0 else -2.5), yaw=cam_start.yaw, roll=cam_start.roll, scale=cam_start.scale)
            blur_intensity = 0.20
            move_style = "pan"
        elif cam_mode == "orbit":
            cam_end = CameraWaypoint(x=cam_start.x + 45, y=cam_start.y - 25, z=cam_start.z + 90, pitch=cam_start.pitch + 6.0, yaw=cam_start.yaw + 14.0, roll=cam_start.roll, scale=cam_start.scale * 1.03)
            blur_intensity = 0.28
            move_style = "orbit"
        elif cam_mode == "handheld":
            cam_end = CameraWaypoint(x=cam_start.x + (25 if idx % 2 == 0 else -20), y=cam_start.y + (12 if idx % 2 == 1 else -15), z=cam_start.z + 50, pitch=cam_start.pitch + 1.5, yaw=cam_start.yaw - 2.0, roll=cam_start.roll + 0.8, scale=cam_start.scale * 1.02)
            blur_intensity = 0.20
            move_style = "drift"
        elif cam_mode == "snap_transitions":
            cam_end = CameraWaypoint(x=cam_start.x + (120 if idx % 2 == 0 else -120), y=cam_start.y, z=cam_start.z, pitch=cam_start.pitch, yaw=cam_start.yaw, roll=cam_start.roll, scale=cam_start.scale)
            blur_intensity = 0.45
            move_style = "whip"
        elif cam_mode == "depth_zoom":
            cam_end = CameraWaypoint(x=cam_start.x, y=cam_start.y - 15, z=cam_start.z + 200, pitch=cam_start.pitch + 3.0, yaw=cam_start.yaw, roll=cam_start.roll, scale=cam_start.scale * 1.10)
            blur_intensity = 0.25
            move_style = "push"
        else: # default drift
            cam_end = CameraWaypoint(x=cam_start.x + 20, y=cam_start.y - 12, z=cam_start.z + 40, pitch=cam_start.pitch + 1.0, yaw=cam_start.yaw + 2.0, roll=cam_start.roll, scale=cam_start.scale * 1.02)
            blur_intensity = 0.10
            move_style = "drift"

        camera_traj = CameraTrajectory(
            start=cam_start,
            end=cam_end,
            motion_style=move_style,
            motion_blur=blur_intensity,
            easing="cubic_out" if move_style != "still" else "linear"
        )

        # ── 3. Visual Motion Primitives ──────────────────────────────────────
        if v_type == "hook":
            enter_prim = "glitch" if strategy.id in ("cyberpunk", "retro_computing") else "spring"
        elif v_type == "code":
            enter_prim = "step"
        elif v_type in ("split", "benchmark"):
            enter_prim = "split_wipe"
        elif strategy.motion_language in ("fluid_orbital", "flowing_curve"):
            enter_prim = "orbit"
        elif strategy.motion_language == "mechanical_step":
            enter_prim = "step"
        elif strategy.motion_language == "drift_inertia":
            enter_prim = "drift_enter"
        elif strategy.motion_language == "snappy_spring":
            enter_prim = "spring"
        else:
            enter_prim = "masked_reveal" if idx % 2 == 0 else "spring"

        primitives_cfg = VisualPrimitivesConfig(
            enter=enter_prim,
            move="drift" if strategy.motion_language == "drift_inertia" else "step",
            transform="expand",
            impact="flash" if strategy.id == "cyberpunk" else "shake",
            exit=strategy.transition_language
        )

        # ── 4. Typography as Motion Object ────────────────────────────────────
        raw_narration = scene.get("narration") or scene.get("voice_text") or topic
        if v_type == "hook":
            headline = elems.get("headline") or f"WHAT HAPPENS WHEN {topic.upper()} EXECUTES?"
            subtext = elems.get("subtext") or "Most developers assume they know. Look inside the machine."
            badge = elems.get("badge") or topic.upper()
        elif v_type == "payoff":
            headline = elems.get("headline") or f"THE DEFINITIVE RULE OF {topic.upper()}."
            subtext = elems.get("secondary_text") or "Deterministic system execution."
            badge = "SENIOR INVARIANT"
        else:
            words = raw_narration.split()
            headline = " ".join(words[:6]).upper() if words else f"{topic.upper()} ARCHITECTURE"
            subtext = " ".join(words[6:18]) if len(words) > 6 else f"Core execution model for {topic}."
            badge = beat_name.upper().replace("_", " ")

        typography_cfg = TypographyBehaviorConfig(
            mode="word_by_word" if strategy.id in ("kinetic_typography", "brutalist") else "line_by_line",
            headline=headline,
            subtext=subtext,
            badge=badge,
            font_size=74 if len(headline) < 30 else 58,
            letter_spacing="-0.02em",
            case="uppercase" if strategy.id in ("brutalist", "kinetic_typography", "technical_blueprint") else "title",
            stagger_frames=3,
            highlight_word_indices=[1, 3] if len(headline.split()) > 3 else [0]
        )

        # ── 5. Primary & Secondary Subject Layering (Content-Aware Semantic Synthesis)
        primary_subject, secondary_subjects = self._synthesize_subject_layers(
            v_type=v_type,
            topic=topic,
            analysis=analysis,
            strategy=strategy,
            template=template,
            elems=elems,
            tech_summary=tech_summary,
            code_assets=code_assets,
            idx=idx
        )

        # ── 6. Pacing & Rhythm Contrast ───────────────────────────────────────
        if dur_t <= 3.5:
            pacing_style = "rapid_burst"
        elif dur_t >= 8.0:
            pacing_style = "long_hold"
        elif move_style == "still":
            pacing_style = "stillness"
        else:
            pacing_style = "major_movement"

        # ── 7. Continuous Visual Carry Relationship ──────────────────────────
        carry_rel = self._formulate_carry_relationship(
            idx=idx,
            num_scenes=num_scenes,
            v_type=v_type,
            topic=topic,
            primary_subject=primary_subject
        )

        recipe = VisualRecipe(
            scene_id=scene.get("id", f"scene_{idx+1}"),
            beat_name=beat_name,
            start_time=start_t,
            end_time=end_t,
            duration_sec=dur_t,
            template_id=template.id,
            composition=comp_style,
            anchor=anchor,
            layout_grammar={
                "grid_columns": 12 if strategy.category in ("editorial", "minimal") else 8,
                "composition_variant": comp_variant,
                "asymmetry_offset_px": 60 if "asymmetric" in comp_style else 0,
                "negative_space_ratio": 0.35 if strategy.id == "swiss_minimal" else 0.18,
            },
            camera=camera_traj,
            primitives=primitives_cfg,
            typography=typography_cfg,
            primary_subject=primary_subject,
            secondary_subjects=secondary_subjects,
            background_style=template.background_style,
            lighting_depth=template.lighting_depth,
            pacing_style=pacing_style,
            carry=carry_rel
        )

        return recipe, cam_end, comp_variant

    def _select_composition_variant(
        self,
        v_type: str,
        strategy: VisualStrategy,
        idx: int,
        analysis: TopicAnalysis
    ) -> str:
        """Assigns intentional, diverse composition variants per scene type."""
        if v_type == "hook":
            variants = ["editorial_left", "giant_type", "split", "terminal", "visual_first", "cinematic", "centered"]
            if strategy.id in ("terminal_story", "retro_computing"):
                return "terminal"
            elif strategy.id in ("kinetic_typography", "brutalist"):
                return "giant_type"
            elif strategy.id in ("editorial_grid", "magazine_editorial"):
                return "editorial_left"
            elif analysis.modalities.get("involves_comparison"):
                return "split"
            elif strategy.id in ("cinematic_diagram", "abstract_motion"):
                return "visual_first"
            return variants[idx % len(variants)]

        elif v_type == "code":
            variants = ["split_execution", "terminal_stream", "diff_comparison", "minimal_floating", "centered_window"]
            if strategy.id in ("terminal_story", "retro_computing"):
                return "terminal_stream"
            elif analysis.modalities.get("involves_comparison"):
                return "diff_comparison"
            elif strategy.id == "code_first":
                return "split_execution"
            elif strategy.id in ("minimal_swiss", "brutalist"):
                return "minimal_floating"
            return variants[idx % len(variants)]

        elif v_type == "diagram":
            variants = ["radial_system", "horizontal_flow", "grid_matrix", "metric_breakdown", "vertical_pipeline"]
            if strategy.id in ("system_architecture", "cinematic_diagram"):
                return "radial_system"
            elif strategy.id == "data_visualization":
                return "metric_breakdown"
            elif strategy.id in ("technical_blueprint", "editorial_grid"):
                return "grid_matrix"
            elif analysis.category == "networking_distributed":
                return "horizontal_flow"
            return variants[idx % len(variants)]

        elif v_type == "metaphor":
            variants = ["volumetric_stage", "split_analog", "interactive_gate", "kinetic_focus"]
            if analysis.category in ("devops_cloud_infra", "operating_systems_lowlevel"):
                return "volumetric_stage"
            elif analysis.category in ("networking_distributed", "web_frontend"):
                return "split_analog"
            elif analysis.modalities.get("involves_code"):
                return "interactive_gate"
            return variants[idx % len(variants)]

        elif v_type in ("payoff", "conclusion"):
            variants = ["callback_anchor", "split_benchmark", "compression_singularity", "editorial_quote", "kinetic_words"]
            if strategy.id in ("kinetic_typography", "brutalist"):
                return "kinetic_words"
            elif analysis.modalities.get("involves_comparison"):
                return "split_benchmark"
            elif strategy.id in ("editorial_grid", "magazine_editorial"):
                return "editorial_quote"
            elif strategy.id == "technical_blueprint":
                return "compression_singularity"
            return variants[idx % len(variants)]

        elif v_type in ("benchmark", "split"):
            variants = ["split_contrast", "dual_meter", "speedup_bar"]
            return variants[idx % len(variants)]

        elif v_type == "math_3d":
            variants = ["isometric_surface", "orbit_equation", "vector_field"]
            return variants[idx % len(variants)]

        return "centered"

    def _synthesize_subject_layers(
        self,
        v_type: str,
        topic: str,
        analysis: TopicAnalysis,
        strategy: VisualStrategy,
        template: MotionTemplateSpec,
        elems: Dict[str, Any],
        tech_summary: Dict[str, Any],
        code_assets: Dict[str, Any],
        idx: int
    ) -> tuple[SubjectLayer, List[SubjectLayer]]:
        """
        Content-Aware Generative Subject Layer Synthesis.
        Infers the best graphical primitive from topic category, intent, modalities,
        and technical facts — NEVER relying solely on fixed keyword matching.
        """
        cat = analysis.category
        modalities = analysis.modalities
        secondary: List[SubjectLayer] = []

        # ── 1. Category & Modality Driven Subject Inference ──────────────────
        t_low = topic.lower()
        if any(k in t_low for k in ["if-else", "if else", "branch", "condition", "switch"]) or v_type == "branching_logic":
            subj_type = "branching_gate"
            subj_props = {
                "condition_expr": "x > 10" if "if" in t_low else "state.ready == true",
                "left_branch": "TRUE: Direct Branch Target",
                "right_branch": "FALSE: Fallthrough Bypass",
                "active_path": "TRUE" if idx % 2 == 0 else "FALSE",
                "hardware_cycle": "1 CPU branch cycle"
            }

        elif modalities.get("involves_mathematics") or cat == "math_theoretical":
            subj_type = "math_surface_3d"
            subj_props = {
                "formula": elems.get("equation_latex") or "$f(x, y) = \\sin(x) \\cdot \\cos(y)$",
                "formula_title": elems.get("formula_title") or f"{topic.upper()} MANIFOLD",
                "mesh_resolution": 36,
                "wireframe": True,
                "color_gradient": ["#00F0FF", "#8B5CF6", "#F59E0B"]
            }

        elif cat in ("system_architecture", "devops_cloud_infra"):
            if any(k in t_low for k in ["docker", "container", "layer", "stack", "volume", "image"]) or (v_type in ("metaphor", "diagram") and (idx % 2 == 0)):
                subj_type = "spatial_layer_stack"
                steps = tech_summary.get("how_it_works_steps") or ["Ingress Gateway", "Microservice Mesh", "Persistent Store", "Telemetry Daemon"]
                subj_props = {
                    "stack_title": f"{topic.upper()} VOLUMETRIC STACK",
                    "layers": [str(s)[:32] for s in steps[:4]],
                    "active_layer_index": min(3, idx),
                    "status": "RUNNING_ACTIVE",
                    "metric": tech_summary.get("diagram_metric_val", "100k req/s")
                }
            else:
                subj_type = "nodes_graph"
                subj_props = {
                    "network_title": f"{topic.upper()} CLUSTER TOPOLOGY",
                    "nodes": ["INGRESS", "CONTROLLER", "REPLICA_POOL", "STORAGE_RAFT"],
                    "edges": [("INGRESS", "CONTROLLER"), ("CONTROLLER", "REPLICA_POOL"), ("REPLICA_POOL", "STORAGE_RAFT")],
                    "active_node_index": idx % 4,
                    "throughput": tech_summary.get("diagram_metric_val", "0.2ms latency")
                }

        elif cat == "networking_distributed":
            if any(k in t_low for k in ["api", "rest", "http", "endpoint", "graphql", "crud"]):
                subj_type = "ui_panel"
                subj_props = {
                    "endpoint": f"/api/v1/{topic.lower().replace(' ', '_')[:16]}",
                    "method": "GET" if idx % 2 == 0 else "POST",
                    "latency_ms": 14.5,
                    "status_code": 200,
                    "pipeline_stages": ["SOCKET_READ", "TLS_DECRYPT", "PAYLOAD_PARSE", "ASYNC_DISPATCH"]
                }
            else:
                subj_type = "stream_flow"
                subj_props = {
                    "endpoint": f"/api/v1/{topic.lower().replace(' ', '_')[:16]}",
                    "method": "GET" if idx % 2 == 0 else "POST",
                    "packet_count": 8,
                    "latency_ms": 14.5,
                    "status_code": 200,
                    "pipeline_stages": ["SOCKET_READ", "TLS_DECRYPT", "PAYLOAD_PARSE", "ASYNC_DISPATCH"]
                }

        elif cat in ("algorithms_data_structures", "database_storage"):
            if modalities.get("involves_comparison") or v_type in ("split", "benchmark"):
                subj_type = "metrics_chart"
                subj_props = {
                    "chart_title": f"{topic.upper()} PERFORMANCE DIVERGENCE",
                    "categories": ["Naive Execution", "Optimized Reality"],
                    "values": [840, 24],
                    "unit": "ms",
                    "speedup": "35x Faster",
                    "complexity": tech_summary.get("time_complexity", "O(log N)")
                }
            else:
                subj_type = "data_partition"
                subj_props = {
                    "array_elements": [3, 8, 14, 21, 28, 35, 42, 59, 73, 91, 105],
                    "target_val": 42,
                    "mid_idx": 6,
                    "search_step": idx + 1,
                    "complexity_stat": tech_summary.get("time_complexity", "O(log N) Time"),
                    "algorithm_name": topic.title()
                }

        elif cat in ("operating_systems_lowlevel", "language_runtime_internals"):
            if v_type == "code":
                subj_type = "code_stream"
                default_code = f"// {topic} execution\n" + "function execute() {\n  return invariant;\n}"
                raw_code = code_assets.get("main_code") or default_code
                lines = raw_code.split("\n") if isinstance(raw_code, str) else raw_code
                subj_props = {
                    "filename": code_assets.get("filename", "runtime_kernel.c"),
                    "lines": lines[:8],
                    "highlight_line": code_assets.get("highlight_line", 3),
                    "annotation": code_assets.get("annotation", "1 CPU cycle branch commit"),
                    "output_text": code_assets.get("terminal_output", "> Execution verified [OK]")
                }
            elif v_type == "metaphor":
                subj_type = "branching_gate"
                subj_props = {
                    "condition_expr": "state.ready == true",
                    "left_branch": "PATH A: FAST IN-MEMORY COMMIT",
                    "right_branch": "PATH B: SLOW PAGE FAULT BYPASS",
                    "active_path": "TRUE" if idx % 2 == 0 else "FALSE",
                    "hardware_cycle": "1 CPU branch cycle"
                }
            else:
                subj_type = "timeline_steps"
                steps = tech_summary.get("how_it_works_steps") or ["Instruction Decode", "Cache Line Lookup", "ALU Execution", "Writeback"]
                subj_props = {
                    "timeline_title": f"{topic.upper()} PIPELINE",
                    "steps": [str(s)[:36] for s in steps[:4]],
                    "active_step_index": min(3, idx),
                    "cycle_time": tech_summary.get("diagram_metric_val", "1 Cycle (0.3ns)")
                }

        elif cat in ("security_cryptography", "web_frontend"):
            subj_type = "terminal_trace"
            subj_props = {
                "command": f"$ verify --target '{topic.lower()}'",
                "buffer_lines": [
                    f"> Initializing {topic} security perimeter...",
                    "> Cryptographic invariant: SECURE [256-bit]",
                    "> Zero-knowledge proof verified in 0.04ms"
                ],
                "exit_status": "EXIT_SUCCESS 0"
            }

        else: # General semantic fallback matching visual strategy
            if strategy.category == "typography":
                subj_type = "kinetic_typography"
                subj_props = {
                    "emphasis_word": topic.split()[-1].upper(),
                    "sub_tokens": ["INVARIANT", "FOUNDATION", "SYSTEM", "ARCHITECTURE"]
                }
            elif strategy.category == "editorial":
                subj_type = "timeline_steps"
                subj_props = {
                    "timeline_title": f"{topic.upper()} CHRONOLOGY",
                    "steps": tech_summary.get("how_it_works_steps", ["Genesis", "Constraint", "Breakthrough", "Standard"])[:4],
                    "active_step_index": idx % 4
                }
            else:
                subj_type = "nodes_graph"
                subj_props = {
                    "network_title": f"{topic.upper()} CONCEPT NETWORK",
                    "nodes": ["ORIGIN", "TRANSFORM", "INVARIANT"],
                    "active_node_index": idx % 3
                }

        primary_layer = SubjectLayer(
            type=subj_type,
            layer_id="primary_focal_subject",
            z_index=2,
            depth_plane="midground",
            properties=subj_props
        )

        # Secondary HUD & telemetry layer
        secondary.append(SubjectLayer(
            type="hud_telemetry",
            layer_id="sec_telemetry_hud",
            z_index=3,
            depth_plane="foreground",
            properties={
                "tag": f"FPS: 60 | BEAT: {idx+1}/{elems.get('beat', 'MAIN')}",
                "status": "LOCK",
                "strategy": strategy.name
            }
        ))

        return primary_layer, secondary

    def _formulate_carry_relationship(
        self,
        idx: int,
        num_scenes: int,
        v_type: str,
        topic: str,
        primary_subject: SubjectLayer
    ) -> Optional[CarryRelationship]:
        """Defines the surviving element that carries across to the next beat."""
        if idx >= num_scenes - 1:
            return None

        transforms = [
            ("headline_token", "expand", "line_to_path", "diagram_root_node"),
            ("diagram_root_node", "morph", "expand", "spatial_system_cluster"),
            ("spatial_system_cluster", "reshape", "card_to_screen", "active_ui_workspace"),
            ("active_ui_workspace", "collapse", "object_to_text", "final_monolith_statement"),
        ]
        t_spec = transforms[min(idx, len(transforms) - 1)]

        return CarryRelationship(
            carrier_element_id=f"carrier_elem_{idx}_{t_spec[0]}",
            entry_primitive=t_spec[1],
            exit_primitive=t_spec[2],
            morph_target=t_spec[3],
            surviving_properties=["color", "position", "velocity_vector"]
        )
