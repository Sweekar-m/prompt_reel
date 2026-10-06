"""
agents/shot_designer_agent.py
=============================
Shot Designer Agent for Prompt Reel.
Operates between Storyboard Assembly and the Render Engine.

Pipeline Stage:
CONTENT -> SCRIPT -> CREATIVE DIRECTION -> STORYBOARD -> [SHOT DESIGNER] -> VISUAL RECIPES -> CONTINUITY -> REMOTION -> QC

Mandate:
- Eliminates "animated presentation slides" and monotonous centered card layouts.
- Decides HOW every idea is visualized as a professional motion-graphics film.
- Produces rich VisualRecipes with varied compositions, 3D camera travel, motion primitives,
  typography behaviors, depth planes, and continuous visual carries.
"""
import hashlib
from typing import Dict, Any, List, Optional
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
        Enhances an existing motion plan by generating rich, renderable Visual Recipes
        for every beat in the storyboard.
        """
        topic = motion_plan.get("topic", "Software Architecture")
        creative_dir = creative_dir or motion_plan.get("creative_direction", {})
        scenes = motion_plan.get("scenes", [])
        total_duration = motion_plan.get("duration", 50.0)

        # 1. Resolve Motion Template System
        style_id = creative_dir.get("style_id")
        template_id = requested_template_id or creative_dir.get("motion_template_id")
        if not template_id:
            # Map legacy styles or topic to high-end motion template
            template = select_best_template_for_topic(topic, requested_style=style_id)
        else:
            template = get_motion_template(template_id)

        # Record chosen template in creative direction
        creative_dir["motion_template"] = template.to_dict()
        creative_dir["motion_template_id"] = template.id

        # 2. Continuous Camera Trajectory Accumulator
        # Starts at initial composition coordinates and flows continuously across beats
        curr_cam = CameraWaypoint(x=0.0, y=0.0, z=0.0, pitch=0.0, yaw=0.0, roll=0.0, scale=1.0)

        # 3. Design each beat as an expressive motion shot
        designed_scenes = []
        num_scenes = len(scenes)

        for idx, scene in enumerate(scenes):
            recipe, curr_cam = self._design_scene_recipe(
                scene=scene,
                idx=idx,
                num_scenes=num_scenes,
                topic=topic,
                template=template,
                curr_cam=curr_cam,
                tech_summary=motion_plan.get("technical_summary", {}),
                code_assets=motion_plan.get("code_assets", {})
            )
            scene["visual_recipe"] = recipe.to_dict()
            scene["visual_recipe_obj"] = recipe
            designed_scenes.append(scene)

        motion_plan["scenes"] = designed_scenes
        motion_plan["shot_designer_version"] = "3.0"
        motion_plan["motion_template"] = template.to_dict()

        return motion_plan

    def _design_scene_recipe(
        self,
        scene: Dict[str, Any],
        idx: int,
        num_scenes: int,
        topic: str,
        template: MotionTemplateSpec,
        curr_cam: CameraWaypoint,
        tech_summary: Dict[str, Any],
        code_assets: Dict[str, Any]
    ) -> tuple[VisualRecipe, CameraWaypoint]:
        """Designs a customized VisualRecipe for a single storyboard beat."""
        v_type = scene.get("visual_type", "metaphor")
        beat_name = scene.get("beat_name", f"beat_{idx+1}")
        start_t = float(scene.get("start", 0.0))
        end_t = float(scene.get("end", start_t + 5.0))
        dur_t = float(scene.get("duration", end_t - start_t))
        elems = scene.get("elements", {})

        # ── 1. Dynamic Composition Variety ────────────────────────────────────
        # Rotates through non-centered, dynamic compositions matching the template
        possible_comps = template.composition_styles
        # Intentionally alternate compositions across beats to eliminate slideshow monotony
        comp_style = possible_comps[idx % len(possible_comps)]

        # Determine geometric anchor based on composition
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

        # ── 2. Continuous Camera Trajectory ──────────────────────────────────
        # Avoids resetting to (0,0) every scene! Camera flows from previous endpoint
        cam_start = CameraWaypoint(
            x=curr_cam.x,
            y=curr_cam.y,
            z=curr_cam.z,
            pitch=curr_cam.pitch,
            yaw=curr_cam.yaw,
            roll=curr_cam.roll,
            scale=curr_cam.scale
        )

        # Calculate camera movement according to template camera grammar
        allowed_moves = template.camera_grammar.get("allowed_moves", ["push", "pan", "drift"])
        cam_move = allowed_moves[idx % len(allowed_moves)]

        # Stillness holds for intentional rhythm contrast
        if cam_move == "still" or (idx == 1 and template.camera_grammar.get("stillness_ratio", 0) > 0.3):
            cam_move = "still"
            cam_end = CameraWaypoint(
                x=cam_start.x,
                y=cam_start.y,
                z=cam_start.z,
                pitch=cam_start.pitch,
                yaw=cam_start.yaw,
                roll=cam_start.roll,
                scale=cam_start.scale
            )
            blur_intensity = 0.0
        elif cam_move == "push":
            cam_end = CameraWaypoint(
                x=cam_start.x + (25 if idx % 2 == 0 else -25),
                y=cam_start.y,
                z=cam_start.z + 180,
                pitch=cam_start.pitch + 2.5,
                yaw=cam_start.yaw,
                roll=cam_start.roll,
                scale=cam_start.scale * 1.08
            )
            blur_intensity = 0.18
        elif cam_move == "pan":
            delta_x = 90 if idx % 2 == 0 else -90
            cam_end = CameraWaypoint(
                x=cam_start.x + delta_x,
                y=cam_start.y + (15 if delta_x > 0 else -15),
                z=cam_start.z,
                pitch=cam_start.pitch,
                yaw=cam_start.yaw + (4.0 if delta_x > 0 else -4.0),
                roll=cam_start.roll + (1.2 if delta_x > 0 else -1.2),
                scale=cam_start.scale
            )
            blur_intensity = 0.28
        elif cam_move == "orbit":
            cam_end = CameraWaypoint(
                x=cam_start.x + 40,
                y=cam_start.y - 30,
                z=cam_start.z + 100,
                pitch=cam_start.pitch + 8.0,
                yaw=cam_start.yaw + 16.0,
                roll=cam_start.roll,
                scale=cam_start.scale * 1.04
            )
            blur_intensity = 0.35
        elif cam_move == "whip":
            cam_end = CameraWaypoint(
                x=cam_start.x - 140,
                y=cam_start.y,
                z=cam_start.z,
                pitch=cam_start.pitch,
                yaw=cam_start.yaw - 8.0,
                roll=cam_start.roll - 3.0,
                scale=cam_start.scale
            )
            blur_intensity = 0.60
        else: # drift
            cam_end = CameraWaypoint(
                x=cam_start.x + 20,
                y=cam_start.y - 15,
                z=cam_start.z + 40,
                pitch=cam_start.pitch + 1.0,
                yaw=cam_start.yaw + 2.0,
                roll=cam_start.roll,
                scale=cam_start.scale * 1.02
            )
            blur_intensity = 0.10

        camera_traj = CameraTrajectory(
            start=cam_start,
            end=cam_end,
            motion_style=cam_move,
            motion_blur=blur_intensity,
            easing="cubic_out" if cam_move != "still" else "linear"
        )

        # ── 3. Visual Motion Primitives ──────────────────────────────────────
        mg = template.motion_grammar
        primitives_cfg = VisualPrimitivesConfig(
            enter=mg.get("enter_primitive", "spring"),
            move=mg.get("move_primitive", "drift"),
            transform=mg.get("transform_primitive", "expand"),
            impact=mg.get("impact_primitive", "shake"),
            exit=template.transition_grammar[idx % len(template.transition_grammar)]
        )

        # ── 4. Typography as Motion-Design Object ─────────────────────────────
        tg = template.typography_grammar
        raw_narration = scene.get("narration") or scene.get("voice_text") or topic

        # Derive punchy kinetic headline & subtext
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
            mode=tg.get("mode", "word_by_word"),
            headline=headline,
            subtext=subtext,
            badge=badge,
            font_size=tg.get("max_font_size", 76),
            letter_spacing="-0.02em" if tg.get("case") == "uppercase" else "-0.01em",
            case=tg.get("case", "uppercase"),
            stagger_frames=tg.get("stagger_frames", 3),
            highlight_word_indices=[1, 3] if len(headline.split()) > 3 else [0]
        )

        # ── 5. Primary & Secondary Subject Layering ───────────────────────────
        primary_subject, secondary_subjects = self._synthesize_subject_layers(
            v_type=v_type,
            topic=topic,
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
        elif cam_move == "still":
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
                "grid_columns": 12 if template.id in ("minimal_swiss", "kinetic_editorial") else 8,
                "asymmetry_offset_px": 60 if "asymmetric" in comp_style else 0,
                "negative_space_ratio": 0.35 if template.visual_density == "stark_minimal" else 0.18,
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

        return recipe, cam_end

    def _synthesize_subject_layers(
        self,
        v_type: str,
        topic: str,
        template: MotionTemplateSpec,
        elems: Dict[str, Any],
        tech_summary: Dict[str, Any],
        code_assets: Dict[str, Any],
        idx: int
    ) -> tuple[SubjectLayer, List[SubjectLayer]]:
        """
        Builds contextual, rich graphic subjects instead of defaulting to a code card:
        - Java if-else: Branching decision tree gate + boolean state comparator
        - Docker: Container block layers + Union filesystem stack + isolated network port
        - Binary search: Array partition segments + spatial search pointer + log N counter
        - REST API: HTTP request/response pipeline + method token + packet telemetry
        - Java OOP: Heap memory blueprint + instance instantiation block
        """
        t = topic.lower()
        secondary = []

        # 1. Topic & Metaphor Tailoring
        if any(k in t for k in ["if", "else", "branch", "condition"]):
            subj_type = "branching_logic"
            subj_props = {
                "condition_expr": "x > 10",
                "left_branch": "TRUE: EXECUTE_PRIMARY_BLOCK",
                "right_branch": "FALSE: JUMP_TO_ELSE",
                "active_path": "TRUE" if idx % 2 == 0 else "FALSE",
                "hardware_cycle": "1 CPU branch cycle",
                "gate_nodes": ["FETCH", "COMPARE", "BRANCH_TARGET"]
            }
        elif any(k in t for k in ["docker", "container", "layer", "image"]):
            subj_type = "spatial_3d_mesh" if template.id == "spatial_3d_explainer" else "diagram_network"
            subj_props = {
                "layers": ["Base OS (Debian Slim)", "Runtime (OpenJDK 21)", "App Artifact (app.jar)", "Writable Container Layer"],
                "active_layer_index": min(3, idx),
                "mount_points": ["/var/run/docker.sock", "/app/data"],
                "status": "CONTAINER_RUNNING",
                "isolation_metric": "Namespace & Cgroup Encapsulated"
            }
        elif any(k in t for k in ["binary search", "search", "partition", "sort"]):
            subj_type = "data_flow"
            subj_props = {
                "array_elements": [2, 7, 12, 19, 24, 38, 45, 56, 71, 88, 93],
                "left_idx": 0,
                "right_idx": 10,
                "mid_idx": 5,
                "target_val": 45,
                "search_step": idx + 1,
                "eliminated_range": "0..4" if idx > 0 else "none",
                "complexity_stat": "O(log N) Time"
            }
        elif any(k in t for k in ["api", "rest", "http", "network"]):
            subj_type = "ui_panel" if template.id == "dynamic_product_ui" else "diagram_network"
            subj_props = {
                "endpoint": "/api/v1/resources",
                "method": "GET" if idx % 2 == 0 else "POST",
                "status_code": 200,
                "latency_ms": 14.2,
                "headers": {"Content-Type": "application/json", "Authorization": "Bearer ***"},
                "response_payload": {"id": "res_8492", "status": "active", "throughput": "100k req/s"}
            }
        elif any(k in t for k in ["oop", "object", "class", "heap"]):
            subj_type = "spatial_3d_mesh" if template.id == "spatial_3d_explainer" else "branching_logic"
            subj_props = {
                "class_name": "AccountService",
                "heap_address": "0x7F9B2004",
                "fields": ["id: UUID", "balance: BigDecimal", "owner: UserRef"],
                "vtable_methods": ["deposit()", "withdraw()", "audit()"],
                "allocation_space": "Eden Space -> Tenured Generation"
            }
        else:
            # General motion system mapping according to template
            if template.id == "kinetic_editorial":
                subj_type = "kinetic_typography"
                subj_props = {"emphasis_word": topic.split()[-1].upper(), "sub_tokens": ["INVARIANT", "EXECUTION", "SYSTEM"]}
            elif template.id == "technical_blueprint":
                subj_type = "diagram_network"
                subj_props = {"schematic_title": f"{topic.upper()} SCHEMATIC", "nodes": ["INPUT", "TRANSFORM", "OUTPUT"], "tolerance": "±0.001ms"}
            elif template.id == "spatial_3d_explainer":
                subj_type = "spatial_3d_mesh"
                subj_props = {"formula": "$f(x, y) = \\sin(x) \\cos(y)$", "mesh_resolution": 32, "wireframe": True}
            elif template.id == "terminal_motion":
                subj_type = "code_stream"
                subj_props = {"command": f"$ ./inspect --trace '{topic}'", "buffer_lines": ["> Loading symbols... [OK]", "> Allocation verified: 0x0040", f"> Executing {topic} logic"]}
            else:
                subj_type = "ui_panel"
                subj_props = {"panel_title": topic.upper(), "metric_value": "99.99% INVARIANT", "system_state": "OPTIMAL"}

        primary_layer = SubjectLayer(
            type=subj_type,
            layer_id="primary_focal_subject",
            z_index=2,
            depth_plane="midground",
            properties=subj_props
        )

        # Secondary supporting layers (Floating HUD tokens, dimensional dimension lines)
        secondary.append(SubjectLayer(
            type="hud_telemetry",
            layer_id="sec_telemetry_hud",
            z_index=3,
            depth_plane="foreground",
            properties={"tag": f"FPS: 60 | BEAT: {idx+1}/{elems.get('beat', 'MAIN')}", "status": "LOCK"}
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
            return None # Final shot completes the visual mark

        # Continuous transformations:
        # text -> line -> diagram -> node network -> UI panel -> final truth
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
