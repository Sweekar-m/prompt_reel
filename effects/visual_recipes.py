"""
effects/visual_recipes.py
=========================
Core Visual Recipe Data Architecture for Prompt Reel's Shot Designer Engine.

Transforms abstract script scenes into concrete, renderable Visual Recipes:
Composition, 3D Camera Trajectory, Motion Primitives, Typography Behavior,
Subject Layering, Lighting & Depth Planes, and Continuity Carries.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class CameraWaypoint:
    x: float = 0.0          # Horizontal pan in px
    y: float = 0.0          # Vertical pan in px
    z: float = 0.0          # Z-depth translation (positive = forward)
    pitch: float = 0.0      # X-axis rotation in degrees
    yaw: float = 0.0        # Y-axis rotation in degrees
    roll: float = 0.0       # Z-axis tilt in degrees
    fov: float = 60.0       # Field of view
    scale: float = 1.0      # Camera zoom factor


@dataclass
class CameraTrajectory:
    start: CameraWaypoint
    end: CameraWaypoint
    motion_style: str       # "push", "pull", "pan", "orbit", "tilt", "rotate", "whip", "track", "follow", "drift", "zoom_through", "depth_planes", "still"
    motion_blur: float = 0.20   # 0.0 to 1.0 temporal blur magnitude
    easing: str = "cubic_out"   # "cubic_out", "spring_snappy", "expo_inout", "linear"


@dataclass
class VisualPrimitivesConfig:
    enter: str              # e.g. "masked_reveal", "path_reveal", "elastic", "spring", "scale"
    move: str               # e.g. "drift", "orbit", "follow", "acceleration", "depth_push"
    transform: str          # e.g. "object_to_text", "line_to_path", "morph", "expand", "split"
    impact: str             # e.g. "shake", "flash", "displacement", "ripple", "squash_stretch"
    exit: str               # e.g. "dissolve", "shoot", "collapse", "wipe", "camera_pass_through"


@dataclass
class TypographyBehaviorConfig:
    mode: str               # "word_by_word", "character_tracking", "scale_stacking", "kinetic_displacement", "line_split", "type_on", "text_to_shape"
    headline: str
    subtext: str
    badge: str
    font_size: int = 72
    letter_spacing: str = "-0.02em"
    case: str = "uppercase" # "uppercase" | "normal" | "lowercase"
    stagger_frames: int = 3
    highlight_word_indices: List[int] = field(default_factory=list)


@dataclass
class SubjectLayer:
    type: str               # "kinetic_typography", "diagram_network", "ui_panel", "spatial_3d_mesh", "abstract_shapes", "data_flow", "branching_logic", "code_stream"
    layer_id: str
    z_index: int = 1
    depth_plane: str = "midground" # "foreground", "midground", "background", "ambient"
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CarryRelationship:
    carrier_element_id: str
    entry_primitive: str
    exit_primitive: str
    morph_target: str       # What this element morphs into in the subsequent beat
    surviving_properties: List[str] = field(default_factory=list) # e.g. ["color", "position", "label"]


@dataclass
class VisualRecipe:
    scene_id: str
    beat_name: str
    start_time: float
    end_time: float
    duration_sec: float
    template_id: str

    # 1. Composition & Framing
    composition: str        # "asymmetric_left", "centered", "split_contrast", "diagonal", "edge_anchored", "full_bleed", "stacked", "radial", "spatial_depth"
    anchor: Dict[str, Any]  # {"x_pct": 20, "y_pct": 50, "align": "left"}
    layout_grammar: Dict[str, Any]

    # 2. Camera Choreography
    camera: CameraTrajectory

    # 3. Motion Primitives
    primitives: VisualPrimitivesConfig

    # 4. Typography as Motion Object
    typography: TypographyBehaviorConfig

    # 5. Visual Subjects & Layers
    primary_subject: SubjectLayer

    # 6. Lighting, Depth & Atmosphere
    background_style: str = "clean_canvas"   # "blueprint_grid", "swiss_ruler", "monochrome_planes", "clean_canvas", "os_workspace", "spatial_depth_grid", "terminal_workspace"
    lighting_depth: str = "flat_high_contrast"     # "flat_high_contrast", "isometric_depth", "cinematic_directional", "subtle_ambient"

    # 7. Rhythm & Timing
    pacing_style: str = "major_movement"       # "rapid_burst", "long_hold", "dramatic_pause", "major_movement", "stillness"

    # 8. Secondary Subjects & Continuity Carry
    secondary_subjects: List[SubjectLayer] = field(default_factory=list)
    carry: Optional[CarryRelationship] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
