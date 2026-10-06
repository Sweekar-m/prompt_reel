"""
effects/audio_dna.py
====================
Audio DNA & Musical Intelligence Engine.
Generates an independent, coherent, and deterministic Audio DNA per video.
Eliminates repetitive BGM, BPM, chord progressions, rhythm structures, and flat energy curves.

Key Components:
1. AudioDNA dataclass & schema
2. 18+ rich musical genres/profiles with range mappings per visual style
3. Modal chord progression generator (Tension, Resolution, Optimistic, Mysterious,
   Futuristic, Emotional, Dark, Triumphant, Minimalist, Cyber-Pulse)
4. Dynamic BPM calculator matching narrative pacing (80 to 175 BPM)
5. 10 rhythmic percussion architectures (four-on-the-floor, broken beat, half-time,
   syncopated, triplet, off-beat percussion, sparse pulse, cinematic hits, rolling, evolving)
6. Dynamic energy curve generator aligned to narrative duration
7. Motion-plan-aware Audio Event Marker extractor
8. Deterministic creative audio seeding
"""
import hashlib
import math
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class AudioEventMarker:
    time: float          # seconds
    type: str           # "intro" | "impact" | "build" | "drop" | "reveal" | "transition" | "resolution"
    intensity: float    # 0.0 to 1.0
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AudioDNA:
    id: str
    genre: str                      # e.g. "cinematic_electronic", "futuristic_ambient", "dark_pulse"
    genre_name: str
    mood: str                       # "tension", "optimistic", "mysterious", "dark", "triumphant", "introspective", "high_velocity"
    energy: str                     # "low_ambient", "pulsing_medium", "high_drive", "dynamic_crescendo"
    bpm: float                      # 80.0 to 175.0
    rhythm: str                     # "four_on_floor", "broken_beat", "half_time", "syncopated", "triplet", "sparse_pulse", "cinematic_hits", "rolling", "evolving"
    percussion_style: str           # "crisp_electro", "orchestral_taiko", "boom_bap_swung", "trap_triplet", "clockwork_ticks", "minimal_clicks", "industrial_crunch"
    bass_style: str                 # "deep_sub_drone", "reese_glide", "braam_horn", "plucked_808", "acid_filter", "walking_pulse"
    harmonic_style: str             # "minor_seventh", "modal_dorian", "power_intervals", "suspended_open", "diminished_tension", "lush_extended"
    chord_progression: List[str]    # e.g. ["Dm", "Bb", "Gm", "A"]
    key_root: str                   # e.g. "D", "A", "F", "C", "E", "G", "B"
    scale_mode: str                 # "natural_minor", "harmonic_minor", "dorian", "major", "phrygian"
    instrument_palette: List[str]   # e.g. ["saw_lead", "warm_rhodes", "sub_braam", "clock_tick"]
    texture: str                    # "analog_tape_grit", "crystal_digital", "deep_sub_space", "metallic_industrial", "clean_swiss"
    intro_style: str                # "cold_open_braam", "subtle_tick_rise", "atmospheric_swell", "immediate_groove", "filtered_intro"
    build_style: str                # "snare_roll_accelerate", "filter_sweep_rise", "harmonic_density_stack", "triplet_pulse_rise"
    drop_style: str                 # "heavy_sub_impact", "melodic_arp_explosion", "full_groove_entry", "stutter_drop"
    outro_style: str                # "reverberant_tail", "sudden_cutoff_punch", "tape_stop", "harmonic_decay", "sub_heartbeat"
    energy_curve: List[Dict[str, Any]] = field(default_factory=list) # [{time_ratio, energy_level, section_name}]
    audio_events: List[Dict[str, Any]] = field(default_factory=list)
    variation_seed: int = 42

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ─────────────────────────────────────────────────────────────────────────────
# 1. 18+ DIVERSE MUSICAL GENRE DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

MUSICAL_GENRES: Dict[str, Dict[str, Any]] = {
    "cinematic_electronic": {
        "name": "Cinematic Electronic",
        "bpm_range": (82, 104),
        "moods": ["tension", "triumphant", "mysterious"],
        "rhythms": ["cinematic_hits", "half_time", "evolving"],
        "percussion": "orchestral_taiko",
        "bass": "braam_horn",
        "harmonic": "minor_seventh",
        "instruments": ["acoustic_sub", "orchestral_strings", "braam_horn", "clock_tick"],
        "texture": "deep_sub_space",
        "intro": "atmospheric_swell",
        "build": "harmonic_density_stack",
        "drop": "heavy_sub_impact",
        "outro": "reverberant_tail"
    },
    "futuristic_ambient": {
        "name": "Futuristic Ambient",
        "bpm_range": (78, 96),
        "moods": ["mysterious", "introspective"],
        "rhythms": ["sparse_pulse", "evolving"],
        "percussion": "minimal_clicks",
        "bass": "deep_sub_drone",
        "harmonic": "suspended_open",
        "instruments": ["bell_sine", "crystal_pad", "deep_sub_drone", "glass_bell"],
        "texture": "crystal_digital",
        "intro": "subtle_tick_rise",
        "build": "filter_sweep_rise",
        "drop": "melodic_arp_explosion",
        "outro": "harmonic_decay"
    },
    "energetic_tech": {
        "name": "Energetic Tech",
        "bpm_range": (124, 142),
        "moods": ["high_velocity", "optimistic"],
        "rhythms": ["four_on_floor", "syncopated"],
        "percussion": "crisp_electro",
        "bass": "acid_filter",
        "harmonic": "power_intervals",
        "instruments": ["saw_sweep", "acid_filter", "crisp_electro", "arp_synth"],
        "texture": "clean_swiss",
        "intro": "filtered_intro",
        "build": "filter_sweep_rise",
        "drop": "full_groove_entry",
        "outro": "sudden_cutoff_punch"
    },
    "minimal_electronic": {
        "name": "Minimal Electronic",
        "bpm_range": (110, 122),
        "moods": ["introspective", "optimistic"],
        "rhythms": ["broken_beat", "sparse_pulse"],
        "percussion": "minimal_clicks",
        "bass": "walking_pulse",
        "harmonic": "modal_dorian",
        "instruments": ["warm_pluck", "sub_sine", "minimal_clicks", "rhodes_key"],
        "texture": "clean_swiss",
        "intro": "subtle_tick_rise",
        "build": "harmonic_density_stack",
        "drop": "full_groove_entry",
        "outro": "harmonic_decay"
    },
    "synthwave": {
        "name": "Synthwave Outrun",
        "bpm_range": (120, 134),
        "moods": ["optimistic", "high_velocity"],
        "rhythms": ["four_on_floor", "rolling"],
        "percussion": "crisp_electro",
        "bass": "reese_glide",
        "harmonic": "minor_seventh",
        "instruments": ["saw_sweep", "reese_glide", "retro_gate_snare", "poly_synth"],
        "texture": "analog_tape_grit",
        "intro": "filtered_intro",
        "build": "filter_sweep_rise",
        "drop": "full_groove_entry",
        "outro": "tape_stop"
    },
    "dark_pulse": {
        "name": "Dark Sub-Pulse",
        "bpm_range": (86, 102),
        "moods": ["dark", "tension"],
        "rhythms": ["half_time", "sparse_pulse"],
        "percussion": "industrial_crunch",
        "bass": "braam_horn",
        "harmonic": "diminished_tension",
        "instruments": ["distorted_sub", "dark_braam", "industrial_metal", "clock_tick"],
        "texture": "metallic_industrial",
        "intro": "cold_open_braam",
        "build": "harmonic_density_stack",
        "drop": "heavy_sub_impact",
        "outro": "sub_heartbeat"
    },
    "glitch_electronic": {
        "name": "Glitch Matrix",
        "bpm_range": (126, 148),
        "moods": ["high_velocity", "mysterious"],
        "rhythms": ["broken_beat", "syncopated"],
        "percussion": "minimal_clicks",
        "bass": "acid_filter",
        "harmonic": "modal_dorian",
        "instruments": ["glitch_clicks", "granular_synth", "sub_sine", "bitcrush_lead"],
        "texture": "crystal_digital",
        "intro": "subtle_tick_rise",
        "build": "triplet_pulse_rise",
        "drop": "stutter_drop",
        "outro": "sudden_cutoff_punch"
    },
    "documentary": {
        "name": "Documentary Acoustic-Electronic",
        "bpm_range": (84, 105),
        "moods": ["introspective", "triumphant"],
        "rhythms": ["evolving", "sparse_pulse"],
        "percussion": "clockwork_ticks",
        "bass": "deep_sub_drone",
        "harmonic": "lush_extended",
        "instruments": ["felt_piano", "warm_cello", "sub_sine", "clock_tick"],
        "texture": "analog_tape_grit",
        "intro": "atmospheric_swell",
        "build": "harmonic_density_stack",
        "drop": "melodic_arp_explosion",
        "outro": "harmonic_decay"
    },
    "organic_percussion": {
        "name": "Organic Kinetic Pulse",
        "bpm_range": (108, 128),
        "moods": ["optimistic", "high_velocity"],
        "rhythms": ["syncopated", "broken_beat"],
        "percussion": "boom_bap_swung",
        "bass": "walking_pulse",
        "harmonic": "modal_dorian",
        "instruments": ["wood_rimshot", "finger_pluck", "warm_bass", "shaker_pulse"],
        "texture": "analog_tape_grit",
        "intro": "immediate_groove",
        "build": "triplet_pulse_rise",
        "drop": "full_groove_entry",
        "outro": "reverberant_tail"
    },
    "lofi_technology": {
        "name": "Lo-Fi Computational Warmth",
        "bpm_range": (80, 92),
        "moods": ["introspective", "optimistic"],
        "rhythms": ["broken_beat", "half_time"],
        "percussion": "boom_bap_swung",
        "bass": "walking_pulse",
        "harmonic": "lush_extended",
        "instruments": ["vintage_rhodes", "tape_crackle", "warm_sub", "swung_snare"],
        "texture": "analog_tape_grit",
        "intro": "immediate_groove",
        "build": "harmonic_density_stack",
        "drop": "full_groove_entry",
        "outro": "tape_stop"
    },
    "orchestral_hybrid": {
        "name": "Orchestral Hybrid Anthem",
        "bpm_range": (88, 112),
        "moods": ["triumphant", "tension"],
        "rhythms": ["cinematic_hits", "evolving"],
        "percussion": "orchestral_taiko",
        "bass": "braam_horn",
        "harmonic": "power_intervals",
        "instruments": ["taiko_drum", "brass_braam", "spiccato_strings", "hybrid_synth"],
        "texture": "deep_sub_space",
        "intro": "cold_open_braam",
        "build": "harmonic_density_stack",
        "drop": "heavy_sub_impact",
        "outro": "reverberant_tail"
    },
    "modern_corporate": {
        "name": "Modern Technical Explainer",
        "bpm_range": (114, 126),
        "moods": ["optimistic", "introspective"],
        "rhythms": ["four_on_floor", "syncopated"],
        "percussion": "crisp_electro",
        "bass": "walking_pulse",
        "harmonic": "lush_extended",
        "instruments": ["muted_guitar", "sine_pad", "clean_kick", "marimba_accent"],
        "texture": "clean_swiss",
        "intro": "filtered_intro",
        "build": "filter_sweep_rise",
        "drop": "full_groove_entry",
        "outro": "harmonic_decay"
    },
    "dark_tech": {
        "name": "Dark Tech Industrial",
        "bpm_range": (126, 140),
        "moods": ["dark", "high_velocity"],
        "rhythms": ["four_on_floor", "rolling"],
        "percussion": "industrial_crunch",
        "bass": "acid_filter",
        "harmonic": "diminished_tension",
        "instruments": ["metal_percussion", "distorted_saw", "sub_boom", "industrial_kick"],
        "texture": "metallic_industrial",
        "intro": "immediate_groove",
        "build": "triplet_pulse_rise",
        "drop": "heavy_sub_impact",
        "outro": "sudden_cutoff_punch"
    },
    "atmospheric_space": {
        "name": "Atmospheric Zero-G",
        "bpm_range": (72, 88),
        "moods": ["mysterious", "introspective"],
        "rhythms": ["sparse_pulse", "evolving"],
        "percussion": "minimal_clicks",
        "bass": "deep_sub_drone",
        "harmonic": "suspended_open",
        "instruments": ["shimmer_reverb", "drone_sub", "glass_bell", "celestial_chime"],
        "texture": "deep_sub_space",
        "intro": "atmospheric_swell",
        "build": "filter_sweep_rise",
        "drop": "melodic_arp_explosion",
        "outro": "reverberant_tail"
    },
    "high_energy_digital": {
        "name": "High-Energy Digital Drill",
        "bpm_range": (138, 165),
        "moods": ["high_velocity", "tension"],
        "rhythms": ["triplet", "syncopated"],
        "percussion": "trap_triplet",
        "bass": "plucked_808",
        "harmonic": "diminished_tension",
        "instruments": ["tuned_cowbell", "sliding_808", "triplet_hihat", "distorted_synth"],
        "texture": "crystal_digital",
        "intro": "immediate_groove",
        "build": "triplet_pulse_rise",
        "drop": "stutter_drop",
        "outro": "sudden_cutoff_punch"
    },
    "minimal_piano_electro": {
        "name": "Minimal Piano & Sub Pulse",
        "bpm_range": (86, 108),
        "moods": ["introspective", "triumphant"],
        "rhythms": ["broken_beat", "sparse_pulse"],
        "percussion": "clockwork_ticks",
        "bass": "deep_sub_drone",
        "harmonic": "lush_extended",
        "instruments": ["felt_piano", "sine_sub", "tape_hiss", "clock_tick"],
        "texture": "analog_tape_grit",
        "intro": "subtle_tick_rise",
        "build": "harmonic_density_stack",
        "drop": "melodic_arp_explosion",
        "outro": "harmonic_decay"
    },
    "deep_bass_drone": {
        "name": "Deep Subsonic Monolith",
        "bpm_range": (75, 92),
        "moods": ["dark", "tension"],
        "rhythms": ["sparse_pulse", "cinematic_hits"],
        "percussion": "industrial_crunch",
        "bass": "deep_sub_drone",
        "harmonic": "diminished_tension",
        "instruments": ["sub_32hz", "resonant_drone", "impact_hit", "metallic_echo"],
        "texture": "deep_sub_space",
        "intro": "cold_open_braam",
        "build": "harmonic_density_stack",
        "drop": "heavy_sub_impact",
        "outro": "sub_heartbeat"
    },
    "fast_rhythmic_math": {
        "name": "Algorithmic Precision Matrix",
        "bpm_range": (132, 156),
        "moods": ["high_velocity", "mysterious"],
        "rhythms": ["rolling", "syncopated"],
        "percussion": "clockwork_ticks",
        "bass": "reese_glide",
        "harmonic": "modal_dorian",
        "instruments": ["glass_bell", "fast_arp", "reese_glide", "relay_click"],
        "texture": "crystal_digital",
        "intro": "immediate_groove",
        "build": "triplet_pulse_rise",
        "drop": "melodic_arp_explosion",
        "outro": "sudden_cutoff_punch"
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. CHORD PROGRESSIONS BY MOOD & HARMONIC INTENT
# ─────────────────────────────────────────────────────────────────────────────

CHORD_PROGRESSIONS_BY_MOOD: Dict[str, List[List[str]]] = {
    "tension": [
        ["Dm", "E", "Am", "F"],
        ["Cm", "Ab", "Fm", "G"],
        ["Em", "Bbm", "C", "B"],
        ["Am", "F", "Dm", "E"],
        ["Fm", "Db", "Bbm", "C"],
        ["Gm", "Eb", "Cm", "D"],
    ],
    "resolution": [
        ["F", "G", "Em", "Am"],
        ["C", "G", "Am", "F"],
        ["Dm", "G", "C", "Am"],
        ["Bb", "C", "Am", "Dm"],
        ["Eb", "F", "Dm", "Gm"],
    ],
    "optimistic": [
        ["D", "A", "Bm", "G"],
        ["C", "F", "Am", "G"],
        ["G", "D", "Em", "C"],
        ["A", "E", "F#m", "D"],
        ["F", "C", "Dm", "Bb"],
    ],
    "mysterious": [
        ["Em", "C", "Am", "B"],
        ["F#m", "D", "A", "C#"],
        ["Am", "F#m", "F", "E"],
        ["Dm", "Bb", "Gm", "A"],
        ["Abm", "E", "Gb", "Ebm"],
    ],
    "futuristic": [
        ["Am", "F", "Dm", "Em"],
        ["Cm", "Eb", "Bb", "Ab"],
        ["Fm", "Cm", "Db", "Eb"],
        ["Dm", "F", "Am", "E"],
        ["Gm", "Bb", "F", "Eb"],
    ],
    "emotional": [
        ["Dm", "Bb", "F", "C"],
        ["Am", "Em", "F", "C"],
        ["Em", "C", "G", "D"],
        ["Bm", "G", "D", "A"],
        ["Cm", "Ab", "Eb", "Bb"],
    ],
    "dark": [
        ["Bbm", "Gb", "Ebm", "F"],
        ["Dm", "Bb", "Gm", "A"],
        ["Em", "C", "Am", "B"],
        ["Fm", "Db", "Bbm", "C"],
        ["Cm", "Ab", "Fm", "G"],
    ],
    "triumphant": [
        ["Eb", "Bb", "Cm", "Ab"],
        ["G", "D", "Em", "C"],
        ["C", "G", "Am", "F"],
        ["D", "A", "Bm", "G"],
        ["F", "C", "Dm", "Bb"],
    ],
    "introspective": [
        ["Am", "Em", "F", "G"],
        ["Dm", "Am", "Bb", "C"],
        ["C", "Am", "F", "G"],
        ["Em", "G", "C", "D"],
        ["Gm", "Dm", "Eb", "F"],
    ],
    "high_velocity": [
        ["Fm", "Db", "Eb", "Cm"],
        ["Dm", "Bb", "C", "Am"],
        ["Am", "F", "G", "Em"],
        ["Em", "C", "D", "Bm"],
        ["Cm", "Ab", "Bb", "Gm"],
    ]
}


# ─────────────────────────────────────────────────────────────────────────────
# 3. TEMPLATE TO COMPATIBLE AUDIO GENRES MAPPING
# ─────────────────────────────────────────────────────────────────────────────

STYLE_TO_AUDIO_GENRES: Dict[str, List[str]] = {
    "editorial": [
        "documentary", "minimal_piano_electro", "minimal_electronic", "organic_percussion"
    ],
    "cinematic": [
        "cinematic_electronic", "orchestral_hybrid", "deep_bass_drone", "atmospheric_space"
    ],
    "cyberpunk": [
        "synthwave", "energetic_tech", "high_energy_digital", "glitch_electronic"
    ],
    "terminal": [
        "dark_tech", "glitch_electronic", "fast_rhythmic_math", "lofi_technology"
    ],
    "brutalist": [
        "dark_tech", "high_energy_digital", "industrial_crunch", "dark_pulse"
    ],
    "minimal": [
        "minimal_electronic", "futuristic_ambient", "minimal_piano_electro", "organic_percussion"
    ],
    "swiss_grid": [
        "modern_corporate", "minimal_electronic", "futuristic_ambient", "organic_percussion"
    ],
    "neo_futuristic": [
        "energetic_tech", "synthwave", "glitch_electronic", "fast_rhythmic_math"
    ],
    "glass_ui": [
        "futuristic_ambient", "atmospheric_space", "minimal_piano_electro", "documentary"
    ],
    "blueprint": [
        "fast_rhythmic_math", "minimal_electronic", "dark_pulse", "documentary"
    ],
    "retro_computing": [
        "synthwave", "lofi_technology", "glitch_electronic", "minimal_electronic"
    ],
    "monochrome": [
        "dark_pulse", "minimal_electronic", "deep_bass_drone", "documentary"
    ],
    "luxury_tech": [
        "cinematic_electronic", "orchestral_hybrid", "modern_corporate", "minimal_piano_electro"
    ],
    "holographic": [
        "futuristic_ambient", "glitch_electronic", "energetic_tech", "synthwave"
    ],
    "paper_technical": [
        "lofi_technology", "organic_percussion", "documentary", "minimal_piano_electro"
    ]
}


# ─────────────────────────────────────────────────────────────────────────────
# 4. DETERMINISTIC SEED & AUDIO DNA BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def compute_audio_seed(
    project_id: str,
    topic: str,
    style_id: str,
    extra_salt: str = ""
) -> int:
    """Computes a deterministic integer hash from project, topic, and style."""
    raw = f"{project_id}_{topic}_{style_id}_{extra_salt}".encode("utf-8")
    h = hashlib.sha256(raw).hexdigest()
    return int(h[:8], 16)


def generate_audio_dna(
    topic: str,
    style_id: str = "cinematic",
    duration_sec: float = 50.0,
    project_id: str = "default_proj",
    requested_genre: Optional[str] = None,
    requested_bpm: Optional[float] = None,
    seed_salt: str = "",
    story_structure_id: Optional[str] = None
) -> AudioDNA:
    """
    Synthesizes a tailored, cohesive AudioDNA for a video.
    Guarantees deterministic reproducibility for identical inputs while
    ensuring creative diversity across different topics and styles.
    """
    seed = compute_audio_seed(project_id, topic, style_id, seed_salt)

    # 1. Select Genre
    candidate_genres = STYLE_TO_AUDIO_GENRES.get(style_id, ["cinematic_electronic", "energetic_tech", "futuristic_ambient"])
    if requested_genre and requested_genre in MUSICAL_GENRES:
        genre_key = requested_genre
    else:
        # Topic-aware genre bias
        t_low = topic.lower()
        if any(w in t_low for w in ["math", "geometry", "3d", "vector", "matrix"]):
            favored = [g for g in candidate_genres if g in ("fast_rhythmic_math", "futuristic_ambient", "cinematic_electronic")]
            genre_key = favored[seed % len(favored)] if favored else candidate_genres[seed % len(candidate_genres)]
        elif any(w in t_low for w in ["lofi", "chill", "relax", "clean"]):
            genre_key = "lofi_technology"
        elif any(w in t_low for w in ["speed", "fast", "crash", "bug", "100x"]):
            favored = [g for g in candidate_genres if g in ("high_energy_digital", "dark_tech", "energetic_tech")]
            genre_key = favored[seed % len(favored)] if favored else candidate_genres[seed % len(candidate_genres)]
        elif any(w in t_low for w in ["hardware", "cpu", "assembly", "register", "ram"]):
            favored = [g for g in candidate_genres if g in ("dark_tech", "glitch_electronic", "fast_rhythmic_math")]
            genre_key = favored[seed % len(favored)] if favored else candidate_genres[seed % len(candidate_genres)]
        else:
            genre_key = candidate_genres[seed % len(candidate_genres)]

    spec = MUSICAL_GENRES.get(genre_key, MUSICAL_GENRES["cinematic_electronic"])

    # 2. Select BPM within genre range (not a single fixed number!)
    min_bpm, max_bpm = spec["bpm_range"]
    if requested_bpm and min_bpm <= requested_bpm <= max_bpm:
        bpm = float(requested_bpm)
    else:
        # Deterministic variation across the range (steps of 2 for musicality)
        bpm_span = int(max_bpm - min_bpm)
        step_count = max(1, bpm_span // 2)
        bpm = float(min_bpm + ((seed // 7) % step_count) * 2)

    # 3. Select Mood & Rhythm
    possible_moods = spec["moods"]
    mood = possible_moods[(seed // 13) % len(possible_moods)]

    possible_rhythms = spec["rhythms"]
    rhythm = possible_rhythms[(seed // 17) % len(possible_rhythms)]

    # 4. Select Chord Progression based on Mood
    prog_list = CHORD_PROGRESSIONS_BY_MOOD.get(mood, CHORD_PROGRESSIONS_BY_MOOD["futuristic"])
    chord_prog = prog_list[(seed // 23) % len(prog_list)]

    # Key root and mode
    first_chord = chord_prog[0]
    key_root = first_chord.replace("m", "").replace("7", "")
    scale_mode = "natural_minor" if "m" in first_chord else "major"

    # 5. Energy Level Classification
    if bpm >= 135:
        energy_level = "high_drive"
    elif bpm >= 115:
        energy_level = "pulsing_medium"
    elif bpm <= 88 and "ambient" in genre_key:
        energy_level = "low_ambient"
    else:
        energy_level = "dynamic_crescendo"

    # 6. Generate Energy Curve across video duration
    energy_curve = _generate_energy_curve(duration_sec, energy_level, seed)

    # Construct unique ID
    dna_id = f"audio_{genre_key}_{int(bpm)}bpm_{seed % 10000:04d}"

    return AudioDNA(
        id=dna_id,
        genre=genre_key,
        genre_name=spec["name"],
        mood=mood,
        energy=energy_level,
        bpm=bpm,
        rhythm=rhythm,
        percussion_style=spec["percussion"],
        bass_style=spec["bass"],
        harmonic_style=spec["harmonic"],
        chord_progression=chord_prog,
        key_root=key_root,
        scale_mode=scale_mode,
        instrument_palette=spec["instruments"],
        texture=spec["texture"],
        intro_style=spec["intro"],
        build_style=spec["build"],
        drop_style=spec["drop"],
        outro_style=spec["outro"],
        energy_curve=energy_curve,
        audio_events=[],
        variation_seed=seed
    )


select_audio_dna = generate_audio_dna


def _generate_energy_curve(
    duration_sec: float,
    energy_level: str,
    seed: int
) -> List[Dict[str, Any]]:
    """
    Constructs an intentional narrative musical energy curve across duration.
    Prevents flat loop fatigue.
    """
    curve_variations = [
        # Variation 0: Classic Narrative Arc (Cold Open -> Build -> Climax -> Payoff)
        [
            {"time_ratio": 0.00, "energy": 0.25, "section": "intro_tension"},
            {"time_ratio": 0.12, "energy": 0.50, "section": "groove_entry"},
            {"time_ratio": 0.35, "energy": 0.75, "section": "core_build"},
            {"time_ratio": 0.68, "energy": 0.40, "section": "deep_breakdown"},
            {"time_ratio": 0.82, "energy": 0.95, "section": "climax_drop"},
            {"time_ratio": 0.95, "energy": 0.30, "section": "resolution"}
        ],
        # Variation 1: High-Impact Front-load (Viral Hook Punch -> Steady Driving -> Climax)
        [
            {"time_ratio": 0.00, "energy": 0.85, "section": "immediate_impact"},
            {"time_ratio": 0.10, "energy": 0.45, "section": "focused_explanation"},
            {"time_ratio": 0.40, "energy": 0.65, "section": "steady_groove"},
            {"time_ratio": 0.75, "energy": 0.90, "section": "final_crescendo"},
            {"time_ratio": 0.92, "energy": 0.20, "section": "sub_tail"}
        ],
        # Variation 2: Ascending Triple-Step (Continuous Escalation)
        [
            {"time_ratio": 0.00, "energy": 0.20, "section": "atmospheric_intro"},
            {"time_ratio": 0.20, "energy": 0.45, "section": "tier_1_pulse"},
            {"time_ratio": 0.45, "energy": 0.70, "section": "tier_2_arps"},
            {"time_ratio": 0.70, "energy": 0.95, "section": "tier_3_maximum"},
            {"time_ratio": 0.90, "energy": 0.35, "section": "harmonic_lock"}
        ]
    ]

    selected_curve = curve_variations[(seed // 31) % len(curve_variations)]
    for pt in selected_curve:
        pt["time_sec"] = round(pt["time_ratio"] * duration_sec, 2)
    return selected_curve


def extract_audio_events_from_motion_plan(
    motion_plan_or_scenes: Any,
    duration_sec: Optional[float] = None
) -> List[AudioEventMarker]:
    """
    Parses a motion plan or scenes list and derives precise musical accent markers:
    - Beat 1 Hook -> "intro" / "impact"
    - Metaphor / Reveal -> "reveal"
    - Diagram / Complexity -> "build"
    - Code execution -> "rhythm_accent"
    - Payoff / Resolution -> "resolution" / "impact"
    """
    if isinstance(motion_plan_or_scenes, dict):
        scenes = motion_plan_or_scenes.get("scenes", [])
    elif isinstance(motion_plan_or_scenes, list):
        scenes = motion_plan_or_scenes
    else:
        scenes = []

    events: List[AudioEventMarker] = []

    if not scenes:
        return events

    for idx, sc in enumerate(scenes):
        start = sc.get("start", 0.0)
        v_type = sc.get("visual_type", "")
        beat_name = sc.get("beat_name", "").upper()

        if idx == 0:
            events.append(AudioEventMarker(
                time=start,
                type="intro",
                intensity=0.8,
                description="Cold open visual entry"
            ))
            # 0.8s impact hit
            events.append(AudioEventMarker(
                time=round(start + 0.8, 2),
                type="impact",
                intensity=0.9,
                description="Hook headline punch"
            ))
        elif v_type in ("metaphor", "math_3d"):
            events.append(AudioEventMarker(
                time=start,
                type="reveal",
                intensity=0.85,
                description=f"{v_type} spatial reveal"
            ))
        elif v_type == "diagram":
            events.append(AudioEventMarker(
                time=start,
                type="build",
                intensity=0.75,
                description="Architectural diagram progression"
            ))
        elif v_type == "code":
            events.append(AudioEventMarker(
                time=start,
                type="transition",
                intensity=0.7,
                description="Code execution enter"
            ))
        elif v_type == "payoff" or idx == len(scenes) - 1:
            events.append(AudioEventMarker(
                time=start,
                type="resolution",
                intensity=1.0,
                description="Climax payoff / final takeaway"
            ))

    return events
