import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { SceneSchema, CreativeDirectionSchema } from "../types";
import { toRgba } from "../utils/colors";
import { renderEquationHtml, cleanLatexString } from "../utils/mathFormatter";

export const Math3DScene: React.FC<{
  scene: SceneSchema;
  creativeDirection: CreativeDirectionSchema;
}> = ({ scene, creativeDirection }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const palette = creativeDirection.palette;
  const elems = scene.elements || {};

  const totalFrames = Math.max(1, Math.round(scene.duration * fps));
  const progress = Math.min(Math.max(frame / totalFrames, 0), 1);

  const rawTitle = (elems.formula_title || elems.title || "2D TO 3D MATHEMATICAL PROJECTION") as string;
  const title = cleanLatexString(rawTitle);
  const rawEquation = (elems.equation_latex || "$z = \\frac{\\sin(\\sqrt{x^2+y^2})}{\\sqrt{x^2+y^2}}$") as string;
  const equation = rawEquation;
  const formula2D = (elems.formula_2d || "$y = \\sin(x)/x$") as string;
  const functionType = (elems.function_type || "sinc") as string;
  const description = (elems.description || "2D cross-section smoothly elevates into an orbiting 3D parametric surface.") as string;

  const equationHtml = React.useMemo(() => {
    return renderEquationHtml(equation, true);
  }, [equation]);

  const cleanEq = cleanLatexString(equation);
  const eqFontSize = cleanEq.length > 55 ? 32 : cleanEq.length > 35 ? 38 : 44;

  // Spring entrance for HUD
  const enterSpring = spring({
    frame,
    fps,
    config: { damping: 15, mass: 0.9, stiffness: 120 },
  });

  const headingFont = creativeDirection.typography?.heading || "Inter, system-ui, sans-serif";
  const monoFont = creativeDirection.typography?.mono || "JetBrains Mono, monospace";

  // Transition choreography:
  // Phase 1: 0.0 -> 0.30 (Pure 2D)
  // Phase 2: 0.30 -> 0.65 (Camera smoothly tilts and yaws into 3D)
  // Phase 3: 0.65 -> 1.0 (Full 3D orbit, waving surface, and depth exploration)
  const pitchDeg = interpolate(progress, [0, 0.28, 0.62, 1.0], [0, 0, 52, 58], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const yawDeg = interpolate(progress, [0, 0.28, 0.62, 1.0], [0, 0, 38, 76], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const meshExtrude = interpolate(progress, [0.28, 0.62], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const zAxisOpacity = interpolate(progress, [0.30, 0.50], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Calculate 3D wireframe mesh points
  const gridSize = 16;
  const extent = 2.4;
  const step = (extent * 2) / gridSize;
  const cx = 540;
  const cy = 1120;
  const scale = 145;

  const pitchRad = (pitchDeg * Math.PI) / 180;
  const yawRad = (yawDeg * Math.PI) / 180;
  const timeOffset = frame * 0.05;

  const project3D = (x: number, y: number, z: number) => {
    // Yaw rotation (around Z axis)
    const x1 = x * Math.cos(yawRad) - y * Math.sin(yawRad);
    const y1 = x * Math.sin(yawRad) + y * Math.cos(yawRad);

    // Pitch rotation (tilt down)
    const y2 = y1 * Math.cos(pitchRad) - z * Math.sin(pitchRad);
    const z2 = y1 * Math.sin(pitchRad) + z * Math.cos(pitchRad);

    // Perspective factor
    const fov = 800;
    const pScale = fov / (fov + z2 * scale * 0.3);

    return {
      u: cx + x1 * scale * pScale,
      v: cy - y2 * scale * pScale,
      depth: z2,
    };
  };

  // Evaluate function height z
  const evaluateZ = (x: number, y: number) => {
    if (functionType === "euler_helix") {
      const r = Math.sqrt(x * x + y * y);
      return Math.sin(r * 3 - timeOffset) * 0.7 * meshExtrude;
    } else if (functionType === "saddle") {
      return (x * x - y * y) * 0.22 * meshExtrude;
    } else {
      // Sinc / circular ripple wave
      const r = Math.sqrt(x * x + y * y) * 2.8 + 1e-4;
      return (Math.sin(r - timeOffset) / r) * 1.3 * meshExtrude;
    }
  };

  // Generate wireframe quadrilateral rows & columns
  const linesH: string[] = [];
  const linesV: string[] = [];
  const points2D: { u: number; v: number }[] = [];

  for (let i = 0; i <= gridSize; i++) {
    const x = -extent + i * step;
    let pathH = "";
    for (let j = 0; j <= gridSize; j++) {
      const y = -extent + j * step;
      const z = evaluateZ(x, y);
      const pt = project3D(x, y, z);
      if (j === 0) pathH += `M ${pt.u.toFixed(1)} ${pt.v.toFixed(1)}`;
      else pathH += ` L ${pt.u.toFixed(1)} ${pt.v.toFixed(1)}`;
    }
    linesH.push(pathH);
  }

  for (let j = 0; j <= gridSize; j++) {
    const y = -extent + j * step;
    let pathV = "";
    for (let i = 0; i <= gridSize; i++) {
      const x = -extent + i * step;
      const z = evaluateZ(x, y);
      const pt = project3D(x, y, z);
      if (i === 0) pathV += `M ${pt.u.toFixed(1)} ${pt.v.toFixed(1)}`;
      else pathV += ` L ${pt.u.toFixed(1)} ${pt.v.toFixed(1)}`;
    }
    linesV.push(pathV);
  }

  // 2D cross-section curve path
  let path2DCurve = "";
  for (let s = 0; s <= 60; s++) {
    const x = -extent + (s / 60) * (extent * 2);
    const y = 0;
    const z = evaluateZ(x, y);
    const pt = project3D(x, y, z);
    if (s === 0) path2DCurve += `M ${pt.u.toFixed(1)} ${pt.v.toFixed(1)}`;
    else path2DCurve += ` L ${pt.u.toFixed(1)} ${pt.v.toFixed(1)}`;
  }

  // 3D Axes
  const origin = project3D(0, 0, 0);
  const axisX = project3D(extent * 1.15, 0, 0);
  const axisY = project3D(0, extent * 1.15, 0);
  const axisZ = project3D(0, 0, 1.25);

  const currentModeBadge =
    progress < 0.28
      ? "2D CARTESIAN CROSS-SECTION"
      : progress < 0.62
      ? "CAMERA PITCH ➔ 3D ISOMETRIC TRANSITION"
      : "3D TENSOR FIELD ORBIT";

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "flex-start",
        padding: "130px 48px 60px",
        textAlign: "center",
        color: toRgba(palette.text, 1),
      }}
    >
      {/* Top HUD: Dimensional Mode Pill */}
      <div
        style={{
          fontFamily: monoFont,
          fontSize: 20,
          fontWeight: 700,
          letterSpacing: "0.22em",
          color: toRgba(palette.accent, 1),
          backgroundColor: toRgba(palette.surface, 0.9),
          border: `1.5px solid ${toRgba(palette.accent, 0.5)}`,
          padding: "10px 24px",
          borderRadius: 40,
          boxShadow: `0 0 30px ${toRgba(palette.accent, 0.25)}`,
          marginBottom: 20,
          opacity: enterSpring,
        }}
      >
        [ {currentModeBadge} ]
      </div>

      {/* Main Mathematical Equation Banner */}
      <div
        style={{
          opacity: enterSpring,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          maxWidth: 960,
          width: "100%",
          padding: "24px 32px",
          borderRadius: 24,
          backgroundColor: toRgba(palette.surface, 0.85),
          border: `1.5px solid ${toRgba(palette.primary, 0.4)}`,
          backdropFilter: "blur(16px)",
          boxShadow: `0 20px 40px -10px rgba(0,0,0,0.7), 0 0 35px ${toRgba(palette.primary, 0.15)}`,
          marginBottom: 16,
        }}
      >
        <span
          style={{
            fontFamily: monoFont,
            fontSize: 18,
            color: toRgba(palette.subtext, 1),
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            marginBottom: 6,
          }}
        >
          {title}
        </span>

        {/* Large Equation Lockup - KaTeX Rendered */}
        <div
          style={{
            fontSize: eqFontSize,
            lineHeight: 1.25,
            color: toRgba(palette.primary, 1),
            textShadow: `0 0 25px ${toRgba(palette.primary, 0.45)}`,
            margin: "6px 0 12px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: "100%",
            overflow: "visible",
          }}
          dangerouslySetInnerHTML={{
            __html: equationHtml,
          }}
        />

        <p
          style={{
            fontFamily: headingFont,
            fontSize: 22,
            lineHeight: 1.4,
            fontWeight: 500,
            color: toRgba(palette.subtext, 1),
            margin: 0,
          }}
        >
          {description}
        </p>
      </div>

      {/* 2D to 3D Canvas / SVG Projection Viewport */}
      <div
        style={{
          position: "relative",
          width: 960,
          height: 820,
          borderRadius: 28,
          backgroundColor: toRgba(palette.surface, 0.45),
          border: `1px solid ${toRgba(palette.accent, 0.25)}`,
          overflow: "hidden",
          boxShadow: `inset 0 0 50px rgba(0,0,0,0.8), 0 20px 60px rgba(0,0,0,0.6)`,
        }}
      >
        <svg
          width="100%"
          height="100%"
          viewBox="0 0 1080 1920"
          style={{
            position: "absolute",
            top: -cy + 410,
            left: -cx + 480,
            width: 1080,
            height: 1920,
            overflow: "visible",
          }}
        >
          <defs>
            <linearGradient id="mathMeshGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={toRgba(palette.accent, 0.85)} />
              <stop offset="50%" stopColor={toRgba(palette.primary, 0.65)} />
              <stop offset="100%" stopColor={toRgba(palette.secondary, 0.85)} />
            </linearGradient>
            <radialGradient id="originGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor={toRgba(palette.accent, 1)} />
              <stop offset="100%" stopColor={toRgba(palette.accent, 0)} />
            </radialGradient>
          </defs>

          {/* 3D Coordinate Axes */}
          {/* X Axis */}
          <line
            x1={origin.u}
            y1={origin.v}
            x2={axisX.u}
            y2={axisX.v}
            stroke={toRgba(palette.accent, 0.8)}
            strokeWidth={3}
            strokeDasharray="4 4"
          />
          <text x={axisX.u + 12} y={axisX.v + 6} fill={toRgba(palette.accent, 1)} fontFamily={monoFont} fontSize={20} fontWeight={700}>
            +X
          </text>

          {/* Y Axis */}
          <line
            x1={origin.u}
            y1={origin.v}
            x2={axisY.u}
            y2={axisY.v}
            stroke={toRgba(palette.primary, 0.8)}
            strokeWidth={3}
            strokeDasharray="4 4"
          />
          <text x={axisY.u + 10} y={axisY.v - 10} fill={toRgba(palette.primary, 1)} fontFamily={monoFont} fontSize={20} fontWeight={700}>
            +Y
          </text>

          {/* Z Axis (Emerges as camera elevates into 3D) */}
          <g opacity={zAxisOpacity}>
            <line
              x1={origin.u}
              y1={origin.v}
              x2={axisZ.u}
              y2={axisZ.v}
              stroke="#F59E0B"
              strokeWidth={4}
            />
            <polygon
              points={`${axisZ.u},${axisZ.v - 14} ${axisZ.u - 8},${axisZ.v + 2} ${axisZ.u + 8},${axisZ.v + 2}`}
              fill="#F59E0B"
            />
            <text x={axisZ.u + 14} y={axisZ.v} fill="#F59E0B" fontFamily={monoFont} fontSize={22} fontWeight={800}>
              +Z (ELEVATION)
            </text>
          </g>

          {/* 3D Wireframe Mesh Lines */}
          <g opacity={meshExtrude * 0.95}>
            {linesH.map((p, idx) => (
              <path key={`h_${idx}`} d={p} fill="none" stroke="url(#mathMeshGrad)" strokeWidth={1.5} opacity={0.65} />
            ))}
            {linesV.map((p, idx) => (
              <path key={`v_${idx}`} d={p} fill="none" stroke="url(#mathMeshGrad)" strokeWidth={1.5} opacity={0.65} />
            ))}
          </g>

          {/* Glowing 2D Cross Section Curve (Always highlighted with thick pulse) */}
          <path
            d={path2DCurve}
            fill="none"
            stroke={toRgba(palette.primary, 1)}
            strokeWidth={5}
            filter={`drop-shadow(0 0 16px ${toRgba(palette.primary, 0.8)})`}
          />

          {/* Origin Marker */}
          <circle cx={origin.u} cy={origin.v} r={8} fill={toRgba(palette.accent, 1)} />
        </svg>

        {/* HUD Realtime Coordinates Overlay */}
        <div
          style={{
            position: "absolute",
            bottom: 18,
            left: 24,
            right: 24,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            fontFamily: monoFont,
            fontSize: 16,
            color: toRgba(palette.subtext, 1),
            padding: "8px 16px",
            backgroundColor: toRgba(palette.surface, 0.85),
            borderRadius: 14,
            border: `1px solid rgba(255,255,255,0.08)`,
          }}
        >
          <div>
            <span style={{ color: toRgba(palette.accent, 1), fontWeight: 700 }}>PITCH:</span> {pitchDeg.toFixed(1)}° &nbsp;|&nbsp;{" "}
            <span style={{ color: toRgba(palette.primary, 1), fontWeight: 700 }}>YAW:</span> {yawDeg.toFixed(1)}°
          </div>
          <div>
            <span style={{ color: "#F59E0B", fontWeight: 700 }}>DIMENSION:</span> {progress < 0.3 ? "ℝ² (Flat Plane)" : "ℝ³ (Spatial Tensor)"}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
