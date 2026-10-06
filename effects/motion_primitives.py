"""
effects/motion_primitives.py
============================
Original Reusable Motion Primitives Library for Prompt Reel.
Inspired by modern motion-design engineering principles (e.g. Jitter, OneTake, Moonb).

Covers the full taxonomy of motion primitives:
1. ENTER: How elements materialize into the visual space.
2. MOVE: How elements travel, accelerate, and interact while active.
3. TRANSFORM: How elements mutate into new visual forms across beats.
4. IMPACT: How physical forces, weight, and energetic accents manifest.
5. EXIT: How elements depart or clear the frame for incoming visual energy.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class MotionPrimitiveSpec:
    id: str
    category: str               # "enter", "move", "transform", "impact", "exit"
    name: str
    description: str
    default_easing: str         # "spring_snappy", "cubic_out", "elastic_out", "expo_inout", "linear"
    typical_duration_frames: int
    physics_params: Dict[str, Any]
    css_transform_template: str
    svg_filter_needed: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ── 1. ENTER PRIMITIVES ───────────────────────────────────────────────────────
ENTER_PRIMITIVES: Dict[str, MotionPrimitiveSpec] = {
    "spring": MotionPrimitiveSpec(
        id="spring",
        category="enter",
        name="Dynamic Spring Overshoot",
        description="Physical harmonic oscillator entry with tailored damping and mass.",
        default_easing="spring_snappy",
        typical_duration_frames=18,
        physics_params={"mass": 0.8, "damping": 12, "stiffness": 170},
        css_transform_template="scale({scale}) translateY({ty}px)",
    ),
    "slide": MotionPrimitiveSpec(
        id="slide",
        category="enter",
        name="Directional Kinetic Slide",
        description="High-velocity directional entry from off-screen or viewport margin.",
        default_easing="cubic_out",
        typical_duration_frames=14,
        physics_params={"distance_px": 280, "angle_deg": 0},
        css_transform_template="translate3d({tx}px, {ty}px, 0)",
    ),
    "scale": MotionPrimitiveSpec(
        id="scale",
        category="enter",
        name="Depth Scale Pop",
        description="Expands outward from zero with punchy acceleration.",
        default_easing="cubic_out",
        typical_duration_frames=16,
        physics_params={"start_scale": 0.15, "end_scale": 1.0},
        css_transform_template="scale({scale})",
    ),
    "overshoot": MotionPrimitiveSpec(
        id="overshoot",
        category="enter",
        name="Elastic Overshoot",
        description="Scales past 100% (e.g. 1.08x) before settling into rigid geometry.",
        default_easing="elastic_out",
        typical_duration_frames=20,
        physics_params={"overshoot_peak": 1.08, "settle_time": 0.6},
        css_transform_template="scale({scale})",
    ),
    "elastic": MotionPrimitiveSpec(
        id="elastic",
        category="enter",
        name="Liquid Elastic Pop",
        description="Under-damped oscillating rubber entry for playful or vibrant accents.",
        default_easing="elastic_out",
        typical_duration_frames=24,
        physics_params={"mass": 1.1, "damping": 9, "stiffness": 140},
        css_transform_template="scale({scale}) rotate({rot}deg)",
    ),
    "masked_reveal": MotionPrimitiveSpec(
        id="masked_reveal",
        category="enter",
        name="Geometric Mask Reveal",
        description="Reveals through a sharp architectural clipping rect or diagonal wipe.",
        default_easing="expo_inout",
        typical_duration_frames=16,
        physics_params={"clip_direction": "horizontal", "feather_px": 0},
        css_transform_template="clip-path: inset({top}% {right}% {bottom}% {left}%)",
    ),
    "clip_reveal": MotionPrimitiveSpec(
        id="clip_reveal",
        category="enter",
        name="Container Clip Expand",
        description="Inner content rises from behind an invisible baseline clipping plane.",
        default_easing="cubic_out",
        typical_duration_frames=15,
        physics_params={"offset_y": 120},
        css_transform_template="translateY({ty}px)",
    ),
    "type_on": MotionPrimitiveSpec(
        id="type_on",
        category="enter",
        name="Kinetic Type-On",
        description="Characters or words populate with micro-staggers and glowing caret.",
        default_easing="linear",
        typical_duration_frames=25,
        physics_params={"char_delay_frames": 1.5, "cursor_blink_hz": 4},
        css_transform_template="opacity: {opacity}",
    ),
    "blur_reveal": MotionPrimitiveSpec(
        id="blur_reveal",
        category="enter",
        name="Optical Blur In",
        description="Dissolves from deep lens blur (24px) to razor-sharp crisp vector.",
        default_easing="cubic_out",
        typical_duration_frames=18,
        physics_params={"max_blur_px": 24, "scale_start": 0.92},
        css_transform_template="filter: blur({blur}px); scale({scale})",
        svg_filter_needed="feGaussianBlur",
    ),
    "path_reveal": MotionPrimitiveSpec(
        id="path_reveal",
        category="enter",
        name="Vector Stroke Path Draw",
        description="Draws vector schematics, graphs, or branching trees via SVG stroke-dashoffset.",
        default_easing="expo_inout",
        typical_duration_frames=22,
        physics_params={"stroke_speed_factor": 1.2},
        css_transform_template="stroke-dashoffset: {dashoffset}",
    ),
}

# ── 2. MOVE PRIMITIVES ────────────────────────────────────────────────────────
MOVE_PRIMITIVES: Dict[str, MotionPrimitiveSpec] = {
    "drift": MotionPrimitiveSpec(
        id="drift",
        category="move",
        name="Continuous Ambient Drift",
        description="Subtle, living spatial translation to keep visual planes dynamic.",
        default_easing="linear",
        typical_duration_frames=90,
        physics_params={"speed_x": 0.4, "speed_y": -0.2, "subtle_tilt": 0.5},
        css_transform_template="translate3d({tx}px, {ty}px, 0)",
    ),
    "orbit": MotionPrimitiveSpec(
        id="orbit",
        category="move",
        name="Radial Orbit Rotation",
        description="Circulates around a central visual focal point or coordinate anchor.",
        default_easing="linear",
        typical_duration_frames=120,
        physics_params={"radius_px": 180, "rpm": 4.5},
        css_transform_template="rotate({deg}deg) translate({r}px) rotate({neg_deg}deg)",
    ),
    "follow": MotionPrimitiveSpec(
        id="follow",
        category="move",
        name="Target Tracking Follow",
        description="Follows a lead trajectory or parent element with damped latency.",
        default_easing="spring_snappy",
        typical_duration_frames=30,
        physics_params={"lag_frames": 4, "damping_ratio": 0.85},
        css_transform_template="translate3d({tx}px, {ty}px, 0)",
    ),
    "magnetic": MotionPrimitiveSpec(
        id="magnetic",
        category="move",
        name="Magnetic Core Attraction",
        description="Snaps toward a target position with inverse-square acceleration.",
        default_easing="cubic_out",
        typical_duration_frames=18,
        physics_params={"gravity_strength": 1.4, "snap_distance_px": 450},
        css_transform_template="translate3d({tx}px, {ty}px, 0) scale({scale})",
    ),
    "acceleration": MotionPrimitiveSpec(
        id="acceleration",
        category="move",
        name="Exponential Surge Forward",
        description="Starts slow and rockets across the screen with aggressive speed.",
        default_easing="cubic_in",
        typical_duration_frames=20,
        physics_params={"peak_velocity_px_s": 2400},
        css_transform_template="translate3d({tx}px, {ty}px, 0)",
    ),
    "deceleration": MotionPrimitiveSpec(
        id="deceleration",
        category="move",
        name="Inertial Friction Deceleration",
        description="High-speed arrival sliding into a precise mathematical stop.",
        default_easing="cubic_out",
        typical_duration_frames=22,
        physics_params={"friction_coeff": 0.88},
        css_transform_template="translate3d({tx}px, {ty}px, 0)",
    ),
    "parallax": MotionPrimitiveSpec(
        id="parallax",
        category="move",
        name="Multi-Plane Depth Parallax",
        description="Layers translate at staggered velocity ratios (0.2x bg, 1.0x mid, 1.6x fg).",
        default_easing="linear",
        typical_duration_frames=60,
        physics_params={"depth_ratios": [0.25, 0.6, 1.0, 1.45]},
        css_transform_template="translate3d({tx}px, {ty}px, {tz}px)",
    ),
    "depth_push": MotionPrimitiveSpec(
        id="depth_push",
        category="move",
        name="Z-Axis Spatial Tunnel Dive",
        description="Pushes directly through the Z plane toward or past the camera lens.",
        default_easing="expo_inout",
        typical_duration_frames=28,
        physics_params={"start_z": -600, "end_z": 400},
        css_transform_template="translate3d(0, 0, {tz}px) scale({scale})",
    ),
    "camera_follow": MotionPrimitiveSpec(
        id="camera_follow",
        category="move",
        name="Dynamic Camera Framing",
        description="Camera tracks the primary moving subject, keeping it in active frame balance.",
        default_easing="cubic_out",
        typical_duration_frames=45,
        physics_params={"smooth_factor": 0.82},
        css_transform_template="translate3d({cam_x}px, {cam_y}px, {cam_z}px)",
    ),
}

# ── 3. TRANSFORM PRIMITIVES ──────────────────────────────────────────────────
TRANSFORM_PRIMITIVES: Dict[str, MotionPrimitiveSpec] = {
    "morph": MotionPrimitiveSpec(
        id="morph",
        category="transform",
        name="Vector Contour Morph",
        description="Continuous cubic bezier deformation from Shape A into Shape B.",
        default_easing="expo_inout",
        typical_duration_frames=20,
        physics_params={"vertex_count": 8, "subdivision_blend": True},
        css_transform_template="d: path('{svg_path}')",
    ),
    "reshape": MotionPrimitiveSpec(
        id="reshape",
        category="transform",
        name="Aspect & Geometry Reshape",
        description="Changes aspect ratio, corner radii, and proportions seamlessly.",
        default_easing="cubic_out",
        typical_duration_frames=18,
        physics_params={"radius_start": 4, "radius_end": 50},
        css_transform_template="width: {w}px; height: {h}px; border-radius: {r}px",
    ),
    "expand": MotionPrimitiveSpec(
        id="expand",
        category="transform",
        name="Structural Expansion",
        description="Single compact node unfolds into an extensive multi-branch tree or grid.",
        default_easing="spring_snappy",
        typical_duration_frames=22,
        physics_params={"branch_count": 4, "stagger_delay": 2},
        css_transform_template="scale({scale})",
    ),
    "collapse": MotionPrimitiveSpec(
        id="collapse",
        category="transform",
        name="Singularity Collapse",
        description="Multi-element complex visual collapses into one ultra-dense dot or glyph.",
        default_easing="expo_inout",
        typical_duration_frames=16,
        physics_params={"gravity_pull": 2.0},
        css_transform_template="scale({scale}) translate3d({tx}px, {ty}px, 0)",
    ),
    "split": MotionPrimitiveSpec(
        id="split",
        category="transform",
        name="Cellular Division Split",
        description="One visual unit fractures into two comparative side-by-side halves.",
        default_easing="cubic_out",
        typical_duration_frames=16,
        physics_params={"separation_distance_px": 280},
        css_transform_template="translateX({tx}px)",
    ),
    "merge": MotionPrimitiveSpec(
        id="merge",
        category="transform",
        name="Coalescent Merge",
        description="Multiple disjoint streams or objects collide and fuse into a single entity.",
        default_easing="cubic_out",
        typical_duration_frames=18,
        physics_params={"fusion_flash": True},
        css_transform_template="translate3d({tx}px, {ty}px, 0)",
    ),
    "rotate_to_next": MotionPrimitiveSpec(
        id="rotate_to_next",
        category="transform",
        name="3D Axis Flip Transition",
        description="90-degree 3D card/panel rotation revealing the next concept on reverse face.",
        default_easing="expo_inout",
        typical_duration_frames=18,
        physics_params={"axis": "Y", "perspective": 1200},
        css_transform_template="rotateY({rot}deg)",
    ),
    "object_to_text": MotionPrimitiveSpec(
        id="object_to_text",
        category="transform",
        name="Object-to-Typography Morph",
        description="Physical icon, diagram node, or container dissolves into an authoritative word.",
        default_easing="expo_inout",
        typical_duration_frames=18,
        physics_params={"dissolve_feather": 0.4},
        css_transform_template="scale({scale}) opacity: {opacity}",
    ),
    "text_to_object": MotionPrimitiveSpec(
        id="text_to_object",
        category="transform",
        name="Typography-to-Object Morph",
        description="Headline glyphs compact and extrude into an interactive interface or schematic.",
        default_easing="cubic_out",
        typical_duration_frames=18,
        physics_params={"extrude_depth": 20},
        css_transform_template="scale({scale}) translateY({ty}px)",
    ),
    "line_to_path": MotionPrimitiveSpec(
        id="line_to_path",
        category="transform",
        name="Linear-to-Network Unfold",
        description="A simple dividing rule expands into a branching pipeline or node graph.",
        default_easing="expo_inout",
        typical_duration_frames=20,
        physics_params={"node_population_delay": 6},
        css_transform_template="stroke-dasharray: {dash}",
    ),
    "card_to_screen": MotionPrimitiveSpec(
        id="card_to_screen",
        category="transform",
        name="Micro-Card to Full Canvas",
        description="Contained UI element explodes to consume the entire 1080x1920 canvas.",
        default_easing="expo_inout",
        typical_duration_frames=20,
        physics_params={"fullscreen_bounds": [1080, 1920]},
        css_transform_template="scale({scale}) translate3d({tx}px, {ty}px, 0)",
    ),
}

# ── 4. IMPACT PRIMITIVES ─────────────────────────────────────────────────────
IMPACT_PRIMITIVES: Dict[str, MotionPrimitiveSpec] = {
    "shake": MotionPrimitiveSpec(
        id="shake",
        category="impact",
        name="Seismic Screen Shake",
        description="Damped multi-axis high-frequency impulse upon critical visual hit.",
        default_easing="spring_snappy",
        typical_duration_frames=12,
        physics_params={"amplitude_px": 14, "decay_rate": 0.75, "frequency_hz": 28},
        css_transform_template="translate3d({sx}px, {sy}px, 0)",
    ),
    "squash_stretch": MotionPrimitiveSpec(
        id="squash_stretch",
        category="impact",
        name="Physical Squash & Stretch",
        description="Preserves volumetric area: squashes on impact (X: 1.25, Y: 0.8) then rebounds.",
        default_easing="elastic_out",
        typical_duration_frames=14,
        physics_params={"squash_factor": 0.78, "stretch_factor": 1.28},
        css_transform_template="scale({sx}, {sy})",
    ),
    "flash": MotionPrimitiveSpec(
        id="flash",
        category="impact",
        name="Luminance Flash Burst",
        description="Instantaneous white/accent brightness spike decaying in 4 frames.",
        default_easing="cubic_out",
        typical_duration_frames=8,
        physics_params={"peak_opacity": 0.85},
        css_transform_template="opacity: {opacity}; filter: brightness({bright})",
    ),
    "displacement": MotionPrimitiveSpec(
        id="displacement",
        category="impact",
        name="Kinetic Vector Displacement",
        description="Surrounding grid lines or particles deflect away from the collision center.",
        default_easing="cubic_out",
        typical_duration_frames=15,
        physics_params={"radius_px": 350, "repel_force": 65},
        css_transform_template="translate3d({dx}px, {dy}px, 0)",
    ),
    "ripple": MotionPrimitiveSpec(
        id="ripple",
        category="impact",
        name="Radial Wavefront Shockwave",
        description="Concentric shockwave rings expand outward across the coordinate background.",
        default_easing="cubic_out",
        typical_duration_frames=20,
        physics_params={"speed_px_f": 18, "max_radius": 520, "ring_thickness": 2},
        css_transform_template="scale({scale}); opacity: {opacity}",
    ),
}

# ── 5. EXIT PRIMITIVES ───────────────────────────────────────────────────────
EXIT_PRIMITIVES: Dict[str, MotionPrimitiveSpec] = {
    "dissolve": MotionPrimitiveSpec(
        id="dissolve",
        category="exit",
        name="Optical Dissolve & Scatter",
        description="Particle dissolution into fine ambient dust.",
        default_easing="cubic_in",
        typical_duration_frames=12,
        physics_params={"scatter_velocity": 4.0},
        css_transform_template="opacity: {opacity}; filter: blur({blur}px)",
    ),
    "collapse": MotionPrimitiveSpec(
        id="collapse",
        category="exit",
        name="Rapid Implosion Collapse",
        description="Scales to zero in 8 frames into an exact geometric point.",
        default_easing="cubic_in",
        typical_duration_frames=10,
        physics_params={"scale_end": 0.0},
        css_transform_template="scale({scale})",
    ),
    "shoot": MotionPrimitiveSpec(
        id="shoot",
        category="exit",
        name="Supersonic Rocket Exit",
        description="Accelerates off-screen at exponential velocity with motion blur streak.",
        default_easing="cubic_in",
        typical_duration_frames=10,
        physics_params={"direction": "up", "speed_px_f": 180},
        css_transform_template="translateY({ty}px)",
        svg_filter_needed="motion_blur_linear",
    ),
    "wipe": MotionPrimitiveSpec(
        id="wipe",
        category="exit",
        name="Architectural Blade Wipe",
        description="Crisp directional curtain or guillotine clear across canvas.",
        default_easing="expo_inout",
        typical_duration_frames=14,
        physics_params={"angle_deg": 90},
        css_transform_template="clip-path: inset(0 {wipe}% 0 0)",
    ),
    "fold": MotionPrimitiveSpec(
        id="fold",
        category="exit",
        name="Dimensional Isometric Fold",
        description="Folds like an origami blueprint into a thin plane before vanishing.",
        default_easing="cubic_in",
        typical_duration_frames=14,
        physics_params={"fold_axis": "X"},
        css_transform_template="rotateX({rot}deg) scale({scale})",
    ),
    "pull_away": MotionPrimitiveSpec(
        id="pull_away",
        category="exit",
        name="Camera Pull-Away Disappearance",
        description="Element recedes into deep Z distance vanishing into the horizon.",
        default_easing="cubic_in",
        typical_duration_frames=16,
        physics_params={"target_z": -1200},
        css_transform_template="translate3d(0, 0, {tz}px) opacity: {opacity}",
    ),
    "camera_pass_through": MotionPrimitiveSpec(
        id="camera_pass_through",
        category="exit",
        name="Lens Pass-Through Dive",
        description="Element scales past the screen edges as if camera flew directly through it.",
        default_easing="cubic_in",
        typical_duration_frames=12,
        physics_params={"target_scale": 4.5},
        css_transform_template="scale({scale}) opacity: {opacity}",
    ),
}

ALL_MOTION_PRIMITIVES = {
    **ENTER_PRIMITIVES,
    **MOVE_PRIMITIVES,
    **TRANSFORM_PRIMITIVES,
    **IMPACT_PRIMITIVES,
    **EXIT_PRIMITIVES
}


def get_primitive(primitive_id: str) -> Optional[MotionPrimitiveSpec]:
    return ALL_MOTION_PRIMITIVES.get(primitive_id)


def list_primitives_by_category(category: str) -> List[MotionPrimitiveSpec]:
    cat = category.lower()
    if cat == "enter": return list(ENTER_PRIMITIVES.values())
    elif cat == "move": return list(MOVE_PRIMITIVES.values())
    elif cat == "transform": return list(TRANSFORM_PRIMITIVES.values())
    elif cat == "impact": return list(IMPACT_PRIMITIVES.values())
    elif cat == "exit": return list(EXIT_PRIMITIVES.values())
    return list(ALL_MOTION_PRIMITIVES.values())
