"""
agents/continuity_weaver_agent.py
==================================
Continuity Weaver Agent.

Sits in the pipeline AFTER ScriptStoryboardAgent and BEFORE QualityAgent.
Its role is to:
  1. Annotate every scene-to-scene boundary with a ContinuityBridge
  2. Run the ContinuityScorer oracle to get a ContinuityScore
  3. If the score is below threshold, produce a regeneration directive
     specifying which bridges must be improved

The agent also enforces the "slideshow rejection" rule:
  A transition is NOT considered successful merely because Scene A disappears
  and Scene B appears. Every major beat must identify an element that CARRIES,
  TRANSFORMS, EXPANDS, COLLAPSES, TRAVELS, or MORPHS into the next beat.

Regeneration protocol:
  If ContinuityScore < CONTINUITY_THRESHOLDS["minimum_overall_score"]:
    → Return needs_regeneration=True with a directive to the StoryboardAgent
    → The StoryboardAgent then adjusts scene visual_types / elements to
       create better carrier relationships
    → Max 2 regeneration attempts before accepting best result
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
import time

from effects.continuity import (
    ContinuityWeaver,
    ContinuityScorer,
    CONTINUITY_THRESHOLDS,
    detect_slideshow_violations,
    CARRY_PRIMITIVES,
    get_carry_primitive,
)


class ContinuityWeaverAgent:
    """
    Annotates motion plans with carry instructions and scores them.
    If score is insufficient, returns regeneration directives.
    """

    MAX_REGENERATION_ATTEMPTS = 2

    def __init__(self):
        self.weaver = ContinuityWeaver()
        self.scorer = ContinuityScorer()

    def weave_and_score(
        self,
        motion_plan: Dict[str, Any],
        attempt: int = 0
    ) -> Dict[str, Any]:
        """
        Main entry point.
        Annotates motion_plan with continuity bridges and scores it.

        Returns the annotated motion_plan with these new fields:
          - continuity_bridges: List[ContinuityBridgeDict]
          - continuity_report: ContinuityReportDict
          - continuity_score: float (0–100)
          - continuity_passed: bool
          - continuity_violations: List[str]
          - needs_continuity_regeneration: bool
          - continuity_regeneration_directive: Optional[str]
        """
        t_start = time.time()

        # Step 1: Annotate all scene boundaries with carry bridges
        annotated = self.weaver.weave(motion_plan)

        # Step 2: Detect slideshow violations (hard rule)
        violations = detect_slideshow_violations(annotated)

        # Step 3: Extract continuity report from weaver
        report = annotated.get("continuity_report", {})
        score = report.get("continuity_score", 0.0)
        passed = report.get("passed", False)

        # Step 4: Determine if regeneration is needed
        needs_regen = (
            not passed
            or len(violations) > 0
        ) and attempt < self.MAX_REGENERATION_ATTEMPTS

        # Step 5: Build regeneration directive if needed
        directive = None
        if needs_regen:
            directive = self._build_regeneration_directive(annotated, report, violations)

        # Add top-level continuity metadata
        annotated["continuity_score"] = score
        annotated["continuity_passed"] = passed
        annotated["continuity_violations"] = violations
        annotated["needs_continuity_regeneration"] = needs_regen
        annotated["continuity_regeneration_directive"] = directive
        annotated["continuity_weave_ms"] = round((time.time() - t_start) * 1000, 1)
        annotated["continuity_attempt"] = attempt

        return annotated

    def repair_motion_plan(
        self,
        motion_plan: Dict[str, Any],
        directive: str,
        attempt: int
    ) -> Dict[str, Any]:
        """
        Applies heuristic repairs to a motion plan that failed continuity scoring.
        Does NOT regenerate content — instead it upgrades the carry metadata
        for weak bridges by substituting better primitives and carrier elements.
        """
        scenes = motion_plan.get("scenes", [])
        report = motion_plan.get("continuity_report", {})
        bridge_scores = report.get("bridge_scores", [])
        topic = motion_plan.get("topic", "")
        is_math = motion_plan.get("is_math", False)

        # Find bridges that failed and fix them
        for i, bs in enumerate(bridge_scores):
            if bs.get("passed", True):
                continue
            if i >= len(scenes) - 1:
                continue

            scene_a = scenes[i]
            scene_b = scenes[i + 1]
            from_type = scene_a.get("visual_type", "unknown")
            to_type = scene_b.get("visual_type", "unknown")

            # Upgrade the carry primitive
            best_prim = get_carry_primitive(from_type, to_type)
            prim_info = CARRY_PRIMITIVES.get(best_prim, {})

            # Compute upgraded carrier
            carrier, desc = self.weaver._compute_bridge(
                scene_a, scene_b, topic, is_math, i
            ).carrier_element, ""
            bridge, _ = (
                self.weaver._compute_bridge(scene_a, scene_b, topic, is_math, i),
                None
            )

            # Update exit/entry carry on scenes
            scenes[i]["exit_carry"] = {
                "primitive": bridge.carry_primitive,
                "carrier": bridge.carrier_element,
                "to_scene": scene_b["id"],
                "overlap_frames": bridge.overlap_frames,
                "motion_blur": bridge.motion_blur_intensity,
                "easing": bridge.easing,
                "repaired": True,
            }
            scenes[i + 1]["entry_carry"] = {
                "primitive": bridge.carry_primitive,
                "carrier": bridge.carrier_element,
                "from_scene": scene_a["id"],
                "overlap_frames": bridge.overlap_frames,
                "motion_blur": bridge.motion_blur_intensity,
                "entry_scale": bridge.entry_scale,
                "repaired": True,
            }

        motion_plan["scenes"] = scenes
        motion_plan["continuity_repair_attempt"] = attempt

        # Re-score after repair
        return self.weave_and_score(motion_plan, attempt=attempt)

    def _build_regeneration_directive(
        self,
        motion_plan: Dict[str, Any],
        report: Dict[str, Any],
        violations: List[str]
    ) -> str:
        """
        Produces a detailed directive telling the StoryboardAgent
        exactly what must change to achieve continuous motion.
        """
        score = report.get("continuity_score", 0.0)
        br_scores = report.get("bridge_scores", [])
        bad_bridges = [b for b in br_scores if not b.get("passed", True)]

        lines = [
            f"CONTINUITY REGENERATION REQUIRED (Score: {score}/100, "
            f"Threshold: {CONTINUITY_THRESHOLDS['minimum_overall_score']})",
            "",
            "FAILED TRANSITIONS:",
        ]
        for b in bad_bridges:
            bridge = b.get("bridge", {})
            lines.append(
                f"  * {bridge.get('from_scene', '?')} [{bridge.get('from_type', '?')}] "
                f"-> {bridge.get('to_scene', '?')} [{bridge.get('to_type', '?')}] "
                f"(Score: {b['score']}/100)"
            )
            violations_here = report.get("violations", [])
            for v in violations_here:
                if v.get("from") == bridge.get("from_scene"):
                    lines.append(f"    Issue: {v.get('issue', 'Weak carry')}")
                    lines.append(f"    Fix:   {v.get('recommendation', 'Add carry primitive')}")

        lines.append("")
        lines.append("CONTINUITY RULES (must be satisfied):")
        lines.append("  1. Every scene must have an exit_carry and entry_carry annotation.")
        lines.append("  2. No carry_primitive of 'crossfade' or 'none' is acceptable.")
        lines.append("  3. overlap_frames must be >= 6.")
        lines.append("  4. The carrier_element must be a specific named element, not 'fade'.")
        lines.append("")
        lines.append("SLIDESHOW VIOLATIONS:")
        for v in violations:
            lines.append(f"  [X] {v}")

        return "\n".join(lines)

    def get_carry_summary(self, motion_plan: Dict[str, Any]) -> str:
        """Returns a human-readable summary of the continuity carry chain."""
        bridges = motion_plan.get("continuity_bridges", [])
        scenes = motion_plan.get("scenes", [])
        score = motion_plan.get("continuity_score", 0.0)
        passed = motion_plan.get("continuity_passed", False)

        lines = [
            f"CONTINUITY CHAIN -- Score: {score}/100 {'[PASS]' if passed else '[FAIL]'}",
            "=" * 60,
        ]
        for b in bridges:
            prim = b.get("carry_primitive", "?")
            carrier = b.get("carrier_element", "?")
            blur = b.get("motion_blur_intensity", 0)
            overlap = b.get("overlap_frames", 0)
            from_type = b.get("from_type", "?")
            to_type = b.get("to_type", "?")
            lines.append(
                f"  [{from_type}] -({prim})-> [{to_type}] "
                f"via '{carrier}' | {overlap}f | blur={blur:.1f}"
            )
        lines.append("=" * 60)
        return "\n".join(lines)
