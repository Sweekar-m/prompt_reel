import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { SceneSchema, CreativeDirectionSchema } from "../types";
import { toRgba } from "../utils/colors";

export const PayoffScene: React.FC<{
  scene: SceneSchema;
  creativeDirection: CreativeDirectionSchema;
}> = ({ scene, creativeDirection }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const palette = creativeDirection.palette;
  const elems = scene.elements || {};

  const title = (elems.title as string) || scene.beat_name || "MASTER TAKEAWAY";
  const stat = (elems.stat as string) || "O(1) OPTIMAL";
  const subtitle = (elems.subtitle as string) || "Deterministic hardware execution";
  const proTip = (elems.pro_tip as string) || "Write branch-friendly conditions to avoid CPU instruction stalls.";

  const enterSpring = spring({
    frame,
    fps,
    config: { damping: 13, mass: 0.9, stiffness: 140 },
  });

  const headingFont = creativeDirection.typography?.heading || "Inter, sans-serif";
  const monoFont = creativeDirection.typography?.mono || "JetBrains Mono, monospace";

  // Radiating glow pulse
  const pulse = interpolate((frame % 45) / 45, [0, 0.5, 1], [0.98, 1.05, 0.98]);

  // Dynamic font sizing
  const statFontSize =
    stat.length > 28 ? 44 : stat.length > 18 ? 54 : stat.length > 10 ? 68 : 84;

  const subtitleFontSize =
    subtitle.length > 80 ? 26 : subtitle.length > 50 ? 30 : 34;

  // Circular gauge animation
  const gaugeFill = interpolate(frame, [0, 45], [0, 100], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 60px",
        textAlign: "center",
        boxSizing: "border-box",
      }}
    >
      {/* Title Badge */}
      <div
        style={{
          fontFamily: monoFont,
          fontSize: 22,
          fontWeight: 800,
          letterSpacing: "0.22em",
          color: toRgba(palette.primary, 1),
          backgroundColor: toRgba(palette.surface, 0.92),
          border: `2px solid ${toRgba(palette.primary, 0.5)}`,
          padding: "10px 32px",
          borderRadius: 40,
          marginBottom: 32,
          maxWidth: 880,
          wordBreak: "break-word",
          textAlign: "center",
          opacity: enterSpring,
          boxShadow: `0 0 30px ${toRgba(palette.primary, 0.25)}`,
        }}
      >
        ✦ {title.replace(/_/g, " ").toUpperCase()} ✦
      </div>

      {/* Hero Stat / Speedup Callout */}
      <div
        style={{
          fontFamily: monoFont,
          fontSize: statFontSize,
          fontWeight: 900,
          color: toRgba(palette.accent, 1),
          textShadow: `0 0 50px ${toRgba(palette.accent, 0.6)}, 0 0 90px ${toRgba(palette.accent, 0.3)}`,
          letterSpacing: stat.length > 15 ? "0.01em" : "-0.02em",
          lineHeight: 1.15,
          maxWidth: 960,
          width: "100%",
          wordBreak: "break-word",
          textAlign: "center",
          marginBottom: 24,
          transform: `scale(${pulse})`,
        }}
      >
        {stat}
      </div>

      {/* Subtitle Takeaway */}
      <h3
        style={{
          fontFamily: headingFont,
          fontSize: subtitleFontSize,
          lineHeight: 1.4,
          fontWeight: 700,
          color: "#ffffff",
          maxWidth: 880,
          width: "100%",
          wordBreak: "break-word",
          textAlign: "center",
          margin: "0 0 40px 0",
          opacity: enterSpring,
          textShadow: "0 2px 10px rgba(0, 0, 0, 0.8)",
        }}
      >
        {subtitle}
      </h3>

      {/* Master Pro Tip Card */}
      {proTip && (
        <div
          style={{
            maxWidth: 900,
            width: "100%",
            backgroundColor: "rgba(10, 15, 26, 0.9)",
            border: `1.5px solid ${toRgba(palette.accent, 0.55)}`,
            borderRadius: 20,
            padding: "20px 32px",
            boxShadow: `0 20px 50px rgba(0, 0, 0, 0.7), 0 0 35px ${toRgba(palette.accent, 0.2)}`,
            textAlign: "left",
            display: "flex",
            alignItems: "center",
            gap: 16,
            opacity: spring({ frame: frame - 15, fps }),
          }}
        >
          <div
            style={{
              width: 50,
              height: 50,
              borderRadius: "50%",
              backgroundColor: toRgba(palette.accent, 0.2),
              border: `1.5px solid ${toRgba(palette.accent, 0.8)}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 24,
              flexShrink: 0,
            }}
          >
            ⭐
          </div>
          <div>
            <div style={{ fontFamily: monoFont, fontSize: 13, color: toRgba(palette.accent, 1), fontWeight: 800, letterSpacing: "0.1em" }}>
              SENIOR ENGINEER RULE
            </div>
            <div style={{ fontFamily: headingFont, fontSize: 20, fontWeight: 600, color: "#f8fafc", marginTop: 4, lineHeight: 1.35 }}>
              {proTip}
            </div>
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};
