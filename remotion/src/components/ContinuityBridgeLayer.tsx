import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, Easing } from "remotion";
import { ContinuityBridgeSchema, SceneSchema, PaletteSchema } from "../types";
import { toRgba } from "../utils/colors";

interface ContinuityBridgeLayerProps {
  bridges: ContinuityBridgeSchema[];
  scenes: SceneSchema[];
  palette: PaletteSchema;
}

export const ContinuityBridgeLayer: React.FC<ContinuityBridgeLayerProps> = ({
  bridges = [],
  scenes = [],
  palette,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  // Find active bridge for current frame
  let activeBridge: ContinuityBridgeSchema | null = null;
  let activeProgress = 0; // 0 to 1
  let activeBridgeIndex = -1;

  for (let i = 0; i < scenes.length - 1; i++) {
    const nextScene = scenes[i + 1];
    const boundaryFrame = Math.round(nextScene.start * fps);
    const bridge = bridges.find(
      (b) => b.from_scene === scenes[i].id && b.to_scene === nextScene.id
    ) || bridges[i];

    const overlap = bridge ? bridge.overlap_frames || 14 : 14;
    const halfOverlap = Math.floor(overlap / 2);
    const startWindow = boundaryFrame - halfOverlap;
    const endWindow = boundaryFrame + (overlap - halfOverlap);

    if (frame >= startWindow && frame <= endWindow) {
      activeBridge = bridge || {
        from_scene: scenes[i].id,
        to_scene: nextScene.id,
        from_type: scenes[i].visual_type,
        to_type: nextScene.visual_type,
        carry_primitive: "expand",
        carrier_element: "focal_node",
        carrier_description: "Dynamic visual carry bridge",
        exit_scale: 1.15,
        entry_scale: 0.9,
        overlap_frames: overlap,
        motion_blur_intensity: 0.6,
        camera_continuity: "punch_z",
        easing: "cubic_out",
        continuity_score_contribution: 85,
        is_slideshow: false,
      };
      activeProgress = interpolate(frame, [startWindow, endWindow], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      activeBridgeIndex = i;
      break;
    }
  }

  if (!activeBridge || activeProgress <= 0 || activeProgress >= 1) {
    return null;
  }

  // Bell-curve intensity: 0 at start, 1.0 at the exact transition point, 0 at end
  const bell = Math.sin(activeProgress * Math.PI);
  const blurStdDev = bell * (activeBridge.motion_blur_intensity || 0.6) * 16;
  const primitive = activeBridge.carry_primitive || "expand";
  const cameraMode = activeBridge.camera_continuity || "punch_z";

  // Palette colors for carrier graphics with fallbacks
  const safePalette = palette || ({} as PaletteSchema);
  const primaryRgba = toRgba(safePalette.primary || [0, 240, 255], 0.9);
  const accentRgba = toRgba(safePalette.accent || [255, 230, 0], 0.95);
  const secondaryRgba = toRgba(safePalette.secondary || [255, 0, 128], 0.85);

  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        zIndex: 50,
      }}
    >
      {/* SVG filter for dynamic directional & motion blur */}
      <svg style={{ position: "absolute", width: 0, height: 0 }}>
        <defs>
          <filter id="continuity-blur-filter" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur
              stdDeviation={
                cameraMode === "whip"
                  ? `${blurStdDev * 1.5} 0`
                  : cameraMode === "travel_y"
                  ? `0 ${blurStdDev * 1.5}`
                  : `${blurStdDev * 0.8} ${blurStdDev * 0.8}`
              }
            />
          </filter>
        </defs>
      </svg>

      {/* Screen flash / chromatic streak at peak transition */}
      {bell > 0.3 && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              cameraMode === "whip"
                ? `linear-gradient(90deg, transparent 0%, ${toRgba(palette.primary, bell * 0.25)} 50%, transparent 100%)`
                : `radial-gradient(circle at center, ${toRgba(palette.accent, bell * 0.22)} 0%, transparent 70%)`,
            mixBlendMode: "screen",
            opacity: bell * 0.7,
            transition: "opacity 0.05s ease",
          }}
        />
      )}

      {/* RENDER CONTINUITY CARRIER PRIMITIVE */}
      {primitive === "expand" && (
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: `translate(-50%, -50%) scale(${interpolate(
              activeProgress,
              [0, 1],
              [0.3, 3.2],
              { easing: Easing.bezier(0.16, 1, 0.3, 1) }
            )})`,
            width: 320,
            height: 320,
            borderRadius: "50%",
            border: `3px solid ${accentRgba}`,
            boxShadow: `0 0 60px ${accentRgba}, inset 0 0 40px ${primaryRgba}`,
            opacity: bell * 0.9,
            filter: "url(#continuity-blur-filter)",
          }}
        />
      )}

      {primitive === "collapse" && (
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: `translate(-50%, -50%) scale(${interpolate(
              activeProgress,
              [0, 0.5, 1],
              [2.4, 0.05, 1.8],
              { easing: Easing.bezier(0.77, 0, 0.175, 1) }
            )}) rotate(${activeProgress * 180}deg)`,
            width: 280,
            height: 280,
            borderRadius: "32px",
            border: `4px solid ${primaryRgba}`,
            boxShadow: `0 0 80px ${primaryRgba}, 0 0 30px ${accentRgba}`,
            opacity: bell * 0.95,
            filter: "url(#continuity-blur-filter)",
          }}
        />
      )}

      {primitive === "morph" && (
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: `translate(-50%, -50%) scale(${interpolate(
              activeProgress,
              [0, 0.5, 1],
              [1.0, 1.45, 1.0]
            )}) rotate(${activeProgress * 90}deg)`,
            width: 220,
            height: 220,
            borderRadius: `${interpolate(activeProgress, [0, 0.5, 1], [16, 50, 24])}%`,
            background: `linear-gradient(135deg, ${primaryRgba}, ${accentRgba})`,
            boxShadow: `0 0 70px ${accentRgba}`,
            opacity: bell * 0.85,
            filter: "url(#continuity-blur-filter)",
          }}
        />
      )}

      {primitive === "punch_z" && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {/* Concentric kinetic rings surging towards camera */}
          {[1, 2, 3].map((ringIdx) => {
            const ringProgress = (activeProgress + ringIdx * 0.25) % 1;
            const scale = interpolate(ringProgress, [0, 1], [0.4, 3.8]);
            const ringOpacity = Math.sin(ringProgress * Math.PI) * bell * 0.6;
            return (
              <div
                key={ringIdx}
                style={{
                  position: "absolute",
                  width: 300,
                  height: 300,
                  borderRadius: "50%",
                  border: `2px dashed ${ringIdx % 2 === 0 ? accentRgba : primaryRgba}`,
                  transform: `scale(${scale})`,
                  opacity: ringOpacity,
                  boxShadow: `0 0 40px ${primaryRgba}`,
                }}
              />
            );
          })}
        </div>
      )}

      {primitive === "travel_x" && (
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: `${interpolate(activeProgress, [0, 1], [-20, 120])}%`,
            transform: "translateY(-50%)",
            width: 350,
            height: 6,
            background: `linear-gradient(90deg, transparent, ${accentRgba} 50%, transparent)`,
            boxShadow: `0 0 35px ${accentRgba}`,
            opacity: bell,
            filter: "url(#continuity-blur-filter)",
          }}
        />
      )}

      {primitive === "travel_y" && (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: `${interpolate(activeProgress, [0, 1], [120, -20])}%`,
            transform: "translateX(-50%)",
            height: 350,
            width: 6,
            background: `linear-gradient(180deg, transparent, ${primaryRgba} 50%, transparent)`,
            boxShadow: `0 0 35px ${primaryRgba}`,
            opacity: bell,
            filter: "url(#continuity-blur-filter)",
          }}
        />
      )}

      {primitive === "orbit_handoff" && (
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: `translate(-50%, -50%) rotate(${interpolate(
              activeProgress,
              [0, 1],
              [-45, 45]
            )}deg) scale(${interpolate(activeProgress, [0, 0.5, 1], [0.9, 1.25, 0.95])})`,
            width: 440,
            height: 440,
            borderRadius: "50%",
            border: `3px solid ${secondaryRgba}`,
            boxShadow: `0 0 50px ${secondaryRgba}`,
            opacity: bell * 0.8,
            filter: "url(#continuity-blur-filter)",
          }}
        />
      )}

      {/* Active carrier badge & continuity marker (subtle high-end visual indicator) */}
      <div
        style={{
          position: "absolute",
          bottom: 28,
          right: 28,
          padding: "6px 14px",
          borderRadius: "99px",
          background: "rgba(10, 14, 24, 0.75)",
          border: `1px solid ${toRgba(safePalette.primary || [0, 240, 255], 0.35)}`,
          backdropFilter: "blur(12px)",
          display: "flex",
          alignItems: "center",
          gap: 8,
          opacity: bell * 0.85,
          transform: `translateY(${interpolate(bell, [0, 1], [15, 0])}px)`,
        }}
      >
        <div
          style={{
            width: 6,
            height: 6,
            borderRadius: "50%",
            background: accentRgba,
            boxShadow: `0 0 8px ${accentRgba}`,
          }}
        />
        <span
          style={{
            fontFamily: "JetBrains Mono, monospace",
            fontSize: 11,
            fontWeight: 600,
            letterSpacing: "0.08em",
            color: toRgba(safePalette.text || [240, 245, 255], 0.9),
            textTransform: "uppercase",
          }}
        >
          {activeBridge.carry_primitive} • {activeBridge.carrier_element}
        </span>
      </div>
    </AbsoluteFill>
  );
};
