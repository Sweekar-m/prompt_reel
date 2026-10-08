"""
effects/closing_strategies.py
=============================
Closing Strategy & Resolution Engine.
Replaces the repetitive "Payoff -> CTA -> circular gauge" pattern with 12 distinct,
narrative-driven closing architectures.

The 12 Closing Strategies:
1. CALLBACK: Returns to the opening question or visual anchor.
2. TRANSFORMATION: The main visual object transforms into the final takeaway message.
3. COMPRESSION: The entire complex concept collapses into a single dense principle.
4. KINETIC_STATEMENT: Massive, authoritative typography delivers the final truth.
5. QUESTION: Ends with a thought-provoking unresolved edge-case or architectural question.
6. VISUAL_RESOLUTION: Multiple fragmented elements converge into a unified whole.
7. LOOP: The ending scene seamlessly loops back into the opening frame.
8. MINIMAL: All visual clutter dissolves into darkness, leaving one stark centered sentence.
9. CTA: Actionable, developer-focused directive ("Build this", "Profile your memory").
10. CONCEPT_REVEAL: Final architectural diagram snapshot highlighting the golden rule.
11. BEFORE_AFTER: Splits or contrasts the naive slow code against the optimized machine.
12. METAPHORICAL_ENDING: Returns to the physical visual metaphor established earlier.
"""
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class ClosingDNA:
    strategy_id: str             # e.g. "callback", "transformation", "kinetic_statement"
    strategy_name: str
    description: str
    layout: str                  # "kinetic_words", "centered_minimal", "split_before_after", "callback_anchor", "compression_singularity", "question_card", "metaphor_resolution", "hero_stat_badge"
    camera_motion: str           # "punch_z_forward", "orbit_tilt", "slow_pull_back", "whip_freeze", "still_dramatic"
    typography_style: str        # "massive_stacked", "clean_minimal", "terminal_prompt", "kinetic_split", "badge_hero"
    visual_accent: str           # "radiating_portal", "particle_collapse", "clean_glow", "singularity_dot", "geometric_lock", "split_divider"
    headline: str                # Primary punchy takeaway
    secondary_text: str          # Contextual insight
    stat_callout: Optional[str]  # e.g. "O(1) MEMORY", "0.35ns", "ZERO LEAKS"
    callback_ref: Optional[str]  # Opening element or phrase being referenced
    action_label: Optional[str]  # For CTA / Directive
    variation_seed: int = 42

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


CLOSING_STRATEGY_DEFS: Dict[str, Dict[str, Any]] = {
    "callback": {
        "name": "Narrative Callback",
        "description": "Returns to the opening hook question to close the narrative loop with certainty.",
        "layout": "callback_anchor",
        "camera_motion": "slow_pull_back",
        "typography_style": "badge_hero",
        "visual_accent": "geometric_lock"
    },
    "transformation": {
        "name": "Object Transformation",
        "description": "The central focal element physically morphs and expands into the final conclusion.",
        "layout": "metaphor_resolution",
        "camera_motion": "orbit_tilt",
        "typography_style": "massive_stacked",
        "visual_accent": "radiating_portal"
    },
    "compression": {
        "name": "Conceptual Compression",
        "description": "Collapses the entire computational mechanism into one ultra-compact takeaway.",
        "layout": "compression_singularity",
        "camera_motion": "punch_z_forward",
        "typography_style": "clean_minimal",
        "visual_accent": "particle_collapse"
    },
    "kinetic_statement": {
        "name": "Kinetic Statement",
        "description": "High-velocity, multi-tier typography delivering an undeniable engineering fact.",
        "layout": "kinetic_words",
        "camera_motion": "whip_freeze",
        "typography_style": "massive_stacked",
        "visual_accent": "clean_glow"
    },
    "question": {
        "name": "Open Engineering Question",
        "description": "Concludes on an intriguing edge-case question that sparks intense debate in comments.",
        "layout": "question_card",
        "camera_motion": "still_dramatic",
        "typography_style": "clean_minimal",
        "visual_accent": "clean_glow"
    },
    "visual_resolution": {
        "name": "Convergence Resolution",
        "description": "All preceding visual layers merge into a unified balanced geometric emblem.",
        "layout": "hero_stat_badge",
        "camera_motion": "orbit_tilt",
        "typography_style": "badge_hero",
        "visual_accent": "radiating_portal"
    },
    "loop": {
        "name": "Infinite Seamless Loop",
        "description": "The final frame aligns perfectly with frame 0, encouraging repeat views on Reels/TikTok.",
        "layout": "callback_anchor",
        "camera_motion": "punch_z_forward",
        "typography_style": "massive_stacked",
        "visual_accent": "singularity_dot"
    },
    "minimal": {
        "name": "Stark Minimal Truth",
        "description": "All decorative assets dissolve into deep black, isolating a single glowing sentence.",
        "layout": "centered_minimal",
        "camera_motion": "still_dramatic",
        "typography_style": "clean_minimal",
        "visual_accent": "clean_glow"
    },
    "cta": {
        "name": "Actionable Engineering Directive",
        "description": "Gives the viewer a concrete challenge or diagnostic command to execute in terminal.",
        "layout": "centered_minimal",
        "camera_motion": "slow_pull_back",
        "typography_style": "terminal_prompt",
        "visual_accent": "geometric_lock"
    },
    "concept_reveal": {
        "name": "Definitive Architectural Law",
        "description": "Displays the formal invariant or algorithmic law governing the concept.",
        "layout": "hero_stat_badge",
        "camera_motion": "slow_pull_back",
        "typography_style": "badge_hero",
        "visual_accent": "radiating_portal"
    },
    "before_after": {
        "name": "Before vs After Contrast",
        "description": "Direct side-by-side or split contrast comparing naive execution to the optimized reality.",
        "layout": "split_before_after",
        "camera_motion": "whip_freeze",
        "typography_style": "kinetic_split",
        "visual_accent": "split_divider"
    },
    "metaphorical_ending": {
        "name": "Metaphor Closure",
        "description": "The established physical metaphor (stack, balance tree, pipeline) completes its full cycle.",
        "layout": "metaphor_resolution",
        "camera_motion": "orbit_tilt",
        "typography_style": "badge_hero",
        "visual_accent": "radiating_portal"
    }
}


def select_closing_strategy(
    topic: str,
    hook_data: Dict[str, Any],
    style_id: str = "editorial",
    story_structure_id: str = "structure_a",
    seed_salt: str = ""
) -> ClosingDNA:
    """
    Selects the optimal Closing Strategy from 12 candidates based on narrative context.
    Evaluates candidate compatibility and prevents repetitive closer tropes.
    """
    raw_hash = f"{topic}_{style_id}_{story_structure_id}_{seed_salt}".encode("utf-8")
    seed = int(hashlib.sha256(raw_hash).hexdigest()[:8], 16)

    t_low = topic.lower()
    hook_headline = hook_data.get("headline", topic.upper())

    # Build ranked compatible candidate strategies
    candidate_keys = []
    if "structure_a" in story_structure_id:  # Mystery & Reveal
        candidate_keys = ["callback", "concept_reveal", "compression", "kinetic_statement"]
    elif "structure_b" in story_structure_id: # Reverse Engineering
        candidate_keys = ["before_after", "compression", "transformation", "minimal"]
    elif "structure_c" in story_structure_id: # Bug & Fix
        candidate_keys = ["before_after", "kinetic_statement", "cta", "callback"]
    elif "structure_d" in story_structure_id: # Empirical Lab
        candidate_keys = ["concept_reveal", "before_after", "question", "minimal"]
    elif "structure_e" in story_structure_id: # Metaphor First
        candidate_keys = ["metaphorical_ending", "transformation", "callback", "visual_resolution"]
    elif "structure_f" in story_structure_id: # Mythbuster
        candidate_keys = ["before_after", "kinetic_statement", "callback", "compression"]
    elif "structure_g" in story_structure_id: # Speedrun
        candidate_keys = ["kinetic_statement", "compression", "minimal", "cta"]
    else:
        candidate_keys = ["callback", "visual_resolution", "transformation", "loop"]

    # Style influences
    if style_id in ("terminal", "brutalist"):
        candidate_keys = [k for k in ["kinetic_statement", "before_after", "cta", "minimal"] if k in candidate_keys] or ["kinetic_statement"]
    elif style_id in ("glass_ui", "minimal"):
        candidate_keys = [k for k in ["minimal", "compression", "concept_reveal"] if k in candidate_keys] or ["minimal"]
    elif style_id in ("neo_futuristic", "cyberpunk"):
        candidate_keys = [k for k in ["transformation", "kinetic_statement", "loop", "visual_resolution"] if k in candidate_keys] or ["transformation"]

    selected_key = candidate_keys[seed % len(candidate_keys)]
    strat = CLOSING_STRATEGY_DEFS.get(selected_key, CLOSING_STRATEGY_DEFS["kinetic_statement"])

    # Formulate tailored content based on strategy
    headline, secondary, stat, callback_ref, action = _formulate_closer_copy(
        selected_key, topic, hook_headline, seed
    )

    return ClosingDNA(
        strategy_id=selected_key,
        strategy_name=strat["name"],
        description=strat["description"],
        layout=strat["layout"],
        camera_motion=strat["camera_motion"],
        typography_style=strat["typography_style"],
        visual_accent=strat["visual_accent"],
        headline=headline,
        secondary_text=secondary,
        stat_callout=stat,
        callback_ref=callback_ref,
        action_label=action,
        variation_seed=seed
    )


def _formulate_closer_copy(
    strategy: str,
    topic: str,
    hook_headline: str,
    seed: int
) -> Tuple[str, str, Optional[str], Optional[str], Optional[str]]:
    """Synthesizes narrative-specific headline, subtext, and callout for the closer."""
    t_clean = topic.strip().title()

    if strategy == "callback":
        if t_clean.lower() in hook_headline.lower():
            headline = f"AND THAT ANSWERS: {hook_headline}"
        else:
            headline = f"AND THAT ANSWERS: {t_clean.upper()}"
        secondary = f"Now you understand the exact physical mechanism powering {t_clean}."
        stat = "VERIFIED IN HARDWARE"
        callback_ref = hook_headline
        action = None

    elif strategy == "transformation":
        headline = f"{t_clean.upper()} IN FULL PERSPECTIVE"
        secondary = "What seemed abstract is completely deterministic when traced in memory."
        stat = "DETERMINISTIC"
        callback_ref = None
        action = None

    elif strategy == "compression":
        headline = f"THE ONE RULE OF {t_clean.upper()}"
        secondary = "Every layer of abstraction obeys the exact same computational bounds."
        stat = "O(1) MENTAL MODEL"
        callback_ref = None
        action = None

    elif strategy == "kinetic_statement":
        headline = f"MASTER {t_clean.upper()}."
        secondary = "Senior engineers don't guess execution order — they know it."
        stat = "10X INSIGHT"
        callback_ref = None
        action = None

    elif strategy == "question":
        headline = f"COULD YOUR CODE BREAK {t_clean.upper()}?"
        secondary = "What happens when concurrency scales past 100,000 workers? Think about it."
        stat = "EDGE CASE"
        callback_ref = None
        action = "Comment your answer"

    elif strategy == "before_after":
        headline = f"NAIVE VS PRODUCTION {t_clean.upper()}"
        secondary = "The difference between unpredictable latency and bounded guarantees."
        stat = "100x SPEEDUP"
        callback_ref = None
        action = None

    elif strategy == "minimal":
        headline = f"{t_clean} is just bounded memory."
        secondary = "Simple primitives stacked together create massive architectures."
        stat = None
        callback_ref = None
        action = None

    elif strategy == "cta":
        headline = f"PROFILE YOUR {t_clean.upper()} TODAY"
        secondary = "Inspect your runtime allocations before pushing to production."
        stat = "CLI COMMAND"
        callback_ref = None
        action = "Run benchmark"

    elif strategy == "loop":
        headline = f"IT ALL STARTS AGAIN WITH {hook_headline}"
        secondary = "Re-watch the initial execution check to see the pattern in reverse."
        stat = "SEAMLESS LOOP"
        callback_ref = hook_headline
        action = None

    elif strategy == "metaphorical_ending":
        headline = f"THE MACHINE RESOLVES {t_clean.upper()}"
        secondary = "Every pointer, frame, and boundary locked in perfect alignment."
        stat = "BALANCED STATE"
        callback_ref = None
        action = None

    else: # concept_reveal / visual_resolution
        headline = f"THE FOUNDATIONAL LAW OF {t_clean.upper()}"
        secondary = "Zero magic. Just deterministic instructions executing on silicon."
        stat = "CORE INVARIANT"
        callback_ref = None
        action = None

    return (headline, secondary, stat, callback_ref, action)
