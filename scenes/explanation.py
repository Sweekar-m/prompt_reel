"""
scenes/explanation.py
Explanation scene: 3–36 seconds.
Step 1 (3–18s): Curiosity + code editor appears + code typed out.
Step 2 (18–28s): Visual execution diagram with animated steps.
Step 3 (28–36s): Values animate, state/counter shown.
Supports any TopicConfig with Bold, Cursive, and Flat typography.
"""
import math
from PIL import Image, ImageDraw
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import *
from effects.typography import (draw_animated_text, draw_code_line, draw_glow_rect,
                                 load_bold, load_flat, load_cursive, load_mono,
                                 draw_mixed_line, draw_cursive_annotation,
                                 ease_out_expo, ease_in_out_cubic, ease_out_back,
                                 text_size)
from effects.particles import ParticleSystem
from effects.lighting import animated_light, apply_vignette, apply_film_grain
from templates.topic_registry import TopicConfig, get_topic_config

_particles = ParticleSystem(WIDTH, HEIGHT, count=60, seed=21)

# ─── Code panel geometry ────────────────────────────────────────────────────
PANEL_X  = 60
PANEL_Y  = 520
PANEL_W  = WIDTH - 120
PANEL_H  = 600
LINE_H   = 60    # line height for code
CODE_PAD = 48    # left padding inside panel (after line numbers)
LN_W     = 56    # line-number column width


def _draw_editor_panel(draw: ImageDraw.Draw, filename: str = "Main.java", alpha: int = 255) -> None:
    """Draw the dark code editor panel."""
    r, g, b = PANEL_COLOR
    draw.rectangle([PANEL_X, PANEL_Y, PANEL_X + PANEL_W, PANEL_Y + PANEL_H],
                    fill=(r, g, b, alpha))
    # top bar (tab bar)
    draw.rectangle([PANEL_X, PANEL_Y, PANEL_X + PANEL_W, PANEL_Y + 48],
                    fill=(22, 24, 34, alpha))
    # window buttons
    colors = [(252, 90, 90), (255, 188, 66), (62, 207, 142)]
    for i, c in enumerate(colors):
        bx = PANEL_X + 16 + i * 24
        by = PANEL_Y + 15
        draw.ellipse([bx, by, bx + 14, by + 14], fill=(*c, alpha))
    # tab label
    tab_font = load_flat(24)
    draw.text((PANEL_X + 90, PANEL_Y + 13), filename, font=tab_font,
               fill=(180, 190, 210, alpha))

    # line-number separator
    sep_x = PANEL_X + LN_W + CODE_PAD - 6
    draw.line([(sep_x, PANEL_Y + 48), (sep_x, PANEL_Y + PANEL_H)],
               fill=(40, 45, 60, alpha), width=1)


def _code_y(line_idx: int) -> int:
    return PANEL_Y + 48 + 24 + line_idx * LINE_H


def _draw_code_with_reveal(img: Image.Image, code_lines: list, line_nums: list, char_progress: float) -> None:
    """Render the code with typing reveal effect."""
    mono = load_mono(36)
    ln_font = load_flat(28)
    draw = ImageDraw.Draw(img)

    all_chars_per_line = []
    for line in code_lines:
        line_str = "".join(seg for seg, _ in line)
        all_chars_per_line.append(len(line_str))

    remaining = int(char_progress)
    for li, (line_tokens, ln_str) in enumerate(zip(code_lines, line_nums)):
        line_len = all_chars_per_line[li]
        chars_this_line = min(remaining, line_len)
        remaining -= chars_this_line

        if chars_this_line <= 0:
            break

        ly = _code_y(li)
        draw.text((PANEL_X + 12, ly + 6), str(ln_str), font=ln_font,
                   fill=(*COMMENT_COLOR, 180))

        cx = PANEL_X + LN_W + CODE_PAD
        shown_chars_in_line = chars_this_line
        for seg_text, seg_color in line_tokens:
            if shown_chars_in_line <= 0:
                break
            visible = seg_text[:shown_chars_in_line]
            draw.text((cx, ly + 4), visible, font=mono, fill=(*seg_color, 255))
            w, _ = text_size(visible, mono)
            cx += w
            shown_chars_in_line -= len(seg_text)

        # Cursor
        if remaining <= 0 and chars_this_line < line_len:
            draw.rectangle([cx + 2, ly + 4, cx + 14, ly + 40], fill=(*ACCENT, 220))


def _draw_full_code(img: Image.Image, code_lines: list, line_nums: list,
                    highlight_line: int = None, highlight_alpha: int = 120) -> None:
    """Draw complete code, optionally with a highlighted line."""
    draw = ImageDraw.Draw(img)
    mono = load_mono(36)
    ln_font = load_flat(28)

    if highlight_line is not None and 0 <= highlight_line < len(code_lines):
        hy = _code_y(highlight_line)
        draw_glow_rect(img, PANEL_X + 1, hy - 4, PANEL_X + PANEL_W - 1, hy + LINE_H - 8,
                       ACCENT, alpha=highlight_alpha, blur=12)
        draw.rectangle([PANEL_X + 1, hy - 4, PANEL_X + PANEL_W - 1, hy + LINE_H - 8],
                        fill=(ACCENT[0], ACCENT[1], ACCENT[2], 30))

    for li, (line_tokens, ln_str) in enumerate(zip(code_lines, line_nums)):
        ly = _code_y(li)
        draw.text((PANEL_X + 12, ly + 6), str(ln_str), font=ln_font,
                   fill=(*COMMENT_COLOR, 200))
        cx = PANEL_X + LN_W + CODE_PAD
        for seg_text, seg_color in line_tokens:
            draw.text((cx, ly + 4), seg_text, font=mono, fill=(*seg_color, 255))
            w, _ = text_size(seg_text, mono)
            cx += w


def _draw_execution_diagram(img: Image.Image, t: float, current_step: int,
                            highlight_step: int, alpha: float, boxes: list) -> None:
    """Draws procedural 5-box flowchart with active glowing stage."""
    draw = ImageDraw.Draw(img)
    box_w = 420
    box_h = 72
    box_x = WIDTH // 2 - box_w // 2
    start_y = PANEL_Y + PANEL_H + 40
    spacing = 100

    font_b = load_bold(30)
    font_r = load_flat(22)

    for idx, b_info in enumerate(boxes):
        by = start_y + idx * spacing
        is_active = (idx == current_step)
        color = b_info.get("color", ACCENT)
        label = b_info.get("label", "")
        sub = b_info.get("sub", "")

        box_alpha = int(alpha * (255 if is_active else 120))
        r, g, b_col = PANEL_COLOR
        draw.rectangle([box_x, by, box_x + box_w, by + box_h],
                        fill=(r, g, b_col, box_alpha))

        if is_active and alpha > 0.2:
            draw_glow_rect(img, box_x - 4, by - 4, box_x + box_w + 4, by + box_h + 4,
                           color, alpha=int(box_alpha * 0.6), blur=14)

        cr, cg, cb = color[:3]
        border_a = box_alpha if is_active else int(box_alpha * 0.4)
        draw.rectangle([box_x, by, box_x + box_w, by + box_h],
                        outline=(cr, cg, cb, border_a), width=2)

        draw.text((box_x + 16, by + 10), label, font=font_b, fill=(cr, cg, cb, box_alpha))
        if sub:
            draw.text((box_x + 16, by + 42), sub, font=font_r, fill=(*WHITE, int(box_alpha * 0.75)))

        if idx < len(boxes) - 1:
            ax = box_x + box_w // 2
            ay1 = by + box_h
            ay2 = by + spacing
            draw.line([(ax, ay1), (ax, ay2)], fill=(*GRAY, int(alpha * 120)), width=2)
            draw.polygon([(ax - 6, ay2 - 10), (ax + 6, ay2 - 10), (ax, ay2)],
                          fill=(*GRAY, int(alpha * 120)))


def _draw_counter(img: Image.Image, label: str, current_val: str, alpha: float) -> None:
    """Large animated state/counter display."""
    font_title = load_flat(32)
    font_counter = load_bold(105)
    a = int(alpha * 255)
    cx = WIDTH // 2
    cy = 280

    draw_glow_rect(img, cx - 220, cy - 80, cx + 220, cy + 80,
                   ACCENT, alpha=int(a * 0.45), blur=30)
    draw_animated_text(img, label, cx, cy - 85,
                       font_title, GRAY, 1.0, anim="fade", max_alpha=int(a * 0.8))
    draw_animated_text(img, str(current_val), cx, cy + 10,
                       font_counter, ACCENT, 1.0, anim="fade",
                       glow=True, glow_color=ACCENT, shadow=True, max_alpha=a)


def render_explanation_frame(t: float, frame_idx: int, topic_cfg: TopicConfig = None) -> Image.Image:
    """Renders frame in the 3..36s explanation window."""
    if topic_cfg is None:
        topic_cfg = get_topic_config(TOPIC)

    t_local = t - T_CURIOSITY_START

    img = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR + (255,))
    light_layer = animated_light(WIDTH, HEIGHT, t, scene="editor")
    img = Image.alpha_composite(img, light_layer)

    p_layer = _particles.render(t * FPS, color=(99, 179, 237), alpha_scale=0.5)
    img = Image.alpha_composite(img, p_layer)
    draw = ImageDraw.Draw(img)

    font_b = load_bold(50)
    font_b2 = load_bold(44)
    font_r = load_flat(34)
    font_c = load_cursive(38)

    # ── Phase 1: 3–8s Curiosity + Code typing
    if t_local < 5.0:
        phase = t_local / 5.0
        # Multi-font Title Lockup
        draw_animated_text(img, "Let's look at this code.",
                           WIDTH // 2, 230, font_b, WHITE,
                           ease_out_expo(min(phase / 0.35, 1.0)), anim="rise")

        # Mixed font subtext
        if phase > 0.2:
            sub_t = ease_out_expo(min((phase - 0.2) / 0.35, 1.0))
            draw_mixed_line(img, [
                ("Three parts. ", "flat", 34, GRAY),
                ("One powerful pattern.", "cursive", 38, ACCENT3)
            ], WIDTH // 2, 320, alpha=int(sub_t * 255))

        panel_a = int(ease_out_expo(min(phase / 0.4, 1.0)) * 255)
        _draw_editor_panel(draw, filename=topic_cfg.filename, alpha=panel_a)

        # Typing progress
        typing_dur = 3.0
        type_p = max(0.0, min((t_local - 1.2) / typing_dur, 1.0))
        total_chars = sum(len("".join(s for s, _ in l)) for l in topic_cfg.code_lines)
        chars = total_chars * ease_in_out_cubic(type_p)
        _draw_code_with_reveal(img, topic_cfg.code_lines, topic_cfg.line_numbers, chars)

    # ── Phase 2: 8–18s Step 1
    elif t_local < 15.0:
        phase = (t_local - 5.0) / 10.0
        _draw_editor_panel(draw, filename=topic_cfg.filename)

        if phase < 0.40:
            sub_p = phase / 0.40
            draw_animated_text(img, topic_cfg.step1_title,
                               WIDTH // 2, 175, font_b, ACCENT3,
                               ease_out_expo(min(sub_p / 0.25, 1.0)), anim="rise")
            draw_animated_text(img, topic_cfg.step1_cursive,
                               WIDTH // 2, 232, font_c, WHITE,
                               ease_out_expo(min((sub_p - 0.05) / 0.25, 1.0)), anim="fade")
            draw_animated_text(img, topic_cfg.step1_desc,
                               WIDTH // 2, 285, font_r, GRAY,
                               ease_out_expo(min((sub_p - 0.1) / 0.25, 1.0)), anim="rise")
            _draw_full_code(img, topic_cfg.code_lines, topic_cfg.line_numbers,
                            highlight_line=topic_cfg.step1_highlight_line, highlight_alpha=160)

            # Cursive arrow annotation
            hl = topic_cfg.step1_highlight_line
            line_str = "".join(seg for seg, _ in topic_cfg.code_lines[hl])
            line_w, _ = text_size(line_str, load_mono(36))
            annot_x = PANEL_X + LN_W + CODE_PAD + line_w + 70
            draw_cursive_annotation(img, topic_cfg.step1_annotation,
                                   annot_x, _code_y(hl) + 4,
                                   alpha=int(ease_out_expo(min(sub_p / 0.3, 1.0)) * 255),
                                   color=ACCENT3, size=32, arrow="left")
        else:
            sub_p = (phase - 0.40) / 0.60
            draw_animated_text(img, "Execution Flow",
                               WIDTH // 2, 175, font_b, HIGHLIGHT,
                               ease_out_expo(min(sub_p / 0.25, 1.0)), anim="rise")
            draw_animated_text(img, "active body in real time",
                               WIDTH // 2, 232, font_c, ACCENT3,
                               ease_out_expo(min((sub_p - 0.05) / 0.25, 1.0)), anim="fade")
            draw_animated_text(img, "The instructions run immediately.",
                               WIDTH // 2, 285, font_r, WHITE,
                               ease_out_expo(min((sub_p - 0.1) / 0.3, 1.0)), anim="rise")
            _draw_full_code(img, topic_cfg.code_lines, topic_cfg.line_numbers,
                            highlight_line=min(1, len(topic_cfg.code_lines) - 1), highlight_alpha=160)

    # ── Phase 3: 18–28s Step 2 (Visual Diagram)
    elif t_local < 25.0:
        phase = (t_local - 15.0) / 10.0
        _draw_editor_panel(draw, filename=topic_cfg.filename)
        _draw_full_code(img, topic_cfg.code_lines, topic_cfg.line_numbers)

        draw_animated_text(img, topic_cfg.step2_title,
                           WIDTH // 2, 175, font_b, ACCENT2,
                           ease_out_expo(min(phase / 0.25, 1.0)), anim="rise")
        draw_animated_text(img, topic_cfg.step2_cursive,
                           WIDTH // 2, 232, font_c, ACCENT3,
                           ease_out_expo(min((phase - 0.05) / 0.25, 1.0)), anim="fade")
        draw_animated_text(img, "Step by step cycle in hardware.",
                           WIDTH // 2, 285, font_r, GRAY,
                           ease_out_expo(min((phase - 0.1) / 0.3, 1.0)), anim="fade")

        current_step = min(int(phase * len(topic_cfg.diagram_boxes)), len(topic_cfg.diagram_boxes) - 1)
        diagram_alpha = ease_out_expo(min(phase / 0.2, 1.0))
        _draw_execution_diagram(img, t, current_step, 0, diagram_alpha, topic_cfg.diagram_boxes)

    # ── Phase 4: 28–36s Step 3 (Values / Counter)
    else:
        phase = (t_local - 25.0) / 8.0
        val_idx = min(int(phase * len(topic_cfg.step3_values)), len(topic_cfg.step3_values) - 1)
        cur_val = topic_cfg.step3_values[val_idx]
        counter_alpha = ease_out_expo(min(phase / 0.2, 1.0))
        _draw_counter(img, topic_cfg.step3_counter_label, cur_val, counter_alpha)

        _draw_editor_panel(draw, filename=topic_cfg.filename)
        _draw_full_code(img, topic_cfg.code_lines, topic_cfg.line_numbers,
                        highlight_line=min(1, len(topic_cfg.code_lines) - 1), highlight_alpha=140)

        draw_animated_text(img, topic_cfg.step3_output,
                           WIDTH // 2, PANEL_Y + PANEL_H + 60,
                           font_b2, HIGHLIGHT,
                           ease_out_expo(min(phase / 0.3, 1.0)), anim="rise",
                           glow=True, glow_color=HIGHLIGHT)

        # Cursive final note
        draw_animated_text(img, "Zero manual effort required.",
                           WIDTH // 2, PANEL_Y + PANEL_H + 140,
                           font_c, ACCENT3,
                           ease_out_expo(min((phase - 0.15) / 0.3, 1.0)), anim="fade")

    # Vignette + grain
    img = apply_vignette(img, strength=0.45)
    img = apply_film_grain(img, strength=0.010, t=t)
    return img.convert("RGB")
