"""
engine/schema_validation.py
===========================
Pydantic validation schemas for Prompt Reel.
Validates the complete structured creative plan: StoryDNA, VisualDNA,
per-scene composition variants, camera trajectories, transitions, and motion plans.
Ensures zero runtime guessing by the renderer.
"""
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field, ConfigDict, field_validator


class StoryDNAModel(BaseModel):
    narrative_structure: str = Field(..., description="ID of narrative structure, e.g. structure_b")
    structure_name: str = Field(default="Narrative Blueprint")
    topic_category: str = Field(..., description="Semantic category e.g. algorithms_data_structures")
    intent: str = Field(..., description="Primary narrative intent e.g. reverse_engineer")
    complexity: str = Field(default="intermediate")
    emotional_tone: str = Field(default="curious")
    hook_type: str = Field(default="question")
    information_density: str = Field(default="balanced")
    pacing: str = Field(default="measured")
    reveal_timing: str = Field(default="mid")
    payoff_type: str = Field(default="invariant_rule")
    scene_count: int = Field(ge=3, le=20, default=5)
    target_duration: float = Field(ge=5.0, le=180.0, default=50.0)
    emotional_progression: List[str] = Field(default_factory=lambda: ["curiosity", "tension", "insight", "mastery"])
    modalities: Dict[str, bool] = Field(default_factory=dict)


class VisualDNAModel(BaseModel):
    visual_strategy: str = Field(..., description="ID of visual strategy e.g. technical_blueprint")
    strategy_name: str = Field(default="Visual Strategy")
    composition_system: str = Field(default="modular_grid")
    typography: Dict[str, Any] = Field(default_factory=dict)
    color_system: Dict[str, Any] = Field(default_factory=dict)
    spacing_system: str = Field(default="balanced")
    camera_language: str = Field(default="slow_push")
    transition_language: str = Field(default="slide")
    motion_language: str = Field(default="precision_linear")
    scene_vocabulary: List[str] = Field(default_factory=list)
    texture: str = Field(default="clean_vector")
    lighting: str = Field(default="ambient_studio")


class ScenePlanModel(BaseModel):
    id: str = Field(...)
    beat_name: Optional[str] = None
    start: float = Field(ge=0.0)
    end: float = Field(ge=0.0)
    duration: float = Field(gt=0.0)
    visual_type: str = Field(..., description="hook, code, diagram, metaphor, benchmark, split, payoff, math_3d")
    composition_variant: Optional[str] = Field(default=None, description="Dynamic composition layout variant")
    voice_text: Optional[str] = None
    narration: Optional[str] = None
    voice_rate: Optional[str] = Field(default="+15%")
    elements: Dict[str, Any] = Field(default_factory=dict)
    visual_recipe: Optional[Dict[str, Any]] = None
    camera: Optional[Dict[str, Any]] = None
    transition: Optional[Dict[str, Any]] = None

    @field_validator("end")
    @classmethod
    def check_end_after_start(cls, v, info):
        start = info.data.get("start", 0.0)
        if v < start:
            raise ValueError(f"Scene end ({v}) cannot be before start ({start})")
        return v


class CreativePlanModel(BaseModel):
    story_dna: StoryDNAModel
    visual_dna: VisualDNAModel
    topic: str
    duration: float = Field(ge=5.0, le=180.0)
    scenes: List[ScenePlanModel]
    audio_dna: Optional[Dict[str, Any]] = None
    closing_dna: Optional[Dict[str, Any]] = None


class MotionPlanModel(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    version: str = Field(default="3.0")
    topic: str
    duration: float = Field(ge=5.0, le=180.0)
    fps: int = Field(default=30)
    total_frames: int = Field(default=1500)
    creative_direction: Dict[str, Any] = Field(...)
    scenes: List[ScenePlanModel]
    story_dna: Optional[StoryDNAModel] = None
    visual_dna: Optional[VisualDNAModel] = None
    technical_summary: Optional[Dict[str, Any]] = None
    code_assets: Optional[Dict[str, Any]] = None
    audio_events: Optional[List[Any]] = None
    continuity_bridges: Optional[List[Dict[str, Any]]] = None


def validate_creative_plan(data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Validates structured creative plan against strict Pydantic model."""
    try:
        model = CreativePlanModel.model_validate(data)
        return True, {
            "status": "valid",
            "narrative_structure": model.story_dna.narrative_structure,
            "visual_strategy": model.visual_dna.visual_strategy,
            "scene_count": len(model.scenes)
        }
    except Exception as e:
        return False, {"status": "invalid", "error": str(e)}


def validate_motion_plan(data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Validates complete motion plan before rendering."""
    import dataclasses
    clean_data = dict(data)
    if "audio_events" in clean_data and clean_data["audio_events"]:
        clean_data["audio_events"] = [
            e.to_dict() if hasattr(e, "to_dict") else (dataclasses.asdict(e) if dataclasses.is_dataclass(e) else dict(e) if isinstance(e, dict) else {"description": str(e)})
            for e in clean_data["audio_events"]
        ]
    try:
        model = MotionPlanModel.model_validate(clean_data)
        return True, {
            "status": "valid",
            "topic": model.topic,
            "duration": model.duration,
            "scene_count": len(model.scenes),
            "version": model.version
        }
    except Exception as e:
        return False, {"status": "invalid", "error": str(e)}
