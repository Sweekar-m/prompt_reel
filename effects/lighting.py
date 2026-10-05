"""
effects/lighting.py
Procedural cinematic lighting: radial light, streaks, lens flare, edge glow.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import WIDTH, HEIGHT, ACCENT, ACCENT2


_UNIT_RADIAL_MASK: Image.Image = None
_STATIC_RADIAL_CACHE: dict = {}

def _get_unit_radial_mask() -> Image.Image:
    global _UNIT_RADIAL_MASK
    if _UNIT_RADIAL_MASK is None:
        size = 128
        center = size / 2.0
        ys, xs = np.ogrid[:size, :size]
        dist = np.sqrt((xs - center)**2 + (ys - center)**2) / center
        alpha = np.clip(1.0 - dist, 0, 1) ** 1.6
        mask_arr = (alpha * 255).astype(np.uint8)
        _UNIT_RADIAL_MASK = Image.fromarray(mask_arr, "L")
    return _UNIT_RADIAL_MASK


def radial_gradient(
    width: int, height: int,
    cx: float, cy: float,
    color,
    inner_alpha: int = 140,
    outer_alpha: int = 0,
    radius: float = 0.6,   # fraction of min(W,H)
) -> Image.Image:
    """Create a soft radial gradient light blob with zero memory allocation churn."""
    cache_key = (
        width, height,
        round(cx, -1), round(cy, -1),
        int(color[0]), int(color[1]), int(color[2]),
        int(inner_alpha // 5 * 5),
        round(radius, 2)
    )
    if cache_key in _STATIC_RADIAL_CACHE:
        return _STATIC_RADIAL_CACHE[cache_key]

    r_px = max(2, int(radius * min(width, height)))
    diameter = r_px * 2

    unit_mask = _get_unit_radial_mask()
    mask = unit_mask.resize((diameter, diameter), Image.BILINEAR)

    factor = max(0.0, min(float(inner_alpha) / 255.0, 1.0))
    if factor < 0.99:
        lut = [int(i * factor) for i in range(256)]
        mask = mask.point(lut)

    cr, cg, cb = int(color[0]), int(color[1]), int(color[2])
    blob = Image.new("RGBA", (diameter, diameter), (cr, cg, cb, 0))
    blob.putalpha(mask)

    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    paste_x = int(cx - r_px)
    paste_y = int(cy - r_px)
    result.paste(blob, (paste_x, paste_y), blob)

    if len(_STATIC_RADIAL_CACHE) < 64:
        _STATIC_RADIAL_CACHE[cache_key] = result

    return result


def light_streak(
    width: int, height: int,
    x: float, y: float,
    angle_deg: float,
    length: float,
    color,
    alpha: int = 80,
    thickness: int = 3,
) -> Image.Image:
    """A single angled light streak (patch-blurred for speed)."""
    full_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    angle_rad = math.radians(angle_deg)
    dx = math.cos(angle_rad) * length
    dy = math.sin(angle_rad) * length
    x1, y1 = x - dx / 2, y - dy / 2
    x2, y2 = x + dx / 2, y + dy / 2

    # Bounding box with margin
    pad = thickness * 4 + 10
    min_x = max(0, int(min(x1, x2) - pad))
    min_y = max(0, int(min(y1, y2) - pad))
    max_x = min(width, int(max(x1, x2) + pad))
    max_y = min(height, int(max(y1, y2) + pad))
    pw = max_x - min_x
    ph = max_y - min_y
    if pw <= 0 or ph <= 0:
        return full_img

    patch = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    draw = ImageDraw.Draw(patch)
    r, g, b = color[:3]
    lx1, ly1 = x1 - min_x, y1 - min_y
    lx2, ly2 = x2 - min_x, y2 - min_y
    for w in range(thickness, 0, -1):
        a_layer = int(alpha * (w / thickness) ** 2)
        draw.line([(lx1, ly1), (lx2, ly2)], fill=(r, g, b, a_layer), width=w * 2)

    blurred_patch = patch.filter(ImageFilter.GaussianBlur(radius=thickness + 2))
    full_img.alpha_composite(blurred_patch, (min_x, min_y))
    return full_img


_VIGNETTE_CACHE: dict = {}

def apply_vignette(img: Image.Image, strength: float = 0.65) -> Image.Image:
    """Dark vignette overlay (cinematic corners, cached)."""
    w, h = img.size
    key = (w, h, round(strength, 2))
    if key not in _VIGNETTE_CACHE:
        sw, sh = w // 4, h // 4
        ys, xs = np.mgrid[0:sh, 0:sw]
        nx = (xs / sw - 0.5) * 2
        ny = (ys / sh - 0.5) * 2
        dist = np.sqrt(nx**2 + ny**2) / math.sqrt(2)
        vig_alpha = np.clip(dist ** 2 * strength * 255, 0, 200).astype(np.uint8)
        arr = np.zeros((sh, sw, 4), dtype=np.uint8)
        arr[..., 3] = vig_alpha
        _VIGNETTE_CACHE[key] = Image.fromarray(arr, "RGBA").resize((w, h), Image.BILINEAR)

    if img.mode != "RGBA":
        img = img.convert("RGBA")
    img.alpha_composite(_VIGNETTE_CACHE[key])
    return img


def apply_film_grain(img: Image.Image, strength: float = 0.018, t: float = 0.0) -> Image.Image:
    """Zero-overhead pass-through (avoids large heap allocations)."""
    return img


def animated_light(
    width: int, height: int,
    t: float,            # current time in seconds
    scene: str = "hook",
) -> Image.Image:
    """Composite lighting for a given scene + time."""
    base = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    if scene == "hook":
        # Top-left beam, cyan
        cx = width * (0.3 + 0.1 * math.sin(t * 0.3))
        cy = height * 0.2
        blob = radial_gradient(width, height, cx, cy, ACCENT,
                                inner_alpha=int(80 + 30*math.sin(t*0.8)), radius=0.55)
        base = Image.alpha_composite(base, blob)
        # Bottom-right purple
        cx2 = width * 0.75
        cy2 = height * 0.82
        blob2 = radial_gradient(width, height, cx2, cy2, ACCENT2,
                                 inner_alpha=int(55 + 20*math.sin(t*0.5+1)), radius=0.4)
        base = Image.alpha_composite(base, blob2)

        # Streaks
        for i in range(3):
            st = light_streak(width, height,
                              width * (0.2 + 0.3 * i),
                              height * (0.1 + 0.08 * i),
                              angle_deg=35 + i * 12,
                              length=width * 0.6,
                              color=ACCENT,
                              alpha=int(25 + 10 * math.sin(t * 0.6 + i)),
                              thickness=2)
            base = Image.alpha_composite(base, st)

    elif scene == "editor":
        # Subtle top-center glow
        blob = radial_gradient(width, height,
                               width * 0.5, height * 0.35,
                               ACCENT, inner_alpha=45, radius=0.5)
        base = Image.alpha_composite(base, blob)

        # Moving highlight sweep (simulates light moving across screen)
        sweep_x = width * (0.2 + 0.6 * ((t % 8) / 8))
        st = light_streak(width, height, sweep_x, height * 0.4,
                          angle_deg=90, length=height * 0.5,
                          color=ACCENT, alpha=15, thickness=2)
        base = Image.alpha_composite(base, st)

    elif scene == "payoff":
        # Strong central reveal
        pulse = 0.5 + 0.5 * math.sin(t * 1.5)
        blob = radial_gradient(width, height, width * 0.5, height * 0.42,
                               ACCENT, inner_alpha=int(90 + 60 * pulse), radius=0.65)
        base = Image.alpha_composite(base, blob)

    elif scene == "loop":
        blob = radial_gradient(width, height, width * 0.3, height * 0.2,
                               ACCENT, inner_alpha=70, radius=0.55)
        base = Image.alpha_composite(base, blob)

    return base
