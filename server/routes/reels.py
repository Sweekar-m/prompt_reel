"""
server/routes/reels.py
======================
API endpoints for Reel project management, storyboard curation,
scene regeneration, deterministic rendering, and video streaming.
"""
import os
import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks, Body
from fastapi.responses import FileResponse, StreamingResponse
from typing import Dict, Any, List, Optional
import json

from server.services.reel_service import ReelService, PROJECTS_DIR

router = APIRouter(prefix="/api/reels", tags=["reels"])
service = ReelService()


@router.get("")
async def list_reels():
    """Lists all stored Reel projects and their metadata."""
    projects = service.list_projects()
    return {
        "status": "success",
        "count": len(projects),
        "reels": projects
    }


@router.post("")
async def create_reel(payload: Dict[str, Any] = Body(...)):
    """Creates a new Reel project draft."""
    topic = payload.get("topic", "How recursion works")
    style = payload.get("style", "cinematic")
    duration = float(payload.get("duration", 50.0))
    bgm_style = payload.get("bgm_style")

    project = service.create_project(topic=topic, style=style, duration=duration)
    if bgm_style:
        project["bgm_style"] = bgm_style
        service.save_project(project)
    return {
        "status": "success",
        "reel": project
    }


@router.post("/chat")
async def chat_director(payload: Dict[str, Any] = Body(...)):
    """Conversational endpoint for the AI Creative Director."""
    message = payload.get("message", "")
    history = payload.get("history", [])
    current_reel_id = payload.get("current_reel_id")

    res = service.chat_director(message, history=history, current_reel_id=current_reel_id)
    return {
        "status": "success",
        **res
    }


@router.post("/create-from-spec")
async def create_from_spec(background_tasks: BackgroundTasks, payload: Dict[str, Any] = Body(...)):
    """Creates a project directly from AI Director's chat blueprint."""
    video_spec = payload.get("video_spec") or payload
    auto_render = payload.get("auto_render", False)

    project = service.create_project_from_spec(video_spec)
    reel_id = project["id"]

    # Pre-generate creative direction and storyboard
    cd = service.creative_director.direct_video(
        project["topic"],
        requested_style=project.get("requested_style", "cinematic"),
        duration_sec=float(project.get("duration", 50.0)),
        custom_hook=project.get("custom_hook"),
        custom_math_spec=project.get("custom_math_spec")
    )

    motion_plan = service.storyboard_agent.generate_motion_plan(
        project["topic"],
        cd,
        float(project.get("duration", 50.0))
    )
    qc = service.quality_agent.audit_motion_plan(motion_plan)

    project["creative_direction"] = cd
    project["creative_dna"] = cd.get("dna", {})
    project["motion_plan"] = motion_plan
    project["quality_report"] = qc
    project["step"] = 5
    project["step_title"] = "Storyboard Ready"
    service.save_project(project)

    if auto_render:
        background_tasks.add_task(service.run_full_pipeline, reel_id, fast_mode=True)

    return {
        "status": "success",
        "reel": project
    }


@router.get("/{reel_id}")
async def get_reel(reel_id: str):
    """Retrieves full details for a specific reel project."""
    project = service.get_project(reel_id)
    if not project:
        raise HTTPException(status_code=404, detail="Reel not found")

    # Overlay live memory progress if pipeline is currently executing
    if reel_id in service.active_status:
        st = service.active_status[reel_id]
        if st.get("step") is not None:
            project["step"] = st["step"]
        if st.get("step_title"):
            project["step_title"] = st["step_title"]
        if st.get("progress_pct") is not None:
            project["progress_pct"] = st["progress_pct"]

    return {
        "status": "success",
        "reel": project
    }


@router.post("/{reel_id}/research")
async def trigger_research(reel_id: str):
    """Executes topic research and trend signals for this reel."""
    project = service.get_project(reel_id)
    if not project:
        raise HTTPException(status_code=404, detail="Reel not found")

    research = service.research_agent.research_topic(project["topic"])
    project["research"] = research
    service.save_project(project)
    return {"status": "success", "research": research}


@router.post("/{reel_id}/storyboard")
async def trigger_storyboard(reel_id: str, payload: Dict[str, Any] = Body(default={})):
    """Generates Creative Direction and Motion Plan storyboard."""
    project = service.get_project(reel_id)
    if not project:
        raise HTTPException(status_code=404, detail="Reel not found")

    topic = project["topic"]
    style = payload.get("style") or project.get("requested_style", "cinematic")
    dur = float(project.get("duration", 50.0))

    cd = service.creative_director.direct_video(topic, requested_style=style, duration_sec=dur)
    motion_plan = service.storyboard_agent.generate_motion_plan(topic, cd, dur)
    qc_report = service.quality_agent.audit_motion_plan(motion_plan)

    project["creative_direction"] = cd
    project["creative_dna"] = cd.get("dna", {})
    project["motion_plan"] = motion_plan
    project["quality_report"] = qc_report
    project["step"] = 5
    project["step_title"] = "Storyboard Ready"
    service.save_project(project)

    return {
        "status": "success",
        "creative_direction": cd,
        "motion_plan": motion_plan,
        "quality_report": qc_report
    }


@router.post("/{reel_id}/render")
async def trigger_render(reel_id: str, background_tasks: BackgroundTasks, payload: Dict[str, Any] = Body(default={})):
    """Dispatches the full async render pipeline in the background."""
    project = service.get_project(reel_id)
    if not project:
        raise HTTPException(status_code=404, detail="Reel not found")

    fast_mode = payload.get("fast", True)
    background_tasks.add_task(service.run_full_pipeline, reel_id, fast_mode=fast_mode)

    return {
        "status": "started",
        "reel_id": reel_id,
        "message": "Render pipeline launched in background."
    }


@router.post("/{reel_id}/regenerate-scene")
async def regenerate_scene(reel_id: str, payload: Dict[str, Any] = Body(...)):
    """Regenerates a specific scene in the storyboard without rebuilding everything."""
    project = service.get_project(reel_id)
    if not project or not project.get("motion_plan"):
        raise HTTPException(status_code=404, detail="Reel or Motion Plan not found")

    scene_index = payload.get("scene_index", 0)
    scenes = project["motion_plan"].get("scenes", [])
    if scene_index < 0 or scene_index >= len(scenes):
        raise HTTPException(status_code=400, detail="Invalid scene index")

    target_scene = scenes[scene_index]
    scene_id = target_scene.get("id", f"scene_{scene_index}")

    # Regenerate content for target scene
    if "narration" in payload:
        target_scene["narration"] = payload["narration"]
    else:
        target_scene["narration"] = f"Updated perspective on {project['topic']}: Key insight for production systems."

    if "headline" in payload and "elements" in target_scene:
        target_scene["elements"]["headline"] = payload["headline"]

    service.save_project(project)
    return {
        "status": "success",
        "scene_index": scene_index,
        "updated_scene": target_scene
    }


@router.get("/{reel_id}/status")
async def get_status(reel_id: str):
    """Returns the current step and completion percentage."""
    if reel_id in service.active_status:
        return service.active_status[reel_id]

    project = service.get_project(reel_id)
    if not project:
        raise HTTPException(status_code=404, detail="Reel not found")

    return {
        "reel_id": reel_id,
        "step": project.get("step", 0),
        "step_title": project.get("step_title", "Draft"),
        "progress_pct": project.get("progress_pct", 0),
        "status": project.get("status", "draft")
    }


@router.get("/{reel_id}/video")
async def get_video(reel_id: str):
    """Streams the rendered MP4 video file for playback or download."""
    project = service.get_project(reel_id)
    if not project:
        raise HTTPException(status_code=404, detail="Reel not found")

    vpath = project.get("video_path")
    if not vpath or not os.path.exists(vpath):
        raise HTTPException(status_code=404, detail="Video has not been rendered yet")

    return FileResponse(vpath, media_type="video/mp4", filename=f"reel_{reel_id}.mp4")


@router.get("/{reel_id}/audio")
async def get_audio(reel_id: str):
    """Streams the master synchronized voiceover and soundtrack."""
    project = service.get_project(reel_id)
    if not project:
        raise HTTPException(status_code=404, detail="Reel not found")

    pdir = os.path.join(PROJECTS_DIR, reel_id)
    mp3_path = os.path.join(pdir, "master_audio.mp3")
    wav_path = os.path.join(pdir, "master_audio_48k.wav")

    if os.path.exists(mp3_path):
        return FileResponse(mp3_path, media_type="audio/mpeg", filename=f"audio_{reel_id}.mp3")
    elif os.path.exists(wav_path):
        return FileResponse(wav_path, media_type="audio/wav", filename=f"audio_{reel_id}.wav")
    else:
        raise HTTPException(status_code=404, detail="Audio soundtrack not generated yet")


@router.get("/{reel_id}/events")
async def stream_render_events(reel_id: str):
    """Server-Sent Events (SSE) endpoint for real-time progress updates."""
    queue = asyncio.Queue()
    if reel_id not in service.active_listeners:
        service.active_listeners[reel_id] = []
    service.active_listeners[reel_id].append(queue)

    async def event_generator():
        try:
            # Send initial current status if available
            if reel_id in service.active_status:
                yield f"data: {json.dumps(service.active_status[reel_id])}\n\n"

            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data)}\n\n"
                if data.get("progress_pct") >= 100 or data.get("step") == -1:
                    break
        finally:
            if reel_id in service.active_listeners and queue in service.active_listeners[reel_id]:
                service.active_listeners[reel_id].remove(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
