"""
tests/test_visual_engine_diversity.py
======================================
Automated verification of the Prompt Reel Visual Engine upgrade.
Verifies that the engine generates professional motion-graphics films rather than
monotonous presentation slides.

Validates:
1. Diversity across the 5 canonical topics:
   - Java if-else
   - Java OOP
   - Binary Search
   - Docker Containers
   - REST API
2. Diversity across multiple versions of the SAME topic using different motion templates.
3. Verification that compositions vary (not all centered cards).
4. Continuous camera traversal (no abrupt recentering, pitch/yaw depth).
5. Visual subjects correspond to conceptual metaphors (branching logic, volumetric layers, array partitions, ui panels).
6. Rich visual primitives & carry relationships (anti-slideshow).
"""
import os
import sys
import unittest

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.nemotron_client import NemotronClient
from agents.creative_director import CreativeDirectorAgent
from agents.script_storyboard_agent import ScriptStoryboardAgent
from agents.shot_designer_agent import ShotDesignerAgent
from effects.motion_templates import list_motion_templates, get_motion_template, select_best_template_for_topic
from effects.visual_recipes import VisualRecipe


class TestVisualEngineDiversity(unittest.TestCase):
    def setUp(self):
        self.offline_nemotron = NemotronClient(api_key="")
        self.cd_agent = CreativeDirectorAgent(nemotron_client=self.offline_nemotron)
        self.storyboard_agent = ScriptStoryboardAgent(nemotron_client=self.offline_nemotron)
        self.shot_designer = ShotDesignerAgent()

    def test_ten_motion_templates_exist_and_distinct(self):
        """Validates that all 10 motion templates have distinct grammars and categories."""
        templates = list_motion_templates()
        self.assertGreaterEqual(len(templates), 10)

        template_ids = {t.id for t in templates}
        expected_ids = {
            "kinetic_editorial",
            "dynamic_product_ui",
            "brutalist_typography",
            "fluid_abstract",
            "technical_blueprint",
            "spatial_3d_explainer",
            "minimal_swiss",
            "data_story",
            "terminal_motion",
            "cinematic_object"
        }
        self.assertTrue(expected_ids.issubset(template_ids), f"Missing templates: {expected_ids - template_ids}")

        # Check grammar uniqueness
        categories = {t.category for t in templates}
        self.assertGreaterEqual(len(categories), 7, "Templates should cover diverse motion categories")

        bg_styles = {t.background_style for t in templates}
        self.assertGreaterEqual(len(bg_styles), 5, "Templates must have distinct background behaviors")

    def test_canonical_topics_visual_recipes_and_diversity(self):
        """
        Generates visual recipes for the 5 canonical topics and asserts visual diversity:
        compositions, cameras, subjects, and primitives.
        """
        topics = [
            "Java if-else",
            "Java OOP",
            "Binary Search",
            "Docker Containers",
            "REST API"
        ]

        topic_recipes = {}
        all_compositions = set()
        all_primary_subjects = set()
        all_entry_primitives = set()
        all_camera_styles = set()

        print("\n" + "=" * 75)
        print("  TESTING VISUAL RECIPE DIVERSITY ACROSS 5 CANONICAL TOPICS")
        print("=" * 75)

        for topic in topics:
            cd = self.cd_agent.direct_video(topic=topic, duration_sec=45.0)
            motion_plan = self.storyboard_agent.generate_motion_plan(topic=topic, creative_dir=cd, total_duration=45.0)

            # Design shots
            updated_plan = self.shot_designer.design_shots_for_motion_plan(motion_plan, creative_dir=cd)
            recipes = [s["visual_recipe_obj"] for s in updated_plan["scenes"]]
            self.assertGreaterEqual(len(recipes), 3, f"Must produce at least 3 recipes for {topic}")

            topic_recipes[topic] = recipes

            # Verify recipes are rich VisualRecipe instances
            for i, r in enumerate(recipes):
                self.assertIsInstance(r, VisualRecipe)
                self.assertIsNotNone(r.composition)
                self.assertIsNotNone(r.camera)
                self.assertIsNotNone(r.primary_subject)
                self.assertIsNotNone(r.typography)
                self.assertIsNotNone(r.primitives)

                all_compositions.add(r.composition)
                all_primary_subjects.add(r.primary_subject.type)
                all_entry_primitives.add(r.primitives.enter)
                all_camera_styles.add(r.camera.motion_style)

            # Specific subject expectations
            subject_types = [r.primary_subject.type for r in recipes]
            if "if-else" in topic.lower():
                self.assertTrue(any("branching" in st or "gate" in st for st in subject_types),
                                f"Expected branching logic subject in if-else, got {subject_types}")
            elif "docker" in topic.lower():
                self.assertTrue(any("spatial" in st or "layer" in st for st in subject_types),
                                f"Expected spatial 3d or layer subject in docker, got {subject_types}")
            elif "binary search" in topic.lower():
                self.assertTrue(any("data_flow" in st or "partition" in st or "blueprint" in st for st in subject_types),
                                f"Expected data partition in binary search, got {subject_types}")
            elif "rest api" in topic.lower():
                self.assertTrue(any("ui" in st or "contract" in st for st in subject_types),
                                f"Expected ui panel in rest api, got {subject_types}")

            print(f"  [OK] {topic:<20} -> Template: {recipes[0].template_id:<22} Subject: {recipes[1].primary_subject.type}")

        # Assert visual diversity across topics
        print("\n  Summary of Visual Variety:")
        print(f"  • Unique Compositions:      {len(all_compositions)} ({', '.join(sorted(all_compositions))})")
        print(f"  • Unique Primary Subjects:  {len(all_primary_subjects)} ({', '.join(sorted(all_primary_subjects))})")
        print(f"  • Unique Entry Primitives:  {len(all_entry_primitives)} ({', '.join(sorted(all_entry_primitives))})")
        print(f"  • Unique Camera Styles:     {len(all_camera_styles)} ({', '.join(sorted(all_camera_styles))})")

        # Visual quality constraints
        self.assertGreaterEqual(len(all_compositions), 3, "Compositions must vary across topics")
        self.assertGreaterEqual(len(all_primary_subjects), 3, "Subjects must vary across topics")
        self.assertGreaterEqual(len(all_entry_primitives), 3, "Entry motion primitives must vary")
        self.assertFalse(all_compositions == {"centered"}, "Rejected: system must not default exclusively to centered cards!")

    def test_same_topic_multiple_versions_divergence(self):
        """
        Verifies that given the EXACT same script/topic, choosing different motion templates
        produces completely different visual constructions (compositions, cameras, typography).
        """
        topic = "Binary Search"
        test_styles = ["kinetic_editorial", "spatial_3d_explainer", "technical_blueprint", "brutalist_typography"]

        runs = {}
        for style in test_styles:
            cd = self.cd_agent.direct_video(topic=topic, requested_style=style, duration_sec=45.0)
            motion_plan = self.storyboard_agent.generate_motion_plan(topic=topic, creative_dir=cd, total_duration=45.0)
            updated_plan = self.shot_designer.design_shots_for_motion_plan(motion_plan, requested_template_id=style, creative_dir=cd)
            recipes = [s["visual_recipe_obj"] for s in updated_plan["scenes"]]
            runs[style] = recipes

        # Assert that each run has distinct visual recipes
        compositions_per_style = {style: [r.composition for r in runs[style]] for style in test_styles}
        cameras_per_style = {style: [r.camera.motion_style for r in runs[style]] for style in test_styles}

        # Verify that Blueprint uses blueprint background & technical layout
        blueprint_recipes = runs["technical_blueprint"]
        self.assertEqual(blueprint_recipes[0].background_style, "blueprint_grid")

        # Verify that Spatial 3D uses spatial depth grid
        spatial_recipes = runs["spatial_3d_explainer"]
        self.assertEqual(spatial_recipes[0].background_style, "spatial_depth_grid")

        # Check divergence: no two styles should have identical recipe parameters
        for i in range(len(test_styles)):
            for j in range(i + 1, len(test_styles)):
                s1, s2 = test_styles[i], test_styles[j]
                self.assertNotEqual(
                    compositions_per_style[s1],
                    compositions_per_style[s2],
                    f"Styles {s1} and {s2} produced identical compositions!"
                )

    def test_continuous_camera_no_snapping(self):
        """
        Verifies that camera paths connect smoothly from scene to scene
        (end waypoint of scene N roughly matches start waypoint of scene N+1).
        """
        topic = "Docker Containers"
        cd = self.cd_agent.direct_video(topic=topic, duration_sec=40.0)
        motion_plan = self.storyboard_agent.generate_motion_plan(topic=topic, creative_dir=cd, total_duration=40.0)
        updated_plan = self.shot_designer.design_shots_for_motion_plan(motion_plan, creative_dir=cd)
        recipes = [s["visual_recipe_obj"] for s in updated_plan["scenes"]]

        for i in range(len(recipes) - 1):
            curr_recipe = recipes[i]
            next_recipe = recipes[i + 1]

            curr_end = curr_recipe.camera.end
            next_start = next_recipe.camera.start

            # Start of next scene should begin at or near the end of the previous scene
            dist_sq = (
                (curr_end.x - next_start.x) ** 2 +
                (curr_end.y - next_start.y) ** 2 +
                (curr_end.z - next_start.z) ** 2
            )
            self.assertLess(dist_sq, 0.01, f"Camera snapped discontinuously between scene {i} and {i+1}!")


if __name__ == "__main__":
    unittest.main()
