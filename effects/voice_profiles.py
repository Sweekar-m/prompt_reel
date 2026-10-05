"""
effects/voice_profiles.py
=========================
Voice Personality and TTS Profiling Engine.
Supports 8 diverse voice personas across gender, region, and energy profiles.
"""
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class VoiceProfile:
    id: str
    name: str
    edge_voice: str
    rate: str           # e.g. "+18%", "+24%", "+5%"
    pitch: str          # e.g. "-2Hz", "+0Hz", "+3Hz"
    energy: str         # "high", "medium", "intense", "relaxed"
    ideal_style: str    # "cyberpunk", "editorial", "cinematic", "terminal", etc.
    sentence_pacing: str # "rapid_punchy", "measured_authoritative", "deep_intense"
    description: str


VOICE_PROFILES: Dict[str, VoiceProfile] = {
    # 1. Energetic Explainer
    "energetic": VoiceProfile(
        id="energetic",
        name="Energetic Tech Explainer",
        edge_voice="en-US-ChristopherNeural",
        rate="+22%",
        pitch="+1Hz",
        energy="high",
        ideal_style="cyberpunk",
        sentence_pacing="rapid_punchy",
        description="Punchy, vibrant, high-tempo modern social media delivery."
    ),

    # 2. Calm Architectural
    "calm": VoiceProfile(
        id="calm",
        name="Calm Senior Architect",
        edge_voice="en-US-GuyNeural",
        rate="+8%",
        pitch="-1Hz",
        energy="relaxed",
        ideal_style="minimal",
        sentence_pacing="measured_authoritative",
        description="Relaxed, assured, crystal-clear explanation with subtle gravitas."
    ),

    # 3. British Documentary
    "documentary": VoiceProfile(
        id="documentary",
        name="British Tech Documentary",
        edge_voice="en-GB-RyanNeural",
        rate="+12%",
        pitch="+0Hz",
        energy="medium",
        ideal_style="editorial",
        sentence_pacing="measured_authoritative",
        description="Refined British RP cadence, perfect for deep engineering histories."
    ),

    # 4. Deep Cinematic
    "deep_cinematic": VoiceProfile(
        id="deep_cinematic",
        name="Deep Theatrical Voiceover",
        edge_voice="en-US-EricNeural",
        rate="+5%",
        pitch="-3Hz",
        energy="intense",
        ideal_style="cinematic",
        sentence_pacing="deep_intense",
        description="Resonant, deep cinematic narration suited for dramatic revelations."
    ),

    # 5. Young Technical
    "young_technical": VoiceProfile(
        id="young_technical",
        name="Modern Silicon Valley Dev",
        edge_voice="en-US-JennyNeural",
        rate="+20%",
        pitch="+2Hz",
        energy="high",
        ideal_style="neo_futuristic",
        sentence_pacing="rapid_punchy",
        description="Crisp, intelligent, engaging Silicon Valley engineer tone."
    ),

    # 6. Fast Explainer Speedrun
    "fast_explainer": VoiceProfile(
        id="fast_explainer",
        name="60-Second Code Speedrunner",
        edge_voice="en-US-ChristopherNeural",
        rate="+28%",
        pitch="+2Hz",
        energy="high",
        ideal_style="brutalist",
        sentence_pacing="rapid_punchy",
        description="High-velocity, information-dense speedrun delivery."
    ),

    # 7. Conversational Mentor
    "conversational": VoiceProfile(
        id="conversational",
        name="Conversational Pair Programmer",
        edge_voice="en-US-AriaNeural",
        rate="+14%",
        pitch="+0Hz",
        energy="medium",
        ideal_style="swiss_grid",
        sentence_pacing="measured_authoritative",
        description="Approachable, articulate mentor walking you through the problem."
    ),

    # 8. Dramatic Mystery
    "dramatic": VoiceProfile(
        id="dramatic",
        name="Theatrical Hacker Noir",
        edge_voice="en-AU-WilliamNeural",
        rate="+10%",
        pitch="-2Hz",
        energy="intense",
        ideal_style="terminal",
        sentence_pacing="deep_intense",
        description="Subtle intensity with dramatic pauses between technical deductions."
    )
}


def get_voice_profile(voice_id: str) -> VoiceProfile:
    return VOICE_PROFILES.get(voice_id, VOICE_PROFILES["energetic"])


def list_voice_profiles() -> List[Dict[str, Any]]:
    return [
        {
            "id": v.id,
            "name": v.name,
            "voice": v.edge_voice,
            "rate": v.rate,
            "pitch": v.pitch,
            "energy": v.energy,
            "description": v.description
        }
        for v in VOICE_PROFILES.values()
    ]
