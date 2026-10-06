"""
audio_pipeline.py
=================
High-energy, synchronized voiceover generator with procedural background music
and sound effects (SFX) using edge-tts, numpy, and scipy.

Features:
- Edge-TTS neural speech generation (en-US-ChristopherNeural) at +15% to +25% rate.
- Scene-by-scene audio alignment with millisecond-exact duration measurement via ffprobe.
- 100% Procedural Cyber/Tech Electronic Music Bed (~124 BPM) with sub-bass drone, chords, arps, and percussion.
- 100% Procedural SFX: whooshes, bass impacts, digital UI clicks/blips, and tension risers.
- True audio ducking (-10 dB during voice activity) with smooth attack/release.
- Peak normalization and soft-limiting to -1.0 dBFS.
- Export to 48 kHz stereo 24-bit/16-bit WAV and MP3.
"""

import os
import sys
import re
import math
import asyncio
import subprocess
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
from scipy import signal
from scipy.io import wavfile
import edge_tts

# ── Global Audio Settings ───────────────────────────────────────────────────
SAMPLE_RATE = 48000
TOTAL_DURATION = 50.0  # seconds
VOICE_NAME = "en-US-ChristopherNeural"
DEFAULT_SPEECH_RATE = "+20%"

# Output directories
TEMP_DIR = "temp_audio"
OUTPUT_DIR = "output_audio"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ── Scene Data Structure ────────────────────────────────────────────────────
@dataclass
class SceneVoice:
    id: str
    text: str
    start_time: float  # in seconds
    rate: str = DEFAULT_SPEECH_RATE
    pitch: str = "+0Hz"
    # Populated after generation:
    duration: float = 0.0
    wav_path: str = ""
    audio_data: Optional[np.ndarray] = None


# ── 1. Text-to-Speech (edge-tts) Pipeline ───────────────────────────────────

async def _synthesize_clip(scene: SceneVoice, voice: str) -> SceneVoice:
    """Generate audio for a single scene voice line via edge-tts."""
    mp3_path = os.path.join(TEMP_DIR, f"{scene.id}.mp3")
    wav_path = os.path.join(TEMP_DIR, f"{scene.id}_48k.wav")

    # Sanitize spoken text so no raw JSON dict syntax is ever read
    text_to_speak = scene.text or ""
    m_dict = re.search(r"['\"](?:text|narration)['\"]\s*:\s*['\"](.*?)['\"]\}?$", text_to_speak, re.DOTALL)
    if m_dict:
        text_to_speak = m_dict.group(1).strip()
    text_to_speak = text_to_speak.replace("{'text':", "").replace('{"text":', "").strip(" '\"{}:")
    if not text_to_speak:
        text_to_speak = f"Observe the execution flow for {scene.id}."

    # Generate MP3 with voice, rate, and pitch
    communicate = edge_tts.Communicate(text_to_speak, voice, rate=scene.rate, pitch=scene.pitch)
    await communicate.save(mp3_path)

    # Convert to 48 kHz stereo WAV using FFmpeg
    cmd_conv = [
        "ffmpeg", "-y",
        "-i", mp3_path,
        "-ar", str(SAMPLE_RATE),
        "-ac", "2",
        "-c:a", "pcm_s16le",
        wav_path
    ]
    subprocess.run(cmd_conv, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Measure exact duration via ffprobe
    cmd_probe = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        wav_path
    ]
    res = subprocess.run(cmd_probe, capture_output=True, text=True, check=True)
    duration = float(res.stdout.strip())

    # Read WAV data into numpy array float32 [-1.0, 1.0]
    sr, raw_data = wavfile.read(wav_path)
    if raw_data.ndim == 1:
        raw_data = np.stack([raw_data, raw_data], axis=-1)
    audio_float = raw_data.astype(np.float32) / 32768.0

    scene.duration = duration
    scene.wav_path = wav_path
    scene.audio_data = audio_float
    return scene


def generate_voiceover_clips(scenes: List[SceneVoice], voice: str = VOICE_NAME) -> List[SceneVoice]:
    """Generate all voiceover clips asynchronously and log timing analysis."""
    print(f"\n[TTS] Generating {len(scenes)} voiceover clips with {voice} ...")

    async def _run_all():
        tasks = [_synthesize_clip(sc, voice) for sc in scenes]
        return await asyncio.gather(*tasks)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        scenes = loop.run_until_complete(_run_all())
    finally:
        loop.close()

    # Timing and sync validation table
    print("\n" + "=" * 78)
    print(f"{'Scene ID':<16} | {'Start (s)':<9} | {'Dur (s)':<8} | {'End (s)':<8} | {'Text Preview'}")
    print("-" * 78)
    for i, sc in enumerate(scenes):
        end_time = sc.start_time + sc.duration
        preview = sc.text if len(sc.text) <= 32 else sc.text[:29] + "..."
        print(f"{sc.id:<16} | {sc.start_time:9.2f} | {sc.duration:8.2f} | {end_time:8.2f} | {preview}")

        # Overlap check
        if i < len(scenes) - 1:
            next_start = scenes[i + 1].start_time
            if end_time > next_start:
                overlap = end_time - next_start
                print(f"  [!] WARNING: Scene '{sc.id}' overlaps next scene by {overlap:.2f}s!")
    print("=" * 78 + "\n")
    return scenes


# ── 2. Procedural Sound Effects (SFX) Synthesizer ───────────────────────────

class SFXGenerator:
    """Procedural synthesis of sound effects using NumPy and SciPy."""

    @staticmethod
    def create_whoosh(duration: float = 0.7, sweep_start: float = 200, sweep_end: float = 1800) -> np.ndarray:
        """Dynamic pitch-swept lowpass filtered noise transition whoosh."""
        n_samples = int(SAMPLE_RATE * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        # White noise base
        rng = np.random.default_rng(101)
        noise = rng.uniform(-1.0, 1.0, n_samples)

        # Swept tonal body
        f_instant = np.linspace(sweep_start, sweep_end, n_samples)
        phase = 2 * np.pi * np.cumsum(f_instant) / SAMPLE_RATE
        tonal = np.sin(phase) * 0.4

        combined = noise * 0.7 + tonal

        # Filter noise with lowpass
        b, a = signal.butter(4, 2500 / (SAMPLE_RATE / 2), btype='low')
        filtered = signal.lfilter(b, a, combined)

        # Smooth parabolic envelope (whoosh curve)
        env = np.sin(np.pi * (t / duration)) ** 2.2
        out = filtered * env

        # Stereo pan movement (sweep from left to right)
        pan = np.linspace(0.2, 0.8, n_samples)
        left = out * (1.0 - pan)
        right = out * pan
        return np.stack([left, right], axis=-1).astype(np.float32)

    @staticmethod
    def create_bass_impact(duration: float = 1.6) -> np.ndarray:
        """Deep bass punch hit with sub-bass drop and low-end rumble."""
        n_samples = int(SAMPLE_RATE * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        # Punch transient click (180 Hz drop to 60 Hz in 40ms)
        click_t = t[:int(SAMPLE_RATE * 0.04)]
        click_freq = np.linspace(220, 60, len(click_t))
        click_phase = 2 * np.pi * np.cumsum(click_freq) / SAMPLE_RATE
        click = np.sin(click_phase) * np.exp(-click_t / 0.01)

        # Sub-bass boom: 85 Hz dropping to 38 Hz with slow decay
        f_boom = 38.0 + 47.0 * np.exp(-t / 0.28)
        boom_phase = 2 * np.pi * np.cumsum(f_boom) / SAMPLE_RATE
        boom_env = np.exp(-t / 0.45)
        boom = np.sin(boom_phase) * boom_env

        # Soft distorted sub harmonics
        sub = np.tanh(boom * 2.0) * 0.6

        # Stereo low-mid rumble noise
        rng = np.random.default_rng(202)
        rumble = rng.normal(0, 0.15, n_samples) * np.exp(-t / 0.35)
        b, a = signal.butter(2, 400 / (SAMPLE_RATE / 2), btype='low')
        rumble = signal.lfilter(b, a, rumble)

        mono = np.zeros(n_samples)
        mono[:len(click)] += click * 0.8
        mono += boom * 0.9 + sub * 0.4 + rumble * 0.3

        # Normalize
        peak = np.max(np.abs(mono))
        if peak > 0:
            mono = mono / peak

        return np.stack([mono, mono], axis=-1).astype(np.float32)

    @staticmethod
    def create_ui_blip(freq: float = 1950.0, duration: float = 0.08) -> np.ndarray:
        """Clean cyber/digital UI click/blip with fast exponential decay."""
        n_samples = int(SAMPLE_RATE * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        # Fast pitch glide down for snappy click
        f = freq * (1.0 + 0.3 * np.exp(-t / 0.01))
        phase = 2 * np.pi * np.cumsum(f) / SAMPLE_RATE
        env = np.exp(-t / 0.018)
        sig = np.sin(phase) * env

        # Harmonic overtone
        sig += 0.25 * np.sin(phase * 2.0) * np.exp(-t / 0.012)
        return np.stack([sig, sig], axis=-1).astype(np.float32)

    @staticmethod
    def create_tension_riser(duration: float = 3.5) -> np.ndarray:
        """Tension riser before payoff: ascending frequency + accelerating noise pulse."""
        n_samples = int(SAMPLE_RATE * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        t_norm = t / duration

        # Exponential pitch rise: 80 Hz -> 950 Hz
        f_rise = 80.0 * (950.0 / 80.0) ** t_norm
        phase = 2 * np.pi * np.cumsum(f_rise) / SAMPLE_RATE

        # Sawtooth harmonic rich wave
        carrier = signal.sawtooth(phase) * 0.3 + np.sin(phase) * 0.4

        # Rising noise wash
        rng = np.random.default_rng(303)
        noise = rng.uniform(-0.5, 0.5, n_samples)
        # Dynamic lowpass filter simulated via modulation
        noise_env = (t_norm ** 2) * 0.4
        noise = noise * noise_env

        # Accelerating rhythmic tremolo
        trem_freq = 2.0 + 12.0 * (t_norm ** 2)  # 2 Hz up to 14 Hz
        trem_phase = 2 * np.pi * np.cumsum(trem_freq) / SAMPLE_RATE
        trem = 0.6 + 0.4 * np.sin(trem_phase)

        env = t_norm ** 1.8  # slow crescendo
        sig = (carrier + noise) * trem * env

        # Soft stereo widening
        pan = np.sin(2 * np.pi * 3.0 * t) * 0.25
        left = sig * (1.0 - pan)
        right = sig * (1.0 + pan)
        return np.stack([left, right], axis=-1).astype(np.float32)


# ── 3. Procedural Background Music Generator ────────────────────────────────

class ProceduralMusicGenerator:
    """
    Advanced procedural multi-genre dynamic music engine:
    Supports:
    - 'dark_math': mystical minor chords, ticking clockwork, deep sub braams, bell pings.
    - 'cinematic': Hans Zimmer ostinato, cinematic sub braams, taiko impacts, string pads.
    - 'lofi_chill': warm vintage Rhodes piano, vinyl crackle, boom-bap swing beat.
    - 'phonk_drift': tuned 808 cowbell melody, saturated sliding 808 sub, trap drums.
    - 'retro_chiptune': 8-bit square pulse waves, chip arps, noise snare.
    - 'cyberpunk': driving electro saw leads, rolling bass, punchy rhythm.
    - 'minimal_electronic': clean warm plucks, subtle sine sub, spacious ticks.
    - Scene-aware dynamic structural arrangement (Hook -> Setup -> Reveal -> Breakdown -> Climax).
    """

class ProceduralMusicGenerator:
    """
    Procedural Music Generator synthesizing diverse, cohesive electronic/hybrid soundtracks.
    Driven by per-video AudioDNA:
    - 10 rhythm architectures (four-on-floor, broken beat, half-time, syncopated, triplet, etc.)
    - Dynamic BPM (80-175 BPM) and modal chord progressions
    - Multi-instrument synthesis (analog saw, warm Rhodes, glass bells, sub braams, chiptune, 808s)
    - Dynamic narrative energy curve modulation
    - Motion-plan audio event synchronization
    - Deterministic creative seeding
    """

    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        bpm: float = 124.0,
        style: str = "cyberpunk",
        chord_progression: Optional[List[str]] = None,
        audio_dna: Optional[Dict[str, Any]] = None,
        audio_events: Optional[List[Dict[str, Any]]] = None
    ):
        self.sr = sample_rate
        self.audio_dna = audio_dna or {}
        self.audio_events = audio_events or []
        self.style = (style or "cyberpunk").lower()

        from effects.sound_profiles import get_music_profile, MUSIC_PROFILES
        self.profile = get_music_profile(self.style)

        # 1. BPM resolution: AudioDNA > argument > profile
        if self.audio_dna.get("bpm"):
            self.bpm = float(self.audio_dna["bpm"])
        elif bpm and bpm > 50 and bpm != 124.0:
            self.bpm = bpm
        else:
            self.bpm = self.profile.bpm

        # 2. Rhythmic & sonic architecture
        self.rhythm = self.audio_dna.get("rhythm") or "four_on_floor"
        self.percussion_style = self.audio_dna.get("percussion_style") or "crisp_electro"
        self.bass_style = self.audio_dna.get("bass_style") or "deep_sub_drone"
        self.instrument_palette = self.audio_dna.get("instrument_palette") or []
        self.energy_curve = self.audio_dna.get("energy_curve") or []
        self.seed = int(self.audio_dna.get("variation_seed", 42))

        self.beat_sec = 60.0 / max(40.0, self.bpm)
        self.step_sec = self.beat_sec / 4.0

        # Algorithmic 12-TET note frequencies across all octaves
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        self.notes = {}
        for midi in range(21, 108):
            freq = 440.0 * (2.0 ** ((midi - 69) / 12.0))
            octave = (midi // 12) - 1
            name = f"{note_names[midi % 12]}{octave}"
            self.notes[name] = freq

        chord_library = {
            "Am": {"root": "A1", "pad": ["A3", "C4", "E4"], "arp": ["A3", "C4", "E4", "A4"]},
            "Em": {"root": "E1", "pad": ["E3", "G3", "B3"], "arp": ["E3", "G3", "B3", "E4"]},
            "Dm": {"root": "D2", "pad": ["D3", "F3", "A3"], "arp": ["D3", "F3", "A3", "D4"]},
            "Fm": {"root": "F1", "pad": ["F3", "G#3", "C4"], "arp": ["F3", "G#3", "C4", "F4"]},
            "Cm": {"root": "C2", "pad": ["C3", "D#3", "G3"], "arp": ["C4", "D#4", "G4", "C5"]},
            "Bbm": {"root": "A#1", "pad": ["A#2", "C#3", "F3"], "arp": ["A#3", "C#4", "F4", "A#4"]},
            "Gm": {"root": "G1", "pad": ["G2", "A#2", "D3"], "arp": ["G3", "A#3", "D4", "G4"]},
            "F": {"root": "F1", "pad": ["F3", "A3", "C4"], "arp": ["F3", "A3", "C4", "F4"]},
            "C": {"root": "C2", "pad": ["C3", "E3", "G3"], "arp": ["C4", "E4", "G4", "C5"]},
            "G": {"root": "G1", "pad": ["G2", "B2", "D3"], "arp": ["G3", "B3", "D4", "G4"]},
            "Db": {"root": "C#1", "pad": ["C#3", "F3", "G#3"], "arp": ["C#4", "F4", "G#4", "C#5"]},
            "Eb": {"root": "D#1", "pad": ["D#3", "G3", "A#3"], "arp": ["D#4", "G4", "A#4", "D#5"]},
            "Bb": {"root": "A#1", "pad": ["A#2", "D3", "F3"], "arp": ["A#3", "D4", "F4", "A#4"]},
            "A": {"root": "A1", "pad": ["A2", "C#3", "E3"], "arp": ["A3", "C#4", "E4", "A4"]},
            "E": {"root": "E1", "pad": ["E2", "G#2", "B2"], "arp": ["E3", "G#3", "B3", "E4"]},
            "F#m": {"root": "F#1", "pad": ["F#3", "A3", "C#4"], "arp": ["F#3", "A3", "C#4", "F#4"]},
            "D": {"root": "D2", "pad": ["D3", "F#3", "A3"], "arp": ["D3", "F#3", "A3", "D4"]},
            "Abm": {"root": "G#1", "pad": ["G#3", "B3", "D#4"], "arp": ["G#3", "B3", "D#4", "G#4"]},
            "Gb": {"root": "F#1", "pad": ["F#3", "A#3", "C#4"], "arp": ["F#3", "A#3", "C#4", "F#4"]},
            "Ebm": {"root": "D#1", "pad": ["D#3", "F#3", "A#3"], "arp": ["D#4", "F#4", "A#4", "D#5"]},
            "Bm": {"root": "B1", "pad": ["B3", "D4", "F#4"], "arp": ["B3", "D4", "F#4", "B4"]},
            "C#m": {"root": "C#2", "pad": ["C#3", "E3", "G#3"], "arp": ["C#4", "E4", "G#4", "C#5"]},
            "B": {"root": "B1", "pad": ["B2", "D#3", "F#3"], "arp": ["B3", "D#4", "F#4", "B4"]},
            "F#": {"root": "F#1", "pad": ["F#2", "A#2", "C#3"], "arp": ["F#3", "A#3", "C#4", "F#4"]},
            "Ab": {"root": "G#1", "pad": ["G#2", "C3", "D#3"], "arp": ["G#3", "C4", "D#4", "G#4"]},
        }

        # 3. Chord progression resolution: AudioDNA > parameter > profile
        dna_prog = self.audio_dna.get("chord_progression")
        prog = dna_prog if (dna_prog and len(dna_prog) >= 3) else (
            chord_progression if (chord_progression and len(chord_progression) >= 3) else self.profile.chord_progression
        )
        self.chords = [chord_library.get(ch, chord_library["Am"]) for ch in prog]

    def _adsr(self, length: int, a: float, d: float, s: float, r: float) -> np.ndarray:
        na = int(a * self.sr)
        nd = int(d * self.sr)
        nr = int(r * self.sr)
        ns = max(0, length - na - nd - nr)
        env = []
        if na > 0: env.append(np.linspace(0, 1, na))
        if nd > 0: env.append(np.linspace(1, s, nd))
        if ns > 0: env.append(np.full(ns, s))
        if nr > 0: env.append(np.linspace(s, 0, nr))
        res = np.concatenate(env) if env else np.ones(length)
        if len(res) < length:
            res = np.pad(res, (0, length - len(res)))
        return res[:length]

    def _synth_pad_note(self, freq: float, duration: float) -> Tuple[np.ndarray, np.ndarray]:
        n = int(self.sr * duration)
        t = np.linspace(0, duration, n, endpoint=False)
        s1 = signal.sawtooth(2 * np.pi * freq * t)
        s2 = signal.sawtooth(2 * np.pi * (freq * 1.004) * t)
        s3 = signal.sawtooth(2 * np.pi * (freq * 0.996) * t)
        mono = (s1 + s2 + s3) / 3.0
        b, a = signal.butter(2, min(900.0, freq * 4.0) / (self.sr / 2), btype='low')
        mono = signal.lfilter(b, a, mono)
        env = self._adsr(n, a=0.35, d=0.3, s=0.7, r=0.45)
        mono *= env
        left = mono * (0.8 + 0.2 * np.sin(2 * np.pi * 0.3 * t))
        right = mono * (0.8 + 0.2 * np.cos(2 * np.pi * 0.3 * t))
        return left, right

    def _synth_rhodes_chord(self, freq: float, duration: float) -> Tuple[np.ndarray, np.ndarray]:
        n = int(self.sr * duration)
        t = np.linspace(0, duration, n, endpoint=False)
        fundamental = np.sin(2 * np.pi * freq * t) * 0.75
        bell = np.sin(2 * np.pi * freq * 3.0 * t) * 0.18 * np.exp(-t / 0.35)
        mono = (fundamental + bell) * np.exp(-t / (duration * 0.8))
        trem = 0.85 + 0.15 * np.sin(2 * np.pi * 4.5 * t)
        mono *= trem
        pan = np.sin(2 * np.pi * 0.4 * t) * 0.2
        return mono * (1.0 - pan), mono * (1.0 + pan)

    def _synth_arp_note(self, freq: float, duration: float) -> np.ndarray:
        n = int(self.sr * duration)
        t = np.linspace(0, duration, n, endpoint=False)
        sig = 0.7 * np.sin(2 * np.pi * freq * t) + 0.3 * signal.sawtooth(2 * np.pi * freq * t, width=0.5)
        env = np.exp(-t / 0.08)
        return (sig * env).astype(np.float32)

    def _synth_chiptune_pulse(self, freq: float, duration: float, duty: float = 0.25) -> np.ndarray:
        n = int(self.sr * duration)
        t = np.linspace(0, duration, n, endpoint=False)
        sig = signal.square(2 * np.pi * freq * t, duty=duty) * 0.4
        env = np.exp(-t / 0.09)
        return (sig * env).astype(np.float32)

    def _synth_glass_bell(self, freq: float, duration: float) -> Tuple[np.ndarray, np.ndarray]:
        n = int(self.sr * duration)
        t = np.linspace(0, duration, n, endpoint=False)
        f1 = np.sin(2 * np.pi * freq * t) * 0.6
        f2 = np.sin(2 * np.pi * freq * 2.76 * t) * 0.25 * np.exp(-t / 0.4)
        f3 = np.sin(2 * np.pi * freq * 5.4 * t) * 0.15 * np.exp(-t / 0.2)
        mono = (f1 + f2 + f3) * np.exp(-t / 1.1)
        return mono * 0.9, mono * 1.1

    def _synth_sub_braam(self, freq: float, duration: float) -> Tuple[np.ndarray, np.ndarray]:
        n = int(self.sr * duration)
        t = np.linspace(0, duration, n, endpoint=False)
        f_glide = freq + 14.0 * np.exp(-t / 0.15)
        phase = 2 * np.pi * np.cumsum(f_glide) / self.sr
        sub = np.sin(phase) * 0.75
        saw = signal.sawtooth(phase) * 0.25
        raw = sub + saw
        dist = np.tanh(raw * 2.2) * 0.65
        env = self._adsr(n, a=0.08, d=0.3, s=0.8, r=0.4)
        mono = dist * env
        return mono * 0.95, mono * 1.05

    def _synth_reese_bass(self, freq: float, duration: float) -> Tuple[np.ndarray, np.ndarray]:
        """Detuned dual-saw Reese bass with thick chorus modulation."""
        n = int(self.sr * duration)
        t = np.linspace(0, duration, n, endpoint=False)
        detune = 1.006
        s1 = signal.sawtooth(2 * np.pi * freq * t)
        s2 = signal.sawtooth(2 * np.pi * (freq * detune) * t)
        raw = (s1 + s2) * 0.5
        b, a = signal.butter(2, min(400.0, freq * 5.0) / (self.sr / 2), btype='low')
        filtered = signal.lfilter(b, a, raw)
        env = self._adsr(n, a=0.04, d=0.2, s=0.85, r=0.2)
        mono = np.tanh(filtered * 1.8) * env * 0.65
        return mono * 0.95, mono * 1.05

    def _synth_phonk_cowbell(self, pitch_mult: float = 1.0) -> np.ndarray:
        dur = 0.18
        n = int(self.sr * dur)
        t = np.linspace(0, dur, n, endpoint=False)
        f1, f2 = 540.0 * pitch_mult, 800.0 * pitch_mult
        sig = (signal.square(2 * np.pi * f1 * t) + signal.square(2 * np.pi * f2 * t)) * 0.4
        b, a = signal.butter(2, [min(600 * pitch_mult, self.sr / 3) / (self.sr / 2), min(3200 * pitch_mult, self.sr / 2.2) / (self.sr / 2)], btype='band')
        filtered = signal.lfilter(b, a, sig)
        env = np.exp(-t / 0.045)
        return (filtered * env * 0.7).astype(np.float32)

    def _synth_kick(self) -> np.ndarray:
        dur = 0.25
        n = int(self.sr * dur)
        t = np.linspace(0, dur, n, endpoint=False)
        f = 42.0 + 88.0 * np.exp(-t / 0.035)
        phase = 2 * np.pi * np.cumsum(f) / self.sr
        env = np.exp(-t / 0.08)
        return (np.tanh(np.sin(phase) * env * 1.5) * 0.8).astype(np.float32)

    def _synth_hihat(self) -> np.ndarray:
        dur = 0.045
        n = int(self.sr * dur)
        t = np.linspace(0, dur, n, endpoint=False)
        noise = np.random.uniform(-1.0, 1.0, n)
        nyquist = self.sr / 2.0
        high_cut = min(16000.0, nyquist * 0.95)
        low_cut = min(5500.0, high_cut * 0.5)
        b, a = signal.butter(3, [low_cut / nyquist, high_cut / nyquist], btype='band')
        filtered = signal.lfilter(b, a, noise)
        env = np.exp(-t / 0.014)
        return (filtered * env * 0.35).astype(np.float32)

    def _synth_snare_or_clap(self) -> np.ndarray:
        dur = 0.16
        n = int(self.sr * dur)
        t = np.linspace(0, dur, n, endpoint=False)
        noise = np.random.uniform(-1.0, 1.0, n) * np.exp(-t / 0.04)
        tone = np.sin(2 * np.pi * 185.0 * t) * np.exp(-t / 0.03) * 0.6
        return (np.tanh((noise + tone) * 1.8) * 0.5).astype(np.float32)

    def _synth_clock_tick(self) -> np.ndarray:
        dur = 0.015
        n = int(self.sr * dur)
        t = np.linspace(0, dur, n, endpoint=False)
        click = np.sin(2 * np.pi * 4200.0 * t) * np.exp(-t / 0.003)
        return click.astype(np.float32)

    def generate_music(self, total_seconds: float = TOTAL_DURATION) -> np.ndarray:
        pid = self.audio_dna.get("genre") or getattr(self.profile, "id", "cyberpunk")
        print(f"[MUSIC] Synthesizing {total_seconds:.1f}s soundtrack: Genre='{pid}', Rhythm='{self.rhythm}', BPM={self.bpm:.1f}...")

        # Seed random generator deterministically
        rng = np.random.RandomState(self.seed % 100000)

        total_samples = int(self.sr * total_seconds)
        track_L = np.zeros(total_samples, dtype=np.float32)
        track_R = np.zeros(total_samples, dtype=np.float32)

        bar_sec = self.beat_sec * 4.0
        bar_samples = int(self.sr * bar_sec)
        n_bars = int(math.ceil(total_seconds / bar_sec))

        kick = self._synth_kick()
        hihat = self._synth_hihat()
        snare = self._synth_snare_or_clap()
        clock_tick = self._synth_clock_tick()

        # Add subtle tape warmth / analog bed for lofi or documentary
        if "lofi" in pid or "documentary" in pid or "tape" in self.audio_dna.get("texture", ""):
            noise_bed = rng.uniform(-0.008, 0.008, total_samples).astype(np.float32)
            track_L += noise_bed
            track_R += noise_bed

        for bar_idx in range(n_bars):
            bar_start_sample = bar_idx * bar_samples
            if bar_start_sample >= total_samples:
                break
            end_sample = min(bar_start_sample + bar_samples, total_samples)
            actual_len = end_sample - bar_start_sample

            chord_data = self.chords[bar_idx % len(self.chords)]
            root_freq = self.notes.get(chord_data["root"], 55.0)

            # Energy modulation from energy curve
            prog_ratio = bar_idx / max(1, n_bars - 1)
            time_sec = bar_idx * bar_sec
            energy_mult = self._get_energy_multiplier(prog_ratio)

            is_hook = prog_ratio < 0.10
            is_breakdown = 0.65 <= prog_ratio < 0.80
            is_climax = 0.80 <= prog_ratio < 0.95

            # ── 1. BASS & SUB-DRONE ──────────────────────────────────────────
            t_bar = np.linspace(0, bar_sec, bar_samples, endpoint=False)
            if self.bass_style == "braam_horn" or "cinematic" in pid or "dark" in pid:
                b_l, b_r = self._synth_sub_braam(root_freq, bar_sec)
                vol = (0.40 if is_hook else (0.65 if is_climax else 0.52)) * energy_mult
                track_L[bar_start_sample:end_sample] += b_l[:actual_len] * vol
                track_R[bar_start_sample:end_sample] += b_r[:actual_len] * vol
            elif self.bass_style == "reese_glide":
                b_l, b_r = self._synth_reese_bass(root_freq, bar_sec)
                vol = (0.35 if is_hook else 0.55) * energy_mult
                track_L[bar_start_sample:end_sample] += b_l[:actual_len] * vol
                track_R[bar_start_sample:end_sample] += b_r[:actual_len] * vol
            else:
                sub_drone = np.sin(2 * np.pi * root_freq * t_bar) * 0.40
                sub_drone += np.sin(2 * np.pi * (root_freq * 2) * t_bar) * 0.10
                sub_env = self._adsr(bar_samples, a=0.06, d=0.2, s=0.85, r=0.1)
                sub_drone *= sub_env * energy_mult
                track_L[bar_start_sample:end_sample] += sub_drone[:actual_len] * 0.50
                track_R[bar_start_sample:end_sample] += sub_drone[:actual_len] * 0.50

            # ── 2. HARMONY & INSTRUMENTS ─────────────────────────────────────
            for p_note in chord_data["pad"]:
                freq = self.notes.get(p_note, 220.0)
                if any(k in self.instrument_palette for k in ("vintage_rhodes", "felt_piano")) or "lofi" in pid:
                    p_l, p_r = self._synth_rhodes_chord(freq, bar_sec)
                    track_L[bar_start_sample:end_sample] += p_l[:actual_len] * (0.32 * energy_mult)
                    track_R[bar_start_sample:end_sample] += p_r[:actual_len] * (0.32 * energy_mult)
                elif any(k in self.instrument_palette for k in ("bell_sine", "glass_bell")) or "ambient" in pid:
                    p_l, p_r = self._synth_glass_bell(freq, bar_sec)
                    track_L[bar_start_sample:end_sample] += p_l[:actual_len] * (0.24 * energy_mult)
                    track_R[bar_start_sample:end_sample] += p_r[:actual_len] * (0.24 * energy_mult)
                else:
                    p_l, p_r = self._synth_pad_note(freq, bar_sec)
                    track_L[bar_start_sample:end_sample] += p_l[:actual_len] * (0.26 * energy_mult)
                    track_R[bar_start_sample:end_sample] += p_r[:actual_len] * (0.26 * energy_mult)

            # ── 3. MELODIC ARPS & LEADS ──────────────────────────────────────
            if not is_hook and not is_breakdown:
                arp_notes = chord_data["arp"]
                for step in range(16):
                    step_start_sec = step * self.step_sec
                    step_sample = bar_start_sample + int(step_start_sec * self.sr)
                    if step_sample >= total_samples:
                        break

                    note_idx = [0, 1, 2, 3, 2, 1, 3, 1, 0, 2, 1, 3, 2, 3, 1, 2][step % 16]
                    freq = self.notes.get(arp_notes[note_idx], 440.0)

                    if "phonk" in pid or "trap" in self.rhythm:
                        if step % 2 == 0:
                            pitch_ratio = [1.0, 1.189, 1.334, 1.498][note_idx % 4]
                            cb = self._synth_phonk_cowbell(pitch_ratio)
                            l = min(len(cb), total_samples - step_sample)
                            track_L[step_sample:step_sample + l] += cb[:l] * 0.30
                            track_R[step_sample:step_sample + l] += cb[:l] * 0.30
                    elif "retro" in pid:
                        chip = self._synth_chiptune_pulse(freq, self.step_sec * 1.5, duty=0.25)
                        l = min(len(chip), total_samples - step_sample)
                        pan = 0.3 + 0.4 * math.sin(step)
                        track_L[step_sample:step_sample + l] += chip[:l] * (1.0 - pan) * 0.28
                        track_R[step_sample:step_sample + l] += chip[:l] * pan * 0.28
                    elif "glass_bell" in self.instrument_palette:
                        if step in [0, 2, 4, 7, 9, 11, 14]:
                            bell_l, bell_r = self._synth_glass_bell(freq * 1.5, self.step_sec * 2.0)
                            l = min(len(bell_l), total_samples - step_sample)
                            track_L[step_sample:step_sample + l] += bell_l[:l] * 0.16
                            track_R[step_sample:step_sample + l] += bell_r[:l] * 0.16
                    else:
                        arp_audio = self._synth_arp_note(freq, self.step_sec * 1.8)
                        l = min(len(arp_audio), total_samples - step_sample)
                        pan = 0.35 + 0.3 * math.sin(step)
                        vol = 0.26 * energy_mult
                        track_L[step_sample:step_sample + l] += arp_audio[:l] * (1.0 - pan) * vol
                        track_R[step_sample:step_sample + l] += arp_audio[:l] * pan * vol

            # ── 4. RHYTHM ARCHITECTURE DISPATCH ──────────────────────────────
            if is_hook:
                # Hook: Minimal tension pulse or subtle ticks
                for step in range(16):
                    step_sample = bar_start_sample + int(step * self.step_sec * self.sr)
                    if step_sample < total_samples:
                        l = min(len(clock_tick), total_samples - step_sample)
                        track_L[step_sample:step_sample + l] += clock_tick[:l] * 0.20
                        track_R[step_sample:step_sample + l] += clock_tick[:l] * 0.20

            elif self.rhythm == "cinematic_hits":
                # Orchestral downbeat impact on beat 1
                k_sample = bar_start_sample
                if k_sample < total_samples:
                    k_l = min(len(kick), total_samples - k_sample)
                    track_L[k_sample:k_sample + k_l] += kick[:k_l] * 0.70
                    track_R[k_sample:k_sample + k_l] += kick[:k_l] * 0.70
                for step in range(16):
                    s_sample = bar_start_sample + int(step * self.step_sec * self.sr)
                    if s_sample < total_samples:
                        l = min(len(clock_tick), total_samples - s_sample)
                        track_L[s_sample:s_sample + l] += clock_tick[:l] * 0.18
                        track_R[s_sample:s_sample + l] += clock_tick[:l] * 0.18

            elif self.rhythm == "broken_beat":
                # Syncopated kick on beats 0, 1.5, 2.75
                for k_beat in [0.0, 1.5, 2.75]:
                    s = bar_start_sample + int(k_beat * self.beat_sec * self.sr)
                    if s < total_samples:
                        l = min(len(kick), total_samples - s)
                        track_L[s:s + l] += kick[:l] * 0.45
                        track_R[s:s + l] += kick[:l] * 0.45
                # Snare on 1.0 and 3.0 (with slight swung micro-timing)
                for sn_beat in [1.0, 3.0]:
                    s = bar_start_sample + int((sn_beat * self.beat_sec + 0.012) * self.sr)
                    if s < total_samples:
                        l = min(len(snare), total_samples - s)
                        track_L[s:s + l] += snare[:l] * 0.35
                        track_R[s:s + l] += snare[:l] * 0.35
                # Shuffled 8th hats
                for h_step in range(8):
                    s = bar_start_sample + int(h_step * self.beat_sec * 0.5 * self.sr)
                    if s < total_samples:
                        l = min(len(hihat), total_samples - s)
                        track_L[s:s + l] += hihat[:l] * 0.22
                        track_R[s:s + l] += hihat[:l] * 0.22

            elif self.rhythm == "half_time":
                # Kick on beat 0, huge snare on beat 2.0
                s = bar_start_sample
                if s < total_samples:
                    l = min(len(kick), total_samples - s)
                    track_L[s:s + l] += kick[:l] * 0.60
                    track_R[s:s + l] += kick[:l] * 0.60
                sn_s = bar_start_sample + int(2.0 * self.beat_sec * self.sr)
                if sn_s < total_samples:
                    l = min(len(snare), total_samples - sn_s)
                    track_L[sn_s:sn_s + l] += snare[:l] * 0.50
                    track_R[sn_s:sn_s + l] += snare[:l] * 0.50
                # Quarter-note hats
                for b in range(4):
                    hs = bar_start_sample + int(b * self.beat_sec * self.sr)
                    if hs < total_samples:
                        l = min(len(hihat), total_samples - hs)
                        track_L[hs:hs + l] += hihat[:l] * 0.25
                        track_R[hs:hs + l] += hihat[:l] * 0.25

            elif self.rhythm == "syncopated":
                # Latin / afro-futurist syncopation: Kick on 0, 1.25, 2.5
                for k_beat in [0.0, 1.25, 2.5]:
                    s = bar_start_sample + int(k_beat * self.beat_sec * self.sr)
                    if s < total_samples:
                        l = min(len(kick), total_samples - s)
                        track_L[s:s + l] += kick[:l] * 0.50
                        track_R[s:s + l] += kick[:l] * 0.50
                # Snare on 1.75 and 3.0
                for sn_beat in [1.75, 3.0]:
                    s = bar_start_sample + int(sn_beat * self.beat_sec * self.sr)
                    if s < total_samples:
                        l = min(len(snare), total_samples - s)
                        track_L[s:s + l] += snare[:l] * 0.35
                        track_R[s:s + l] += snare[:l] * 0.35

            elif self.rhythm == "triplet":
                # Drill / Trap rhythm: Kick on 0, 2.25 | Snare on 2.0 | Triplet hats
                for k_beat in [0.0, 2.25]:
                    s = bar_start_sample + int(k_beat * self.beat_sec * self.sr)
                    if s < total_samples:
                        l = min(len(kick), total_samples - s)
                        track_L[s:s + l] += kick[:l] * 0.55
                        track_R[s:s + l] += kick[:l] * 0.55
                sn_s = bar_start_sample + int(2.0 * self.beat_sec * self.sr)
                if sn_s < total_samples:
                    l = min(len(snare), total_samples - sn_s)
                    track_L[sn_s:sn_s + l] += snare[:l] * 0.45
                    track_R[sn_s:sn_s + l] += snare[:l] * 0.45
                # 12-step triplet hi-hats
                trip_step = bar_sec / 12.0
                for step in range(12):
                    s = bar_start_sample + int(step * trip_step * self.sr)
                    if s < total_samples:
                        l = min(len(hihat), total_samples - s)
                        track_L[s:s + l] += hihat[:l] * 0.28
                        track_R[s:s + l] += hihat[:l] * 0.28

            elif self.rhythm == "sparse_pulse":
                # Gentle downbeat pulse only
                s = bar_start_sample
                if s < total_samples:
                    l = min(len(kick), total_samples - s)
                    track_L[s:s + l] += kick[:l] * 0.38
                    track_R[s:s + l] += kick[:l] * 0.38
                for step in [4, 8, 12]:
                    s = bar_start_sample + int(step * self.step_sec * self.sr)
                    if s < total_samples:
                        l = min(len(clock_tick), total_samples - s)
                        track_L[s:s + l] += clock_tick[:l] * 0.22
                        track_R[s:s + l] += clock_tick[:l] * 0.22

            elif self.rhythm == "rolling":
                # Continuous driving rolling percussion
                for beat in range(4):
                    s = bar_start_sample + int(beat * self.beat_sec * self.sr)
                    if s < total_samples:
                        l = min(len(kick), total_samples - s)
                        track_L[s:s + l] += kick[:l] * 0.45
                        track_R[s:s + l] += kick[:l] * 0.45
                for step in range(16):
                    s = bar_start_sample + int(step * self.step_sec * self.sr)
                    if s < total_samples:
                        vel = 0.15 + 0.15 * math.sin(step * 0.8)
                        l = min(len(hihat), total_samples - s)
                        track_L[s:s + l] += hihat[:l] * vel
                        track_R[s:s + l] += hihat[:l] * vel

            elif self.rhythm == "evolving":
                # Pacing evolves dynamically across sections
                if prog_ratio < 0.25:
                    # Sparse
                    s = bar_start_sample
                    if s < total_samples:
                        l = min(len(kick), total_samples - s)
                        track_L[s:s + l] += kick[:l] * 0.40
                        track_R[s:s + l] += kick[:l] * 0.40
                elif prog_ratio < 0.70:
                    # Half-time groove
                    s = bar_start_sample
                    if s < total_samples:
                        l = min(len(kick), total_samples - s)
                        track_L[s:s + l] += kick[:l] * 0.48
                        track_R[s:s + l] += kick[:l] * 0.48
                    sn_s = bar_start_sample + int(2.0 * self.beat_sec * self.sr)
                    if sn_s < total_samples:
                        l = min(len(snare), total_samples - sn_s)
                        track_L[sn_s:sn_s + l] += snare[:l] * 0.40
                        track_R[sn_s:sn_s + l] += snare[:l] * 0.40
                else:
                    # Full driving electro
                    for beat in range(4):
                        s = bar_start_sample + int(beat * self.beat_sec * self.sr)
                        if s < total_samples:
                            l = min(len(kick), total_samples - s)
                            track_L[s:s + l] += kick[:l] * 0.50
                            track_R[s:s + l] += kick[:l] * 0.50
                        if beat in [1, 3]:
                            l = min(len(snare), total_samples - s)
                            track_L[s:s + l] += snare[:l] * 0.38
                            track_R[s:s + l] += snare[:l] * 0.38

            else:
                # Standard Driving Electro (four_on_floor)
                for beat in range(4):
                    s = bar_start_sample + int(beat * self.beat_sec * self.sr)
                    if s < total_samples:
                        l = min(len(kick), total_samples - s)
                        track_L[s:s + l] += kick[:l] * 0.45
                        track_R[s:s + l] += kick[:l] * 0.45
                    if beat in [1, 3] and not is_breakdown:
                        if s < total_samples:
                            l = min(len(snare), total_samples - s)
                            track_L[s:s + l] += snare[:l] * 0.35
                            track_R[s:s + l] += snare[:l] * 0.35
                for step in range(16):
                    if step % 2 == 1:
                        s = bar_start_sample + int(step * self.step_sec * self.sr)
                        if s < total_samples:
                            l = min(len(hihat), total_samples - s)
                            track_L[s:s + l] += hihat[:l] * 0.25
                            track_R[s:s + l] += hihat[:l] * 0.25

        # ── 5. AUDIO EVENT SFX INJECTIONS ────────────────────────────────────
        from effects.sound_profiles import generate_semantic_sfx
        for ev in self.audio_events:
            ev_time = float(ev.get("time", 0.0))
            ev_type = ev.get("type", "impact")
            ev_sample = int(ev_time * self.sr)
            if ev_sample < total_samples:
                if ev_type in ("impact", "resolution"):
                    sfx = generate_semantic_sfx("sub_impact", self.sr)
                    l = min(len(sfx), total_samples - ev_sample)
                    track_L[ev_sample:ev_sample + l] += sfx[:l] * 0.45
                    track_R[ev_sample:ev_sample + l] += sfx[:l] * 0.45
                elif ev_type in ("reveal", "build"):
                    sfx = generate_semantic_sfx("tonal_rise", self.sr)
                    l = min(len(sfx), total_samples - ev_sample)
                    track_L[ev_sample:ev_sample + l] += sfx[:l] * 0.35
                    track_R[ev_sample:ev_sample + l] += sfx[:l] * 0.35

        # Normalization
        peak = max(np.max(np.abs(track_L)), np.max(np.abs(track_R)))
        if peak > 0:
            track_L = track_L / peak * 0.55
            track_R = track_R / peak * 0.55

        return np.stack([track_L, track_R], axis=-1)

    def _get_energy_multiplier(self, ratio: float) -> float:
        """Interpolates energy multiplier from the energy curve."""
        if not self.energy_curve:
            return 1.0
        # Find segment in energy curve
        for i in range(len(self.energy_curve) - 1):
            r1 = self.energy_curve[i].get("time_ratio", 0.0)
            r2 = self.energy_curve[i + 1].get("time_ratio", 1.0)
            if r1 <= ratio <= r2:
                e1 = self.energy_curve[i].get("energy", 0.5)
                e2 = self.energy_curve[i + 1].get("energy", 0.5)
                t = (ratio - r1) / max(0.001, (r2 - r1))
                return float(e1 + t * (e2 - e1))
        return float(self.energy_curve[-1].get("energy", 0.5))


# ── 4. Master Audio Mixer with Ducking & Limiting ────────────────────────────

def apply_audio_ducking(
    music: np.ndarray,
    voice_active_mask: np.ndarray,
    sample_rate: int = SAMPLE_RATE,
    duck_gain_db: float = -10.0,
    attack_ms: float = 40.0,
    release_ms: float = 220.0
) -> np.ndarray:
    """
    Applies smooth audio ducking to the music track whenever voiceover is active.
    - Lowers music volume by duck_gain_db (-10 dB).
    - Uses smooth envelope filtering (attack and release) to prevent clicks.
    """
    target_attenuation = 10.0 ** (duck_gain_db / 20.0)  # ~0.316 (-10 dB)
    target_curve = np.where(voice_active_mask, target_attenuation, 1.0).astype(np.float32)

    # Smooth the ducking curve with exponential moving average
    attack_alpha = np.exp(-1.0 / (sample_rate * (attack_ms / 1000.0)))
    release_alpha = np.exp(-1.0 / (sample_rate * (release_ms / 1000.0)))

    smoothed_curve = np.zeros_like(target_curve)
    curr = 1.0
    for i in range(len(target_curve)):
        tgt = target_curve[i]
        if tgt < curr:  # ducking down (attack)
            curr = attack_alpha * curr + (1.0 - attack_alpha) * tgt
        else:           # returning up (release)
            curr = release_alpha * curr + (1.0 - release_alpha) * tgt
        smoothed_curve[i] = curr

    ducked_music = music * smoothed_curve[:, np.newaxis]
    return ducked_music


def build_master_audio(
    scenes: List[SceneVoice],
    total_duration: float = TOTAL_DURATION,
    sfx_events: Optional[List[Dict]] = None,
    output_dir: str = OUTPUT_DIR,
    bpm: float = 124.0,
    style: str = "cyberpunk",
    chord_progression: Optional[List[str]] = None,
    audio_dna: Optional[Dict[str, Any]] = None,
    audio_events: Optional[List[Dict[str, Any]]] = None
) -> Tuple[str, str]:
    """
    Combines voiceover, background music, and SFX into a balanced master mix.
    - Accurately positions speech at scene timestamps.
    - Ducks music by -10 dB during speech.
    - Normalizes master to -1.0 dBFS with soft limiting.
    - Exports to WAV and MP3.
    """
    if audio_dna:
        bpm = float(audio_dna.get("bpm", bpm))
        style = str(audio_dna.get("genre", style))
        chord_progression = audio_dna.get("chord_progression", chord_progression)

    print(f"\n[MIXER] Assembling master synchronized soundtrack (Style: {style}, BPM: {bpm})...")
    total_samples = int(SAMPLE_RATE * total_duration)

    # 1. Voiceover Bus & Activity Mask
    voice_bus = np.zeros((total_samples, 2), dtype=np.float32)
    voice_active_mask = np.zeros(total_samples, dtype=bool)

    for sc in scenes:
        if sc.audio_data is None:
            continue
        start_samp = int(sc.start_time * SAMPLE_RATE)
        clip_len = min(len(sc.audio_data), total_samples - start_samp)
        if start_samp < total_samples and clip_len > 0:
            voice_bus[start_samp:start_samp + clip_len] += sc.audio_data[:clip_len]
            # Voice mask with 80ms padding
            pad_s = int(0.08 * SAMPLE_RATE)
            m_start = max(0, start_samp - pad_s)
            m_end = min(total_samples, start_samp + clip_len + pad_s)
            voice_active_mask[m_start:m_end] = True

    # 2. Procedural Music Track (Dynamically styled & chord-progressed via AudioDNA)
    music_gen = ProceduralMusicGenerator(
        sample_rate=SAMPLE_RATE,
        bpm=bpm,
        style=style,
        chord_progression=chord_progression,
        audio_dna=audio_dna,
        audio_events=audio_events
    )
    raw_music = music_gen.generate_music(total_seconds=total_duration)

    # 3. Audio Ducking
    duck_db = getattr(music_gen.profile, "ducking_db", -10.0)
    print(f"[MIXER] Applying {duck_db:.1f} dB dynamic ducking on '{getattr(music_gen.profile, 'id', style)}' music track...")
    ducked_music = apply_audio_ducking(raw_music, voice_active_mask, duck_gain_db=duck_db)

    # 4. SFX Bus
    sfx_bus = np.zeros((total_samples, 2), dtype=np.float32)
    sfx_gen = SFXGenerator()

    # Pre-generate standard SFX primitives
    whoosh = sfx_gen.create_whoosh(duration=0.65)
    impact = sfx_gen.create_bass_impact(duration=1.8)
    blip_high = sfx_gen.create_ui_blip(freq=2100.0)
    blip_mid = sfx_gen.create_ui_blip(freq=1550.0)
    riser = sfx_gen.create_tension_riser(duration=3.6)

    # Dynamically schedule SFX matching scene transitions if not provided
    if sfx_events is None:
        sfx_events = [
            {"type": "impact", "time": 0.05, "vol": 0.85},
        ]
        for sc in scenes:
            st = sc.start_time
            if st > 1.0:
                sfx_events.append({"type": "whoosh", "time": max(0.0, st - 0.35), "vol": 0.45})
        # Riser before final payoff
        riser_t = max(0.0, total_duration - 7.0)
        sfx_events.append({"type": "riser", "time": riser_t, "vol": 0.65})
        sfx_events.append({"type": "impact", "time": max(0.0, total_duration - 4.5), "vol": 0.90})

    print(f"[MIXER] Scheduling {len(sfx_events)} procedural SFX events...")
    for ev in sfx_events:
        t_sec = ev["time"]
        vol = ev.get("vol", 0.5)
        st = ev["type"]

        if st == "whoosh": snd = whoosh
        elif st == "impact": snd = impact
        elif st == "blip_high": snd = blip_high
        elif st == "blip_mid": snd = blip_mid
        elif st == "riser": snd = riser
        else: continue

        i = int(t_sec * SAMPLE_RATE)
        if i < total_samples:
            l = min(len(snd), total_samples - i)
            sfx_bus[i:i + l] += snd[:l] * vol

    # 5. Master Composite
    # Priority balance: Voice (1.35) + Ducked Music (0.40) + SFX (0.45)
    master = voice_bus * 1.35 + ducked_music * 0.40 + sfx_bus * 0.45

    # 6. Peak Normalization and Soft Limiter to -1.0 dBFS
    target_peak = 10.0 ** (-1.0 / 20.0)  # ~0.891
    max_peak = np.max(np.abs(master))
    print(f"[MIXER] Raw Master Peak: {max_peak:.2f}")

    if max_peak > 0:
        master = np.tanh(master / (max_peak * 0.95)) * target_peak
    else:
        master = master * target_peak

    # 7. Write output 48 kHz 16-bit WAV
    os.makedirs(output_dir, exist_ok=True)
    wav_out = os.path.join(output_dir, "master_audio_48k.wav")
    mp3_out = os.path.join(output_dir, "master_audio.mp3")

    int16_master = np.clip(master * 32767.0, -32767.0, 32767.0).astype(np.int16)
    wavfile.write(wav_out, SAMPLE_RATE, int16_master)
    print(f"[MIXER] ✓ Master WAV saved: {os.path.abspath(wav_out)}")

    # Convert to 320 kbps MP3 via FFmpeg
    cmd_mp3 = [
        "ffmpeg", "-y",
        "-i", wav_out,
        "-b:a", "320k",
        "-ar", str(SAMPLE_RATE),
        "-ac", "2",
        mp3_out
    ]
    subprocess.run(cmd_mp3, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[MIXER] ✓ Master MP3 saved: {os.path.abspath(mp3_out)}")

    return wav_out, mp3_out


def generate_voiceover_and_soundtrack(
    scenes: List[Dict[str, Any]],
    output_dir: str,
    voice: str = "en-US-ChristopherNeural",
    bpm: float = 124.0,
    total_duration: float = 50.0,
    style: str = "cyberpunk",
    chord_progression: Optional[List[str]] = None,
    pitch: str = "+0Hz",
    audio_dna: Optional[Dict[str, Any]] = None,
    audio_events: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Standard studio interface: Generates neural voiceover, procedural music,
    and ducked SFX directly into output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)
    scene_voices = []
    for sc in scenes:
        scene_voices.append(
            SceneVoice(
                id=sc.get("id", "scene"),
                text=sc.get("text", ""),
                start_time=float(sc.get("start_time", 0.0)),
                rate=sc.get("rate", DEFAULT_SPEECH_RATE),
                pitch=sc.get("pitch", pitch)
            )
        )

    # 1. Synthesize voice clips with persona
    processed = generate_voiceover_clips(scene_voices, voice=voice)

    # 2. Master mixing with procedural music & ducked SFX
    wav_path, mp3_path = build_master_audio(
        processed,
        total_duration=total_duration,
        output_dir=output_dir,
        bpm=bpm,
        style=style,
        chord_progression=chord_progression,
        audio_dna=audio_dna,
        audio_events=audio_events
    )

    return {
        "wav_path": wav_path,
        "mp3_path": mp3_path,
        "total_duration": total_duration
    }


# ── 5. Main Execution Example ───────────────────────────────────────────────

def main():
    print("=" * 68)
    print("  SYNCHRONIZED VOICE & PROCEDURAL AUDIO PIPELINE")
    print("  Engine: edge-tts ('en-US-ChristopherNeural') + numpy + scipy")
    print("=" * 68)

    # Structured scene voiceover breakdown for 50-second coding reel
    # Pacing: +20% to +25% for punchy, energetic delivery
    scenes = [
        SceneVoice(
            id="scene_01_hook",
            text="Wait. Do you actually know how your for loop runs?",
            start_time=0.3,
            rate="+24%"
        ),
        SceneVoice(
            id="scene_02_curiosity",
            text="Most beginners misunderstand this. Let's look inside.",
            start_time=4.15,
            rate="+22%"
        ),
        SceneVoice(
            id="scene_03_init",
            text="First, initialization. i equals zero sets up your counter.",
            start_time=8.60,
            rate="+22%"
        ),
        SceneVoice(
            id="scene_04_cond_exec",
            text="Second, condition check. If i is less than 5, the body executes.",
            start_time=13.70,
            rate="+22%"
        ),
        SceneVoice(
            id="scene_05_update",
            text="Third, the update. i increments, and the loop repeats.",
            start_time=19.60,
            rate="+24%"
        ),
        SceneVoice(
            id="scene_06_execution",
            text="Watch it count: 0, 1, 2, 3, 4! At 5, it stops.",
            start_time=24.5,
            rate="+22%"
        ),
        SceneVoice(
            id="scene_07_payoff",
            text="One single line replaces repetitive code. Pure automation.",
            start_time=34.0,
            rate="+20%"
        ),
        SceneVoice(
            id="scene_08_loop",
            text="Next time you write a loop, you'll know what's happening.",
            start_time=42.5,
            rate="+20%"
        ),
    ]

    # Step 1: Synthesize voice lines
    scenes = generate_voiceover_clips(scenes, voice=VOICE_NAME)

    # Step 2 & 3: Procedural Music + SFX + Master Mixing & Export
    wav_path, mp3_path = build_master_audio(scenes, total_duration=TOTAL_DURATION)

    print("\n" + "=" * 68)
    print("  AUDIO PIPELINE COMPLETE!")
    print(f"  Master WAV (48kHz): {wav_path}")
    print(f"  Master MP3:        {mp3_path}")
    print("=" * 68)


if __name__ == "__main__":
    main()
