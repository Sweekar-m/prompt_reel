"""
effects/typography_registry.py
==============================
Font Registry and Style Pairing Engine.
Supports editorial, brutalist, swiss, serif, and technical monospace pairings.
Avoids cursive ubiquity — empowers creative diversity.
"""
import os
import functools
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional
from PIL import ImageFont

WIN_FONT_DIR = "C:/Windows/Fonts"
ASSET_FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")


@dataclass
class FontPairing:
    id: str
    name: str
    category: str        # "editorial", "brutalist", "swiss", "cinematic_serif", "tech_mono", "modern_sans"
    heading_font_candidates: List[str]
    body_font_candidates: List[str]
    mono_font_candidates: List[str]
    description: str


FONT_PAIRINGS: Dict[str, FontPairing] = {
    # 1. Inter + JetBrains Mono
    "inter_jetbrains": FontPairing(
        id="inter_jetbrains",
        name="Inter + JetBrains Mono",
        category="modern_sans",
        heading_font_candidates=["Inter-Bold.ttf", "segoeuib.ttf", "arialbd.ttf"],
        body_font_candidates=["Inter-Regular.ttf", "segoeui.ttf", "arial.ttf"],
        mono_font_candidates=["JetBrainsMono-Regular.ttf", "consola.ttf"],
        description="Clean, balanced, modern high-tech developer aesthetic."
    ),

    # 2. Space Grotesk + IBM Plex Mono
    "space_grotesk_ibm": FontPairing(
        id="space_grotesk_ibm",
        name="Space Grotesk + IBM Plex Mono",
        category="editorial",
        heading_font_candidates=["trebucbd.ttf", "impact.ttf", "segoeuib.ttf", "arialbd.ttf"],
        body_font_candidates=["trebuc.ttf", "segoeui.ttf", "calibri.ttf"],
        mono_font_candidates=["consola.ttf", "JetBrainsMono-Regular.ttf"],
        description="Tech-editorial with geometric quirks and engineering precision."
    ),

    # 3. Bebas Neue + Inter
    "bebas_inter": FontPairing(
        id="bebas_inter",
        name="Bebas Neue + Inter",
        category="giant_condensed",
        heading_font_candidates=["impact.ttf", "ariblk.ttf", "segoeuib.ttf"],
        body_font_candidates=["Inter-Regular.ttf", "segoeui.ttf", "arial.ttf"],
        mono_font_candidates=["JetBrainsMono-Regular.ttf", "consola.ttf"],
        description="Massive punchy condensed headlines with ultra-clean body text."
    ),

    # 4. Manrope + Source Code Pro
    "manrope_source": FontPairing(
        id="manrope_source",
        name="Manrope + Source Code Pro",
        category="swiss",
        heading_font_candidates=["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf"],
        body_font_candidates=["segoeui.ttf", "calibri.ttf", "arial.ttf"],
        mono_font_candidates=["consola.ttf", "JetBrainsMono-Regular.ttf"],
        description="Humanist Swiss geometry with open, friendly technical rhythm."
    ),

    # 5. DM Sans + JetBrains Mono
    "dm_sans_jetbrains": FontPairing(
        id="dm_sans_jetbrains",
        name="DM Sans + JetBrains Mono",
        category="modern_sans",
        heading_font_candidates=["segoeuib.ttf", "arialbd.ttf", "Inter-Bold.ttf"],
        body_font_candidates=["segoeui.ttf", "arial.ttf", "Inter-Regular.ttf"],
        mono_font_candidates=["JetBrainsMono-Regular.ttf", "consola.ttf"],
        description="Understated modern product design standard."
    ),

    # 6. Archivo Black + IBM Plex Mono
    "archivo_ibm": FontPairing(
        id="archivo_ibm",
        name="Archivo Black + IBM Plex Mono",
        category="brutalist",
        heading_font_candidates=["ariblk.ttf", "impact.ttf", "segoeuib.ttf"],
        body_font_candidates=["arialbd.ttf", "segoeuib.ttf", "consola.ttf"],
        mono_font_candidates=["consola.ttf", "JetBrainsMono-Regular.ttf"],
        description="Heavyweight brutalist impact with raw industrial presence."
    ),

    # 7. Playfair Display + Inter
    "playfair_inter": FontPairing(
        id="playfair_inter",
        name="Playfair Display + Inter",
        category="cinematic_serif",
        heading_font_candidates=["georgiab.ttf", "timesbd.ttf", "palab.ttf"],
        body_font_candidates=["Inter-Regular.ttf", "segoeui.ttf", "arial.ttf"],
        mono_font_candidates=["JetBrainsMono-Regular.ttf", "consola.ttf"],
        description="High-contrast editorial serif paired with modern neutral sans."
    )
}


@functools.lru_cache(maxsize=128)
def _resolve_font_path(candidate_names: Tuple[str, ...]) -> Optional[str]:
    """Find the first existing font path from candidates."""
    for name in candidate_names:
        # Check assets/fonts
        asset_p = os.path.join(ASSET_FONT_DIR, name)
        if os.path.isfile(asset_p):
            return asset_p
        # Check Windows Fonts
        win_p = os.path.join(WIN_FONT_DIR, name)
        if os.path.isfile(win_p):
            return win_p
        # Direct path check
        if os.path.isfile(name):
            return name
    return None


@functools.lru_cache(maxsize=256)
def load_font(pairing_id: str, role: str, size: int) -> ImageFont.FreeTypeFont:
    """
    Load a font for a specific role ('heading', 'body', 'mono')
    within a registered font pairing.
    """
    pairing = FONT_PAIRINGS.get(pairing_id, FONT_PAIRINGS["inter_jetbrains"])

    if role == "heading":
        candidates = tuple(pairing.heading_font_candidates)
    elif role == "mono":
        candidates = tuple(pairing.mono_font_candidates)
    else:
        candidates = tuple(pairing.body_font_candidates)

    path = _resolve_font_path(candidates)
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass

    # Fallback to default
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def list_font_pairings() -> List[Dict[str, Any]]:
    return [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "description": p.description
        }
        for p in FONT_PAIRINGS.values()
    ]
