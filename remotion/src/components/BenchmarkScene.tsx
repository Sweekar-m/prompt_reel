import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { SceneSchema, CreativeDirectionSchema } from "../types";
import { toRgba } from "../utils/colors";

export const BenchmarkScene: React.FC<{
  scene: SceneSchema;
  creativeDirection: CreativeDirectionSchema;
}> = ({ scene, creativeDirection }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const palette = creativeDirection.palette;
  const elems = scene.elements || {};

  const statCallout = elems.stat_callout || "100x FASTER";
  const leftLabel = elems.left_label || "WITHOUT";
  const rightLabel = elems.right_label || "WITH";
  const leftCode = elems.left_code || ["linear search", "O(N) operations", "stack overflow risk"];
  const rightCode = elems.right_code || ["memoized call", "O(log N) operations", "constant space"];

  const enterSpring = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.9, stiffness: 120 },
  });

  const monoFont = creativeDirection.typography?.mono || "JetBrains Mono, monospace";
  const headingFont = creativeDirection.typography?.heading || "Inter, sans-serif";

  const statFontSize =
    statCallout.length > 24 ? 36 : statCallout.length > 14 ? 44 : 54;

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 60px",
      }}
    >
      {/* Title */}
      <h2
        style={{
          fontFamily: headingFont,
          fontSize: 48,
          fontWeight: 800,
          color: toRgba(palette.text, 1),
          letterSpacing: "0.08em",
          margin: "0 0 24px 0",
          opacity: enterSpring,
        }}
      >
        PERFORMANCE CONTRAST
      </h2>

      {/* Big Stat Hero Pill */}
      <div
        style={{
          fontFamily: monoFont,
          fontSize: statFontSize,
          fontWeight: 900,
          color: toRgba(palette.accent, 1),
          backgroundColor: toRgba(palette.surface, 0.9),
          border: `2px solid ${toRgba(palette.accent, 0.6)}`,
          padding: "16px 40px",
          borderRadius: 40,
          boxShadow: `0 0 35px ${toRgba(palette.accent, 0.35)}`,
          marginBottom: 48,
          maxWidth: 900,
          wordBreak: "break-word",
          overflowWrap: "break-word",
          textAlign: "center",
          transform: `scale(${interpolate(enterSpring, [0, 1], [0.85, 1])})`,
          opacity: enterSpring,
        }}
      >
        {statCallout}
      </div>

      {/* Side by side comparison cards */}
      <div
        style={{
          display: "flex",
          gap: 36,
          width: "100%",
          maxWidth: 960,
          justifyContent: "center",
        }}
      >
        {/* Left Card (Without) */}
        <div
          style={{
            flex: 1,
            backgroundColor: "rgba(239, 68, 68, 0.08)",
            border: "1.5px solid rgba(239, 68, 68, 0.4)",
            borderRadius: 20,
            padding: "32px 28px",
            boxShadow: "0 10px 30px rgba(239, 68, 68, 0.1)",
          }}
        >
          <div
            style={{
              fontFamily: monoFont,
              fontSize: 24,
              fontWeight: 800,
              color: "rgb(239, 68, 68)",
              letterSpacing: "0.15em",
              marginBottom: 20,
              display: "flex",
              alignItems: "center",
              gap: 10,
            }}
          >
            <span>✕</span> {leftLabel}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {leftCode.slice(0, 5).map((l, i) => (
              <div
                key={i}
                style={{
                  fontFamily: monoFont,
                  fontSize: 22,
                  color: toRgba(palette.subtext, 0.85),
                  backgroundColor: "rgba(0, 0, 0, 0.25)",
                  padding: "10px 16px",
                  borderRadius: 10,
                }}
              >
                {l}
              </div>
            ))}
          </div>
        </div>

        {/* Right Card (With) */}
        <div
          style={{
            flex: 1,
            backgroundColor: "rgba(34, 197, 94, 0.1)",
            border: "1.5px solid rgba(34, 197, 94, 0.5)",
            borderRadius: 20,
            padding: "32px 28px",
            boxShadow: "0 10px 30px rgba(34, 197, 94, 0.15)",
          }}
        >
          <div
            style={{
              fontFamily: monoFont,
              fontSize: 24,
              fontWeight: 800,
              color: "rgb(34, 197, 94)",
              letterSpacing: "0.15em",
              marginBottom: 20,
              display: "flex",
              alignItems: "center",
              gap: 10,
            }}
          >
            <span>✓</span> {rightLabel}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {rightCode.slice(0, 5).map((l, i) => (
              <div
                key={i}
                style={{
                  fontFamily: monoFont,
                  fontSize: 22,
                  color: toRgba(palette.text, 1),
                  fontWeight: 600,
                  backgroundColor: "rgba(0, 0, 0, 0.35)",
                  padding: "10px 16px",
                  borderRadius: 10,
                  borderLeft: "3px solid rgb(34, 197, 94)",
                }}
              >
                {l}
              </div>
            ))}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
