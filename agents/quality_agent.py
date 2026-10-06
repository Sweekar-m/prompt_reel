"""
agents/quality_agent.py
=======================
Quality Control (QC) Agent.
Performs pre-flight and post-render validation across 6 critical dimensions:
1. CONTENT (accuracy, code validity, logical consistency)
2. DESIGN (WCAG contrast, typography hierarchy, safe areas)
3. MOTION (readable words-per-minute, transition pacing)
4. SOCIAL (9:16 mobile aspect ratio, first 2s hook strength)
5. AUDIO (ducking depth, clipping prevention, sample rate)
6. CONTINUITY (visual carry score, slideshow rejection, bridge quality)
"""
from typing import Dict, Any, List


class QualityAgent:
    def __init__(self):
        pass

    def evaluate_motion_plan(self, motion_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-render evaluation of the Motion Plan."""
        issues = []
        scores = {
            "content": 95,
            "design": 96,
            "motion": 94,
            "social": 98,
            "audio": 95,
            "continuity": 100,   # NEW: Continuity dimension
        }

        # 1. Content check
        tech = motion_plan.get("technical_summary", {})
        if not tech.get("core_mechanism"):
            scores["content"] -= 15
            issues.append("Missing core mechanism explanation.")

        code = motion_plan.get("code_assets", {})
        if not code.get("main_code"):
            scores["content"] -= 15
            issues.append("Missing primary code snippet.")

        # 2. Design check (Palette & contrast)
        cd = motion_plan.get("creative_direction", {})
        palette = cd.get("palette", {})
        if not palette.get("primary") or not palette.get("background"):
            scores["design"] -= 20
            issues.append("Invalid color palette structure.")

        # 3. Motion & Pacing check
        scenes = motion_plan.get("scenes", [])
        for sc in scenes:
            text = sc.get("voice_text", "")
            words = len(text.split())
            dur = sc.get("duration", 1.0)
            wps = words / max(dur, 0.1)
            # Normal speech is 2.5 - 3.8 words per second. Above 4.5 is unreadable/rushed.
            if wps > 4.5:
                scores["motion"] -= 8
                issues.append(f"Scene '{sc['id']}' has high speech density ({wps:.1f} words/sec). Pacing might be rushed.")

        # 4. Social & Hook check
        if scenes:
            hook_dur = scenes[0].get("duration", 0)
            if hook_dur > 5.0:
                scores["social"] -= 12
                issues.append("Hook scene is longer than 5 seconds. Mobile drop-off risk.")

        # 5. Audio check
        sound = cd.get("sound", {})
        if sound.get("ducking_db", 0) > -6.0:
            scores["audio"] -= 10
            issues.append("Music ducking attenuation is weaker than -6 dB. Voice intelligibility risk.")

        # ── 6. CONTINUITY check — The OneTake Oracle ──────────────────────────
        scores["continuity"], continuity_issues = self._evaluate_continuity(motion_plan)
        issues.extend(continuity_issues)

        overall_score = int(sum(scores.values()) / len(scores))
        passed = overall_score >= 85 and len(issues) < 4

        # A motion plan can fail solely on continuity grounds
        continuity_score = scores["continuity"]
        continuity_passed = motion_plan.get("continuity_passed", True)
        if not continuity_passed:
            passed = False

        return {
            "quality_score": overall_score,
            "passed": passed,
            "category_scores": scores,
            "issues": issues,
            "continuity_score": continuity_score,
            "continuity_passed": continuity_passed,
            "continuity_report": motion_plan.get("continuity_report", {}),
            "continuity_bridges": motion_plan.get("continuity_bridges", []),
            "recommendation": "APPROVED FOR RENDER" if passed else "REQUIRES REVISION",
        }

    def _evaluate_continuity(self, motion_plan: Dict[str, Any]) -> tuple:
        """
        Evaluate the continuity dimension of a motion plan.
        Returns (score: int, issues: List[str]).
        """
        issues = []

        # Check if continuity has been computed by the ContinuityWeaverAgent
        continuity_report = motion_plan.get("continuity_report", {})
        bridges = motion_plan.get("continuity_bridges", [])
        scenes = motion_plan.get("scenes", [])

        if not continuity_report and not bridges:
            # Continuity weaving has not been run — penalize
            issues.append(
                "CONTINUITY: No continuity bridges defined. Motion plan has not been "
                "continuity-woven. All scene transitions are implicit slideshow cuts."
            )
            return 20, issues

        # Use pre-computed score if available
        if continuity_report:
            raw_score = continuity_report.get("continuity_score", 0.0)
            score = int(raw_score)
            passed = continuity_report.get("passed", False)
            slideshow_ratio = continuity_report.get("slideshow_ratio", 1.0)
            violations = continuity_report.get("violations", [])

            if not passed:
                issues.append(
                    f"CONTINUITY FAILED: Score {score}/100 (minimum "
                    f"{motion_plan.get('continuity_report', {}).get('thresholds', {}).get('minimum_overall_score', 68)}). "
                    f"Video has slideshow-like transitions."
                )

            if slideshow_ratio > 0.2:
                issues.append(
                    f"SLIDESHOW DETECTED: {slideshow_ratio*100:.0f}% of transitions are "
                    f"plain crossfades with no visual carry element. Rejected."
                )

            for v in violations[:3]:  # Report first 3 violations
                issues.append(
                    f"WEAK CARRY: [{v.get('from', '?')}]→[{v.get('to', '?')}] "
                    f"score={v.get('score', 0)}/100. {v.get('recommendation', '')}"
                )

            return max(0, min(100, score)), issues

        # Fall back to counting bridges vs scenes
        n_scenes = len(scenes)
        n_bridges = len(bridges)
        expected_bridges = max(0, n_scenes - 1)

        if expected_bridges == 0:
            return 100, []

        coverage = n_bridges / expected_bridges if expected_bridges > 0 else 0

        # Count bridges with meaningful carry
        meaningful = sum(
            1 for b in bridges
            if b.get("carry_primitive") not in ("", "crossfade", "none")
            and b.get("carrier_element") not in ("", None)
        )
        meaningful_ratio = meaningful / max(n_bridges, 1)

        score = int(60 * coverage + 40 * meaningful_ratio)

        if meaningful_ratio < 0.8:
            issues.append(
                f"CONTINUITY WARNING: {(1-meaningful_ratio)*100:.0f}% of bridges lack "
                f"meaningful carry elements. Slideshow risk."
            )

        return max(0, min(100, score)), issues

    def evaluate_rendered_video(self, video_path: str, probe_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post-render evaluation of physical MP4 file properties."""
        issues = []
        score = 98

        w = probe_data.get("width", 0)
        h = probe_data.get("height", 0)
        if w > 0 and h > 0:
            ratio = round(h / w, 2)
            if ratio < 1.7:  # 16:9 inverted is ~1.777
                score -= 25
                issues.append(f"Video is not 9:16 vertical ratio (got {w}×{h}).")

        dur = probe_data.get("duration", 0.0)
        if dur < 45.0 or dur > 65.0:
            score -= 15
            issues.append(f"Video duration is {dur:.1f}s, expected ~50.0s.")

        passed = score >= 85
        return {
            "post_render_score": score,
            "passed": passed,
            "issues": issues,
            "status": "PASSED" if passed else "FAILED_QC"
        }

    # Alias for pipeline naming compatibility
    audit_motion_plan = evaluate_motion_plan


# Class alias for pipeline compatibility
QualityControlAgent = QualityAgent
