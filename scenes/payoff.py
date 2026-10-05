"""
scenes/payoff.py
PAYOFF scene: 36–44 seconds. Cinematic reveal of the key insight.
Supports any TopicConfig with Bold, Cursive, and Flat typography.
"""
import math
from PIL import Image, ImageDraw
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import *
from effects.typography import (draw_animated_text, draw_glow_rect,
                                 load_bold, load_flat, load_cursive, load_mono,
                                 draw_mixed_line, draw_cursive_annotation,
                                 ease_out_expo, ease_out_back, ease_in_out_cubic,
                                 text_size)
from effects.particles import ParticleSystem
from effects.lighting import animated_light, apply_vignette, apply_film_grain
from templates.topic_registry import TopicConfig, get_topic_config

_particles = ParticleSystem(WIDTH, HEIGHT, count=80, seed=99)


def render_payoff_frame(t: float, frame_idx: int, topic_cfg: TopicConfig = None) -> Image.Image:
    """t = absolute time (36..44 s). Returns 1080×1920 RGB."""
    if topic_cfg is None:
        topic_cfg = get_topic_config(TOPIC)

    t_local = t - T_PAYOFF_START
    t_norm  = min(t_local / (T_PAYOFF_END - T_PAYOFF_START), 1.0)

    img = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR + (255,))

    # Light
    light = animated_light(WIDTH, HEIGHT, t, scene="payoff")
    img = Image.alpha_composite(img, light)

    # Particles
    p = _particles.render(t * FPS, color=(62, 207, 142), alpha_scale=1.0)
    img = Image.alpha_composite(img, p)

    draw = ImageDraw.Draw(img)
    font_huge = load_bold(110)
    font_med  = load_bold(50)
    font_r    = load_flat(38)
    font_c    = load_cursive(44)

    # ── Phase 1: Giant Stat + Cursive Tagline (0–30%)
    if t_norm > 0.02:
        t1 = ease_out_back(min((t_norm - 0.02) / 0.28, 1.0))
        # Cursive accent above stat
        draw_animated_text(img, topic_cfg.payoff_cursive, WIDTH // 2, HEIGHT // 2 - 530,
                           font_c, ACCENT3, t1, anim="fade", shadow=True)
        # Giant Bold Stat
        draw_animated_text(img, topic_cfg.payoff_stat, WIDTH // 2, HEIGHT // 2 - 440,
                           font_huge, ACCENT, t1, anim="scale",
                           glow=True, glow_color=ACCENT, shadow=True)

    # ── Phase 2: Code comparison block (30–60%)
    mono = load_mono(28)
    if t_norm > 0.28:
        t2 = ease_out_expo(min((t_norm - 0.28) / 0.25, 1.0))
        a2 = int(t2 * 255)

        # "Before / Without" side + drawn red X
        draw.text((120, HEIGHT // 2 - 320), "Without", font=load_bold(34),
                   fill=(*RED_ERR, a2))
        cx_x, cy_x = 280, HEIGHT // 2 - 304
        draw.line([(cx_x - 8, cy_x - 8), (cx_x + 8, cy_x + 8)], fill=(*RED_ERR, a2), width=3)
        draw.line([(cx_x + 8, cy_x - 8), (cx_x - 8, cy_x + 8)], fill=(*RED_ERR, a2), width=3)

        for li, line in enumerate(topic_cfg.payoff_before):
            ly = HEIGHT // 2 - 265 + li * 44
            draw.text((120, ly), line, font=mono, fill=(*GRAY, a2))

        # Strike-through effect
        if t2 > 0.5:
            st_a = int((t2 - 0.5) / 0.5 * 200)
            draw.line([(110, HEIGHT // 2 - 250),
                        (WIDTH // 2 - 40, HEIGHT // 2 + 10)],
                       fill=(*RED_ERR, st_a), width=3)

    # "With / After" side (40–70%)
    if t_norm > 0.38:
        t3 = ease_out_expo(min((t_norm - 0.38) / 0.25, 1.0))
        a3 = int(t3 * 255)

        # "With" label + drawn green checkmark
        draw.text((WIDTH // 2 + 20, HEIGHT // 2 - 320), "With", font=load_bold(34),
                   fill=(*HIGHLIGHT, a3))
        cx_c, cy_c = WIDTH // 2 + 120, HEIGHT // 2 - 304
        draw.line([(cx_c - 10, cy_c), (cx_c - 3, cy_c + 8)], fill=(*HIGHLIGHT, a3), width=3)
        draw.line([(cx_c - 3, cy_c + 8), (cx_c + 10, cy_c - 8)], fill=(*HIGHLIGHT, a3), width=3)

        # Glowing code block
        draw_glow_rect(img, WIDTH // 2 + 14, HEIGHT // 2 - 275,
                       WIDTH - 80, HEIGHT // 2 + 30,
                       HIGHLIGHT, alpha=int(a3 * 0.3), blur=18)
        draw.rectangle([WIDTH // 2 + 14, HEIGHT // 2 - 275,
                         WIDTH - 80, HEIGHT // 2 + 30],
                        fill=(*PANEL_COLOR, int(a3 * 0.85)))

        cx_code = WIDTH // 2 + 30
        for li, line_toks in enumerate(topic_cfg.payoff_after):
            ly = HEIGHT // 2 - 245 + li * 50
            cx = cx_code
            for seg, col in line_toks:
                r, g, b = col
                draw.text((cx, ly), seg, font=mono, fill=(r, g, b, a3))
                w, _ = text_size(seg, mono)
                cx += w

    # ── Phase 3: Key insight text (55–85%)
    if t_norm > 0.52:
        t4 = ease_out_expo(min((t_norm - 0.52) / 0.30, 1.0))
        draw_animated_text(img, topic_cfg.payoff_takeaway, WIDTH // 2, HEIGHT // 2 + 110,
                           font_med, ACCENT3, t4, anim="blur_reveal",
                           glow=True, glow_color=ACCENT3)

    if t_norm > 0.66:
        t5 = ease_out_expo(min((t_norm - 0.66) / 0.25, 1.0))
        draw_mixed_line(img, [
            ("Consistent result. ", "flat", 36, WHITE),
            ("Every single time.", "cursive", 40, HIGHLIGHT)
        ], WIDTH // 2, HEIGHT // 2 + 205, alpha=int(t5 * 255))

    if t_norm > 0.78:
        t6 = ease_out_expo(min((t_norm - 0.78) / 0.22, 1.0))
        draw_animated_text(img, f"That's the power of {topic_cfg.hook_tag.lower()}.", WIDTH // 2, HEIGHT // 2 + 295,
                           font_r, GRAY, t6, anim="fade")

    # Vignette + grain
    img = apply_vignette(img, strength=0.50)
    img = apply_film_grain(img, strength=0.011, t=t)
    return img.convert("RGB")
