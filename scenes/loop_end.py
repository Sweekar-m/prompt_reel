"""
scenes/loop_end.py
LOOP ENDING scene: 44–50 seconds. Seamless callback to the opening hook.
Pairs Bold + Cursive + Flat typography with seamless visual crossfade.
"""
import math
from PIL import Image, ImageDraw
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import *
from effects.typography import (draw_animated_text, load_bold, load_flat, load_cursive,
                                 draw_mixed_line, ease_out_expo, ease_in_out_cubic)
from effects.particles import ParticleSystem
from effects.lighting import animated_light, apply_vignette, apply_film_grain
from scenes.hook import render_hook_frame
from templates.topic_registry import TopicConfig, get_topic_config

_particles = ParticleSystem(WIDTH, HEIGHT, count=90, seed=55)
_cached_hook_images = {}


def render_loop_frame(t: float, frame_idx: int, topic_cfg: TopicConfig = None) -> Image.Image:
    """t = absolute time (44..50 s). Returns 1080×1920 RGB."""
    if topic_cfg is None:
        topic_cfg = get_topic_config(TOPIC)

    t_local = t - T_LOOP_START
    t_norm  = min(t_local / (T_LOOP_END - T_LOOP_START), 1.0)

    img = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR + (255,))

    # Lighting (same as hook for seamless match cut)
    light = animated_light(WIDTH, HEIGHT, t, scene="loop")
    img = Image.alpha_composite(img, light)

    p = _particles.render(t * FPS, color=(99, 179, 237), alpha_scale=0.9)
    img = Image.alpha_composite(img, p)

    font_big  = load_bold(82)
    font_med  = load_bold(46)
    font_c    = load_cursive(52)
    font_r    = load_flat(38)

    # Phase 0–55%: payoff callback + multi-font callback text
    if t_norm < 0.55:
        phase = t_norm / 0.55
        if phase > 0.0:
            # Expressive cursive prompt: e.g. "And now?" or "Next time you see this..."
            draw_animated_text(img, topic_cfg.loop_cursive, WIDTH // 2, HEIGHT // 2 - 380,
                               font_c, ACCENT3,
                               ease_out_expo(min(phase / 0.3, 1.0)),
                               anim="rise", shadow=True)
        if phase > 0.20:
            draw_animated_text(img, "Every time you encounter this pattern...",
                               WIDTH // 2, HEIGHT // 2 - 260,
                               font_r, GRAY,
                               ease_out_expo(min((phase - 0.20) / 0.30, 1.0)),
                               anim="rise")
        if phase > 0.40:
            draw_animated_text(img, topic_cfg.loop_code_hint,
                               WIDTH // 2, HEIGHT // 2 - 120,
                               load_bold(46), ACCENT,
                               ease_out_expo(min((phase - 0.40) / 0.30, 1.0)),
                               anim="blur_reveal", glow=True, glow_color=ACCENT)

        if phase > 0.60:
            draw_mixed_line(
                img,
                [
                    ("You'll know ", "flat", 44, WHITE),
                    ("the exact secret.", "cursive", 48, HIGHLIGHT),
                ],
                WIDTH // 2, HEIGHT // 2 + 60,
                alpha=int(ease_out_expo(min((phase - 0.60) / 0.35, 1.0)) * 255)
            )

    # Phase 55–100%: crossfade back into hook frame 0
    else:
        phase = (t_norm - 0.55) / 0.45
        fade_out = 1.0 - ease_out_expo(min(phase / 0.4, 1.0))
        if fade_out > 0.05:
            draw_mixed_line(
                img,
                [
                    ("You'll know ", "flat", 44, WHITE),
                    ("the exact secret.", "cursive", 48, HIGHLIGHT),
                ],
                WIDTH // 2, HEIGHT // 2 + 60,
                alpha=int(fade_out * 255)
            )

        # Cross-fade in the hook frame (at t=0, cached by topic)
        if topic_cfg.id not in _cached_hook_images:
            _cached_hook_images[topic_cfg.id] = render_hook_frame(0.0, 0, topic_cfg=topic_cfg).convert("RGBA")
        hook_img = _cached_hook_images[topic_cfg.id]
        hook_blend_alpha = int(ease_out_expo(min(phase / 0.7, 1.0)) * 255)

        overlay = hook_img.copy()
        overlay.putalpha(hook_blend_alpha)
        img.alpha_composite(overlay)

    # Vignette + grain
    img = apply_vignette(img, strength=0.55)
    img = apply_film_grain(img, strength=0.012, t=t)
    return img.convert("RGB")
