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

export interface CreativeDirectionSchema {
  style_id?: string;
  palette: PaletteSchema;
  typography?: TypographySchema;
  hook?: {
    headline_template?: string;
    subtext_template?: string;
  };
  visual_metaphor?: string;
  sound_profile?: {
    bpm?: number;
  };
  voice?: {
    voice?: string;
    rate?: string;
  };
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

export interface SceneSchema {
  id: string;
  beat_name?: string;
  start: number;
  end: number;
  duration: number;
  visual_type: "hook" | "math_3d" | "metaphor" | "code" | "benchmark" | "split" | "diagram" | "payoff" | string;
  voice_text?: string;
  elements: SceneElements;
}

export interface MotionPlanSchema {
  version?: string;
  topic: string;
  duration: number;
  fps?: number;
  total_frames?: number;
  creative_direction: CreativeDirectionSchema;
  technical_summary?: Record<string, unknown>;
  code_assets?: Record<string, unknown>;
  scenes: SceneSchema[];
  audio_url?: string;
}

export interface ReelCompositionProps {
  motionPlan: MotionPlanSchema;
}
