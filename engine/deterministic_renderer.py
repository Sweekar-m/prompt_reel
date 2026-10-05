"""
engine/deterministic_renderer.py
================================
Deterministic Multi-Style Render Engine.
Renders individual frames strictly based on the Motion Plan JSON.
Does NOT invent content — translates creative direction into math and pixels.
"""
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, Tuple, Optional

from effects.typography_registry import load_font
from effects.palettes import ColorPalette, get_palette
from effects.lighting import animated_light, apply_vignette
from effects.camera import Camera, interpolate_camera
from engine.metaphor_renderer import render_metaphor_frame

WIDTH = 1080
HEIGHT = 1920


def render_motion_plan_frame(
    motion_plan: Dict[str, Any],
    t: float,
    frame_idx: int,
    canvas_size: Tuple[int, int] = (1080, 1920)
) -> Image.Image:
    """
    Renders a single frame at time t (in seconds) deterministically
    from a verified Motion Plan.
    """
    W, H = canvas_size
    cd = motion_plan["creative_direction"]
    palette_data = cd["palette"]
    palette_id = palette_data.get("id", "electric_matrix")
    palette = get_palette(palette_id)
    font_pair_id = cd["typography"]["id"]

    # 1. Base Canvas with background color
    bg = palette.background
    frame = Image.new("RGBA", (W, H), (bg[0], bg[1], bg[2], 255))
    draw = ImageDraw.Draw(frame)

    # 2. Lighting & Style Environment
    style_id = cd.get("style_id", "cyberpunk")
    light_scene = "hook" if t < 4.0 else ("editor" if t < 35.0 else "payoff")
    light_layer = animated_light(W, H, t, scene=light_scene)
    frame.alpha_composite(light_layer)

    # 3. Locate active scene from Motion Plan
    scenes = motion_plan.get("scenes", [])
    active_scene = None
    for sc in scenes:
        if sc["start"] <= t <= sc["end"]:
            active_scene = sc
            break
    if active_scene is None and scenes:
        active_scene = scenes[-1] if t >= scenes[-1]["end"] else scenes[0]

    # Calculate local normalized progress within scene (0.0 to 1.0)
    dur = max(active_scene["duration"], 0.1)
    local_p = min(max((t - active_scene["start"]) / dur, 0.0), 1.0)
    ease_p = 1.0 - math.pow(1.0 - local_p, 3) # ease-out cubic

    v_type = active_scene.get("visual_type", "hook")
    elems = active_scene.get("elements", {})

    # Calculate scale relative to reference 1080x1920
    scale = W / 1080.0
    mid_x = W // 2

    font_huge = load_font(font_pair_id, "heading", int(72 * scale))
    font_title = load_font(font_pair_id, "heading", int(48 * scale))
    font_body = load_font(font_pair_id, "body", int(32 * scale))
    font_mono = load_font(font_pair_id, "mono", int(26 * scale))

    def draw_text_centered(text: str, cy: int, font: ImageFont.ImageFont, fill: Tuple[int, ...], max_w: Optional[int] = None):
        """Draws single line or wrapped lines centered horizontally at cy."""
        if not text:
            return
        # Basic word wrap if max_w provided
        target_w = max_w or int(W * 0.85)
        words = text.split()
        lines = []
        cur_line = []
        for word in words:
            test_line = " ".join(cur_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if (bbox[2] - bbox[0]) <= target_w or not cur_line:
                cur_line.append(word)
            else:
                lines.append(" ".join(cur_line))
                cur_line = [word]
        if cur_line:
            lines.append(" ".join(cur_line))

        # Render each line stacked around cy
        line_height = int(font.size * 1.25)
        total_h = len(lines) * line_height
        top_y = cy - total_h // 2
        for i, l in enumerate(lines):
            bbox = draw.textbbox((0, 0), l, font=font)
            lw = bbox[2] - bbox[0]
            lx = (W - lw) // 2
            ly = top_y + i * line_height
            draw.text((lx, ly), l, fill=fill, font=font)

    # ── Scene Type Dispatch ──────────────────────────────────────────────────
    if v_type == "hook":
        # ── Viral Hook Scene ──
        badge_text = elems.get("badge", motion_plan["topic"].upper())
        draw_text_centered(f"[ {badge_text} ]", int(H * 0.30), font_mono, (*palette.accent, 220))

        # Dividing animated line
        line_w = int(ease_p * (W * 0.75))
        line_y = int(H * 0.35)
        draw.line([(mid_x - line_w // 2, line_y), (mid_x + line_w // 2, line_y)],
                  fill=(*palette.primary, int(ease_p * 200)), width=max(2, int(3 * scale)))

        # Headline
        headline = elems.get("headline", "CAN YOU SOLVE THIS?")
        draw_text_centered(headline, int(H * 0.44), font_huge, (*palette.primary, 255), max_w=int(W * 0.88))

        # Subtext
        if local_p > 0.15:
            sub = elems.get("subtext", "Watch what happens in hardware.")
            draw_text_centered(sub, int(H * 0.55), font_body, (*palette.subtext, 255), max_w=int(W * 0.85))

    elif v_type == "metaphor":
        # ── Tactile Procedural Metaphor Scene ──
        meta_id = elems.get("metaphor_id", "tabbed_book_index")
        label = elems.get("label", "MENTAL MODEL")
        draw_text_centered(label, int(H * 0.12), font_title, (*palette.primary, 240))

        desc = elems.get("description", "")
        if desc:
            draw_text_centered(desc, int(H * 0.17), font_body, (*palette.subtext, 200), max_w=int(W * 0.85))

        meta_layer = render_metaphor_frame(
            metaphor_id=meta_id,
            progress=local_p,
            canvas_size=(W, H),
            primary_color=palette.primary,
            secondary_color=palette.secondary,
            accent_color=palette.accent,
            surface_color=palette.surface,
            font=font_mono
        )
        frame.alpha_composite(meta_layer)

    elif v_type == "code":
        # ── Code Dissection Scene ──
        filename = elems.get("filename", "solution.py")
        draw_text_centered(filename, int(H * 0.12), font_mono, (*palette.accent, 255))

        # Editor container
        pad_x = int(W * 0.08)
        pad_y = int(H * 0.16)
        box_w = W - (pad_x * 2)
        box_h = int(H * 0.60)
        draw.rectangle([pad_x, pad_y, pad_x + box_w, pad_y + box_h],
                       fill=(*palette.surface, 235), outline=(*palette.primary, 140), width=max(1, int(2 * scale)))
        # Window controls
        colors = [(252, 90, 90), (255, 188, 66), (62, 207, 142)]
        dot_r = max(4, int(7 * scale))
        for i, c in enumerate(colors):
            bx = pad_x + int(20 * scale) + i * int(22 * scale)
            by = pad_y + int(14 * scale)
            draw.ellipse([bx, by, bx + dot_r * 2, by + dot_r * 2], fill=c)

        # Code lines
        lines = elems.get("lines", [])
        hl_idx = elems.get("highlight_line", 2) - 1
        line_spacing = int(46 * scale)
        for idx, line in enumerate(lines[:10]):
            ly = pad_y + int(50 * scale) + idx * line_spacing
            is_hl = (idx == hl_idx)
            if is_hl:
                draw.rectangle([pad_x + 4, ly - 2, pad_x + box_w - 4, ly + line_spacing - 4],
                               fill=(palette.primary[0], palette.primary[1], palette.primary[2], 55))
            col = palette.text if not is_hl else palette.primary
            draw.text((pad_x + int(30 * scale), ly), f"{idx+1}  {line}", fill=(*col, 255), font=font_mono)

        # Annotation note
        annot = elems.get("annotation", "critical logic")
        draw_text_centered(f"Note: {annot}", pad_y + box_h + int(40 * scale), font_body, (*palette.accent, 240))

    elif v_type == "split" or v_type == "benchmark":
        # ── Side-by-Side Comparison ──
        draw_text_centered("PERFORMANCE CONTRAST", int(H * 0.12), font_title, (*palette.primary, 255))

        stat = elems.get("stat_callout", "100x FASTER")
        draw_text_centered(stat, int(H * 0.20), font_huge, (*palette.accent, 255))

        # Left (Without)
        left_x = int(W * 0.08)
        draw.text((left_x, int(H * 0.32)), "WITHOUT", fill=(255, 80, 80, 255), font=font_title)
        draw.line([(left_x, int(H * 0.38)), (mid_x - int(20 * scale), int(H * 0.38))], fill=(255, 80, 80, 220), width=3)
        for i, l in enumerate(elems.get("left_code", [])[:6]):
            draw.text((left_x, int(H * 0.40) + i * int(38 * scale)), l[:20], fill=(*palette.subtext, 220), font=font_mono)

        # Right (With)
        right_x = mid_x + int(20 * scale)
        draw.text((right_x, int(H * 0.32)), "WITH", fill=(60, 220, 120, 255), font=font_title)
        draw.rectangle([right_x - 6, int(H * 0.38), W - int(W * 0.08), int(H * 0.70)],
                       fill=(*palette.surface, 220), outline=(60, 220, 120, 180), width=2)
        for i, l in enumerate(elems.get("right_code", [])[:6]):
            draw.text((right_x + 8, int(H * 0.40) + i * int(38 * scale)), l[:20], fill=(*palette.text, 255), font=font_mono)

    else:
        # ── Diagram / Payoff Scene ──
        title = elems.get("title", "KEY ARCHITECTURE")
        draw_text_centered(title, int(H * 0.22), font_title, (*palette.primary, 255))

        stat = elems.get("stat", "O(log N)")
        draw_text_centered(stat, int(H * 0.38), font_huge, (*palette.accent, 255))

        sub = elems.get("subtitle", "Pure mathematical efficiency.")
        draw_text_centered(sub, int(H * 0.52), font_body, (*palette.subtext, 255), max_w=int(W * 0.85))

    # 4. Vignette Polish
    vig_strength = 0.50 if palette.is_dark else 0.20
    frame = apply_vignette(frame, strength=vig_strength)

    return frame.convert("RGB")
