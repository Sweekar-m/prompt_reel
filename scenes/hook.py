"""
scenes/hook.py
HOOK scene: 0–3 seconds. Strong cinematic opening with multi-font kinetic typography.
Pairs Bold display + expressive Cursive + clean Flat sans.
"""
import math
from PIL import Image, ImageDraw
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import *
from effects.typography import (draw_animated_text, load_bold, load_flat, load_cursive,
                                draw_mixed_line, draw_paired_title,
                                ease_out_expo, ease_out_back)
from effects.particles import ParticleSystem
from effects.lighting import animated_light, apply_vignette, apply_film_grain
from templates.topic_registry import TopicConfig, get_topic_config

_particles_main = ParticleSystem(WIDTH, HEIGHT, count=100, seed=7)
_particles_bg   = ParticleSystem(WIDTH, HEIGHT, count=50, seed=13)


def render_hook_frame(t: float, frame_idx: int, topic_cfg: TopicConfig = None) -> Image.Image:
    """
    t = absolute time in seconds (0..3).
    Returns a 1080×1920 RGB PIL image.
    """
    if topic_cfg is None:
        topic_cfg = get_topic_config(TOPIC)

    tn = min(t / 3.0, 1.0)   # normalized 0..1 within hook

    # ── Background ─────────────────────────────────────────────────────────
    img = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR + (255,))

    # ── Lighting ────────────────────────────────────────────────────────────
    light_layer = animated_light(WIDTH, HEIGHT, t, scene="hook")
    img = Image.alpha_composite(img, light_layer)

    # ── Particles ───────────────────────────────────────────────────────────
    p_layer = _particles_bg.render(t * FPS, color=(99, 179, 237), alpha_scale=0.6)
    img = Image.alpha_composite(img, p_layer)
    p_layer2 = _particles_main.render(t * FPS, color=(159, 122, 234), alpha_scale=0.8)
    img = Image.alpha_composite(img, p_layer2)

    draw = ImageDraw.Draw(img)

    # ── Thin horizontal accent line ─────────────────────────────────────────
    if tn > 0.2:
        line_alpha = int(ease_out_expo((tn - 0.2) / 0.8) * 180)
        cy = HEIGHT // 2 - 250
        line_w = int(ease_out_expo((tn - 0.2) / 0.8) * (WIDTH - 120))
        x_start = WIDTH // 2 - line_w // 2
        x_end   = WIDTH // 2 + line_w // 2
        draw.rectangle([x_start, cy - 1, x_end, cy + 1],
                        fill=(ACCENT[0], ACCENT[1], ACCENT[2], line_alpha))

    # ── Multi-Font Kinetic Typography ───────────────────────────────────────
    # 1. Cursive casual lead-in ("wait... did you know")
    if tn > 0.05:
        t1 = ease_out_back(min((tn - 0.05) / 0.3, 1.0))
        draw_animated_text(img, topic_cfg.hook_lead, WIDTH // 2, HEIGHT // 2 - 340,
                           load_cursive(46), ACCENT3, t1, anim="fade", shadow=True)

    # 2. Heavy Bold Title ("HOW LOOPS RUN" or "WHAT RECURSION")
    if tn > 0.22:
        t2 = ease_out_back(min((tn - 0.22) / 0.35, 1.0))
        draw_animated_text(img, topic_cfg.hook_bold, WIDTH // 2, HEIGHT // 2 - 180,
                           load_bold(92), WHITE, t2, anim="scale",
                           glow=True, glow_color=ACCENT, shadow=True)

    # 3. Flat clean subtitle ("what actually happens under the hood?")
    if tn > 0.38:
        t3 = ease_out_expo(min((tn - 0.38) / 0.35, 1.0))
        draw_animated_text(img, topic_cfg.hook_flat, WIDTH // 2, HEIGHT // 2 - 80,
                           load_flat(38), GRAY, t3, anim="rise", shadow=True)

    # 4. Big accent word (e.g. "FOR LOOP" or "RECURSION")
    if tn > 0.55:
        t4 = ease_out_back(min((tn - 0.55) / 0.45, 1.0))
        draw_animated_text(img, topic_cfg.hook_tag, WIDTH // 2, HEIGHT // 2 + 55,
                           load_bold(68), ACCENT, t4, anim="blur_reveal",
                           glow=True, glow_color=ACCENT)

    # 5. Mixed Font Bottom Hint: Flat + Cursive
    if tn > 0.72:
        t5 = ease_out_expo(min((tn - 0.72) / 0.28, 1.0))
        alpha_t5 = int(t5 * 255)
        draw_mixed_line(
            img,
            [
                (topic_cfg.curiosity_cursive + " ", "cursive", 40, ACCENT3),
                (topic_cfg.curiosity_bold, "bold", 34, WHITE),
            ],
            WIDTH // 2, HEIGHT // 2 + 200,
            alpha=alpha_t5
        )

    # ── Vignette + grain ────────────────────────────────────────────────────
    img = apply_vignette(img, strength=0.55)
    img = apply_film_grain(img, strength=0.012, t=t)

    return img.convert("RGB")
