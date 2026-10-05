"""
effects/typography.py
Kinetic typography helpers for text animations.
"""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import *

# ── font cache ──────────────────────────────────────────────────────────────
_font_cache: dict = {}

def _load_font(path: str, size: int, style: str = "flat") -> ImageFont.FreeTypeFont:
    key = (path, size, style)
    if key not in _font_cache:
        # Style-specific fallback lists
        style_fallbacks = {
            "bold": [
                path,
                "C:/Windows/Fonts/segoeuib.ttf",
                "C:/Windows/Fonts/arialbd.ttf",
                "C:/Windows/Fonts/ariblk.ttf",
                "C:/Windows/Fonts/calibrib.ttf",
            ],
            "cursive": [
                path,
                "C:/Windows/Fonts/segoesc.ttf",
                "C:/Windows/Fonts/segoescb.ttf",
                "C:/Windows/Fonts/Inkfree.ttf",
                "C:/Windows/Fonts/segoeprb.ttf",
                "C:/Windows/Fonts/segoepr.ttf",
                "C:/Windows/Fonts/Gabriola.ttf",
            ],
            "flat": [
                path,
                "C:/Windows/Fonts/segoeui.ttf",
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
            ],
            "mono": [
                path,
                "C:/Windows/Fonts/consola.ttf",
                "C:/Windows/Fonts/cour.ttf",
            ]
        }

        fallbacks = style_fallbacks.get(style, style_fallbacks["flat"])
        loaded = False
        for fb in fallbacks:
            if fb and os.path.exists(fb):
                try:
                    _font_cache[key] = ImageFont.truetype(fb, size)
                    loaded = True
                    break
                except Exception:
                    continue
        if not loaded:
            _font_cache[key] = ImageFont.load_default()
    return _font_cache[key]

def load_bold(size: int) -> ImageFont.FreeTypeFont:
    return _load_font(BOLD_FONT, size, style="bold")

def load_cursive(size: int) -> ImageFont.FreeTypeFont:
    return _load_font(CURSIVE_FONT, size, style="cursive")

def load_flat(size: int) -> ImageFont.FreeTypeFont:
    return _load_font(FLAT_FONT, size, style="flat")

def load_regular(size: int) -> ImageFont.FreeTypeFont:
    return load_flat(size)

def load_mono(size: int) -> ImageFont.FreeTypeFont:
    return _load_font(MONO_FONT, size, style="mono")

# ── easing ──────────────────────────────────────────────────────────────────
def ease_out_expo(t: float) -> float:
    return 1.0 if t >= 1 else 1 - pow(2, -10 * t)

def ease_in_out_cubic(t: float) -> float:
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2

def ease_out_back(t: float, s: float = 1.70158) -> float:
    c1 = s
    c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)

def lerp(a, b, t):
    return a + (b - a) * t

# ── text measurement ────────────────────────────────────────────────────────
def text_size(text: str, font) -> tuple[int, int]:
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

# ── animated text draw ──────────────────────────────────────────────────────
def draw_animated_text(
    img: Image.Image,
    text: str,
    cx: float,              # center x
    cy: float,              # center y
    font,
    color,
    t: float,               # 0..1 animation progress
    anim: str = "rise",     # "rise" | "scale" | "blur_reveal" | "slide_left" | "fade"
    glow: bool = True,
    glow_color = None,
    shadow: bool = True,
    max_alpha: int = 255,
) -> None:
    """Draw text on img with the chosen animation style."""

    draw = ImageDraw.Draw(img)

    if anim == "rise":
        alpha = int(ease_out_expo(t) * max_alpha)
        off_y = int((1 - ease_out_expo(t)) * 60)
    elif anim == "scale":
        progress = ease_out_back(min(t, 1.0))
        scale = 0.2 + progress * 0.8
        alpha = int(min(t * 3, 1) * max_alpha)
        off_y = 0
    elif anim == "blur_reveal":
        alpha = int(ease_out_expo(t) * max_alpha)
        off_y = 0
    elif anim == "slide_left":
        alpha = int(ease_out_expo(t) * max_alpha)
        off_y = 0
    elif anim == "fade":
        alpha = int(t * max_alpha)
        off_y = 0
    else:
        alpha = max_alpha
        off_y = 0

    if alpha < 4:
        return

    tw, th = text_size(text, font)

    # Scale animation: render to temp surface, resize
    if anim == "scale":
        tmp_size = (int(tw * 2 + 40), int(th * 2 + 40))
        tmp = Image.new("RGBA", tmp_size, (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        tx = tmp_size[0] // 2 - tw // 2
        ty = tmp_size[1] // 2 - th // 2
        r, g, b = color[:3]
        td.text((tx, ty), text, font=font, fill=(r, g, b, alpha))
        scaled_w = int(tmp_size[0] * scale)
        scaled_h = int(tmp_size[1] * scale)
        if scaled_w > 0 and scaled_h > 0:
            scaled = tmp.resize((scaled_w, scaled_h), Image.LANCZOS)
            px = int(cx - scaled_w / 2)
            py = int(cy - scaled_h / 2)
            img.paste(scaled, (px, py), scaled)
        return

    # Blur reveal
    if anim == "blur_reveal":
        blur_amount = max(0, (1 - t) * 12)
        tmp = Image.new("RGBA", (tw + 40, th + 40), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        r, g, b = color[:3]
        td.text((20, 20), text, font=font, fill=(r, g, b, 255))
        if blur_amount > 0.3:
            tmp = tmp.filter(ImageFilter.GaussianBlur(radius=blur_amount))
        # Apply alpha
        if alpha < 255:
            r, g, b, a = tmp.split()
            a = a.point(lambda p: int(p * alpha / 255))
            tmp.putalpha(a)
        px = int(cx - (tw + 40) / 2)
        py = int(cy - (th + 40) / 2 + off_y)
        img.alpha_composite(tmp, (px, py))
        return

    x = int(cx - tw / 2)
    y = int(cy - th / 2 + off_y)

    if anim == "slide_left":
        x = int(cx - tw / 2 + (1 - ease_out_expo(t)) * 120)

    r, g, b = color[:3]

    # Glow layer (patch-based blur)
    if glow and glow_color is not None and alpha > 30:
        gc = glow_color
        pad = 32
        gw, gh = tw + pad * 2, th + pad * 2
        g_box = Image.new("RGBA", (gw, gh), (0, 0, 0, 0))
        gd = ImageDraw.Draw(g_box)
        gd.text((pad, pad), text, font=font, fill=(gc[0], gc[1], gc[2], int(alpha * 0.75)))
        g_blurred = g_box.filter(ImageFilter.GaussianBlur(radius=10))
        img.alpha_composite(g_blurred, (x - pad, y - pad))

    # Shadow
    if shadow:
        draw.text((x + 3, y + 4), text, font=font, fill=(0, 0, 0, int(alpha * 0.5)))

    draw.text((x, y), text, font=font, fill=(r, g, b, alpha))


def draw_code_line(
    img: Image.Image,
    text: str,
    x: int, y: int,
    font,
    tokens: list,   # list of (text_segment, color) tuples
    alpha: int = 255,
) -> int:
    """Draw a syntax-highlighted code line. Returns the y advance."""
    draw = ImageDraw.Draw(img)
    cur_x = x
    for segment, color in tokens:
        r, g, b = color[:3]
        draw.text((cur_x, y), segment, font=font, fill=(r, g, b, alpha))
        w, _ = text_size(segment, font)
        cur_x += w
    _, line_h = text_size("Mg", font)
    return line_h + 8


def draw_glow_rect(
    img: Image.Image,
    x1: int, y1: int, x2: int, y2: int,
    color,
    alpha: int = 80,
    blur: float = 18,
) -> None:
    """Draw a blurred glowing rectangle (patch-based for fast rendering)."""
    pad = int(blur * 2 + 4)
    w = (x2 - x1) + pad * 2
    h = (y2 - y1) + pad * 2
    if w <= 0 or h <= 0:
        return
    tmp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    r, g, b = color[:3]
    d.rectangle([pad, pad, pad + (x2 - x1), pad + (y2 - y1)], fill=(r, g, b, alpha))
    blurred = tmp.filter(ImageFilter.GaussianBlur(radius=blur))
    img.alpha_composite(blurred, (x1 - pad, y1 - pad))


# ── Multi-Font Compositing Helpers ──────────────────────────────────────────

def draw_mixed_line(
    img: Image.Image,
    segments: list,       # List of (text, style, size, color) tuples
    cx: float,            # Center X
    cy: float,            # Baseline Y
    alpha: int = 255,
    shadow: bool = True
) -> None:
    """
    Renders mixed font styles seamlessly side-by-side on the same line.
    styles: 'bold' | 'cursive' | 'flat' | 'mono'
    """
    if alpha < 5:
        return

    draw = ImageDraw.Draw(img)
    measured = []
    total_w = 0
    max_h = 0

    for text, style, size, color in segments:
        if style == "bold": font = load_bold(size)
        elif style == "cursive": font = load_cursive(size)
        elif style == "mono": font = load_mono(size)
        else: font = load_flat(size)

        w, h = text_size(text, font)
        measured.append((text, font, color, w, h))
        total_w += w
        max_h = max(max_h, h)

    cur_x = int(cx - total_w / 2)
    for text, font, color, w, h in measured:
        y_pos = int(cy - h / 2)
        r, g, b = color[:3]
        if shadow:
            draw.text((cur_x + 2, y_pos + 3), text, font=font, fill=(0, 0, 0, int(alpha * 0.45)))
        draw.text((cur_x, y_pos), text, font=font, fill=(r, g, b, alpha))
        cur_x += w


def draw_cursive_annotation(
    img: Image.Image,
    text: str,
    x: int,
    y: int,
    alpha: int = 255,
    color = ACCENT3,
    size: int = 34,
    arrow: str = "left"   # 'left' | 'right' | 'down' | 'none'
) -> None:
    """Draws an expressive hand-annotated cursive note with a hand-drawn arrow."""
    if alpha < 10:
        return
    draw = ImageDraw.Draw(img)
    font = load_cursive(size)
    r, g, b = color[:3]

    # Draw cursive text
    draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, int(alpha * 0.5)))
    draw.text((x, y), text, font=font, fill=(r, g, b, alpha))

    # Hand-drawn arrow
    tw, th = text_size(text, font)
    if arrow == "left":
        ax = x - 12
        ay = y + th // 2
        draw.line([(ax, ay), (ax - 28, ay)], fill=(r, g, b, alpha), width=2)
        draw.line([(ax - 28, ay), (ax - 18, ay - 6)], fill=(r, g, b, alpha), width=2)
        draw.line([(ax - 28, ay), (ax - 18, ay + 6)], fill=(r, g, b, alpha), width=2)
    elif arrow == "right":
        ax = x + tw + 12
        ay = y + th // 2
        draw.line([(ax, ay), (ax + 28, ay)], fill=(r, g, b, alpha), width=2)
        draw.line([(ax + 28, ay), (ax + 18, ay - 6)], fill=(r, g, b, alpha), width=2)
        draw.line([(ax + 28, ay), (ax + 18, ay + 6)], fill=(r, g, b, alpha), width=2)
    elif arrow == "down":
        ax = x + tw // 2
        ay = y + th + 6
        draw.line([(ax, ay), (ax, ay + 20)], fill=(r, g, b, alpha), width=2)
        draw.line([(ax, ay + 20), (ax - 6, ay + 12)], fill=(r, g, b, alpha), width=2)
        draw.line([(ax, ay + 20), (ax + 6, ay + 12)], fill=(r, g, b, alpha), width=2)


def draw_paired_title(
    img: Image.Image,
    cursive_lead: str,     # e.g. "wait... did you know"
    bold_main: str,        # e.g. "HOW THIS WORKS"
    flat_sub: str,         # e.g. "under the hood"
    cx: float,
    cy: float,
    t: float,
    glow_color = ACCENT
) -> None:
    """
    Iconic motion graphics lockup combining:
    1. Cursive casual lead-in
    2. Giant bold punchy title (with glow)
    3. Flat clean modern subtitle
    """
    alpha = int(ease_out_expo(t) * 255)
    if alpha < 5:
        return

    # 1. Cursive lead-in
    if cursive_lead:
        c_font = load_cursive(42)
        c_y = cy - 100
        draw_animated_text(img, cursive_lead, cx, c_y, c_font, ACCENT3,
                           t, anim="fade", shadow=True, max_alpha=alpha)

    # 2. Giant Bold Title
    if bold_main:
        b_font = load_bold(88)
        draw_animated_text(img, bold_main, cx, cy, b_font, WHITE,
                           t, anim="scale", glow=True, glow_color=glow_color, max_alpha=alpha)

    # 3. Flat clean subtitle
    if flat_sub:
        f_font = load_flat(36)
        f_y = cy + 95
        draw_animated_text(img, flat_sub, cx, f_y, f_font, GRAY,
                           t, anim="rise", shadow=True, max_alpha=alpha)

