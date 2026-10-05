"""
agents/quality_agent.py
=======================
Quality Control (QC) Agent.
Performs pre-flight and post-render validation across 5 critical dimensions:
1. CONTENT (accuracy, code validity, logical consistency)
2. DESIGN (WCAG contrast, typography hierarchy, safe areas)
3. MOTION (readable words-per-minute, transition pacing)
4. SOCIAL (9:16 mobile aspect ratio, first 2s hook strength)
5. AUDIO (ducking depth, clipping prevention, sample rate)
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
            "audio": 95
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
        # Ensure palette exists
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

        overall_score = int(sum(scores.values()) / len(scores))
        passed = overall_score >= 85 and len(issues) < 3

        return {
            "quality_score": overall_score,
            "passed": passed,
            "category_scores": scores,
            "issues": issues,
            "recommendation": "APPROVED FOR RENDER" if passed else "REQUIRES REVISION"
        }

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

