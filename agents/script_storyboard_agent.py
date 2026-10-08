"""
agents/script_storyboard_agent.py
=================================
Script and Storyboard Agent.
Synthesizes the Topic, Technical Facts, and Creative Direction into
a comprehensive, deterministic Motion Plan containing scene-by-scene timing,
voiceover scripts, typography lockups, code tokens, and metaphor parameters.

CONTINUITY MANDATE (OneTake Principle):
  Every scene produced by this agent MUST be designed so that at least one
  element can carry, transform, expand, collapse, travel, or morph into the
  next scene. Scenes that merely replace each other (slideshow) are rejected.
  Each scene receives a `continuity_intent` block describing:
    - what element exits and how
    - what element the next scene should receive
  This data feeds the ContinuityWeaverAgent for bridge annotation.
"""
from typing import Dict, Any, List, Optional
from ai.nemotron_client import NemotronClient
from effects.continuity import get_carry_primitive, CARRY_PRIMITIVES
from effects.audio_dna import extract_audio_events_from_motion_plan


class ScriptStoryboardAgent:
    def __init__(self, nemotron_client: NemotronClient = None):
        self.nemotron = nemotron_client or NemotronClient()

    def generate_motion_plan(
        self,
        topic: str,
        creative_dir: Optional[Dict[str, Any]] = None,
        total_duration: float = 50.0,
        creative_direction: Optional[Dict[str, Any]] = None,
        duration_sec: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Produces a complete Motion Plan JSON ready for deterministic rendering.
        """
        creative_dir = creative_dir or creative_direction or {}
        if duration_sec is not None:
            total_duration = duration_sec

        # Step 1: Query technical explanation and code snippets
        tech_info = self.nemotron.explain_technical_concept(topic)
        code_info = self.nemotron.generate_code_snippets(topic)

        # Step 1b: Natural duration check
        story_dna = creative_dir.get("story_dna", {})
        if story_dna and story_dna.get("target_duration"):
            total_duration = float(story_dna["target_duration"])

        # Step 2: Extract timeline from creative direction's story structure
        if "story_structure" not in creative_dir or not creative_dir.get("story_structure", {}).get("timeline"):
            s_dna = creative_dir.get("story_dna", {})
            struct_id = s_dna.get("narrative_structure") or s_dna.get("id") or "structure_a"
            from effects.story_structures import STORY_STRUCTURES
            struct_obj = STORY_STRUCTURES.get(struct_id, STORY_STRUCTURES["structure_a"])
            creative_dir["story_structure"] = struct_obj.to_story_structure_dict(total_duration)

        timeline_beats = creative_dir["story_structure"]["timeline"]

        # Step 3: Generate engaging, topic-tailored conversational narration
        generated_scripts = self.nemotron.generate_script(topic, timeline_beats, tech_info, code_info)
        voice_profile = creative_dir.get("voice", {})
        voice_rate = voice_profile.get("rate", "+20%") if isinstance(voice_profile, dict) else "+20%"

        scenes = []
        is_math = creative_dir.get("is_math") or self.nemotron._is_math_topic(topic)
        math_spec = creative_dir.get("math_spec") or (self.nemotron.generate_math_3d_concept(topic) if is_math else None)

        for idx, beat in enumerate(timeline_beats):
            scene_id = f"scene_{idx+1}_{beat['beat'].lower()}"
            start_t = beat["start"]
            dur_t = beat["duration"]
            v_type = beat["visual_type"]

            # If math topic, promote metaphor/diagram scenes to math_3d
            if is_math and v_type in ("metaphor", "diagram"):
                v_type = "math_3d"

            # Use opening_voice for hook scene if provided by creative director
            if idx == 0 and creative_dir.get("hook", {}).get("opening_voice"):
                script_text = creative_dir["hook"]["opening_voice"]
            else:
                script_text = generated_scripts[idx] if idx < len(generated_scripts) else f"That is how {topic} operates."

            # Guaranteed clean spoken string without any JSON dictionary representation
            import re
            clean_script = str(script_text).strip()
            m_dict = re.search(r"['\"](?:text|narration)['\"]\s*:\s*['\"](.*?)['\"]\}?$", clean_script, re.DOTALL)
            if m_dict:
                clean_script = m_dict.group(1).strip()
            clean_script = clean_script.replace("{'text':", "").replace('{"text":', "").strip(" '\"{}:")
            if not clean_script:
                clean_script = f"Here is how {topic} behaves under real execution."

            scenes.append({
                "id": scene_id,
                "beat_name": beat["beat"],
                "start": start_t,
                "end": beat["end"],
                "duration": dur_t,
                "visual_type": v_type,
                "voice_text": clean_script,
                "narration": clean_script,
                "voice_rate": voice_rate,
                "elements": self._build_scene_elements(v_type, beat, topic, tech_info, code_info, creative_dir, math_spec)
            })

        # Inject continuity_intent into each scene so the ContinuityWeaver has
        # specific carrier data to work with — this is the OneTake mandate.
        scenes = self._annotate_continuity_intent(scenes, topic, is_math)

        # Extract semantic audio events aligned to scene boundaries and pacing
        audio_events = extract_audio_events_from_motion_plan(scenes, total_duration)

        motion_plan = {
            "version": "3.0",
            "topic": topic,
            "duration": total_duration,
            "fps": 30,
            "total_frames": int(total_duration * 30),
            "creative_direction": creative_dir,
            "story_dna": story_dna,
            "visual_dna": creative_dir.get("visual_dna", {}),
            "technical_summary": tech_info,
            "code_assets": code_info,
            "is_math": is_math,
            "math_spec": math_spec,
            "scenes": scenes,
            "audio_events": audio_events,
            # Placeholder — filled by ContinuityWeaverAgent
            "continuity_bridges": [],
            "continuity_report": None,
        }

        return motion_plan

    def _annotate_continuity_intent(
        self,
        scenes: List[Dict[str, Any]],
        topic: str,
        is_math: bool
    ) -> List[Dict[str, Any]]:
        """
        Adds a `continuity_intent` block to each scene describing:
          - exit_element: the specific element that should carry OUT of this scene
          - exit_primitive: the suggested carry primitive for the exit
          - entry_element: the specific element expected to enter from the previous scene
          - entry_primitive: the carry primitive from the incoming bridge

        This gives the ContinuityWeaver concrete carrier material.
        """
        n = len(scenes)
        for i, scene in enumerate(scenes):
            from_type = scene.get("visual_type", "unknown")
            elements = scene.get("elements", {})

            # Exit intent (carry OUT)
            exit_prim = "travel"  # default
            exit_elem = "primary_element"
            exit_desc = f"Primary element travels to next scene"

            if i < n - 1:
                to_type = scenes[i + 1].get("visual_type", "unknown")
                exit_prim = get_carry_primitive(from_type, to_type)
                exit_elem, exit_desc = self._name_exit_element(from_type, to_type, elements, topic, is_math)

            # Entry intent (receive FROM)
            entry_prim = "travel"  # default
            entry_elem = "primary_element"
            entry_desc = f"Receives carried element from previous scene"

            if i > 0:
                prev_type = scenes[i - 1].get("visual_type", "unknown")
                entry_prim = get_carry_primitive(prev_type, from_type)
                entry_elem, entry_desc = self._name_entry_element(prev_type, from_type, elements, topic, is_math)

            scene["continuity_intent"] = {
                "exit_element": exit_elem,
                "exit_primitive": exit_prim,
                "exit_description": exit_desc,
                "entry_element": entry_elem,
                "entry_primitive": entry_prim,
                "entry_description": entry_desc,
                "is_first_scene": (i == 0),
                "is_last_scene": (i == n - 1),
            }

        return scenes

    def _name_exit_element(self, from_type: str, to_type: str, elements: Dict, topic: str, is_math: bool):
        """Name the specific element that carries OUT of from_type into to_type."""
        if is_math:
            return "math_surface_mesh", "3D parametric mesh continues orbit into next beat"
        if from_type == "hook":
            badge = elements.get("badge", topic.upper())
            headline = elements.get("headline", topic)
            if to_type in ("code", "diagram"):
                return "headline_text", f"'{headline}' expands and transforms into next scene header"
            return "hook_badge", f"'{badge}' badge punches forward as a Z-axis portal"
        if from_type == "code":
            fname = elements.get("filename", "main.py")
            hi = elements.get("highlight_line", 1)
            ann = elements.get("annotation", "key operation")
            return "highlighted_code_line", f"Line {hi} ('{ann}') in {fname} morphs into next visual"
        if from_type == "metaphor":
            label = elements.get("label", "simulation node")
            return "simulation_node", f"'{label}' node travels to anchor the next scene"
        if from_type == "diagram":
            steps = elements.get("steps", ["final step"])
            last_step = steps[-1] if steps else "final step"
            return "diagram_step_node", f"'{last_step}' node collapses and unfurls into code line"
        if from_type == "math_3d":
            formula = elements.get("formula_title", topic)
            return "math_surface_mesh", f"'{formula}' mesh continues orbiting into next beat"
        title = elements.get("headline") or elements.get("title") or elements.get("stat") or topic
        return "primary_element", f"'{title}' collapses/travels to next scene"

    def _name_entry_element(self, prev_type: str, to_type: str, elements: Dict, topic: str, is_math: bool):
        """Name the specific element that is RECEIVED from the previous scene."""
        if is_math:
            return "math_surface_mesh", "Continuous orbit from previous math beat"
        if to_type == "code":
            fname = elements.get("filename", "main.py")
            return "code_editor_header", f"Headline from previous scene resolves as '{fname}' editor header"
        if to_type == "metaphor":
            label = elements.get("label", "core node")
            return "primary_sim_node", f"Incoming element becomes '{label}' simulation node"
        if to_type == "diagram":
            steps = elements.get("steps", ["first step"])
            first_step = steps[0] if steps else "first step"
            return "diagram_anchor", f"Carried element becomes '{first_step}' diagram node"
        if to_type == "payoff":
            title = elements.get("headline") or elements.get("title") or topic
            return "payoff_headline", f"Element collapses into '{title}' payoff card"
        return "primary_element", "Receives carried element from previous scene"

    def regenerate_for_continuity(
        self,
        motion_plan: Dict[str, Any],
        directive: str,
        attempt: int
    ) -> Dict[str, Any]:
        """
        Called by the pipeline when continuity scoring fails.
        Applies targeted fixes to scene visual types and elements
        to create stronger carrier relationships between adjacent beats.

        Strategy:
          - If two adjacent scenes have weak type-pair compatibility,
            consider adjusting the first scene's visual_type to improve the bridge.
          - Enrich elements to provide better carrier sources.
          - Re-annotate continuity_intent.
        """
        from effects.continuity import CARRY_COMPATIBILITY, CARRY_FALLBACK_SEQUENCE

        scenes = motion_plan.get("scenes", [])
        topic = motion_plan.get("topic", "")
        is_math = motion_plan.get("is_math", False)
        code_info = motion_plan.get("code_assets", {})
        tech_info = motion_plan.get("technical_summary", {})

        # Find weak pairs mentioned in directive
        for i in range(len(scenes) - 1):
            a = scenes[i]
            b = scenes[i + 1]
            from_type = a.get("visual_type", "")
            to_type = b.get("visual_type", "")

            key = (from_type.lower(), to_type.lower())
            if key not in CARRY_COMPATIBILITY:
                # Nudge: convert weak type pair to a stronger one
                # e.g. 'diagram' → 'diagram' can be one too many diagrams;
                # change the second to 'code' for a stronger carry
                if from_type == to_type and from_type not in ("hook", "payoff"):
                    if from_type == "diagram":
                        scenes[i + 1]["visual_type"] = "code"
                    elif from_type == "code":
                        scenes[i + 1]["visual_type"] = "metaphor"
                    elif from_type == "metaphor":
                        scenes[i + 1]["visual_type"] = "diagram"

                    # Re-build elements for the updated visual type
                    beat = {
                        "beat": scenes[i + 1].get("beat_name", f"beat_{i+1}"),
                        "start": scenes[i + 1].get("start", 0),
                        "end": scenes[i + 1].get("end", 0),
                        "duration": scenes[i + 1].get("duration", 8),
                    }
                    math_spec = motion_plan.get("math_spec")
                    scenes[i + 1]["elements"] = self._build_scene_elements(
                        scenes[i + 1]["visual_type"],
                        beat,
                        topic,
                        tech_info,
                        code_info,
                        motion_plan.get("creative_direction", {}),
                        math_spec
                    )

        # Re-annotate continuity intent with repaired scene types
        scenes = self._annotate_continuity_intent(scenes, topic, is_math)
        motion_plan["scenes"] = scenes
        motion_plan["continuity_repair_attempt"] = attempt
        return motion_plan

    def _build_scene_elements(
        self,
        visual_type: str,
        beat: Dict[str, Any],
        topic: str,
        tech_info: Dict[str, Any],
        code_info: Dict[str, Any],
        creative_dir: Dict[str, Any],
        math_spec: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        hook = creative_dir.get("hook", {})
        if visual_type == "hook":
            headline = hook.get("headline") or hook.get("headline_template") or topic.upper()
            subtext = hook.get("subtext") or hook.get("subtext_template") or "Watch what happens in execution."
            badge = hook.get("badge") or topic.upper()
            return {
                "headline": headline,
                "subtext": subtext,
                "badge": badge,
                "animation_style": hook.get("animation_style", "split_reveal")
            }
        elif visual_type == "math_3d":
            ms = math_spec or self.nemotron.generate_math_3d_concept(topic)
            return {
                "title": ms.get("formula_title", "2D TO 3D MATHEMATICAL PROJECTION"),
                "formula_title": ms.get("formula_title", "2D TO 3D MATHEMATICAL PROJECTION"),
                "equation_latex": ms.get("equation_latex", "$z = f(x, y)$"),
                "formula_2d": ms.get("formula_2d", "$y = f(x)$"),
                "function_type": ms.get("function_type", "sinc"),
                "description": ms.get("description", "Flat 2D Cartesian cross-section extends into 3D isometric surface mesh."),
                "camera_motion": ms.get("camera_motion", "Locked 2D overhead pitch=0 transitioning smoothly to 55° isometric 3D orbit."),
                "color_gradient": ms.get("color_gradient", ["#00F0FF", "#8B5CF6", "#F59E0B"]),
                "visual_cues": ms.get("visual_cues", ["2D Cross Section", "Camera 3D Pitch", "Parametric Tensor Surface"])
            }
        elif visual_type == "metaphor":
            sim_type = tech_info.get("simulation_type")
            t = topic.lower()
            if not sim_type or sim_type in ("neural_core", "math_3d"):
                if any(k in t for k in ["oop", "object", "class", "inherit", "polymorph", "encapsulat", "heap", "instance"]):
                    sim_type = "heap_objects"
                elif any(k in t for k in ["api", "rest", "http", "network", "async", "await", "event loop", "stream", "queue"]):
                    sim_type = "data_pipeline"
                elif any(k in t for k in ["tree", "graph", "b-tree", "sql", "db", "database", "git", "ast"]):
                    sim_type = "tree_graph"
                elif any(k in t for k in ["binary search", "search", "sort", "array", "list", "pointer", "partition"]):
                    sim_type = "array_search"
                elif any(k in t for k in ["recur", "stack", "call stack", "memory"]):
                    sim_type = "stack_memory"
                elif any(k in t for k in ["loop", "for", "while", "iterator"]):
                    sim_type = "loop_turbine"
                elif any(k in t for k in ["if", "condition", "switch", "branch", "logic", "boolean"]):
                    sim_type = "decision_gate"
                else:
                    sim_type = "heap_objects" if "java" in t else "data_pipeline"

            return {
                "topic": topic,
                "metaphor_id": creative_dir.get("visual_metaphor", sim_type),
                "simulation_type": sim_type,
                "label": beat["beat"].upper(),
                "description": tech_info.get("core_mechanism", f"Deterministic execution model for {topic}."),
                "hardware_reality": tech_info.get("cpu_hardware_reality", "Direct instruction execution in CPU pipeline.")
            }
        elif visual_type == "code":
            raw_code = code_info.get("main_code", "")
            lines = raw_code.split("\n") if isinstance(raw_code, str) else raw_code
            
            # Formulate simulated live variable state & console output directly from code analysis
            output_msg = code_info.get("terminal_output")
            if not output_msg:
                t = topic.lower()
                if "if" in t:
                    output_msg = "> Condition evaluated: branch taken"
                elif "binary" in t or "search" in t:
                    output_msg = "> Element found at target index: 4"
                elif "loop" in t:
                    output_msg = "> Items processed: 100% [OK]"
                elif "recur" in t:
                    output_msg = "> Base case hit: return 1"
                elif any(k in t for k in ["oop", "class", "object"]):
                    output_msg = "> Instance created on heap: 0x7FA3 [OK]"
                elif "sql" in t or "db" in t:
                    output_msg = "> 1 row returned (0.12ms) [INDEX SEEK]"
                else:
                    output_msg = f"> {topic}: executed successfully [OK]"

            var_name = code_info.get("variable_name") or ("user" if "oop" in topic.lower() or "class" in topic.lower() else "state")
            var_val = code_info.get("variable_value") or ("User@0x7FA3" if "oop" in topic.lower() else "active")
            eval_res = code_info.get("eval_result") or ("INSTANTIATED" if "oop" in topic.lower() else "RESOLVED")

            return {
                "topic": topic,
                "filename": code_info.get("filename", "Main.java" if "java" in topic.lower() else "main.py"),
                "lines": lines,
                "highlight_line": code_info.get("highlight_line", 2),
                "annotation": code_info.get("annotation", "evaluates in 1 CPU cycle"),
                "output_text": output_msg,
                "variable_state": {
                    "var_name": var_name,
                    "var_value": var_val,
                    "eval_result": eval_res
                }
            }
        elif visual_type == "diagram":
            diag_title = tech_info.get("diagram_title") or f"{topic.upper()} ARCHITECTURE"
            diag_sub = tech_info.get("diagram_subtitle") or tech_info.get("cpu_hardware_reality", "Direct execution in hardware memory registers")
            m_label = tech_info.get("diagram_metric_label") or "TIME COMPLEXITY"
            m_val = tech_info.get("diagram_metric_val") or tech_info.get("time_complexity", "O(1) Constant Time")

            return {
                "topic": topic,
                "title": diag_title,
                "subtitle": diag_sub,
                "steps": tech_info.get("how_it_works_steps", [
                    "Fetch instruction or memory pointer into execution context",
                    "Evaluate core operational logic and data boundaries",
                    "Commit state transition with zero excess overhead"
                ]),
                "time_complexity": tech_info.get("time_complexity", "O(1) Constant Time"),
                "space_complexity": tech_info.get("space_complexity", "O(1) Auxiliary"),
                "metric_label": m_label,
                "metric_val": m_val,
                "pro_tip": tech_info.get("pro_tip", "Mastering low-level execution invariants unlocks 10x engineering performance.")
            }
        elif visual_type == "split" or visual_type == "benchmark":
            return {
                "left_label": "Without",
                "left_code": code_info.get("inefficient_before", "").split("\n"),
                "right_label": "With",
                "right_code": code_info.get("optimized_after", "").split("\n"),
                "stat_callout": tech_info.get("time_complexity", "O(log N)")
            }
        elif visual_type == "payoff" or beat["beat"].lower() in ("payoff", "conclusion", "ending", "loop"):
            closing_dna = creative_dir.get("closing_dna") or {}
            c_strat = closing_dna.get("strategy_id", "kinetic_statement")
            c_layout = closing_dna.get("layout", "kinetic_words")
            c_headline = closing_dna.get("headline") or tech_info.get("accurate_reality") or f"{topic.upper()} RESOLVED"
            c_sub = closing_dna.get("secondary_text") or tech_info.get("core_mechanism") or "Deterministic hardware execution"
            c_stat = closing_dna.get("stat_callout") or tech_info.get("time_complexity", "O(1)")
            c_ref = closing_dna.get("callback_ref") or creative_dir.get("hook", {}).get("headline") or topic
            c_action = closing_dna.get("action_label") or "TEST THIS NOW"

            return {
                "title": beat["beat"].replace("_", " ").upper(),
                "closing_strategy": c_strat,
                "strategy_id": c_strat,
                "strategy_name": closing_dna.get("strategy_name", "Resolution"),
                "layout": c_layout,
                "camera_motion": closing_dna.get("camera_motion", "punch_z_forward"),
                "typography_style": closing_dna.get("typography_style", "massive_stacked"),
                "visual_accent": closing_dna.get("visual_accent", "clean_glow"),
                "headline": c_headline,
                "secondary_text": c_sub,
                "stat": c_stat,
                "stat_callout": c_stat,
                "subtitle": c_sub,
                "callback_ref": c_ref,
                "action_label": c_action,
                "pro_tip": tech_info.get("pro_tip", "Mastering low-level execution invariants unlocks 10x engineering performance.")
            }
        else:
            return {
                "title": beat["beat"].replace("_", " ").upper(),
                "stat": tech_info.get("time_complexity", "O(1)"),
                "subtitle": tech_info.get("accurate_reality", "Deterministic hardware execution"),
                "pro_tip": tech_info.get("pro_tip", "Mastering low-level execution invariants unlocks 10x engineering performance.")
            }
