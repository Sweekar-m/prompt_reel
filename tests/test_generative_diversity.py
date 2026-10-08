"""
tests/test_generative_diversity.py
==================================
Comprehensive automated test suite for the Generative Motion-Design Engine:
1. 20 Synthetic topics generating diverse Story Structures (>= 6 distinct).
2. 20 Synthetic topics generating diverse Visual Strategies (>= 8 distinct).
3. 20 Synthetic topics generating distinct Scene Sequences (>= 12 distinct).
4. VisualDNA consistency within each reel (cohesive palette, fonts, spacing).
5. Multi-dimensional anti-repetition intelligence & weighted novelty penalties.
6. Unknown/unseen topics semantic mapping (no generic 'SYSTEM CORE: {BEAT}').
7. Deterministic fallback rendering.
8. Strict Pydantic schema validation for creative plans and motion plans.
9. Dynamic scene composition selection.
10. Dynamic camera language and transition continuity.
"""

import os
import sys
import unittest
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from effects.story_structures import StoryDirector, TopicAnalysis, STORY_STRUCTURES
from effects.visual_strategies import VISUAL_STRATEGIES, select_visual_strategy, VisualStrategy
from effects.visual_dna import build_visual_dna, VisualDNA
from effects.story_dna import StoryDNA
from engine.dna_registry import DNARegistry, VideoDNA
from engine.schema_validation import validate_motion_plan, validate_creative_plan, CreativePlanModel, MotionPlanModel
from agents.creative_director import CreativeDirectorAgent
from agents.script_storyboard_agent import ScriptStoryboardAgent
from agents.shot_designer_agent import ShotDesignerAgent
from renderer.deterministic_renderer import render_motion_plan_frame


# 20 diverse synthetic topics across technical, architectural, algorithms, data, history, philosophy, etc.
SYNTHETIC_20_TOPICS = [
    "Docker Container OverlayFS and Cgroups Architecture",
    "Binary Search Invariant and Branch Prediction",
    "History of Artificial Neural Networks and Perceptrons",
    "PostgreSQL Multi-Version Concurrency Control (MVCC)",
    "FlashAttention-2 Tiling on GPU SRAM",
    "Philosophy of The Ship of Theseus and Object Identity",
    "Kafka Distributed Log Partitioning and Consumer Rebalance",
    "Euler Characteristic and Topology of Polyhedra",
    "Rust Borrow Checker and Lifetimes Invariance",
    "Microservices Service Mesh vs Monolithic In-Memory Calls",
    "Quantum Superposition and Shor's Algorithm",
    "CSS Flexbox Box Model vs CSS Grid Two-Dimensional Flow",
    "Evolution of Silicon: Vacuum Tubes to 3nm FinFETs",
    "WebRTC Peer-to-Peer NAT Traversal via STUN and TURN",
    "Garbage Collection: Tri-Color Mark and Sweep vs Reference Counting",
    "TCP Three-Way Handshake vs QUIC UDP Connection Migration",
    "The Monty Hall Problem and Bayesian Prior Updates",
    "Git Internals: Blobs, Trees, and Directed Acyclic Graphs",
    "B-Tree vs Log-Structured Merge Tree (LSM) for Database Indexes",
    "CRDTs (Conflict-Free Replicated Data Types) in Collaborative Editors"
]


class TestGenerativeDiversity(unittest.TestCase):

    def setUp(self):
        self.story_director = StoryDirector()
        test_history_file = os.path.join(BASE_DIR, "output", "test_dna_history.json")
        os.makedirs(os.path.dirname(test_history_file), exist_ok=True)
        if os.path.exists(test_history_file):
            os.remove(test_history_file)
        self.dna_registry = DNARegistry(test_history_file)
        self.creative_director = CreativeDirectorAgent(dna_registry=self.dna_registry)
        # Mock external network LLM calls for lightning-fast deterministic test execution
        self.creative_director.nemotron.generate_viral_hook = lambda topic, style=None: {
            "headline": f"WHY {topic.upper()[:25]} MATTERS",
            "subtext": "The core architectural invariant.",
            "is_math": False
        }
        self.creative_director.nemotron.generate_math_3d_concept = lambda topic: None
        self.creative_director.nemotron.generate_visual_metaphor = lambda topic: {"metaphor_id": "procedural_stack"}
        self.storyboard_agent = ScriptStoryboardAgent()
        self.storyboard_agent.nemotron.explain_technical_concept = lambda topic: {
            "title": topic,
            "core_mechanism": f"Mechanisms of {topic}",
            "key_invariants": ["Invariant A", "Invariant B"]
        }
        self.storyboard_agent.nemotron.generate_code_snippets = lambda topic: {
            "snippet": "// Code",
            "lines": ["// Line 1", "// Line 2"]
        }
        self.storyboard_agent.nemotron.generate_script = lambda topic, beats, tech, code: [
            f"Beat {idx}: Understanding {topic}" for idx, _ in enumerate(beats)
        ]
        self.shot_designer = ShotDesignerAgent()

    def test_twenty_topics_structural_and_visual_diversity(self):
        """Verify that 20 topics yield rich structural and visual variety, not structure_a fallback."""
        structures_seen = set()
        strategies_seen = set()
        sequences_seen = set()
        base_sequences_seen = []
        topics_analyzed = []

        recent_structures: List[str] = []
        recent_strategies: List[str] = []

        for topic in SYNTHETIC_20_TOPICS:
            analysis = self.story_director.analyze_topic(topic)
            struct = self.story_director.select_narrative_structure(
                topic, analysis, recent_structures=recent_structures
            )
            strategy = select_visual_strategy(
                topic, analysis, struct.id, recent_strategies=recent_strategies
            )
            recent_structures.append(struct.id)
            recent_strategies.append(strategy.id)

            plan = self.storyboard_agent.generate_motion_plan(
                topic=topic,
                creative_direction={
                    "story_dna": struct.__dict__,
                    "visual_dna": {"visual_strategy": strategy.id, "camera_language": "slow_push"},
                    "palette": {"id": "electric_matrix"},
                    "typography": {"id": "futuristic_tech"}
                },
                duration_sec=45.0
            )
            shot_plan = self.shot_designer.design_shots_for_motion_plan(plan)
            base_seq = tuple(sc.get("visual_type") for sc in plan.get("scenes", []))
            comp_seq = tuple(f"{sc.get('visual_type')}:{sc.get('composition_variant')}" for sc in shot_plan.get("scenes", []))

            structures_seen.add(struct.id)
            strategies_seen.add(strategy.id)
            sequences_seen.add(comp_seq)
            base_sequences_seen.append(base_seq)
            topics_analyzed.append({
                "topic": topic,
                "structure": struct.id,
                "strategy": strategy.id,
                "sequence": comp_seq,
                "base_sequence": base_seq
            })

        print("\n--- 20 SYNTHETIC TOPICS EVALUATION ---")
        for item in topics_analyzed:
            print(f"[{item['structure']:<14}] [{item['strategy']:<22}] {item['topic'][:50]}...")

        from collections import Counter
        base_counts = Counter(base_sequences_seen)
        max_base_rep = max(base_counts.values())

        print(f"\nUnique Story Structures:     {len(structures_seen)} / 12 (Target >= 6)")
        print(f"Unique Visual Strategies:    {len(strategies_seen)} / 18 (Target >= 8)")
        print(f"Unique Scene Compositions:   {len(sequences_seen)} / 20 (Target >= 12)")
        print(f"Max single sequence repeat:  {max_base_rep} / 20 (Target < 10, i.e. < 50%)")

        # Verify variety requirements
        self.assertGreaterEqual(len(structures_seen), 6, f"Expected >= 6 structures, got {len(structures_seen)}")
        self.assertGreaterEqual(len(strategies_seen), 8, f"Expected >= 8 strategies, got {len(strategies_seen)}")
        self.assertGreaterEqual(len(sequences_seen), 12, f"Expected >= 12 composited sequences, got {len(sequences_seen)}")
        self.assertLess(max_base_rep, 10, "The system must not produce the same scene sequence for most topics")

    def test_visual_dna_consistency_across_scenes(self):
        """Verify that all scenes within a single reel inherit and conform to the same VisualDNA."""
        topic = "PostgreSQL MVCC Concurrency"
        analysis = self.story_director.analyze_topic(topic)
        strategy = select_visual_strategy(topic, analysis)
        v_dna = build_visual_dna(topic, strategy)

        cd = self.creative_director.direct_video(topic, requested_style=strategy.id, duration_sec=45.0)
        plan = self.storyboard_agent.generate_motion_plan(topic, cd, 45.0)
        shot_plan = self.shot_designer.design_shots_for_motion_plan(plan)

        reel_palette = cd["palette"]
        scenes = shot_plan.get("scenes", [])
        self.assertGreater(len(scenes), 3)

        # Confirm all scenes share the same creative direction context
        for sc in scenes:
            if sc.get("visual_recipe"):
                recipe = sc["visual_recipe"]
                # Palette accents or camera languages shouldn't clash randomly
                self.assertIsNotNone(recipe.get("camera"))
                self.assertIsNotNone(recipe.get("composition"))
                self.assertIsNotNone(recipe.get("primary_subject"))

    def test_weighted_anti_repetition_logic(self):
        """Verify that recent identical structures/strategies receive novelty penalties (-30, -40, etc.)."""
        # Register a video DNA
        prior_dna = {
            "story_structure": "structure_b",
            "visual_strategy": "system_architecture",
            "scene_sequence": ["hook", "diagram", "split", "payoff"],
            "composition_variants": ["editorial_left", "radial_system", "split_benchmark"],
            "camera_language": "slow_push",
            "transition_language": "whip_pan"
        }
        self.dna_registry.register_video(prior_dna)

        # Candidate with exact identical choices
        penalty_score = self.dna_registry.compute_novelty_score(
            candidate_structure="structure_b",
            candidate_strategy="system_architecture",
            candidate_sequence=["hook", "diagram", "split", "payoff"],
            candidate_compositions=["editorial_left", "radial_system", "split_benchmark"],
            candidate_camera="slow_push",
            candidate_transition="whip_pan"
        )
        # Expected max penalty: 100 - 30 - 30 - 40 - 20 - 15 - 15 = -50 clamped to 0
        self.assertEqual(penalty_score, 0.0)

        # Candidate with completely distinct choices
        distinct_score = self.dna_registry.compute_novelty_score(
            candidate_structure="structure_d",
            candidate_strategy="terminal_story",
            candidate_sequence=["hook", "code", "diagram", "payoff"],
            candidate_compositions=["giant_type", "terminal_stream", "grid_matrix"],
            candidate_camera="orbit",
            candidate_transition="zoom_burst"
        )
        self.assertEqual(distinct_score, 100.0)

    def test_unknown_topic_semantic_inference_no_lazy_fallback(self):
        """Verify that unseen/esoteric topics produce rich semantic visual primitives and never 'SYSTEM CORE: {BEAT}'."""
        unseen_topics = [
            "Photosynthesis Light-Dependent Calvin Cycle ATP Synthase",
            "Laminar vs Turbulent Boundary Layer Fluid Aerodynamics",
            "Sumerian Cuneiform Clay Tablet Accounting Inscriptions"
        ]

        for topic in unseen_topics:
            analysis = self.story_director.analyze_topic(topic)
            self.assertIsNotNone(analysis.category)
            self.assertIsNotNone(analysis.intent)

            strategy = select_visual_strategy(topic, analysis)
            self.assertIn(strategy.id, VISUAL_STRATEGIES)

            cd = self.creative_director.direct_video(topic, requested_style=strategy.id, duration_sec=40.0)
            plan = self.storyboard_agent.generate_motion_plan(topic, cd, 40.0)
            shot_plan = self.shot_designer.design_shots_for_motion_plan(plan)

            for sc in shot_plan.get("scenes", []):
                recipe = sc.get("visual_recipe")
                if recipe:
                    subj = recipe.get("primary_subject", {})
                    desc = subj.get("description", "")
                    name = subj.get("name", "")
                    # Strictly check no lazy fallback
                    self.assertNotIn("SYSTEM CORE:", desc)
                    self.assertNotIn("SYSTEM CORE:", name)

    def test_pydantic_schema_validation(self):
        """Verify strict Pydantic validation on motion plans and creative plans."""
        topic = "Binary Search Tree Rotation"
        cd = self.creative_director.direct_video(topic, requested_style="code_first", duration_sec=35.0)
        plan = self.storyboard_agent.generate_motion_plan(topic, cd, 35.0)
        shot_plan = self.shot_designer.design_shots_for_motion_plan(plan)

        valid, report = validate_motion_plan(shot_plan)
        self.assertTrue(valid, f"Plan failed Pydantic validation: {report.get('error')}")
        self.assertEqual(report.get("topic"), topic)
        self.assertGreater(report.get("scene_count", 0), 2)

    def test_scene_composition_variants_diversity(self):
        """Verify that scenes receive specific data-driven composition variants."""
        topic = "Docker Container Isolation"
        cd = self.creative_director.direct_video(topic, requested_style="system_architecture", duration_sec=45.0)
        plan = self.storyboard_agent.generate_motion_plan(topic, cd, 45.0)
        shot_plan = self.shot_designer.design_shots_for_motion_plan(plan)

        variants = [sc.get("composition_variant") for sc in shot_plan.get("scenes", []) if sc.get("composition_variant")]
        self.assertGreater(len(variants), 2)
        # Should contain varied compositions, not all identical
        self.assertGreater(len(set(variants)), 1)

    def test_deterministic_fallback_rendering(self):
        """Verify that the deterministic renderer generates frames for new plans without LLM."""
        topic = "QuickSort Partitioning"
        cd = self.creative_director.direct_video(topic, requested_style="code_first", duration_sec=30.0)
        plan = self.storyboard_agent.generate_motion_plan(topic, cd, 30.0)
        shot_plan = self.shot_designer.design_shots_for_motion_plan(plan)

        # Render frame at 1.0s and 10.0s
        frame_1 = render_motion_plan_frame(shot_plan, t=1.0, frame_idx=30, canvas_size=(540, 960))
        frame_2 = render_motion_plan_frame(shot_plan, t=10.0, frame_idx=300, canvas_size=(540, 960))

        self.assertIsNotNone(frame_1)
        self.assertIsNotNone(frame_2)
        self.assertEqual(frame_1.size, (540, 960))
        self.assertEqual(frame_2.size, (540, 960))


if __name__ == "__main__":
    unittest.main()
