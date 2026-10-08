export interface RGBColor {
  r: number;
  g: number;
  b: number;
}

export type ColorValue = [number, number, number] | string;

export interface PaletteSchema {
  id?: string;
  name?: string;
  background: ColorValue;
  primary: ColorValue;
  secondary: ColorValue;
  accent: ColorValue;
  surface: ColorValue;
  text: ColorValue;
  subtext: ColorValue;
}

export interface TypographySchema {
  id?: string;
  heading?: string;
  body?: string;
  mono?: string;
}

export interface AudioEventSchema {
  time: number;
  type: string;
  source_scene?: string;
  weight?: number;
}

export interface AudioDNASchema {
  genre: string;
  mood: string;
  energy: string;
  bpm: number;
  rhythm: string;
  percussion_style?: string;
  bass_style?: string;
  harmonic_style?: string;
  chord_progression: string[];
  instrument_palette?: string[];
  texture?: string;
  intro_style?: string;
  build_style?: string;
  drop_style?: string;
  outro_style?: string;
  variation_seed?: number;
}

export interface ClosingDNASchema {
  strategy_id: string;
  strategy_name?: string;
  description?: string;
  layout?: string;
  camera_motion?: string;
  typography_style?: string;
  visual_accent?: string;
  headline?: string;
  secondary_text?: string;
  stat_callout?: string;
  callback_ref?: string;
  action_label?: string;
  variation_seed?: number;
}

export interface VisualDNASchema {
  visual_strategy: string;
  strategy_name?: string;
  composition_system?: string;
  typography?: Record<string, any>;
  color_system?: Record<string, any>;
  spacing_system?: string;
  camera_language?: string;
  transition_language?: string;
  motion_language?: string;
  scene_vocabulary?: string[];
  texture?: string;
  lighting?: string;
}

export interface StoryDNASchema {
  narrative_structure: string;
  structure_name?: string;
  topic_category?: string;
  intent?: string;
  complexity?: string;
  emotional_tone?: string;
  hook_type?: string;
  information_density?: string;
  pacing?: string;
  reveal_timing?: string;
  payoff_type?: string;
  scene_count?: number;
  target_duration?: number;
  emotional_progression?: string[];
}

export interface CreativeDirectionSchema {
  style_id?: string;
  visual_strategy_id?: string;
  palette: PaletteSchema;
  typography?: TypographySchema;
  hook?: {
    headline_template?: string;
    subtext_template?: string;
    headline?: string;
    subtext?: string;
  };
  visual_metaphor?: string;
  sound_profile?: {
    bpm?: number;
  };
  voice?: {
    voice?: string;
    rate?: string;
  };
  audio_dna?: AudioDNASchema;
  closing_dna?: ClosingDNASchema;
  visual_dna?: VisualDNASchema;
  story_dna?: StoryDNASchema;
  creative_seed?: string;
  audio_seed?: number;
  closing_seed?: number;
  motion_template?: Record<string, any>;
  motion_template_id?: string;
}

export interface SceneElements {
  headline?: string;
  subtext?: string;
  badge?: string;
  metaphor_id?: string;
  label?: string;
  description?: string;
  filename?: string;
  lines?: string[];
  highlight_line?: number;
  annotation?: string;
  left_label?: string;
  left_code?: string[];
  right_label?: string;
  right_code?: string[];
  stat_callout?: string;
  title?: string;
  subtitle?: string;
  stat?: string;
  formula_title?: string;
  equation_latex?: string;
  formula_2d?: string;
  function_type?: string;
  camera_motion?: string;
  color_gradient?: string[];
  visual_cues?: string[];
  [key: string]: unknown;
}

// ── Continuity System Types (OneTake Principle) ───────────────────────────────

/** The carry instruction for a scene's exit into or entry from an adjacent beat */
export interface CarryInstruction {
  primitive: string;          // "expand" | "morph" | "travel" | "collapse" | "whip_pan" | ...
  carrier: string;            // The specific element that carries (e.g. "headline_text")
  to_scene?: string;
  from_scene?: string;
  overlap_frames: number;     // Frames the carry spans across both scenes
  motion_blur: number;        // 0.0–1.0 blur intensity at peak of carry
  easing: string;             // Easing token e.g. "cubic_out", "expo_inout"
  entry_scale?: number;       // Scale factor at which the element enters
  exit_scale?: number;        // Scale factor at which the element exits
  repaired?: boolean;         // True if this bridge was patched by auto-repair
}

/** A ContinuityBridge connecting two adjacent scenes */
export interface ContinuityBridgeSchema {
  from_scene: string;
  to_scene: string;
  from_type: string;
  to_type: string;
  carry_primitive: string;
  carrier_element: string;
  carrier_description: string;
  exit_position?: { x: number; y: number };
  entry_position?: { x: number; y: number };
  exit_scale: number;
  entry_scale: number;
  overlap_frames: number;
  motion_blur_intensity: number;
  camera_continuity: string;  // "maintain" | "orbit_continue" | "whip" | "punch_z"
  easing: string;
  continuity_score_contribution: number;
  is_slideshow: boolean;
}

/** Per-bridge score returned by the oracle */
export interface BridgeScoreResult {
  bridge: ContinuityBridgeSchema;
  score: number;              // 0–100
  is_slideshow: boolean;
  passed: boolean;
}

/** The full continuity report from the ContinuityScorer oracle */
export interface ContinuityReportSchema {
  continuity_score: number;   // 0–100 overall score
  passed: boolean;
  slideshow_ratio: number;    // 0.0–1.0 fraction of bridges that are plain slideshows
  slideshow_bridge_count: number;
  total_bridges: number;
  bridge_scores: BridgeScoreResult[];
  violations: Array<{
    from: string;
    to: string;
    score: number;
    issue: string;
    recommendation: string;
  }>;
  recommendation: string;
  thresholds?: {
    minimum_bridge_score: number;
    minimum_overall_score: number;
    maximum_slideshow_ratio: number;
  };
}

/** The per-scene continuity intent annotations from ScriptStoryboardAgent */
export interface ContinuityIntentSchema {
  exit_element: string;
  exit_primitive: string;
  exit_description: string;
  entry_element: string;
  entry_primitive: string;
  entry_description: string;
  is_first_scene: boolean;
  is_last_scene: boolean;
}

// ── Visual Recipe & Shot Designer Schemas ────────────────────────────────────

export interface CameraWaypointSchema {
  x: number;
  y: number;
  z: number;
  pitch: number;
  yaw: number;
  roll: number;
  fov?: number;
  scale?: number;
}

export interface CameraTrajectorySchema {
  start: CameraWaypointSchema;
  end: CameraWaypointSchema;
  motion_style: string;
  motion_blur?: number;
  easing?: string;
}

export interface VisualPrimitivesSchema {
  enter: string;
  move: string;
  transform: string;
  impact: string;
  exit: string;
}

export interface TypographyBehaviorSchema {
  mode: string;
  headline: string;
  subtext: string;
  badge: string;
  font_size?: number;
  letter_spacing?: string;
  case?: string;
  stagger_frames?: number;
  highlight_word_indices?: number[];
}

export interface SubjectLayerSchema {
  type: string;
  layer_id: string;
  z_index?: number;
  depth_plane?: string;
  properties?: Record<string, any>;
}

export interface CarryRelationshipSchema {
  carrier_element_id: string;
  entry_primitive: string;
  exit_primitive: string;
  morph_target: string;
  surviving_properties?: string[];
}

export interface VisualRecipeSchema {
  scene_id: string;
  beat_name: string;
  start_time: number;
  end_time: number;
  duration_sec: number;
  template_id: string;
  composition: string;
  anchor: {
    x_pct: number;
    y_pct: number;
    align: string;
  };
  layout_grammar: Record<string, any>;
  camera: CameraTrajectorySchema;
  primitives: VisualPrimitivesSchema;
  typography: TypographyBehaviorSchema;
  primary_subject: SubjectLayerSchema;
  secondary_subjects?: SubjectLayerSchema[];
  background_style: string;
  lighting_depth: string;
  pacing_style: string;
  carry?: CarryRelationshipSchema;
}

// ─────────────────────────────────────────────────────────────────────────────

export interface SceneSchema {
  id: string;
  beat_name?: string;
  start: number;
  end: number;
  duration: number;
  visual_type: "hook" | "math_3d" | "metaphor" | "code" | "benchmark" | "split" | "diagram" | "payoff" | string;
  composition_variant?: string;
  voice_text?: string;
  elements: SceneElements;
  // Dynamic Shot Designer Visual Recipe (Universal Visual Engine)
  visual_recipe?: VisualRecipeSchema;
  // Continuity carry annotations (added by ContinuityWeaverAgent)
  continuity_intent?: ContinuityIntentSchema;
  exit_carry?: CarryInstruction;
  entry_carry?: CarryInstruction;
}

export interface MotionPlanSchema {
  version?: string;
  topic: string;
  duration: number;
  fps?: number;
  total_frames?: number;
  creative_direction: CreativeDirectionSchema;
  story_dna?: StoryDNASchema;
  visual_dna?: VisualDNASchema;
  composition_variants?: string[];
  technical_summary?: Record<string, unknown>;
  code_assets?: Record<string, unknown>;
  scenes: SceneSchema[];
  audio_url?: string;
  audio_events?: AudioEventSchema[];
  is_math?: boolean;
  math_spec?: Record<string, unknown>;
  // Continuity system (populated by ContinuityWeaverAgent oracle)
  continuity_bridges?: ContinuityBridgeSchema[];
  continuity_report?: ContinuityReportSchema;
  continuity_score?: number;
  continuity_passed?: boolean;
  continuity_violations?: string[];
  continuity_attempt?: number;
}

export interface ReelCompositionProps {
  motionPlan: MotionPlanSchema;
}
