"""
config.py - Central configuration for the Coding Reel generator.
"""

# ─────────────────────────────────────────────
#  TOPIC  (change this to any coding concept)
# ─────────────────────────────────────────────
TOPIC = "How a for loop actually works"

# ─── Canvas ──────────────────────────────────
WIDTH  = 1080
HEIGHT = 1920
FPS    = 30
DURATION = 50          # seconds
TOTAL_FRAMES = FPS * DURATION

# ─── Colour palette ──────────────────────────
BG_COLOR       = (10,  11,  16)   # near-black
PANEL_COLOR    = (18,  20,  28)   # editor bg
ACCENT         = (99,  179, 237)  # cool cyan-blue
ACCENT2        = (159, 122, 234)  # purple
ACCENT3        = (246, 173,  85)  # warm amber
WHITE          = (255, 255, 255)
GRAY           = (120, 130, 150)
HIGHLIGHT      = (62, 207, 142)   # green success
RED_ERR        = (252,  90,  90)
KEYWORD_COLOR  = (129, 162, 190)
STRING_COLOR   = (152, 195, 121)
NUMBER_COLOR   = (209, 154, 102)
COMMENT_COLOR  = (90,  100, 115)
FUNC_COLOR     = (97,  175, 239)
TYPE_COLOR     = (224, 108,  117)

# ─── Typography ──────────────────────────────
MONO_FONT    = "assets/fonts/JetBrainsMono-Regular.ttf"
BOLD_FONT    = "assets/fonts/Inter-Bold.ttf"
REGULAR_FONT = "assets/fonts/Inter-Regular.ttf"
CURSIVE_FONT = "assets/fonts/Caveat-Bold.ttf"
FLAT_FONT    = "assets/fonts/Inter-Regular.ttf"

# ─── Timeline (seconds) ──────────────────────
T_HOOK_START       = 0.0
T_HOOK_END         = 3.0
T_CURIOSITY_START  = 3.0
T_CURIOSITY_END    = 8.0
T_STEP1_START      = 8.0
T_STEP1_END        = 18.0
T_STEP2_START      = 18.0
T_STEP2_END        = 28.0
T_STEP3_START      = 28.0
T_STEP3_END        = 36.0
T_PAYOFF_START     = 36.0
T_PAYOFF_END       = 44.0
T_LOOP_START       = 44.0
T_LOOP_END         = 50.0

# ─── Paths ────────────────────────────────────
TEMP_DIR   = "temp"
OUTPUT_DIR = "output"
FINAL_MP4  = "output/FINAL_REEL.mp4"
VOICE_WAV  = "temp/voiceover.wav"
MUSIC_WAV  = "temp/music.wav"
SFX_DIR    = "temp/sfx"

# ─── Audio ────────────────────────────────────
SAMPLE_RATE    = 48000
MUSIC_VOLUME   = 0.18
MUSIC_DUCK     = 0.07
SFX_VOLUME     = 0.5

# ─── Script (~100 spoken words, fits ~50s of TTS) ─────────────────────────────
NARRATION_SCRIPT = (
    "Wait. Do you know what really happens when your for loop runs? "
    "Most beginners think it just repeats code. But there is a clear cycle inside. "
    "Here is the code. "
    "for int i equals zero. i less than five. i plus plus. "
    "Step one. i is set to zero. The initializer. Runs once. "
    "Step two. The condition is checked. Is i less than five? Yes. So the code runs. "
    "Then i plus plus. Now i is one. Back to the condition. Still less than five. Run again. "
    "Zero. One. Two. Three. Four. "
    "When i reaches five the condition fails. The loop stops. "
    "One line. Five controlled repetitions. "
    "That is the power of a for loop. "
    "Now every time you see one, you will know exactly what is happening inside."
)
