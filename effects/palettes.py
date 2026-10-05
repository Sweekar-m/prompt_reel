"""
effects/palettes.py
===================
Professional Color Palette Engine with WCAG Contrast Validation.
Guarantees harmonious, high-contrast, accessible palettes.
Zero random uncontrolled RGB generation.
"""
import math
from dataclasses import dataclass
from typing import Tuple, Dict, List, Optional

RGBColor = Tuple[int, int, int]


@dataclass
class ColorPalette:
    id: str
    name: str
    background: RGBColor
    primary: RGBColor     # main contrast text / hero element
    secondary: RGBColor   # vibrant brand / thematic accent
    accent: RGBColor      # punctuation / warning / cursor
    text: RGBColor        # high-legibility body text
    subtext: RGBColor     # muted secondary label
    surface: RGBColor     # container / panel background
    is_dark: bool = True

    def validate_contrast(self) -> Dict[str, float]:
        """Compute WCAG relative luminance contrast ratios."""
        l_bg = calculate_relative_luminance(self.background)
        l_surf = calculate_relative_luminance(self.surface)
        l_text = calculate_relative_luminance(self.text)
        l_pri = calculate_relative_luminance(self.primary)
        l_sec = calculate_relative_luminance(self.secondary)

        return {
            "text_on_bg": contrast_ratio(l_text, l_bg),
            "text_on_surface": contrast_ratio(l_text, l_surf),
            "primary_on_bg": contrast_ratio(l_pri, l_bg),
            "secondary_on_bg": contrast_ratio(l_sec, l_bg),
        }


def calculate_relative_luminance(rgb: RGBColor) -> float:
    """Calculate WCAG 2.1 relative luminance for an sRGB color."""
    vals = []
    for c in rgb[:3]:
        s = c / 255.0
        if s <= 0.03928:
            vals.append(s / 12.92)
        else:
            vals.append(((s + 0.055) / 1.055) ** 2.4)
    return 0.2126 * vals[0] + 0.7152 * vals[1] + 0.0722 * vals[2]


def contrast_ratio(l1: float, l2: float) -> float:
    """Return contrast ratio between two luminance values (1.0 to 21.0)."""
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


# ── Curated Professional Palette Library ─────────────────────────────────────

CURATED_PALETTES: Dict[str, ColorPalette] = {
    # Palette A: Black / Electric Blue / White
    "electric_matrix": ColorPalette(
        id="electric_matrix",
        name="Electric Matrix",
        background=(10, 12, 18),
        primary=(0, 240, 255),
        secondary=(75, 130, 255),
        accent=(255, 60, 110),
        text=(255, 255, 255),
        subtext=(140, 160, 190),
        surface=(18, 22, 34),
        is_dark=True
    ),

    # Palette B: Cream / Black / Orange
    "cream_terracotta": ColorPalette(
        id="cream_terracotta",
        name="Editorial Cream & Orange",
        background=(246, 243, 238),
        primary=(20, 20, 24),
        secondary=(235, 85, 35),
        accent=(30, 100, 180),
        text=(20, 20, 24),
        subtext=(100, 100, 110),
        surface=(235, 230, 222),
        is_dark=False
    ),

    # Palette C: Deep Green / Lime / White
    "terminal_matrix": ColorPalette(
        id="terminal_matrix",
        name="Cybernetic Deep Lime",
        background=(8, 16, 12),
        primary=(50, 255, 120),
        secondary=(204, 255, 0),
        accent=(255, 210, 40),
        text=(245, 255, 245),
        subtext=(80, 170, 110),
        surface=(14, 26, 18),
        is_dark=True
    ),

    # Palette D: Navy / Coral / Ivory
    "navy_coral": ColorPalette(
        id="navy_coral",
        name="Nordic Navy & Coral",
        background=(14, 20, 32),
        primary=(255, 110, 90),
        secondary=(90, 195, 255),
        accent=(255, 205, 90),
        text=(248, 248, 252),
        subtext=(145, 165, 195),
        surface=(22, 32, 50),
        is_dark=True
    ),

    # Palette E: Burgundy / Pink / Cream
    "burgundy_velvet": ColorPalette(
        id="burgundy_velvet",
        name="Velvet Burgundy & Rose",
        background=(22, 10, 16),
        primary=(255, 140, 180),
        secondary=(255, 220, 160),
        accent=(255, 70, 110),
        text=(255, 245, 248),
        subtext=(180, 140, 160),
        surface=(36, 18, 28),
        is_dark=True
    ),

    # Palette F: White / Cobalt / Black
    "swiss_cobalt": ColorPalette(
        id="swiss_cobalt",
        name="Swiss International Cobalt",
        background=(250, 250, 252),
        primary=(12, 16, 28),
        secondary=(15, 80, 240),
        accent=(235, 45, 40),
        text=(12, 16, 28),
        subtext=(90, 100, 125),
        surface=(238, 242, 248),
        is_dark=False
    ),

    # Palette G: Charcoal / Gold / White
    "charcoal_gold": ColorPalette(
        id="charcoal_gold",
        name="Executive Charcoal & Gold",
        background=(14, 14, 16),
        primary=(235, 205, 145),
        secondary=(255, 255, 255),
        accent=(190, 150, 90),
        text=(250, 250, 250),
        subtext=(150, 150, 155),
        surface=(24, 24, 28),
        is_dark=True
    ),

    # Palette H: Violet / Cyan / Black
    "aurora_violet": ColorPalette(
        id="aurora_violet",
        name="Aurora Violet & Cyan",
        background=(12, 10, 24),
        primary=(185, 110, 255),
        secondary=(0, 240, 255),
        accent=(255, 100, 190),
        text=(255, 255, 255),
        subtext=(155, 145, 185),
        surface=(22, 18, 40),
        is_dark=True
    ),

    # Additional Styles:
    "blueprint_cyan": ColorPalette(
        id="blueprint_cyan",
        name="Architectural Blueprint",
        background=(12, 45, 95),
        primary=(255, 255, 255),
        secondary=(120, 210, 255),
        accent=(255, 210, 70),
        text=(255, 255, 255),
        subtext=(160, 205, 245),
        surface=(18, 60, 125),
        is_dark=True
    ),

    "stark_noir": ColorPalette(
        id="stark_noir",
        name="Stark High-Contrast Noir",
        background=(8, 8, 8),
        primary=(255, 255, 255),
        secondary=(210, 210, 210),
        accent=(255, 255, 255),
        text=(255, 255, 255),
        subtext=(130, 130, 130),
        surface=(20, 20, 20),
        is_dark=True
    )
}


def get_palette(palette_id: str) -> ColorPalette:
    """Retrieve curated palette by ID with fallback."""
    if palette_id in CURATED_PALETTES:
        return CURATED_PALETTES[palette_id]
    # Default to electric matrix if unknown
    return CURATED_PALETTES["electric_matrix"]


def list_palettes() -> List[Dict[str, Any]]:
    """List all available palettes with metadata and contrast validation scores."""
    result = []
    for pid, pal in CURATED_PALETTES.items():
        contrasts = pal.validate_contrast()
        result.append({
            "id": pal.id,
            "name": pal.name,
            "is_dark": pal.is_dark,
            "bg": list(pal.background),
            "primary": list(pal.primary),
            "secondary": list(pal.secondary),
            "accent": list(pal.accent),
            "text": list(pal.text),
            "contrasts": contrasts,
            "wcag_aa_passed": contrasts["text_on_bg"] >= 4.5
        })
    return result
