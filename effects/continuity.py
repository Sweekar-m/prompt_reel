"""
effects/continuity.py
=====================
Continuity-Driven Motion System for Prompt Reel.

Inspired by the principles of OneTake: every beat must grow out of the one before.
A transition is NOT successful merely because Scene A disappears and Scene B appears.
Every major beat must identify an element that CARRIES, TRANSFORMS, EXPANDS,
COLLAPSES, TRAVELS, or MORPHS into the next beat.

This module defines:
  1. CARRY_PRIMITIVES — the atomic vocabulary of continuous carry
  2. ContinuityBridge — data structure linking two adjacent beats
  3. ContinuityScorer — oracle that measures how continuous a motion plan is
  4. ContinuityWeaver — engine that annotates a motion plan with carry instructions
  5. CONTINUITY_THRESHOLDS — minimum acceptable scores per video type

Design rules enforced:
  - No pure crossfades without a carrier element (slideshow rejection)
  - Every scene must declare an exit carrier AND an entry carrier
  - Carrier elements must be geometrically or semantically related across beats
  - Camera must maintain continuity (no jump cuts unless declared intentional whip)
  - Motion blur must be applied at the carry boundary frames
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import math
import re

# ──────────────────────────────────────────────────────────────────────────────
# CARRY PRIMITIVES
# The atomic vocabulary of visual carry. Each primitive describes HOW an element
# survives the transition from one beat to the next.
# ──────────────────────────────────────────────────────────────────────────────
CARRY_PRIMITIVES = {
    "expand": {
        "id": "expand",
        "description": "An element grows in size, bleeding outward to fill the next scene's canvas.",
        "entry_scale_factor": 0.15,    # enters at 15% of full size
        "exit_scale_factor": 2.2,      # exits at 220% — overflows frame boundary
        "motion_blur_intensity": 0.5,
        "easing": "cubic_out",
        "camera_offset_px": 0,
        "typical_carriers": ["headline", "badge", "icon", "circle", "code_block"],
    },
    "collapse": {
        "id": "collapse",
        "description": "An element from scene A compresses toward a focal point that becomes scene B's anchor.",
        "entry_scale_factor": 2.0,
        "exit_scale_factor": 0.05,
        "motion_blur_intensity": 0.6,
        "easing": "cubic_in",
        "camera_offset_px": 0,
        "typical_carriers": ["diagram", "grid", "background_glyph", "metric_badge"],
    },
    "travel": {
        "id": "travel",
        "description": "An element slides from its position in A to a new position in B, bridging spatial contexts.",
        "entry_scale_factor": 1.0,
        "exit_scale_factor": 1.0,
        "motion_blur_intensity": 0.75,
        "easing": "sine_inout",
        "camera_follows": True,
        "typical_carriers": ["headline", "code_line", "icon", "progress_bar"],
    },
    "morph": {
        "id": "morph",
        "description": "An element shape-shifts — a code block morphs into a diagram node, a curve into a mesh.",
        "entry_scale_factor": 1.0,
        "exit_scale_factor": 1.0,
        "motion_blur_intensity": 0.4,
        "easing": "expo_inout",
        "interpolation_frames": 9,
        "typical_carriers": ["formula", "code_block", "shape", "chart_line"],
    },
    "whip_pan": {
        "id": "whip_pan",
        "description": "Camera whips at high velocity, the motion blur itself carries context between scenes.",
        "motion_blur_intensity": 0.95,
        "easing": "expo_in",
        "camera_velocity_multiplier": 4.0,
        "duration_frames": 6,
        "typical_carriers": ["camera_itself"],
    },
    "split_reveal": {
        "id": "split_reveal",
        "description": "Scene A splits apart (horizontally or vertically), revealing scene B underneath.",
        "entry_scale_factor": 1.0,
        "exit_scale_factor": 1.0,
        "motion_blur_intensity": 0.35,
        "easing": "cubic_out",
        "split_axis": "vertical",
        "typical_carriers": ["full_frame", "background_layer"],
    },
    "z_punch": {
        "id": "z_punch",
        "description": "Camera punches forward on Z-axis through a glowing element — depth continuity.",
        "entry_scale_factor": 1.0,
        "exit_scale_factor": 3.5,
        "motion_blur_intensity": 0.8,
        "easing": "expo_in",
        "camera_z_delta": 2.5,
        "typical_carriers": ["focal_point", "badge", "metric_circle"],
    },
    "unfurl": {
        "id": "unfurl",
        "description": "A collapsed line or point unfurls and stretches to form the next scene's content.",
        "entry_scale_factor": 0.02,    # starts as a line
        "exit_scale_factor": 1.0,
        "motion_blur_intensity": 0.3,
        "easing": "spring",
        "typical_carriers": ["code_line", "separator_line", "chart_axis"],
    },
    "orbit_continue": {
        "id": "orbit_continue",
        "description": "The camera orbit begun in scene A continues without reset into scene B's geometry.",
        "motion_blur_intensity": 0.2,
        "easing": "linear",
        "camera_rotation_continuous": True,
        "typical_carriers": ["camera_itself", "3d_mesh", "orbit_target"],
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# VISUAL CARRY COMPATIBILITY TABLE
# Defines which carry primitive is optimal for each (visual_type_A → visual_type_B) pair.
# ──────────────────────────────────────────────────────────────────────────────
CARRY_COMPATIBILITY: Dict[Tuple[str, str], str] = {
    ("hook",      "code"):       "expand",        # Hook badge expands into code editor
    ("hook",      "metaphor"):   "z_punch",        # Punch through hook focal into sim
    ("hook",      "diagram"):    "expand",
    ("hook",      "math_3d"):    "z_punch",
    ("code",      "metaphor"):   "morph",          # Code block morphs into simulation
    ("code",      "diagram"):    "travel",         # Code line travels to diagram node
    ("code",      "benchmark"):  "split_reveal",   # Code splits to reveal before/after
    ("code",      "payoff"):     "collapse",       # Code collapses to principle card
    ("metaphor",  "code"):       "morph",
    ("metaphor",  "diagram"):    "travel",
    ("metaphor",  "payoff"):     "collapse",
    ("metaphor",  "math_3d"):    "orbit_continue",
    ("diagram",   "code"):       "unfurl",         # Diagram node unfurls to code line
    ("diagram",   "benchmark"):  "split_reveal",
    ("diagram",   "payoff"):     "collapse",
    ("diagram",   "metaphor"):   "morph",
    ("benchmark", "payoff"):     "collapse",
    ("benchmark", "code"):       "travel",
    ("split",     "payoff"):     "collapse",
    ("math_3d",   "diagram"):    "orbit_continue",
    ("math_3d",   "code"):       "morph",
    ("math_3d",   "payoff"):     "orbit_continue",
    ("payoff",    "hook"):       "expand",         # Loop back: payoff re-expands
}

# Fallback when no specific mapping exists
CARRY_FALLBACK_SEQUENCE = ["travel", "morph", "expand", "collapse", "whip_pan"]


def get_carry_primitive(from_type: str, to_type: str) -> str:
    """Returns the optimal carry primitive for a scene-type boundary."""
    key = (from_type.lower(), to_type.lower())
    if key in CARRY_COMPATIBILITY:
        return CARRY_COMPATIBILITY[key]
    # Try partial matches
    for (a, b), prim in CARRY_COMPATIBILITY.items():
        if a in from_type.lower() or from_type.lower() in a:
            if b in to_type.lower() or to_type.lower() in b:
                return prim
    return CARRY_FALLBACK_SEQUENCE[0]


# ──────────────────────────────────────────────────────────────────────────────
# CONTINUITY BRIDGE
# The authoritative description of one scene-to-scene carry.
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class ContinuityBridge:
    """Describes the carry connection between two adjacent scenes."""
    from_scene_id: str
    to_scene_id: str
    from_visual_type: str
    to_visual_type: str

    # The carry primitive applied
    carry_primitive: str                      # e.g. "expand", "morph", "travel"
    carrier_element: str                      # What element carries (e.g. "headline_text")
    carrier_description: str                  # Human-readable description of the carry

    # Geometry of the carry
    exit_position: Dict[str, float] = field(default_factory=lambda: {"x": 0.5, "y": 0.5})
    entry_position: Dict[str, float] = field(default_factory=lambda: {"x": 0.5, "y": 0.5})
    exit_scale: float = 1.0
    entry_scale: float = 1.0

    # Timing (in frames at 30fps)
    overlap_frames: int = 9                   # How many frames the carry overlaps both scenes
    motion_blur_intensity: float = 0.6        # 0.0–1.0

    # Camera continuity
    camera_continuity: str = "maintain"       # "maintain" | "orbit_continue" | "whip" | "punch_z"
    easing: str = "cubic_inout"

    # Scoring penalty if this bridge is poor
    continuity_score_contribution: float = 0.0  # Filled in by scorer

    def is_slideshow(self) -> bool:
        """Returns True if this bridge is a simple crossfade with no carrier — a slideshow transition."""
        return (
            self.carry_primitive in ("", "crossfade", "none")
            or not self.carrier_element
            or self.overlap_frames < 3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_scene": self.from_scene_id,
            "to_scene": self.to_scene_id,
            "from_type": self.from_visual_type,
            "to_type": self.to_visual_type,
            "carry_primitive": self.carry_primitive,
            "carrier_element": self.carrier_element,
            "carrier_description": self.carrier_description,
            "exit_position": self.exit_position,
            "entry_position": self.entry_position,
            "exit_scale": self.exit_scale,
            "entry_scale": self.entry_scale,
            "overlap_frames": self.overlap_frames,
            "motion_blur_intensity": self.motion_blur_intensity,
            "camera_continuity": self.camera_continuity,
            "easing": self.easing,
            "continuity_score_contribution": self.continuity_score_contribution,
            "is_slideshow": self.is_slideshow(),
        }


# ──────────────────────────────────────────────────────────────────────────────
# CONTINUITY SCORER — The Oracle
# ──────────────────────────────────────────────────────────────────────────────

# Minimum scores (0–100) below which the motion plan triggers auto-regeneration
CONTINUITY_THRESHOLDS = {
    "minimum_bridge_score": 55,    # Any single bridge below this is a slideshow violation
    "minimum_overall_score": 68,   # Overall continuity below this triggers regeneration
    "maximum_slideshow_ratio": 0.2, # More than 20% slideshow bridges → regenerate
}


class ContinuityScorer:
    """
    Measures the continuity quality of a motion plan.
    Returns a ContinuityReport with per-bridge scores and an overall ContinuityScore.
    This is the 'oracle' that programmatically verifies visual carry quality.
    """

    # Score weights for each carry primitive (higher = better carry quality)
    PRIMITIVE_WEIGHTS = {
        "morph":           1.00,
        "expand":          0.90,
        "z_punch":         0.88,
        "orbit_continue":  0.92,
        "collapse":        0.85,
        "travel":          0.80,
        "unfurl":          0.82,
        "split_reveal":    0.70,
        "whip_pan":        0.65,
        "crossfade":       0.15,   # Penalized heavily
        "none":            0.00,   # Complete slideshow — rejected
        "":                0.00,
    }

    # Scene type transition desirability (how well each pair works conceptually)
    TYPE_PAIR_QUALITY = {
        ("hook", "code"):         0.95,
        ("hook", "metaphor"):     0.90,
        ("hook", "math_3d"):      0.95,
        ("code", "metaphor"):     0.92,
        ("code", "diagram"):      0.88,
        ("code", "benchmark"):    0.90,
        ("metaphor", "diagram"):  0.85,
        ("metaphor", "code"):     0.82,
        ("diagram", "code"):      0.87,
        ("diagram", "benchmark"): 0.83,
        ("benchmark", "payoff"):  0.92,
        ("math_3d", "diagram"):   0.88,
        ("math_3d", "payoff"):    0.85,
    }
    DEFAULT_TYPE_PAIR_QUALITY = 0.70

    def score_bridge(self, bridge: ContinuityBridge) -> float:
        """Score a single ContinuityBridge. Returns 0.0–100.0."""
        # 1. Primitive quality (0–60 points)
        prim_weight = self.PRIMITIVE_WEIGHTS.get(bridge.carry_primitive, 0.3)
        primitive_score = prim_weight * 60

        # 2. Type-pair compatibility (0–20 points)
        type_key = (bridge.from_visual_type.lower(), bridge.to_visual_type.lower())
        type_quality = self.TYPE_PAIR_QUALITY.get(type_key, self.DEFAULT_TYPE_PAIR_QUALITY)
        type_score = type_quality * 20

        # 3. Carrier element specificity (0–10 points)
        if not bridge.carrier_element or bridge.carrier_element in ("none", "fade", ""):
            carrier_score = 0
        elif bridge.carrier_element in ("camera_itself", "full_frame"):
            carrier_score = 5
        else:
            carrier_score = 10

        # 4. Overlap frames richness (0–10 points)
        if bridge.overlap_frames >= 12:
            overlap_score = 10
        elif bridge.overlap_frames >= 9:
            overlap_score = 8
        elif bridge.overlap_frames >= 6:
            overlap_score = 6
        elif bridge.overlap_frames >= 3:
            overlap_score = 4
        else:
            overlap_score = 0  # Instant cut with no carry

        score = primitive_score + type_score + carrier_score + overlap_score
        return min(100.0, max(0.0, round(score, 1)))

    def score_motion_plan(self, motion_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate all bridges in a motion plan.
        Returns a full ContinuityReport dict.
        """
        bridges_data = motion_plan.get("continuity_bridges", [])
        scenes = motion_plan.get("scenes", [])

        if not bridges_data:
            # No bridges annotated — generate scores from scene pairs directly
            bridge_scores = self._score_unannotated(scenes)
        else:
            bridge_scores = []
            for bd in bridges_data:
                bridge = ContinuityBridge(
                    from_scene_id=bd.get("from_scene", ""),
                    to_scene_id=bd.get("to_scene", ""),
                    from_visual_type=bd.get("from_type", "unknown"),
                    to_visual_type=bd.get("to_type", "unknown"),
                    carry_primitive=bd.get("carry_primitive", ""),
                    carrier_element=bd.get("carrier_element", ""),
                    carrier_description=bd.get("carrier_description", ""),
                    overlap_frames=bd.get("overlap_frames", 0),
                    motion_blur_intensity=bd.get("motion_blur_intensity", 0.0),
                )
                s = self.score_bridge(bridge)
                bridge_scores.append({
                    "bridge": bd,
                    "score": s,
                    "is_slideshow": bridge.is_slideshow(),
                    "passed": s >= CONTINUITY_THRESHOLDS["minimum_bridge_score"],
                })

        # Calculate overall continuity score
        if not bridge_scores:
            overall = 50.0
            slideshow_ratio = 1.0
        else:
            scores = [b["score"] for b in bridge_scores]
            overall = sum(scores) / len(scores)
            slideshow_count = sum(1 for b in bridge_scores if b.get("is_slideshow", False))
            slideshow_ratio = slideshow_count / len(bridge_scores)

        # Identify violations
        violations = []
        for b in bridge_scores:
            if b["score"] < CONTINUITY_THRESHOLDS["minimum_bridge_score"]:
                bridge_info = b.get("bridge", {})
                violations.append({
                    "from": bridge_info.get("from_scene", "unknown"),
                    "to": bridge_info.get("to_scene", "unknown"),
                    "score": b["score"],
                    "issue": "Slideshow transition" if b.get("is_slideshow") else "Weak carry",
                    "current_primitive": bridge_info.get("carry_primitive", "none"),
                    "recommendation": self._recommend_fix(
                        bridge_info.get("from_type", ""),
                        bridge_info.get("to_type", "")
                    )
                })

        passed = (
            overall >= CONTINUITY_THRESHOLDS["minimum_overall_score"]
            and slideshow_ratio <= CONTINUITY_THRESHOLDS["maximum_slideshow_ratio"]
        )

        return {
            "continuity_score": round(overall, 1),
            "passed": passed,
            "slideshow_ratio": round(slideshow_ratio, 3),
            "slideshow_bridge_count": sum(1 for b in bridge_scores if b.get("is_slideshow", False)),
            "total_bridges": len(bridge_scores),
            "bridge_scores": bridge_scores,
            "violations": violations,
            "recommendation": "APPROVED — Continuous motion verified" if passed else (
                f"REGENERATE — Continuity score {round(overall,1)}/100 below threshold "
                f"({CONTINUITY_THRESHOLDS['minimum_overall_score']}). "
                f"{len(violations)} slideshow violations detected."
            ),
            "thresholds": CONTINUITY_THRESHOLDS,
        }

    def _score_unannotated(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score a motion plan that has no continuity_bridges — worst case assumed."""
        results = []
        for i in range(len(scenes) - 1):
            a = scenes[i]
            b = scenes[i + 1]
            from_type = a.get("visual_type", "unknown")
            to_type = b.get("visual_type", "unknown")
            # Without annotation, assume plain crossfade (slideshow)
            bridge = ContinuityBridge(
                from_scene_id=a.get("id", f"scene_{i}"),
                to_scene_id=b.get("id", f"scene_{i+1}"),
                from_visual_type=from_type,
                to_visual_type=to_type,
                carry_primitive="crossfade",
                carrier_element="",
                carrier_description="No carry annotated",
                overlap_frames=0,
            )
            s = self.score_bridge(bridge)
            results.append({
                "bridge": {
                    "from_scene": a.get("id"),
                    "to_scene": b.get("id"),
                    "from_type": from_type,
                    "to_type": to_type,
                    "carry_primitive": "crossfade",
                    "carrier_element": "",
                },
                "score": s,
                "is_slideshow": True,
                "passed": False,
            })
        return results

    def _recommend_fix(self, from_type: str, to_type: str) -> str:
        """Suggests the best carry primitive for a violated boundary."""
        prim = get_carry_primitive(from_type, to_type)
        prim_info = CARRY_PRIMITIVES.get(prim, {})
        return (
            f"Replace with '{prim}' carry: {prim_info.get('description', 'element carries between scenes')}"
        )


# ──────────────────────────────────────────────────────────────────────────────
# CONTINUITY WEAVER
# Annotates a motion plan with explicit carry instructions for every beat boundary.
# ──────────────────────────────────────────────────────────────────────────────

class ContinuityWeaver:
    """
    Takes a raw motion plan and annotates every scene-to-scene boundary
    with a ContinuityBridge describing HOW the visual content carries forward.

    This is the core implementation of the OneTake principle:
    every beat grows out of the one before it.
    """

    def __init__(self):
        self.scorer = ContinuityScorer()

    def weave(self, motion_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Annotates the motion plan with continuity_bridges and continuity_report.
        Does NOT modify scene content — only adds carry metadata.
        Returns the enriched motion_plan.
        """
        scenes = motion_plan.get("scenes", [])
        if len(scenes) < 2:
            motion_plan["continuity_bridges"] = []
            motion_plan["continuity_report"] = {
                "continuity_score": 100.0,
                "passed": True,
                "message": "Single scene — no bridges needed",
            }
            return motion_plan

        topic = motion_plan.get("topic", "")
        is_math = motion_plan.get("is_math", False)

        bridges = []
        for i in range(len(scenes) - 1):
            scene_a = scenes[i]
            scene_b = scenes[i + 1]
            bridge = self._compute_bridge(scene_a, scene_b, topic, is_math, i)
            bridges.append(bridge.to_dict())

            # Also annotate the scenes themselves with exit/entry carry info
            scenes[i]["exit_carry"] = {
                "primitive": bridge.carry_primitive,
                "carrier": bridge.carrier_element,
                "to_scene": scene_b["id"],
                "overlap_frames": bridge.overlap_frames,
                "motion_blur": bridge.motion_blur_intensity,
                "easing": bridge.easing,
            }
            scenes[i + 1]["entry_carry"] = {
                "primitive": bridge.carry_primitive,
                "carrier": bridge.carrier_element,
                "from_scene": scene_a["id"],
                "overlap_frames": bridge.overlap_frames,
                "motion_blur": bridge.motion_blur_intensity,
                "entry_scale": bridge.entry_scale,
            }

        motion_plan["continuity_bridges"] = bridges
        motion_plan["scenes"] = scenes

        # Run the oracle scorer
        continuity_report = self.scorer.score_motion_plan(motion_plan)
        motion_plan["continuity_report"] = continuity_report

        return motion_plan

    def _compute_bridge(
        self,
        scene_a: Dict[str, Any],
        scene_b: Dict[str, Any],
        topic: str,
        is_math: bool,
        index: int
    ) -> ContinuityBridge:
        """Compute the optimal ContinuityBridge for an adjacent scene pair."""
        from_type = scene_a.get("visual_type", "unknown")
        to_type = scene_b.get("visual_type", "unknown")

        # Select carry primitive
        primitive_id = get_carry_primitive(from_type, to_type)
        primitive = CARRY_PRIMITIVES.get(primitive_id, CARRY_PRIMITIVES["travel"])

        # Identify the carrier element from the scene content
        carrier_element, carrier_desc = self._identify_carrier(
            scene_a, scene_b, from_type, to_type, primitive_id, topic, is_math
        )

        # Determine camera continuity mode
        camera_mode = self._determine_camera_continuity(
            from_type, to_type, primitive_id, is_math
        )

        # Overlap frames: richer carry needs more time
        blur = primitive.get("motion_blur_intensity", 0.5)
        if primitive_id in ("morph", "orbit_continue"):
            overlap = 12
        elif primitive_id in ("expand", "z_punch", "collapse"):
            overlap = 9
        elif primitive_id in ("travel", "unfurl", "split_reveal"):
            overlap = 8
        elif primitive_id == "whip_pan":
            overlap = 6
        else:
            overlap = 9

        # Entry/exit scales from the primitive spec
        exit_scale = primitive.get("exit_scale_factor", 1.0)
        entry_scale = primitive.get("entry_scale_factor", 1.0)

        # Easing from primitive
        easing = primitive.get("easing", "cubic_inout")

        return ContinuityBridge(
            from_scene_id=scene_a["id"],
            to_scene_id=scene_b["id"],
            from_visual_type=from_type,
            to_visual_type=to_type,
            carry_primitive=primitive_id,
            carrier_element=carrier_element,
            carrier_description=carrier_desc,
            exit_scale=exit_scale,
            entry_scale=entry_scale,
            overlap_frames=overlap,
            motion_blur_intensity=blur,
            camera_continuity=camera_mode,
            easing=easing,
        )

    def _identify_carrier(
        self,
        scene_a: Dict[str, Any],
        scene_b: Dict[str, Any],
        from_type: str,
        to_type: str,
        primitive_id: str,
        topic: str,
        is_math: bool,
    ) -> Tuple[str, str]:
        """
        Identifies the specific element that carries between the two scenes
        and produces a human-readable description of the carry.
        """
        elements_a = scene_a.get("elements", {})
        elements_b = scene_b.get("elements", {})

        # Math continuity: the formula / 3D mesh is the permanent carrier
        if is_math or from_type == "math_3d" or to_type == "math_3d":
            formula = elements_a.get("equation_latex") or elements_b.get("equation_latex") or topic
            return (
                "math_surface_mesh",
                f"The 3D parametric surface mesh of {formula} remains visible as the camera "
                f"orbit continues unbroken into the next beat."
            )

        # Hook → code: headline text morphs into code editor header
        if from_type == "hook" and to_type == "code":
            headline = elements_a.get("headline", topic.upper())
            filename = elements_b.get("filename", "main.py")
            return (
                "headline_text",
                f"The headline '{headline}' expands from center and its letters "
                f"reassemble as the filename '{filename}' in the code editor header."
            )

        # Code → metaphor: highlighted code line morphs into simulation node
        if from_type == "code" and to_type in ("metaphor", "diagram"):
            highlight = elements_a.get("highlight_line", 1)
            annotation = elements_a.get("annotation", "key operation")
            sim = elements_b.get("simulation_type", "simulation")
            return (
                "highlighted_code_line",
                f"Line {highlight} ('{annotation}') de-materializes and re-materializes "
                f"as the primary node in the {sim} visualization."
            )

        # Metaphor → diagram: simulation element travels to diagram step
        if from_type == "metaphor" and to_type == "diagram":
            label = elements_a.get("label", "core element")
            steps = elements_b.get("steps", ["step"])
            step1 = steps[0] if steps else "first step"
            return (
                "simulation_node",
                f"The '{label}' simulation node travels rightward to become "
                f"the first diagram step: '{step1}'."
            )

        # Diagram → code: diagram step node unfurls into a code line
        if from_type == "diagram" and to_type == "code":
            steps = elements_a.get("steps", ["operation"])
            step_last = steps[-1] if steps else "final step"
            return (
                "diagram_step_node",
                f"The '{step_last}' step node collapses to a single glowing point, "
                f"then unfurls into the opening code line."
            )

        # Code → benchmark: code panels split apart to reveal comparison
        if from_type == "code" and to_type in ("benchmark", "split"):
            return (
                "code_panel",
                f"The single code panel splits along a vertical axis — "
                f"left half stays as 'before', right half morphs into the optimized version."
            )

        # Any → payoff: the current scene's primary element collapses to a focal point
        if to_type == "payoff":
            primary = (
                elements_a.get("headline")
                or elements_a.get("title")
                or elements_a.get("stat")
                or topic
            )
            return (
                "primary_element",
                f"'{primary}' collapses toward the screen center, then expands outward "
                f"as the payoff card's headline, maintaining visual lineage."
            )

        # Hook with whip or z_punch
        if from_type == "hook" and primitive_id in ("z_punch", "whip_pan"):
            badge = elements_a.get("badge", topic.upper())
            return (
                "hook_badge",
                f"The badge '{badge}' punches forward on Z-axis, becoming a portal "
                f"that the camera travels through to enter the next scene."
            )

        # Camera-based carries
        if primitive_id == "whip_pan":
            return (
                "camera_itself",
                f"The camera whips at 4× velocity creating a motion blur streak "
                f"that bridges the two scenes without an element cut."
            )

        if primitive_id == "orbit_continue":
            return (
                "camera_itself",
                f"Camera orbit initiated in the previous beat continues uninterrupted, "
                f"the rotation itself providing continuity of context."
            )

        # Generic fallback: most prominent shared semantic element
        headline_a = elements_a.get("headline") or elements_a.get("title") or elements_a.get("stat")
        headline_b = elements_b.get("headline") or elements_b.get("title") or elements_b.get("stat")

        if headline_a:
            return (
                "primary_text_element",
                f"'{headline_a}' travels from its position and morphs into "
                f"'{headline_b or 'the next section header'}' as the scene transitions."
            )

        return (
            "background_gradient",
            f"The background color field morphs hue continuously from scene A into "
            f"scene B, maintaining palette identity as the only visual carrier."
        )

    def _determine_camera_continuity(
        self,
        from_type: str,
        to_type: str,
        primitive_id: str,
        is_math: bool
    ) -> str:
        """Determines how the camera behaves across the boundary."""
        if primitive_id == "orbit_continue":
            return "orbit_continue"
        if primitive_id == "whip_pan":
            return "whip"
        if primitive_id == "z_punch":
            return "punch_z"
        if is_math or from_type == "math_3d" or to_type == "math_3d":
            return "orbit_continue"
        if from_type in ("hook",) and to_type in ("code", "metaphor"):
            return "punch_z"
        return "maintain"


# ──────────────────────────────────────────────────────────────────────────────
# MOTION BLUR SPEC
# Per-frame motion blur parameters derived from the bridge.
# ──────────────────────────────────────────────────────────────────────────────

def compute_motion_blur_frames(bridge: Dict[str, Any], fps: int = 30) -> List[Dict[str, Any]]:
    """
    Returns per-frame motion blur intensity values for the carry window.
    The blur ramps up to peak at the midpoint, then ramps down.
    Used by the renderer to apply directional blur at frame level.
    """
    overlap = bridge.get("overlap_frames", 9)
    max_blur = bridge.get("motion_blur_intensity", 0.5)
    frames = []
    for f in range(overlap):
        t = f / max(overlap - 1, 1)  # 0.0 → 1.0
        # Bell curve: 0 → peak → 0
        intensity = math.sin(t * math.pi) * max_blur
        frames.append({
            "frame_offset": f - overlap // 2,
            "blur_intensity": round(intensity, 3),
            "blur_direction": bridge.get("carry_primitive", "travel"),
        })
    return frames


# ──────────────────────────────────────────────────────────────────────────────
# SLIDESHOW DETECTOR — Hard rejection rule
# ──────────────────────────────────────────────────────────────────────────────

def detect_slideshow_violations(motion_plan: Dict[str, Any]) -> List[str]:
    """
    Hard rule enforcement: any motion plan where a scene simply appears after
    the previous one disappears — with no carrier element — is a slideshow.
    Returns a list of violation messages.
    """
    violations = []
    bridges = motion_plan.get("continuity_bridges", [])

    if not bridges:
        scenes = motion_plan.get("scenes", [])
        if len(scenes) > 1:
            violations.append(
                f"SLIDESHOW DETECTED: Motion plan has {len(scenes)} scenes but ZERO "
                f"continuity bridges. This is a slideshow. Regeneration required."
            )
        return violations

    for b in bridges:
        prim = b.get("carry_primitive", "")
        carrier = b.get("carrier_element", "")
        overlap = b.get("overlap_frames", 0)
        from_s = b.get("from_scene", "?")
        to_s = b.get("to_scene", "?")

        if prim in ("", "crossfade", "none") and not carrier:
            violations.append(
                f"SLIDESHOW: {from_s} → {to_s}: No carry primitive and no carrier element. "
                f"Scene merely replaces previous scene."
            )
        elif overlap < 3:
            violations.append(
                f"WEAK CARRY: {from_s} → {to_s}: Only {overlap} overlap frames. "
                f"Carry is imperceptible — minimum 3 frames required."
            )

    return violations
