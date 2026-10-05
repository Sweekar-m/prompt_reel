"""
effects/sound_profiles.py
=========================
Sound Design and Music Profiling Engine.
Supports 9 distinct algorithmic music profiles and semantic sound design:
- Code appearing -> Keyboard/UI ticks
- Stack building -> Mechanical clicks
- Data movement -> Digital sweep
- Error -> Distorted impact
- Reveal -> Tonal rise
- Payoff -> Sub-bass impact
"""
import numpy as np
from scipy.signal import butter, lfilter
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple


@dataclass
class MusicProfile:
    id: str
    name: str
    bpm: float
    chord_progression: List[str]  # e.g. ["Fm", "Cm", "Db", "Bbm"]
    lead_timbre: str              # "square_lead", "warm_pluck", "bell_sine", "saw_sweep", "acoustic_sub"
    bass_freq: float              # Fundamental sub bass Hz
    ducking_db: float             # Dynamic attenuation during speech
    description: str


MUSIC_PROFILES: Dict[str, MusicProfile] = {
    "cyberpunk": MusicProfile(
        id="cyberpunk",
        name="Cyberpunk Synthwave",
        bpm=126.0,
        chord_progression=["Fm", "Cm", "Db", "Eb"],
        lead_timbre="saw_sweep",
        bass_freq=45.0,
        ducking_db=-10.0,
        description="Driving 126 BPM electro-synth with rolling bass and energetic momentum."
    ),

    "dark_math": MusicProfile(
        id="dark_math",
        name="Dark Mathematical Tension",
        bpm=88.0,
        chord_progression=["Dm", "F", "Am", "E"],
        lead_timbre="bell_sine",
        bass_freq=38.0,
        ducking_db=-14.0,
        description="Mystical geometric minor chords, ticking clockwork, and deep sub-bass braams."
    ),

    "cinematic": MusicProfile(
        id="cinematic",
        name="Cinematic Sub Braam & Pulse",
        bpm=86.0,
        chord_progression=["Dm", "Bb", "Gm", "A"],
        lead_timbre="acoustic_sub",
        bass_freq=36.0,
        ducking_db=-14.0,
        description="Hans Zimmer-style dramatic ostinato, massive cinematic braams, and evolving sub drones."
    ),

    "lofi_chill": MusicProfile(
        id="lofi_chill",
        name="Lo-Fi Coding & Math Beat",
        bpm=84.0,
        chord_progression=["Dm", "G", "C", "Am"],
        lead_timbre="warm_pluck",
        bass_freq=52.0,
        ducking_db=-12.0,
        description="Warm vintage Rhodes electric piano, vinyl tape warmth, and relaxed boom-bap swing."
    ),

    "phonk_drift": MusicProfile(
        id="phonk_drift",
        name="Phonk Tech Drift",
        bpm=138.0,
        chord_progression=["Fm", "Db", "Bbm", "C"],
        lead_timbre="square_lead",
        bass_freq=40.0,
        ducking_db=-9.0,
        description="Aggressive tuned cowbell stabs, saturated sliding 808 sub, and trap-style rhythm."
    ),

    "retro_chiptune": MusicProfile(
        id="retro_chiptune",
        name="8-Bit Arcade Computing",
        bpm=128.0,
        chord_progression=["C", "G", "Am", "F"],
        lead_timbre="square_lead",
        bass_freq=58.0,
        ducking_db=-10.0,
        description="Authentic nostalgic 8-bit square wave arpeggios with punchy retro energy."
    ),

    "minimal_electronic": MusicProfile(
        id="minimal_electronic",
        name="Minimal Clean Tech",
        bpm=118.0,
        chord_progression=["Am", "Em", "F", "G"],
        lead_timbre="warm_pluck",
        bass_freq=55.0,
        ducking_db=-12.0,
        description="Clean, understated, warm Rhodes/sine plucks with gentle pulse."
    ),

    "ambient": MusicProfile(
        id="ambient",
        name="Ethereal Ambient Space",
        bpm=75.0,
        chord_progression=["C", "Am", "F", "G"],
        lead_timbre="bell_sine",
        bass_freq=50.0,
        ducking_db=-15.0,
        description="Floating, open reverberant atmosphere suited for deep thinking and geometry."
    ),

    "dark_tech": MusicProfile(
        id="dark_tech",
        name="Dark Tech Industrial",
        bpm=130.0,
        chord_progression=["Em", "Bbm", "C", "B"],
        lead_timbre="saw_sweep",
        bass_freq=42.0,
        ducking_db=-10.0,
        description="Gritty underground tech pulse with sharp mechanical transients."
    ),

    "experimental": MusicProfile(
        id="experimental",
        name="Experimental Glitch Matrix",
        bpm=124.0,
        chord_progression=["Abm", "E", "Gb", "Ebm"],
        lead_timbre="bell_sine",
        bass_freq=44.0,
        ducking_db=-11.0,
        description="Complex granular textures, syncopated micro-pulses, and digital sweeps."
    )
}


def get_music_profile(query: str, is_math: bool = False) -> MusicProfile:
    """Intelligently resolves any style string, sound direction, or keyword to the optimal MusicProfile."""
    q = (query or "").lower().strip()
    if is_math and not any(k in q for k in ["lofi", "phonk", "retro"]):
        return MUSIC_PROFILES["dark_math"]

    if any(k in q for k in ["math", "geometry", "dimension", "equation", "spiral", "helix"]):
        return MUSIC_PROFILES["dark_math"]
    if any(k in q for k in ["lofi", "lo-fi", "chill", "relax", "cozy", "jazzy", "study"]):
        return MUSIC_PROFILES["lofi_chill"]
    if any(k in q for k in ["phonk", "drift", "trap", "aggressive", "hype", "fast"]):
        return MUSIC_PROFILES["phonk_drift"]
    if any(k in q for k in ["braam", "cinematic", "film", "dramatic", "theatrical", "orchestral"]):
        return MUSIC_PROFILES["cinematic"]
    if any(k in q for k in ["retro", "8bit", "8-bit", "chiptune", "arcade", "1984"]):
        return MUSIC_PROFILES["retro_chiptune"]
    if any(k in q for k in ["minimal", "clean", "stark", "sub", "swiss"]):
        return MUSIC_PROFILES["minimal_electronic"]
    if any(k in q for k in ["ambient", "ethereal", "space", "glass", "float"]):
        return MUSIC_PROFILES["ambient"]
    if any(k in q for k in ["industrial", "concrete", "dark_tech", "hardware"]):
        return MUSIC_PROFILES["dark_tech"]
    if any(k in q for k in ["experimental", "glitch", "matrix"]):
        return MUSIC_PROFILES["experimental"]

    return MUSIC_PROFILES.get(q, MUSIC_PROFILES["cyberpunk"])


# ── Semantic Procedural SFX Generators ───────────────────────────────────────

def generate_semantic_sfx(kind: str, sr: int = 48000) -> np.ndarray:
    """
    Procedurally synthesize semantic sound effects:
    - keyboard_tick: sharp micro-transient when code types
    - mechanical_click: tactile relay click when stack builds
    - digital_sweep: high-frequency filtered noise for data movement
    - distorted_impact: saturated low punch for error or bug
    - tonal_rise: exponential sine pitch sweep for reveal
    - sub_impact: cinematic 80Hz -> 28Hz sub-bass drop for payoff
    """
    if kind == "keyboard_tick":
        dur = 0.04
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        click = np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 220)
        noise = np.random.uniform(-0.3, 0.3, len(t)) * np.exp(-t * 180)
        return (click * 0.7 + noise * 0.3).astype(np.float32)

    elif kind == "mechanical_click":
        dur = 0.06
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        click1 = np.sin(2 * np.pi * 1400 * t) * np.exp(-t * 120)
        click2 = np.sin(2 * np.pi * 700 * t) * np.exp(-t * 80)
        return (click1 * 0.5 + click2 * 0.5).astype(np.float32)

    elif kind == "digital_sweep":
        dur = 0.28
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        freq = np.linspace(800, 4200, len(t))
        sweep = np.sin(2 * np.pi * freq * t) * np.sin(np.pi * t / dur)
        return (sweep * 0.35).astype(np.float32)

    elif kind == "distorted_impact":
        dur = 0.45
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        sub = np.sin(2 * np.pi * np.linspace(160, 40, len(t)) * t)
        noise = np.random.uniform(-0.8, 0.8, len(t)) * np.exp(-t * 18)
        raw = (sub * 0.7 + noise * 0.5) * np.exp(-t * 7)
        distorted = np.tanh(raw * 2.5) * 0.6
        return distorted.astype(np.float32)

    elif kind == "tonal_rise":
        dur = 0.55
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        freq = 300 * np.exp(t * 3.2)
        env = np.sin(np.pi * (t / dur) ** 1.8)
        rise = np.sin(2 * np.pi * freq * t) * env
        return (rise * 0.45).astype(np.float32)

    elif kind == "sub_impact":
        dur = 1.10
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        freq = 80 * np.exp(-t * 1.6)
        env = np.exp(-t * 3.2)
        sub = np.sin(2 * np.pi * freq * t) * env
        return (sub * 0.85).astype(np.float32)

    else:
        # Default gentle click
        dur = 0.05
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        return (np.sin(2 * np.pi * 1000 * t) * np.exp(-t * 90) * 0.4).astype(np.float32)
