"""
assets/generate_audio.py
Generates procedural background music and SFX using numpy/scipy.
All assets are synthesized — no external files required.
"""
import os, sys, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import SAMPLE_RATE, TEMP_DIR

SR = SAMPLE_RATE
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(os.path.join(TEMP_DIR, "sfx"), exist_ok=True)


# ─── Waveform helpers ────────────────────────────────────────────────────────

def sine(freq, t_arr, phase=0.0):
    return np.sin(2 * np.pi * freq * t_arr + phase)

def sawtooth(freq, t_arr):
    return 2 * (t_arr * freq - np.floor(t_arr * freq + 0.5))

def square(freq, t_arr, duty=0.5):
    s = sine(freq, t_arr)
    return np.where(s >= 0, 1.0, -1.0) * duty

def env_adsr(n, sr, attack=0.01, decay=0.05, sustain=0.7, release=0.1):
    """ADSR envelope (returns float array 0..1 of length n)."""
    env = np.zeros(n)
    a = min(int(attack  * sr), n)
    d = min(int(decay   * sr), max(0, n - a))
    r = min(int(release * sr), max(0, n - a - d))
    s_len = max(0, n - a - d - r)

    if a > 0: env[:a] = np.linspace(0, 1, a)
    if d > 0: env[a:a+d] = np.linspace(1, sustain, d)
    env[a+d:a+d+s_len] = sustain
    if r > 0: env[a+d+s_len:a+d+s_len+r] = np.linspace(sustain, 0, r)
    return env

def lowpass(audio, cutoff, sr=SR, order=4):
    sos = butter(order, cutoff / (sr / 2), btype='low', output='sos')
    return sosfilt(sos, audio)

def highpass(audio, cutoff, sr=SR, order=4):
    sos = butter(order, cutoff / (sr / 2), btype='high', output='sos')
    return sosfilt(sos, audio)

def reverb_simple(audio, delay_secs=0.04, decay=0.35, n_taps=6):
    """Simple comb-filter reverb."""
    delay_samples = int(delay_secs * SR)
    out = audio.copy().astype(np.float64)
    for tap in range(1, n_taps + 1):
        d = delay_samples * tap
        padded = np.concatenate([np.zeros(d), audio[:len(audio) - d]])
        out += padded * (decay ** tap)
    return out / (1 + n_taps * decay)

def to_int16(audio):
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.88
    return np.clip(audio * 32767, -32767, 32767).astype(np.int16)

def write_wav(path, audio, sr=SR):
    if audio.ndim == 1:
        audio = np.stack([audio, audio], axis=1)  # stereo
    wavfile.write(path, sr, audio.astype(np.int16))


# ─── Background music ────────────────────────────────────────────────────────

def generate_music(duration_secs=55.0, out_path=None):
    """
    Generates a cinematic, minimal ambient/electronic music bed.
    Tempo: ~92 BPM  Key: A minor
    Structure: pad + bass + subtle arp + hi-hat + bass drum
    """
    if out_path is None:
        out_path = os.path.join(TEMP_DIR, "music.wav")

    n = int(duration_secs * SR)
    t = np.linspace(0, duration_secs, n, endpoint=False)

    # ── Chord pad (A minor → C major → G major → E minor) ──────────────────
    bpm = 92.0
    beat = 60.0 / bpm
    bar  = beat * 4

    def chord_pad(freqs, t_arr, amp=0.06, detune=0.004):
        sig = np.zeros(len(t_arr))
        for f in freqs:
            for d in [-detune, 0, detune]:
                sig += sine(f * (1 + d), t_arr)
        sig *= amp
        return sig

    A_MINOR = [110.0, 130.81, 164.81, 220.0]  # A2 C3 E3 A3
    C_MAJOR  = [130.81, 164.81, 196.0, 261.63]  # C3 E3 G3 C4
    G_MAJOR  = [98.0,  123.47, 146.83, 196.0]    # G2 B2 D3 G3
    E_MINOR  = [82.41, 98.0,   123.47, 164.81]   # E2 G2 B2 E3

    chords = [A_MINOR, C_MAJOR, G_MAJOR, E_MINOR]
    n_bars = int(duration_secs / bar) + 1
    pad = np.zeros(n)

    for bi in range(n_bars):
        t_start = bi * bar
        t_end   = t_start + bar
        if t_start >= duration_secs:
            break
        i_start = int(t_start * SR)
        i_end   = min(int(t_end * SR), n)
        chord_t = t[i_start:i_end]
        chord   = chords[bi % len(chords)]
        seg = chord_pad(chord, chord_t - t_start)
        fade_in  = np.clip(np.linspace(0, 1, min(int(0.15*SR), len(seg))), 0, 1)
        fade_out = np.clip(np.linspace(1, 0, min(int(0.15*SR), len(seg))), 0, 1)
        env = np.ones(len(seg))
        env[:len(fade_in)]  *= fade_in
        env[-len(fade_out):] *= fade_out
        seg *= env
        pad[i_start:i_end] += seg

    pad = lowpass(pad, 3000)

    # ── Sub bass ─────────────────────────────────────────────────────────────
    bass_notes = [55.0, 65.41, 49.0, 41.20]  # A1, C2, G1, E1
    bass = np.zeros(n)
    for bi in range(n_bars):
        t_start = bi * bar
        t_end   = t_start + bar * 0.6
        if t_start >= duration_secs:
            break
        i_start = int(t_start * SR)
        i_end   = min(int(t_end * SR), n)
        t_seg = t[i_start:i_end] - t_start
        f = bass_notes[bi % len(bass_notes)]
        seg = sine(f, t_seg) * 0.09
        env = env_adsr(len(seg), SR, attack=0.02, decay=0.3, sustain=0.5, release=0.2)
        bass[i_start:i_end] += seg * env

    bass = lowpass(bass, 120)

    # ── Arpeggiated synth (high, subtle) ────────────────────────────────────
    arp_notes = [440, 523.25, 659.25, 783.99,   # A4 C5 E5 G5
                 523.25, 659.25, 880.0, 659.25]
    arp_speed = beat / 2   # 8th notes
    arp = np.zeros(n)
    n_arp_notes = int(duration_secs / arp_speed) + 1
    for ai in range(n_arp_notes):
        t_start = ai * arp_speed
        t_end   = t_start + arp_speed * 0.55
        if t_start >= duration_secs:
            break
        i_start = int(t_start * SR)
        i_end   = min(int(t_end * SR), n)
        t_seg = t[i_start:i_end] - t_start
        f = arp_notes[ai % len(arp_notes)]
        seg = sine(f, t_seg) * 0.025
        env = env_adsr(len(seg), SR, attack=0.005, decay=0.08, sustain=0.3, release=0.12)
        arp[i_start:i_end] += seg * env

    arp = highpass(arp, 800)

    # ── Bass drum (kick) ─────────────────────────────────────────────────────
    kick_period = beat
    kick = np.zeros(n)
    n_kicks = int(duration_secs / kick_period) + 1
    kick_len = int(0.18 * SR)

    def make_kick():
        t_k = np.linspace(0, 0.18, kick_len)
        freq_env = 200 * np.exp(-t_k * 22)
        sig = sine(freq_env, t_k) * env_adsr(kick_len, SR, 0.003, 0.05, 0.0, 0.13)
        return sig * 0.6

    k_sig = make_kick()
    for ki in range(n_kicks):
        t_start = ki * kick_period
        i_start = int(t_start * SR)
        i_end   = min(i_start + kick_len, n)
        kick[i_start:i_end] += k_sig[:i_end - i_start]

    # ── Hi-hat ───────────────────────────────────────────────────────────────
    hat_period = beat / 2
    hat = np.zeros(n)
    hat_len = int(0.04 * SR)
    n_hats = int(duration_secs / hat_period) + 1
    rng = np.random.default_rng(42)

    def make_hat():
        noise = rng.uniform(-1, 1, hat_len).astype(np.float32)
        env = env_adsr(hat_len, SR, 0.001, 0.015, 0.0, 0.025)
        return highpass(noise * env * 0.09, 7000)

    h_sig = make_hat()
    for hi in range(n_hats):
        t_start = hi * hat_period
        i_start = int(t_start * SR)
        i_end   = min(i_start + hat_len, n)
        hat[i_start:i_end] += h_sig[:i_end - i_start]

    # ── Mix ──────────────────────────────────────────────────────────────────
    mix = pad + bass + arp * 0.6 + kick + hat * 0.7

    # Fade in / out
    fade_in_samples  = int(2.0 * SR)
    fade_out_samples = int(2.5 * SR)
    mix[:fade_in_samples]  *= np.linspace(0, 1, fade_in_samples)
    mix[-fade_out_samples:] *= np.linspace(1, 0, fade_out_samples)

    # Reverb
    mix = reverb_simple(mix, delay_secs=0.035, decay=0.28, n_taps=5)

    # Master limiter / normalize
    mix = to_int16(mix)
    stereo = np.stack([mix, mix], axis=1)

    wavfile.write(out_path, SR, stereo)
    print(f"[MUSIC] Generated: {out_path}  ({duration_secs:.1f}s)")
    return out_path


# ─── Sound Effects ────────────────────────────────────────────────────────────

def generate_sfx():
    sfx_dir = os.path.join(TEMP_DIR, "sfx")

    # 1. Keyboard type click (short metallic tap)
    def make_key_click(seed=0):
        rng = np.random.default_rng(seed)
        n = int(0.06 * SR)
        noise = rng.uniform(-1, 1, n).astype(np.float32)
        env = env_adsr(n, SR, 0.001, 0.008, 0.0, 0.05)
        sig = highpass(noise * env, 2000) * 0.4
        tone = sine(1800 + rng.integers(-200, 200), np.linspace(0, 0.06, n))
        sig += tone * env * 0.15
        return to_int16(sig)

    clicks = [make_key_click(i) for i in range(6)]
    for i, c in enumerate(clicks):
        write_wav(os.path.join(sfx_dir, f"key_{i}.wav"), c)

    # 2. Whoosh (scene transition)
    def make_whoosh(direction=1):
        n = int(0.35 * SR)
        t_arr = np.linspace(0, 0.35, n)
        noise = np.random.default_rng(7).normal(0, 1, n).astype(np.float32)
        # Pitch sweep
        freq_sweep = np.exp(np.linspace(np.log(200), np.log(3000), n) * direction)
        carrier = np.sin(np.cumsum(freq_sweep / SR * 2 * np.pi))
        sig = noise * 0.3 + carrier * 0.1
        env = np.exp(-t_arr * 8) * np.linspace(0, 1, n) ** 0.5
        sig *= env * 0.7
        sig = lowpass(sig, 5000)
        return to_int16(sig)

    write_wav(os.path.join(sfx_dir, "whoosh_up.wav"), make_whoosh(1))
    write_wav(os.path.join(sfx_dir, "whoosh_down.wav"), make_whoosh(-1))

    # 3. Impact hit (bass impact for text reveals)
    def make_impact():
        n = int(0.5 * SR)
        t_arr = np.linspace(0, 0.5, n)
        sub = sine(60, t_arr) * np.exp(-t_arr * 9) * 0.8
        click = np.random.default_rng(3).normal(0, 1, int(0.01*SR)).astype(np.float32) * 0.4
        sig = np.concatenate([click, sub[int(0.01*SR):]])[:n]
        env = env_adsr(n, SR, 0.001, 0.08, 0.2, 0.4)
        return to_int16(sig * env)

    write_wav(os.path.join(sfx_dir, "impact.wav"), make_impact())

    # 4. Riser (builds tension before payoff)
    def make_riser(dur=4.0):
        n = int(dur * SR)
        t_arr = np.linspace(0, dur, n)
        freq = np.exp(np.linspace(np.log(80), np.log(800), n))
        sig = np.sin(np.cumsum(freq / SR * 2 * np.pi))
        noise = np.random.default_rng(9).normal(0, 0.08, n).astype(np.float32)
        sig = sig * 0.25 + noise
        env = np.linspace(0, 1, n) ** 1.5
        sig *= env * 0.5
        return to_int16(lowpass(sig, 4000))

    write_wav(os.path.join(sfx_dir, "riser.wav"), make_riser(4.0))

    # 5. Digital blip (UI select sound)
    def make_blip(freq=880, dur=0.12):
        n = int(dur * SR)
        t_arr = np.linspace(0, dur, n)
        sig = sine(freq, t_arr) * 0.35
        env = env_adsr(n, SR, 0.003, 0.04, 0.0, 0.08)
        return to_int16(sig * env)

    write_wav(os.path.join(sfx_dir, "blip.wav"), make_blip(1046))
    write_wav(os.path.join(sfx_dir, "blip_low.wav"), make_blip(523, 0.10))

    print(f"[SFX] Generated all SFX → {sfx_dir}")


if __name__ == "__main__":
    generate_music()
    generate_sfx()
