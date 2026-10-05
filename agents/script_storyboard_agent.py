"""
agents/script_storyboard_agent.py
=================================
Script and Storyboard Agent.
Synthesizes the Topic, Technical Facts, and Creative Direction into
a comprehensive, deterministic Motion Plan containing scene-by-scene timing,
voiceover scripts, typography lockups, code tokens, and metaphor parameters.
"""
from typing import Dict, Any, List
from ai.nemotron_client import NemotronClient


class ScriptStoryboardAgent:
    def __init__(self, nemotron_client: NemotronClient = None):
        self.nemotron = nemotron_client or NemotronClient()

    def generate_motion_plan(
        self,
        topic: str,
        creative_dir: Dict[str, Any],
        total_duration: float = 50.0
    ) -> Dict[str, Any]:
        """
        Produces a complete Motion Plan JSON ready for deterministic rendering.
        """
        # Step 1: Query technical explanation and code snippets
        tech_info = self.nemotron.explain_technical_concept(topic)
        code_info = self.nemotron.generate_code_snippets(topic)

        # Step 2: Extract timeline from creative direction's story structure
        timeline_beats = creative_dir["story_structure"]["timeline"]

        # Step 3: Generate engaging, topic-tailored conversational narration
        generated_scripts = self.nemotron.generate_script(topic, timeline_beats, tech_info, code_info)
        voice_profile = creative_dir["voice"]
        voice_rate = voice_profile.get("rate", "+20%")

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

        motion_plan = {
            "version": "2.0",
            "topic": topic,
            "duration": total_duration,
            "fps": 30,
            "total_frames": int(total_duration * 30),
            "creative_direction": creative_dir,
            "technical_summary": tech_info,
            "code_assets": code_info,
            "is_math": is_math,
            "math_spec": math_spec,
            "scenes": scenes
        }

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
        else:
            return {
                "title": beat["beat"].replace("_", " ").upper(),
                "stat": tech_info.get("time_complexity", "O(1)"),
                "subtitle": tech_info.get("accurate_reality", "Deterministic hardware execution"),
                "pro_tip": tech_info.get("pro_tip", "Mastering low-level execution invariants unlocks 10x engineering performance.")
            }
