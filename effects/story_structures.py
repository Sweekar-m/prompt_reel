"""
effects/story_structures.py
===========================
Narrative Story Structure Engine & Intelligent Story Director.
Provides 12 distinct structural blueprints with semantic topic analysis:
- STRUCTURE_A: Mystery & Reveal
- STRUCTURE_B: Reverse Engineering (Result -> Breakdown -> Logic -> Synthesis)
- STRUCTURE_C: The Bug & The Fix (Crisis -> Collapse -> Debug -> Invariant)
- STRUCTURE_D: The Empirical Lab (Hypothesis -> Benchmark -> Divergence -> Law)
- STRUCTURE_E: Metaphor to Metal (Physical Mental Model -> RAM/CPU -> Proof)
- STRUCTURE_F: Mythbuster (Common Tutorial Myth -> Hard Contradiction -> Hardware Reality)
- STRUCTURE_G: Speedrun Masterclass (Cold Open -> 3 Takeaways -> Deep Dive)
- STRUCTURE_H: Engineering Crisis & Breakthrough (Scale Bottleneck -> Breakthrough -> Resolution)
- STRUCTURE_I: System Architecture Walkthrough (Topology -> Ingestion -> Cluster -> Reliability)
- STRUCTURE_J: Comparative Showdown (Method A vs Method B -> Live Benchmark -> Verdict)
- STRUCTURE_K: Mathematical 3D Dimension Shift (2D Equation -> 3D Surface -> Geometric Invariant)
- STRUCTURE_L: Evolution & Timeline (Legacy Pain -> Paradigm Shift -> Modern Invariant)
"""
import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class StoryBeat:
    name: str
    duration_ratio: float  # Fraction of total duration (sums to 1.0)
    intent: str
    visual_type: str       # "hook", "metaphor", "code", "benchmark", "diagram", "split", "payoff", "math_3d"


@dataclass
class StoryStructure:
    id: str
    name: str
    description: str
    beats: List[StoryBeat]
    suitable_intents: List[str] = field(default_factory=list)
    suitable_topic_types: List[str] = field(default_factory=list)
    preferred_scene_types: List[str] = field(default_factory=list)
    pacing_profile: str = "measured"              # "rapid", "measured", "accelerating", "deliberate"
    emotional_profile: str = "analytical"         # "curious", "urgent", "mind_bending", "pragmatic", "authoritative"
    compatible_visual_strategies: List[str] = field(default_factory=list)

    def compute_timeline(self, total_duration: float = 50.0) -> List[Dict[str, Any]]:
        """Calculate start and end seconds for each beat."""
        timeline = []
        current_time = 0.0
        for b in self.beats:
            dur = round(total_duration * b.duration_ratio, 2)
            end_t = min(round(current_time + dur, 2), total_duration)
            timeline.append({
                "beat": b.name,
                "start": current_time,
                "end": end_t,
                "duration": round(end_t - current_time, 2),
                "intent": b.intent,
                "visual_type": b.visual_type
            })
            current_time = end_t
        return timeline

    def to_story_structure_dict(self, total_duration: float = 50.0) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "timeline": self.compute_timeline(total_duration),
            "total_duration": total_duration
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "beats": [asdict(b) for b in self.beats],
            "suitable_intents": self.suitable_intents,
            "suitable_topic_types": self.suitable_topic_types,
            "preferred_scene_types": self.preferred_scene_types,
            "pacing_profile": self.pacing_profile,
            "emotional_profile": self.emotional_profile,
            "compatible_visual_strategies": self.compatible_visual_strategies,
        }


STORY_STRUCTURES: Dict[str, StoryStructure] = {
    # STRUCTURE_A: Mystery & Reveal
    "structure_a": StoryStructure(
        id="structure_a",
        name="Mystery & Reveal",
        description="Creates an intriguing puzzle before delivering an aha-moment breakdown.",
        suitable_intents=["explain_mechanism", "explore_curiosity", "deep_dive"],
        suitable_topic_types=["language_runtime_internals", "operating_systems_lowlevel", "algorithms_data_structures"],
        preferred_scene_types=["hook", "code", "metaphor", "diagram", "payoff"],
        pacing_profile="measured",
        emotional_profile="curious",
        compatible_visual_strategies=["editorial_grid", "cinematic_diagram", "magazine_editorial", "swiss_minimal"],
        beats=[
            StoryBeat("Hook", 0.08, "Provoke curiosity with an unexpected question", "hook"),
            StoryBeat("Mystery", 0.16, "Present the puzzling behavior or counter-intuitive code", "code"),
            StoryBeat("Reveal", 0.22, "Show the underlying mechanism in action", "metaphor"),
            StoryBeat("Explanation", 0.34, "Step-by-step breakdown of how it works", "diagram"),
            StoryBeat("Payoff", 0.20, "Before/after benchmark and definitive principle", "payoff")
        ]
    ),

    # STRUCTURE_B: Reverse Engineering
    "structure_b": StoryStructure(
        id="structure_b",
        name="Reverse Engineering",
        description="Starts with the astounding end result, then tears apart the engine piece by piece.",
        suitable_intents=["reverse_engineer", "benchmark_showcase", "explain_mechanism"],
        suitable_topic_types=["algorithms_data_structures", "ai_machine_learning", "database_storage"],
        preferred_scene_types=["benchmark", "diagram", "code", "payoff"],
        pacing_profile="accelerating",
        emotional_profile="analytical",
        compatible_visual_strategies=["technical_blueprint", "data_visualization", "terminal_story"],
        beats=[
            StoryBeat("Result", 0.12, "Show impossible benchmark: 1 billion items found in 20 steps", "benchmark"),
            StoryBeat("Disassembly", 0.26, "Strip away the surface to expose the core math", "diagram"),
            StoryBeat("Explanation", 0.34, "Trace the binary division logic line by line", "code"),
            StoryBeat("Synthesis", 0.28, "Reassemble the pattern into a reusable mental model", "payoff")
        ]
    ),

    # STRUCTURE_C: Problem -> Failure -> Debugging -> Solution
    "structure_c": StoryStructure(
        id="structure_c",
        name="The Bug & The Fix",
        description="A relatable engineering crisis: stack overflow or memory leak, followed by the surgical fix.",
        suitable_intents=["solve_crisis", "debug_failure", "prevent_disaster"],
        suitable_topic_types=["operating_systems_lowlevel", "language_runtime_internals", "database_storage"],
        preferred_scene_types=["hook", "metaphor", "code", "split", "payoff"],
        pacing_profile="rapid",
        emotional_profile="urgent",
        compatible_visual_strategies=["terminal_story", "brutalist", "code_first", "cyberpunk"],
        beats=[
            StoryBeat("Problem", 0.10, "Production failure or fatal crash warning", "hook"),
            StoryBeat("Failure", 0.22, "Visualizing exactly why memory or CPU collapsed", "metaphor"),
            StoryBeat("Debugging", 0.32, "Pinpointing the offending instruction", "code"),
            StoryBeat("Comparison", 0.18, "Broken versus fixed execution side-by-side", "split"),
            StoryBeat("Solution", 0.18, "Applying the correct pattern with zero crash guarantee", "payoff")
        ]
    ),

    # STRUCTURE_D: Question -> Experiment -> Observation -> Law
    "structure_d": StoryStructure(
        id="structure_d",
        name="The Empirical Lab",
        description="Scientific testing approach: hypothesis, benchmark experiment, and empirical proof.",
        suitable_intents=["empirical_lab", "benchmark_showcase", "test_hypothesis"],
        suitable_topic_types=["algorithms_data_structures", "database_storage", "ai_machine_learning"],
        preferred_scene_types=["hook", "benchmark", "diagram", "code", "payoff"],
        pacing_profile="measured",
        emotional_profile="authoritative",
        compatible_visual_strategies=["data_visualization", "technical_blueprint", "swiss_minimal"],
        beats=[
            StoryBeat("Hypothesis", 0.10, "Can we run this in O(1) space instead of O(N)?", "hook"),
            StoryBeat("Experiment", 0.26, "Run both algorithms against 10 million test cases", "benchmark"),
            StoryBeat("Dissection", 0.30, "Trace the underlying data flow divergence", "diagram"),
            StoryBeat("Verification", 0.18, "Compiler instruction level verification", "code"),
            StoryBeat("Law", 0.16, "State the formal computational law governing the result", "payoff")
        ]
    ),

    # STRUCTURE_E: Metaphor-First Mental Model
    "structure_e": StoryStructure(
        id="structure_e",
        name="Metaphor-First Mental Model",
        description="Grounds the concept immediately in physical objects before showing technical execution.",
        suitable_intents=["explain_mechanism", "intuitive_grounding", "mental_model"],
        suitable_topic_types=["networking_distributed", "system_architecture", "web_frontend", "philosophical_conceptual"],
        preferred_scene_types=["metaphor", "diagram", "code", "payoff"],
        pacing_profile="deliberate",
        emotional_profile="mind_bending",
        compatible_visual_strategies=["abstract_motion", "cinematic_diagram", "editorial_grid", "system_architecture"],
        beats=[
            StoryBeat("Metaphor_Hook", 0.14, "Show physical blocks stacking or restaurant kitchen", "metaphor"),
            StoryBeat("Mapping", 0.30, "Map physical objects directly to RAM and CPU registers", "diagram"),
            StoryBeat("Code_Proof", 0.32, "Show how 3 lines of code implement the exact physical machine", "code"),
            StoryBeat("Mastery", 0.24, "Lock in the visual intuition forever", "payoff")
        ]
    ),

    # STRUCTURE_F: Mythbuster
    "structure_f": StoryStructure(
        id="structure_f",
        name="Mythbuster",
        description="Destroys a common textbook myth and replaces it with real engineering truth.",
        suitable_intents=["debunk_myth", "correct_misconception", "senior_insight"],
        suitable_topic_types=["language_runtime_internals", "web_frontend", "operating_systems_lowlevel"],
        preferred_scene_types=["hook", "split", "diagram", "payoff"],
        pacing_profile="rapid",
        emotional_profile="authoritative",
        compatible_visual_strategies=["kinetic_typography", "editorial_grid", "brutalist"],
        beats=[
            StoryBeat("The_Myth", 0.12, "What 90% of beginners and tutorials teach", "hook"),
            StoryBeat("Contradiction", 0.24, "Prove where conventional wisdom fails completely", "split"),
            StoryBeat("Hardware_Proof", 0.38, "Demonstrate the real hardware or compiler behavior", "diagram"),
            StoryBeat("New_Standard", 0.26, "The true mental model used by senior engineers", "payoff")
        ]
    ),

    # STRUCTURE_G: Speedrun Masterclass
    "structure_g": StoryStructure(
        id="structure_g",
        name="Speedrun Masterclass",
        description="Fast-paced, high-density technical briefing with zero fluff.",
        suitable_intents=["rapid_takeaway", "deep_dive", "cheat_sheet"],
        suitable_topic_types=["devops_cloud_infra", "security_cryptography", "language_runtime_internals"],
        preferred_scene_types=["hook", "diagram", "code", "payoff"],
        pacing_profile="rapid",
        emotional_profile="pragmatic",
        compatible_visual_strategies=["terminal_story", "retro_computing", "code_first"],
        beats=[
            StoryBeat("Cold_Open", 0.08, "Immediate core statement on frame 1", "hook"),
            StoryBeat("Rapid_Breakdown", 0.26, "3 instant architectural takeaways", "diagram"),
            StoryBeat("Deep_Dive", 0.42, "Detailed dissection of the critical invariant", "code"),
            StoryBeat("Final_Insight", 0.24, "Architectural rule of thumb", "payoff")
        ]
    ),

    # STRUCTURE_H: Engineering Narrative
    "structure_h": StoryStructure(
        id="structure_h",
        name="Engineering Narrative",
        description="Narrative journey through a classic computer science dilemma and its triumphant resolution.",
        suitable_intents=["historical_narrative", "solve_crisis", "scale_journey"],
        suitable_topic_types=["system_architecture", "networking_distributed", "database_storage"],
        preferred_scene_types=["hook", "split", "diagram", "code", "payoff"],
        pacing_profile="measured",
        emotional_profile="urgent",
        compatible_visual_strategies=["documentary", "cinematic_diagram", "magazine_editorial"],
        beats=[
            StoryBeat("Scenario", 0.12, "Setting the scene: scaling to 100,000 requests/sec", "hook"),
            StoryBeat("Bottleneck", 0.24, "The architectural bottleneck threatening the system", "split"),
            StoryBeat("Breakthrough", 0.36, "The algorithmic breakthrough that unlocked scale", "diagram"),
            StoryBeat("Implementation", 0.16, "The essential lines of code embodying the change", "code"),
            StoryBeat("Resolution", 0.12, "System operating smoothly at scale", "payoff")
        ]
    ),

    # STRUCTURE_I: System Architecture Walkthrough
    "structure_i": StoryStructure(
        id="structure_i",
        name="System Architecture Walkthrough",
        description="Comprehensive topology walkthrough for distributed infrastructure and systems without mandatory code cards.",
        suitable_intents=["architectural_blueprint", "explain_mechanism", "topology_tour"],
        suitable_topic_types=["system_architecture", "devops_cloud_infra", "networking_distributed"],
        preferred_scene_types=["hook", "diagram", "metaphor", "diagram", "payoff"],
        pacing_profile="deliberate",
        emotional_profile="authoritative",
        compatible_visual_strategies=["system_architecture", "technical_blueprint", "cinematic_diagram"],
        beats=[
            StoryBeat("Cluster_Hook", 0.10, "What happens when 1,000 nodes execute simultaneously", "hook"),
            StoryBeat("Topology_Map", 0.28, "Cluster topology: control plane, ingress, worker pools", "diagram"),
            StoryBeat("State_Synchronization", 0.24, "How consensus and state sync without lock contention", "metaphor"),
            StoryBeat("Data_Pipeline", 0.22, "End-to-end packet delivery path through network mesh", "diagram"),
            StoryBeat("Resilience_Payoff", 0.16, "The zero-downtime invariant of modern architecture", "payoff")
        ]
    ),

    # STRUCTURE_J: Comparative Showdown
    "structure_j": StoryStructure(
        id="structure_j",
        name="Comparative Showdown",
        description="Direct head-to-head comparison of two architectures, frameworks, or algorithms.",
        suitable_intents=["compare_alternatives", "benchmark_showcase", "choose_right_tool"],
        suitable_topic_types=["web_frontend", "database_storage", "system_architecture", "product_engineering"],
        preferred_scene_types=["hook", "split", "benchmark", "diagram", "payoff"],
        pacing_profile="rapid",
        emotional_profile="analytical",
        compatible_visual_strategies=["split_screen_comparison", "data_visualization", "editorial_grid"],
        beats=[
            StoryBeat("Showdown_Hook", 0.10, "Approach A vs Approach B: which actually wins?", "hook"),
            StoryBeat("Head_To_Head", 0.26, "Side-by-side execution comparison", "split"),
            StoryBeat("Stress_Benchmark", 0.28, "Live latency, memory, and throughput showdown", "benchmark"),
            StoryBeat("Architectural_Tradeoff", 0.22, "Why neither is universally better: tradeoff matrix", "diagram"),
            StoryBeat("Selection_Rule", 0.14, "The definitive decision rubric for your team", "payoff")
        ]
    ),

    # STRUCTURE_K: Mathematical 3D Dimension Shift
    "structure_k": StoryStructure(
        id="structure_k",
        name="Mathematical 3D Dimension Shift",
        description="Visualizes formulas, tensors, and mathematical objects by elevating from 2D symbols into 3D spatial geometry.",
        suitable_intents=["mathematical_visualization", "intuitive_grounding", "dimension_shift"],
        suitable_topic_types=["math_theoretical", "ai_machine_learning"],
        preferred_scene_types=["hook", "math_3d", "diagram", "math_3d", "payoff"],
        pacing_profile="deliberate",
        emotional_profile="mind_bending",
        compatible_visual_strategies=["mathematical_3d", "abstract_motion", "technical_blueprint"],
        beats=[
            StoryBeat("Formula_Hook", 0.10, "The 2D formula that looks intimidating on paper", "hook"),
            StoryBeat("Spatial_Extrusion", 0.30, "Extruding the symbols into a continuous 3D geometric surface", "math_3d"),
            StoryBeat("Tensor_Dissection", 0.24, "Slicing through coordinate planes to reveal invariants", "diagram"),
            StoryBeat("Geometric_Flow", 0.22, "Tracing particle trajectories across the manifold", "math_3d"),
            StoryBeat("Universal_Intuition", 0.14, "The geometric truth behind the equation", "payoff")
        ]
    ),

    # STRUCTURE_L: Evolution & Timeline
    "structure_l": StoryStructure(
        id="structure_l",
        name="Evolution & Timeline",
        description="Traces the generational evolution of a paradigm from historic constraints to modern solutions.",
        suitable_intents=["historical_narrative", "paradigm_shift", "generational_evolution"],
        suitable_topic_types=["history_evolution", "philosophical_conceptual", "web_frontend", "operating_systems_lowlevel"],
        preferred_scene_types=["hook", "diagram", "split", "diagram", "payoff"],
        pacing_profile="measured",
        emotional_profile="authoritative",
        compatible_visual_strategies=["documentary", "magazine_editorial", "retro_computing"],
        beats=[
            StoryBeat("Epoch_Hook", 0.10, "How computing operated before this paradigm existed", "hook"),
            StoryBeat("Historic_Constraint", 0.26, "The hardware bottleneck that forced early engineers to compromise", "diagram"),
            StoryBeat("Generational_Leap", 0.28, "Before vs After: the single invention that changed everything", "split"),
            StoryBeat("Modern_Standard", 0.22, "How every modern smartphone and cloud runs on this today", "diagram"),
            StoryBeat("Future_Horizon", 0.14, "The next architectural frontier", "payoff")
        ]
    )
}


@dataclass
class TopicAnalysis:
    topic: str
    category: str
    intent: str
    complexity: str
    emotional_tone: str
    educational_vs_promotional_vs_storytelling: str
    modalities: Dict[str, bool]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class StoryDirector:
    """
    Intelligent Story Director.
    Analyzes topics semantically and selects the most optimal narrative structure
    based on intent, topic category, complexity, modalities, and anti-repetition history.
    """

    CATEGORIES = [
        "algorithms_data_structures",
        "system_architecture",
        "networking_distributed",
        "operating_systems_lowlevel",
        "ai_machine_learning",
        "language_runtime_internals",
        "database_storage",
        "security_cryptography",
        "web_frontend",
        "devops_cloud_infra",
        "math_theoretical",
        "philosophical_conceptual",
        "product_engineering",
        "history_evolution",
    ]

    INTENTS = [
        "explain_mechanism",
        "solve_crisis",
        "debunk_myth",
        "reverse_engineer",
        "compare_alternatives",
        "historical_narrative",
        "empirical_lab",
        "architectural_blueprint",
        "mathematical_visualization",
        "rapid_takeaway",
    ]

    @classmethod
    def analyze_topic(cls, topic: str) -> TopicAnalysis:
        t = topic.lower()

        # ── 1. Modality Detection ─────────────────────────────────────────────
        modalities = {
            "involves_code": bool(re.search(r"\b(code|syntax|function|method|class|java|python|rust|c\+\+|js|typescript|go|struct|pointer|loop|if|promise|async)\b", t)),
            "involves_data": bool(re.search(r"\b(data|array|tree|graph|list|hash|metric|latency|throughput|search|sort|partition|matrix)\b", t)),
            "involves_diagrams": bool(re.search(r"\b(architecture|system|pipeline|flow|network|distributed|cluster|docker|k8s|cloud|microservice)\b", t)),
            "involves_mathematics": bool(re.search(r"\b(math|equation|formula|calculus|euler|sinc|fourier|geometry|dimension|3d|helix|vector|tensor|spiral|algebra|quantum|probability|bayesian|topology|superposition)\b", t)),
            "involves_systems": bool(re.search(r"\b(docker|container|linux|kernel|cpu|memory|os|heap|stack|thread|cache|process|cluster|distributed)\b", t)),
            "involves_comparison": bool(re.search(r"\b(vs|versus|difference|compare|benchmark|faster|alternative|choice|which|pros|cons)\b", t)),
            "involves_history": bool(re.search(r"\b(history|evolution|origin|how\s+we\s+got|timeline|past|generations?|classic)\b", t)),
            "involves_abstract": bool(re.search(r"\b(philosophy|concept|mental\s+model|why|future|meaning|clean\s+code|paradigm|theseus|identity)\b", t)),
        }

        # ── 2. Category Detection ─────────────────────────────────────────────
        category = "algorithms_data_structures"
        if modalities["involves_mathematics"] or any(k in t for k in ["euler", "complex", "sine", "cosine", "equation", "formula", "helix", "geometry", "quantum", "bayesian", "monty hall", "topology", "superposition"]):
            category = "math_theoretical"
        elif bool(re.search(r"\b(ai|llm|attention|flashattention|neural|transformer|diffusion|weights|deep learning)\b", t)):
            category = "ai_machine_learning"
        elif any(k in t for k in ["docker", "container", "kubernetes", "k8s", "terraform", "ci/cd", "devops", "cloud", "aws"]):
            category = "devops_cloud_infra"
        elif any(k in t for k in ["architecture", "microservice", "distributed", "event-driven", "kafka", "mq", "pubsub", "cluster"]):
            category = "system_architecture"
        elif any(k in t for k in ["api", "rest", "grpc", "http", "socket", "network", "tcp", "udp", "dns", "packet"]):
            category = "networking_distributed"
        elif any(k in t for k in ["kernel", "cpu", "cache", "assembly", "register", "hardware", "syscall", "page table", "mmu"]):
            category = "operating_systems_lowlevel"
        elif any(k in t for k in ["garbage collector", "jvm", "heap", "vtable", "jit", "runtime", "gil", "event loop", "async", "await", "coroutine"]):
            category = "language_runtime_internals"
        elif any(k in t for k in ["database", "sql", "index", "b-tree", "postgres", "lsm", "acid", "redis", "query"]):
            category = "database_storage"
        elif any(k in t for k in ["security", "auth", "jwt", "oauth", "encrypt", "crypto", "zero trust", "hack", "ssl", "tls"]):
            category = "security_cryptography"
        elif any(k in t for k in ["react", "vue", "dom", "css", "browser", "frontend", "html", "web component"]):
            category = "web_frontend"
        elif modalities["involves_history"]:
            category = "history_evolution"
        elif modalities["involves_abstract"] or any(k in t for k in ["clean code", "dry", "solid", "kiss", "conway", "turing"]):
            category = "philosophical_conceptual"
        elif any(k in t for k in ["billing", "stripe", "rate limit", "feature flag", "product"]):
            category = "product_engineering"
        elif any(k in t for k in ["sort", "search", "binary search", "b-tree", "graph", "tree", "linked list", "hash table", "dp", "recursion"]):
            category = "algorithms_data_structures"

        # ── 3. Intent Detection ───────────────────────────────────────────────
        intent = "explain_mechanism"
        if modalities["involves_comparison"]:
            intent = "compare_alternatives"
        elif any(k in t for k in ["myth", "wrong", "lie", "misconception", "stop using", "never"]):
            intent = "debunk_myth"
        elif any(k in t for k in ["bug", "crash", "error", "leak", "deadlock", "fail", "slow", "freeze", "overflow"]):
            intent = "solve_crisis"
        elif any(k in t for k in ["how to build", "reverse engineer", "under the hood", "teardown", "dissect"]):
            intent = "reverse_engineer"
        elif any(k in t for k in ["benchmark", "speed", "fast", "throughput", "10x", "million", "billion"]):
            intent = "empirical_lab"
        elif any(k in t for k in ["architecture", "topology", "cluster", "enterprise", "system"]):
            intent = "architectural_blueprint"
        elif any(k in t for k in ["history", "evolution", "rise of", "past"]):
            intent = "historical_narrative"
        elif modalities["involves_mathematics"]:
            intent = "mathematical_visualization"
        elif any(k in t for k in ["quick", "speedrun", "in 45 seconds", "in 30 seconds", "in 60 seconds", "cheat sheet"]):
            intent = "rapid_takeaway"

        # ── 4. Complexity & Emotional Tone ────────────────────────────────────
        complexity = "intermediate"
        if any(k in t for k in ["beginner", "101", "intro", "basics", "simple", "for dummies"]):
            complexity = "beginner"
        elif any(k in t for k in ["internals", "under the hood", "advanced", "deep dive", "kernel", "assembly", "speculative"]):
            complexity = "advanced"

        emotional_tone = "curious"
        if intent == "solve_crisis":
            emotional_tone = "urgent"
        elif intent in ("debunk_myth", "architectural_blueprint"):
            emotional_tone = "authoritative"
        elif intent in ("empirical_lab", "compare_alternatives"):
            emotional_tone = "analytical"
        elif intent in ("mathematical_visualization", "intuitive_grounding"):
            emotional_tone = "mind_bending"
        elif intent == "rapid_takeaway":
            emotional_tone = "pragmatic"

        # ── 5. Intent Mode ────────────────────────────────────────────────────
        intent_mode = "educational"
        if any(k in t for k in ["story", "journey", "how i", "history", "crisis"]):
            intent_mode = "storytelling"
        elif any(k in t for k in ["showcase", "why you should use", "best tool", "pro"]):
            intent_mode = "promotional"

        return TopicAnalysis(
            topic=topic,
            category=category,
            intent=intent,
            complexity=complexity,
            emotional_tone=emotional_tone,
            educational_vs_promotional_vs_storytelling=intent_mode,
            modalities=modalities,
        )

    @classmethod
    def select_structure(
        cls,
        topic: str,
        analysis: Optional[TopicAnalysis] = None,
        recent_structures: Optional[List[str]] = None
    ) -> StoryStructure:
        """
        Selects the best narrative structure through multidimensional scoring:
        Score = Intent Match + Category Match + Modality Match - Novelty Penalty.
        Never blindly defaults to structure_a.
        """
        if analysis is None:
            analysis = cls.analyze_topic(topic)

        recent = recent_structures or []
        scores: Dict[str, float] = {}

        for sid, struct in STORY_STRUCTURES.items():
            score = 10.0  # Base score

            # Intent compatibility (+35 max)
            if analysis.intent in struct.suitable_intents:
                score += 35.0

            # Topic category compatibility (+30 max)
            if analysis.category in struct.suitable_topic_types:
                score += 30.0

            # Modality-specific bonuses
            if analysis.modalities.get("involves_mathematics") and sid == "structure_k":
                score += 45.0
            if analysis.modalities.get("involves_comparison") and sid == "structure_j":
                score += 45.0
            if analysis.modalities.get("involves_history") and sid == "structure_l":
                score += 45.0
            if analysis.intent == "solve_crisis" and sid == "structure_c":
                score += 40.0
            if analysis.intent == "debunk_myth" and sid == "structure_f":
                score += 40.0
            if analysis.intent == "reverse_engineer" and sid == "structure_b":
                score += 40.0
            if analysis.intent == "architectural_blueprint" and sid == "structure_i":
                score += 40.0
            if analysis.intent == "rapid_takeaway" and sid == "structure_g":
                score += 35.0

            # Pacing alignment
            if analysis.complexity == "advanced" and struct.pacing_profile == "deliberate":
                score += 10.0
            elif analysis.complexity == "beginner" and struct.pacing_profile == "measured":
                score += 10.0

            # Weighted Novelty Penalty:
            # -30 if used in the most recent video
            # -15 if used in the 2nd most recent
            # -8 if used in the 3rd most recent
            if recent:
                if len(recent) > 0 and recent[-1] == sid:
                    score -= 30.0
                if len(recent) > 1 and recent[-2] == sid:
                    score -= 15.0
                if len(recent) > 2 and recent[-3] == sid:
                    score -= 8.0

            scores[sid] = score

        best_sid = max(scores, key=lambda s: scores[s])
        return STORY_STRUCTURES[best_sid]

    select_narrative_structure = select_structure


def select_story_structure(
    topic: str,
    style_id: str = "editorial",
    recent_structures: Optional[List[str]] = None
) -> StoryStructure:
    """Backward-compatible entry point delegating to intelligent StoryDirector."""
    analysis = StoryDirector.analyze_topic(topic)
    return StoryDirector.select_structure(topic, analysis, recent_structures=recent_structures)
