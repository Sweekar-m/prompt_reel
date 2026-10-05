"""
server/services/reel_service.py
===============================
Orchestrates the 10-step AI-Native Reel Studio creation pipeline:
1. Research
2. Fact Check
3. Technical Explanation
4. Visual Metaphor
5. Creative Direction (Video DNA)
6. Storyboard Assembly (Motion Plan)
7. Voice Synthesis
8. Procedural Audio / SFX
9. Deterministic Render Engine
10. Quality Control & Final MP4

Stores every project in `projects/{reel_id}`.
"""
import os
import re
import json
import uuid
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

from agents.research_agent import ResearchAgent
from agents.content_agent import ContentAgent
from agents.fact_checker import FactCheckerAgent
from agents.creative_director import CreativeDirectorAgent
from agents.script_storyboard_agent import ScriptStoryboardAgent
from agents.quality_agent import QualityControlAgent
from engine.dna_registry import DNARegistry

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
STYLES_DIR = os.path.join(BASE_DIR, "styles")
os.makedirs(PROJECTS_DIR, exist_ok=True)


class ReelService:
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.content_agent = ContentAgent()
        self.fact_checker = FactCheckerAgent()
        self.dna_registry = DNARegistry(os.path.join(BASE_DIR, "dna_history.json"))
        self.creative_director = CreativeDirectorAgent(dna_registry=self.dna_registry)
        self.storyboard_agent = ScriptStoryboardAgent()
        self.quality_agent = QualityControlAgent()
        # Active background rendering tasks and listeners
        self.active_listeners: Dict[str, List[asyncio.Queue]] = {}
        self.active_status: Dict[str, Dict[str, Any]] = {}

    def get_styles(self) -> List[Dict[str, Any]]:
        """Returns all 15 creative style specifications."""
        styles = []
        if os.path.exists(STYLES_DIR):
            for fname in sorted(os.listdir(STYLES_DIR)):
                if fname.endswith(".json"):
                    fpath = os.path.join(STYLES_DIR, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            styles.append(data)
                    except Exception:
                        pass
        return styles

    def get_style(self, style_id: str) -> Optional[Dict[str, Any]]:
        fpath = os.path.join(STYLES_DIR, f"{style_id}.json")
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def list_projects(self) -> List[Dict[str, Any]]:
        projects = []
        for pid in os.listdir(PROJECTS_DIR):
            pdir = os.path.join(PROJECTS_DIR, pid)
            pfile = os.path.join(pdir, "project.json")
            if os.path.isdir(pdir) and os.path.exists(pfile):
                try:
                    with open(pfile, "r", encoding="utf-8") as f:
                        projects.append(json.load(f))
                except Exception:
                    pass
        projects.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return projects

    def get_project(self, reel_id: str) -> Optional[Dict[str, Any]]:
        pfile = os.path.join(PROJECTS_DIR, reel_id, "project.json")
        if os.path.exists(pfile):
            with open(pfile, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def create_project(self, topic: str, style: Optional[str] = None, duration: float = 50.0) -> Dict[str, Any]:
        reel_id = str(uuid.uuid4())[:8]
        pdir = os.path.join(PROJECTS_DIR, reel_id)
        os.makedirs(pdir, exist_ok=True)

        now = datetime.now().isoformat()
        project = {
            "id": reel_id,
            "topic": topic,
            "requested_style": style or "cinematic",
            "duration": duration,
            "status": "draft",
            "step": 0,
            "step_title": "Project Initialized",
            "progress_pct": 0,
            "created_at": now,
            "updated_at": now,
            "creative_dna": None,
            "motion_plan": None,
            "quality_report": None,
            "has_video": False,
            "video_path": None
        }
        self.save_project(project)
        return project

    def create_project_from_spec(self, video_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a project directly from AI Director chat blueprint with custom hook and math spec."""
        topic = video_spec.get("topic") or "2D to 3D Math Equation Reel"
        style = video_spec.get("style") or "cinematic"
        duration = float(video_spec.get("duration", 50.0))

        project = self.create_project(topic=topic, style=style, duration=duration)

        if "viral_hook" in video_spec and video_spec["viral_hook"]:
            project["custom_hook"] = video_spec["viral_hook"]

        if "math_spec" in video_spec and video_spec["math_spec"]:
            project["custom_math_spec"] = video_spec["math_spec"]
            project["is_math"] = True
        elif video_spec.get("is_math"):
            project["is_math"] = True

        if "bgm_style" in video_spec and video_spec["bgm_style"]:
            project["bgm_style"] = video_spec["bgm_style"]

        self.save_project(project)
        return project

    def chat_director(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        current_reel_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Provides interactive AI Creative Director advice, viral hooks, and video blueprints."""
        current_state = None
        if current_reel_id:
            current_state = self.get_project(current_reel_id)

        return self.creative_director.nemotron.chat_director(
            message=message,
            history=history,
            current_state=current_state
        )

    def save_project(self, project: Dict[str, Any]):
        reel_id = project["id"]
        pdir = os.path.join(PROJECTS_DIR, reel_id)
        os.makedirs(pdir, exist_ok=True)
        pfile = os.path.join(pdir, "project.json")
        project["updated_at"] = datetime.now().isoformat()
        with open(pfile, "w", encoding="utf-8") as f:
            json.dump(project, f, indent=2)

    def subscribe_progress(self, reel_id: str) -> asyncio.Queue:
        q = asyncio.Queue()
        if reel_id not in self.active_listeners:
            self.active_listeners[reel_id] = []
        self.active_listeners[reel_id].append(q)
        return q

    async def broadcast_progress(self, reel_id: str, step: int, title: str, pct: int, payload: Optional[Dict[str, Any]] = None):
        msg = {
            "reel_id": reel_id,
            "step": step,
            "step_title": title,
            "progress_pct": pct,
            "timestamp": time.time(),
            "payload": payload or {}
        }
        self.active_status[reel_id] = msg
        if reel_id in self.active_listeners:
            for q in self.active_listeners[reel_id]:
                await q.put(msg)

    async def run_full_pipeline(self, reel_id: str, fast_mode: bool = True):
        project = self.get_project(reel_id)
        if not project:
            return

        topic = project["topic"]
        style_req = project.get("requested_style", "cinematic")
        dur = float(project.get("duration", 50.0))
        pdir = os.path.join(PROJECTS_DIR, reel_id)

        project["status"] = "processing"
        project["error"] = None
        self.save_project(project)

        try:
            # ── STEP 1: Research ─────────────────────────────────────────────
            await self.broadcast_progress(reel_id, 1, "Researching topic trends & curiosity signals...", 10)
            loop = asyncio.get_event_loop()
            research = await loop.run_in_executor(None, self.research_agent.research_topic, topic)
            project["research"] = research

            # ── STEP 2: Fact Checking ────────────────────────────────────────
            await self.broadcast_progress(reel_id, 2, "Verifying technical accuracy & computational bounds...", 20)
            claims = [
                f"{topic} runtime complexity and memory behavior",
                f"Core invariants and execution order of {topic}"
            ]
            fact_report = await loop.run_in_executor(None, self.fact_checker.audit_claims, topic, claims)
            project["fact_check"] = fact_report

            # ── STEP 3: Technical Explanation & Metaphor ────────────────────
            await self.broadcast_progress(reel_id, 3, "Formulating precise mental model & visual metaphor...", 30)
            expl = await loop.run_in_executor(None, self.content_agent.generate_explanation, topic)
            metaphor = await loop.run_in_executor(None, self.content_agent.suggest_visual_metaphor, topic)
            project["explanation"] = expl
            project["metaphor"] = metaphor

            # ── STEP 4: Creative Direction (Video DNA) ───────────────────────
            await self.broadcast_progress(reel_id, 4, "Directing visual style, palette & typography...", 42)
            cd = await loop.run_in_executor(
                None,
                lambda: self.creative_director.direct_video(topic, requested_style=style_req, duration_sec=dur)
            )

            # Apply user overrides from AI Director chat if present
            if project.get("custom_hook"):
                for k, v in project["custom_hook"].items():
                    cd.setdefault("hook", {})[k] = v
            if project.get("custom_math_spec"):
                cd["math_spec"] = project["custom_math_spec"]
                cd["is_math"] = True
                cd["visual_metaphor"] = "math_3d"

            project["creative_direction"] = cd
            project["creative_dna"] = cd.get("dna", {})

            # ── STEP 5: Storyboard Assembly (Motion Plan) ────────────────────
            await self.broadcast_progress(reel_id, 5, "Compiling narrative storyboard & timing plan...", 55)
            motion_plan = await loop.run_in_executor(
                None,
                lambda: self.storyboard_agent.generate_motion_plan(topic, cd, dur)
            )
            project["motion_plan"] = motion_plan

            # ── STEP 6: Quality Control Pre-flight ───────────────────────────
            await self.broadcast_progress(reel_id, 6, "Running design hierarchy & WCAG contrast audit...", 65)
            qc_report = await loop.run_in_executor(
                None,
                lambda: self.quality_agent.audit_motion_plan(motion_plan)
            )
            project["quality_report"] = qc_report

            # ── STEP 7: Voiceover & Audio Synthesis ─────────────────────────
            await self.broadcast_progress(reel_id, 7, "Synthesizing synchronized neural voice & procedural music...", 75)
            from audio_pipeline import generate_voiceover_and_soundtrack

            scenes_cfg = []
            for sc in motion_plan["scenes"]:
                v_text = sc.get("narration") or sc.get("voice_text") or ""
                # Strip any accidental dict string formatting
                clean_v = str(v_text).strip()
                m_sub = re.search(r"['\"](?:text|narration)['\"]\s*:\s*['\"](.*?)['\"]\}?$", clean_v, re.DOTALL)
                if m_sub:
                    clean_v = m_sub.group(1).strip()
                clean_v = clean_v.replace("{'text':", "").replace('{"text":', "").strip(" '\"{}:")
                if not clean_v:
                    clean_v = f"Notice the structure of {sc.get('id', 'this section')}."

                scenes_cfg.append({
                    "id": sc["id"],
                    "text": clean_v,
                    "start_time": sc["start"],
                    "rate": sc.get("voice_rate", "+15%")
                })

            voice_cfg = cd.get("voice_profile") or cd.get("voice", {})
            if isinstance(voice_cfg, str):
                voice_name = voice_cfg
                pitch = "+0Hz"
            else:
                voice_name = voice_cfg.get("edge_voice") or voice_cfg.get("voice", "en-US-ChristopherNeural")
                pitch = voice_cfg.get("pitch", "+0Hz")

            # Dynamic BGM style & progression extraction
            from effects.sound_profiles import get_music_profile
            sound_obj = cd.get("sound") if isinstance(cd.get("sound"), dict) else {}
            bgm_override = project.get("bgm_style") or project.get("custom_sound")
            raw_style = bgm_override or sound_obj.get("id") or cd.get("sound_profile") or cd.get("dna", {}).get("sound_profile", "cyberpunk")
            prof = get_music_profile(str(raw_style), is_math=cd.get("is_math", False))

            sound_style = prof.id
            bpm = float(sound_obj.get("bpm") or prof.bpm)
            chord_prog = sound_obj.get("chord_progression") or prof.chord_progression

            audio_res = await loop.run_in_executor(
                None,
                lambda: generate_voiceover_and_soundtrack(
                    scenes=scenes_cfg,
                    output_dir=pdir,
                    voice=voice_name,
                    bpm=bpm,
                    total_duration=dur,
                    style=sound_style,
                    chord_progression=chord_prog,
                    pitch=pitch
                )
            )
            project["audio_meta"] = {
                "wav": audio_res.get("wav_path"),
                "mp3": audio_res.get("mp3_path"),
                "total_duration": audio_res.get("total_duration")
            }

            # ── STEP 8: Video Rendering (Remotion with Pillow Fallback) ───────
            raw_video_path = os.path.join(pdir, "raw_video.mp4")
            remotion_success = False

            try:
                from renderer.remotion_renderer import is_remotion_available, render_remotion_video

                if is_remotion_available():
                    await self.broadcast_progress(reel_id, 8, "Rendering motion graphics with Remotion engine...", 85)

                    def remotion_cb(pct: int, msg: str):
                        try:
                            asyncio.run_coroutine_threadsafe(
                                self.broadcast_progress(reel_id, 8, msg, pct),
                                loop
                            )
                        except Exception:
                            pass

                    remotion_success = await loop.run_in_executor(
                        None,
                        lambda: render_remotion_video(
                            motion_plan,
                            raw_video_path,
                            fast_mode=fast_mode,
                            progress_callback=remotion_cb
                        )
                    )
            except Exception as rem_err:
                print(f"[ReelService] Remotion render attempt encountered error: {rem_err}", flush=True)
                remotion_success = False

            # Fallback to deterministic Pillow/OpenCV renderer if Remotion unavailable or failed
            if not remotion_success:
                await self.broadcast_progress(reel_id, 8, "Rendering motion graphics with fallback Pillow/OpenCV engine...", 85)
                from renderer.deterministic_renderer import render_motion_plan_frame
                import cv2
                import numpy as np

                fps = 30
                total_frames = int(dur * fps)
                canvas_size = (540, 960) if fast_mode else (1080, 1920)

                # Render in batches to report progress
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                writer = cv2.VideoWriter(raw_video_path, fourcc, fps, canvas_size)

                for fi in range(total_frames):
                    t = fi / float(fps)
                    frame_img = render_motion_plan_frame(motion_plan, t, fi, canvas_size=canvas_size)
                    # PIL RGB to OpenCV BGR
                    frame_cv = cv2.cvtColor(np.array(frame_img), cv2.COLOR_RGB2BGR)
                    writer.write(frame_cv)

                    if fi % 150 == 0:
                        pct = 85 + int((fi / total_frames) * 10)
                        await self.broadcast_progress(reel_id, 8, f"Rendering frame {fi}/{total_frames} ({pct}%)...", pct)
                        await asyncio.sleep(0.01)

                writer.release()

            # ── STEP 9: Final Assembly with FFmpeg ────────────────────────────
            await self.broadcast_progress(reel_id, 9, "Muxing audio & encoding mobile-optimized MP4...", 96)
            import subprocess
            final_mp4_path = os.path.join(pdir, "reel_final.mp4")
            audio_track = audio_res.get("wav_path") or audio_res.get("mp3_path") if isinstance(audio_res, dict) else None

            v_codec = ["-c:v", "copy"] if remotion_success else ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "20"]

            if audio_track and os.path.exists(audio_track):
                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-i", raw_video_path,
                    "-i", audio_track,
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    *v_codec,
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-shortest",
                    final_mp4_path
                ]
            else:
                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-i", raw_video_path,
                    *v_codec,
                    final_mp4_path
                ]

            await loop.run_in_executor(None, lambda: subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))

            # ── STEP 10: Complete & Persistence ───────────────────────────────
            # Save dedicated motion_plan.json and script.json in project dir
            with open(os.path.join(pdir, "motion_plan.json"), "w", encoding="utf-8") as mp_f:
                json.dump(motion_plan, mp_f, indent=2, ensure_ascii=False)

            script_data = {
                "topic": topic,
                "duration": dur,
                "scenes": [
                    {
                        "id": sc.get("id"),
                        "beat": sc.get("beat_name"),
                        "narration": sc.get("narration") or sc.get("voice_text"),
                        "start": sc.get("start"),
                        "duration": sc.get("duration")
                    }
                    for sc in motion_plan.get("scenes", [])
                ]
            }
            with open(os.path.join(pdir, "script.json"), "w", encoding="utf-8") as sc_f:
                json.dump(script_data, sc_f, indent=2, ensure_ascii=False)

            project["has_video"] = True
            project["video_path"] = final_mp4_path
            project["status"] = "completed"
            project["step"] = 10
            project["progress_pct"] = 100
            project["step_title"] = "Final Video Complete"
            self.save_project(project)

            # Store in DNA registry
            if project.get("creative_dna"):
                try:
                    self.dna_registry.register_video(project["creative_dna"])
                except Exception as dna_err:
                    print(f"[ReelService] DNA registration note: {dna_err}")

            await self.broadcast_progress(reel_id, 10, "Final Video Complete & Ready!", 100, {"video_url": f"/api/reels/{reel_id}/video"})

        except Exception as e:
            project["status"] = "error"
            project["error"] = str(e)
            self.save_project(project)
            await self.broadcast_progress(reel_id, -1, f"Render Error: {str(e)}", 0)
            raise e
