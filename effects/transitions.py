"""
effects/transitions.py
Cinematic transition effects: whip pan, zoom-through, light flash, directional blur.
"""
import numpy as np
from PIL import Image, ImageFilter


def transition_flash(img_a: Image.Image, img_b: Image.Image, t: float) -> Image.Image:
    """Quick white/light flash then reveal next scene."""
    w, h = img_a.size
    if t < 0.4:
        nt = t / 0.4
        # img_a fades to white
        white = Image.new("RGBA", (w, h), (220, 235, 255, 255))
        alpha = int(nt * 255)
        white.putalpha(alpha)
        result = img_a.copy().convert("RGBA")
        result.alpha_composite(white)
        return result.convert("RGB")
    else:
        nt = (t - 0.4) / 0.6
        # white fades to img_b
        white = Image.new("RGBA", (w, h), (220, 235, 255, 255))
        alpha = int((1 - nt) * 255)
        white.putalpha(alpha)
        result = img_b.copy().convert("RGBA")
        result.alpha_composite(white)
        return result.convert("RGB")


def transition_zoom_through(img_a: Image.Image, img_b: Image.Image, t: float) -> Image.Image:
    """Zoom into img_a then zoom out of img_b."""
    w, h = img_a.size
    smooth_t = t * t * (3 - 2 * t)  # smoothstep

    if smooth_t < 0.5:
        nt = smooth_t / 0.5
        zoom = 1.0 + nt * 0.25
        new_w = int(w / zoom)
        new_h = int(h / zoom)
        ox = (w - new_w) // 2
        oy = (h - new_h) // 2
        crop = img_a.crop((ox, oy, ox + new_w, oy + new_h))
        return crop.resize((w, h), Image.BILINEAR)
    else:
        nt = (smooth_t - 0.5) / 0.5
        zoom = 1.25 - nt * 0.25
        new_w = int(w / zoom)
        new_h = int(h / zoom)
        ox = (w - new_w) // 2
        oy = (h - new_h) // 2
        crop = img_b.crop((ox, oy, ox + new_w, oy + new_h))
        return crop.resize((w, h), Image.BILINEAR)


def transition_directional_blur(img_a: Image.Image, img_b: Image.Image,
                                 t: float, direction: str = "up") -> Image.Image:
    """Whip-pan style: blur + slide."""
    w, h = img_a.size
    smooth_t = t * t * (3 - 2 * t)

    # Directional offset
    if direction == "up":
        dy = -int(smooth_t * h * 0.6)
        dx = 0
    elif direction == "down":
        dy = int(smooth_t * h * 0.6)
        dx = 0
    elif direction == "left":
        dx = -int(smooth_t * w * 0.6)
        dy = 0
    else:
        dx = int(smooth_t * w * 0.6)
        dy = 0

    # Blend
    alpha = smooth_t

    # Shift img_a
    shifted_a = Image.new("RGB", (w, h), (10, 11, 16))
    src_a = img_a.crop((max(0, -dx), max(0, -dy),
                         w - max(0, dx), h - max(0, dy)))
    shifted_a.paste(src_a, (max(0, dx), max(0, dy)))

    # Motion blur on shifted
    blur_amount = int(smooth_t * 12 + 1)
    if blur_amount > 1:
        shifted_a = shifted_a.filter(ImageFilter.GaussianBlur(radius=blur_amount * 0.7))

    # Cross-fade
    result = Image.blend(shifted_a, img_b.convert("RGB"), alpha)
    return result


def transition_crossfade(img_a: Image.Image, img_b: Image.Image, t: float) -> Image.Image:
    smooth_t = t * t * (3 - 2 * t)
    return Image.blend(img_a.convert("RGB"), img_b.convert("RGB"), smooth_t)
