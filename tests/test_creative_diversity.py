"""
tests/test_creative_diversity.py
================================
Validates that Prompt Reel produces distinct creative identities across
multiple videos rather than reusing the same template, BGM, BPM, beat, chords, and closer.

Tests the 5 canonical topics:
1. Java if-else
2. Java OOP
3. REST APIs
4. Docker
5. Binary Search
"""
import os
import sys
import unittest
import numpy as np

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.nemotron_client import NemotronClient
from agents.creative_director import CreativeDirectorAgent
from agents.script_storyboard_agent import ScriptStoryboardAgent
from engine.dna_registry import DNARegistry
from effects.audio_dna import select_audio_dna, compute_audio_seed, extract_audio_events_from_motion_plan
from effects.closing_strategies import select_closing_strategy
from audio_pipeline import ProceduralMusicGenerator


class TestCreativeDiversity(unittest.TestCase):
    def setUp(self):
        self.dna_registry = DNARegistry(history_file="test_dna_history.json")
        # Clear test history
        if os.path.exists("test_dna_history.json"):
            os.remove("test_dna_history.json")
        offline_nemo = NemotronClient(api_key="")
        self.cd_agent = CreativeDirectorAgent(nemotron_client=offline_nemo, dna_registry=self.dna_registry)
        self.storyboard_agent = ScriptStoryboardAgent(nemotron_client=offline_nemo)

    def tearDown(self):
        if os.path.exists("test_dna_history.json"):
            os.remove("test_dna_history.json")

    def test_five_topic_creative_diversity(self):
        topics = [
            "Java if-else",
            "Java OOP",
            "REST APIs",
            "Docker",
            "Binary Search"
        ]

        plans = []
        creative_dirs = []

        print("\n" + "=" * 70)
        print("  TESTING CREATIVE DIVERSITY ACROSS 5 CORE TOPICS")
        print("=" * 70)

        for idx, topic in enumerate(topics):
            cd = self.cd_agent.direct_video(
                topic=topic,
                duration_sec=50.0,
                project_id=f"proj_{idx+1}"
            )
            motion_plan = self.storyboard_agent.generate_motion_plan(
                topic=topic,
                creative_dir=cd,
                total_duration=50.0
            )

            plans.append(motion_plan)
            creative_dirs.append(cd)

            # Register video DNA to simulate multi-video production history
            self.dna_registry.register_video(cd["dna"])

        # ── 1. Check Audio DNA Diversity ─────────────────────────────────────
        audio_dnas = [cd["audio_dna"] for cd in creative_dirs]
        genres = [a["genre"] for a in audio_dnas]
        bpms = [a["bpm"] for a in audio_dnas]
        rhythms = [a["rhythm"] for a in audio_dnas]
        chords = [tuple(a["chord_progression"]) for a in audio_dnas]
        audio_seeds = [a["variation_seed"] for a in audio_dnas]

        print("\n--- AUDIO DNA DIVERSITY ---")
        for i, t in enumerate(topics):
            print(f"[{t}] Genre: {genres[i]} | BPM: {bpms[i]} | Rhythm: {rhythms[i]} | Chords: {list(chords[i])}")

        # Assert genres are not all identical
        self.assertGreater(len(set(genres)), 1, "Expected distinct genres across 5 topics")
        # Assert BPMs have variation
        self.assertGreater(len(set(bpms)), 1, "Expected distinct BPMs across 5 topics")
        # Assert rhythms are diverse
        self.assertGreater(len(set(rhythms)), 1, "Expected diverse rhythm architectures")
        # Assert chord progressions are not all identical
        self.assertGreater(len(set(chords)), 1, "Expected diverse modal chord progressions")
        # Assert distinct deterministic audio seeds
        self.assertEqual(len(set(audio_seeds)), 5, "Every video must have a unique audio seed")

        # ── 2. Check Closing DNA Diversity ───────────────────────────────────
        closing_dnas = [cd["closing_dna"] for cd in creative_dirs]
        strategies = [c["strategy_id"] for c in closing_dnas]
        layouts = [c["layout"] for c in closing_dnas]
        headlines = [c["headline"] for c in closing_dnas]

        print("\n--- CLOSING STRATEGY DIVERSITY ---")
        for i, t in enumerate(topics):
            print(f"[{t}] Strategy: {strategies[i]} | Layout: {layouts[i]} | Headline: {headlines[i]}")

        # Assert closing strategies are not all identical
        self.assertGreater(len(set(strategies)), 1, "Expected distinct closing strategies across 5 topics")
        self.assertGreater(len(set(layouts)), 1, "Expected distinct closing layouts")
        self.assertEqual(len(set(headlines)), 5, "Every closer should have a topic-specific headline")

        # ── 3. Check Motion Plan Payoff Scenes ────────────────────────────────
        for i, plan in enumerate(plans):
            payoff_scene = next((s for s in plan["scenes"] if s.get("visual_type") == "payoff"), None)
            self.assertIsNotNone(payoff_scene, f"Topic '{topics[i]}' missing payoff scene")
            elems = payoff_scene["elements"]
            self.assertIn("closing_strategy", elems)
            self.assertIn("layout", elems)
            self.assertIn("headline", elems)
            self.assertEqual(elems["closing_strategy"], strategies[i])

            # Check semantic audio events
            self.assertIn("audio_events", plan)
            self.assertGreaterEqual(len(plan["audio_events"]), 3, "Motion plan must expose timed audio events")

        # ── 4. Creative Repetition Detector Pairwise Verification ────────────
        print("\n--- CREATIVE SIMILARITY BREAKDOWNS ---")
        history = self.dna_registry.get_history()
        for i in range(len(history)):
            for j in range(i + 1, len(history)):
                bd = self.dna_registry.compute_similarity_breakdown(history[i], history[j])
                overall = bd["overall_creative_similarity"]
                print(f"Similarity between '{topics[i]}' & '{topics[j]}': {overall:.2f} "
                      f"(audio={bd['audio_similarity']:.2f}, visual={bd['visual_similarity']:.2f}, "
                      f"closing={bd['closing_similarity']:.2f}, motion={bd['motion_similarity']:.2f})")
                self.assertLess(overall, 0.70, f"Pair ({topics[i]}, {topics[j]}) exceeds similarity threshold!")

    def test_procedural_audio_with_audio_dna_and_events(self):
        """Validates that ProceduralMusicGenerator generates non-zero audio respecting AudioDNA."""
        dna = select_audio_dna(
            topic="Distributed Consensus Paxos",
            style_id="cyberpunk",
            story_structure_id="structure_a",
            duration_sec=10.0,
            seed_salt="test_audio_seed"
        )
        audio_events = [
            {"time": 0.0, "type": "intro"},
            {"time": 2.5, "type": "impact"},
            {"time": 5.0, "type": "reveal"},
            {"time": 8.0, "type": "resolution"}
        ]

        gen = ProceduralMusicGenerator(
            sample_rate=24000,
            bpm=dna.bpm,
            style=dna.genre,
            chord_progression=dna.chord_progression,
            audio_dna=dna.to_dict(),
            audio_events=audio_events
        )

        music = gen.generate_music(total_seconds=10.0)
        self.assertIsInstance(music, np.ndarray)
        self.assertEqual(music.shape, (24000 * 10, 2))
        max_amplitude = np.max(np.abs(music))
        self.assertGreater(max_amplitude, 0.1, "Generated music track should have audible amplitude")
        self.assertLessEqual(max_amplitude, 1.0, "Music should not clip beyond 1.0 peak")

    def test_granular_regeneration_audio_and_closing(self):
        """Validates conversational requests: change music and change ending."""
        cd = self.cd_agent.direct_video("Docker Containers", duration_sec=50.0)
        orig_audio = cd["audio_dna"]
        orig_closing = cd["closing_dna"]

        # Regenerate only audio
        fresh_audio = self.cd_agent.regenerate_audio_dna("Docker Containers", cd, salt="reroll_1")
        self.assertNotEqual(fresh_audio["variation_seed"], orig_audio["variation_seed"])

        # Regenerate only closing
        fresh_closing = self.cd_agent.regenerate_closing_dna("Docker Containers", cd, salt="reroll_2")
        self.assertNotEqual(fresh_closing["variation_seed"], orig_closing["variation_seed"])


if __name__ == "__main__":
    unittest.main()
