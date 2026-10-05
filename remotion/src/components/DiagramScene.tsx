import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { SceneSchema, CreativeDirectionSchema } from "../types";
import { toRgba } from "../utils/colors";

export const DiagramScene: React.FC<{
  scene: SceneSchema;
  creativeDirection: CreativeDirectionSchema;
}> = ({ scene, creativeDirection }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const palette = creativeDirection.palette;
  const elems = scene.elements || {};

  const title = (elems.title as string) || "CPU ARCHITECTURE & PIPELINE";
  const subtitle = (elems.subtitle as string) || "Instruction execution through hardware registers";
  const steps = (elems.steps as string[]) || [
    "Fetch instruction from L1 cache into pipeline",
    "Evaluate condition flags in Arithmetic Logic Unit",
    "Branch predictor commits zero-latency instruction pointer",
  ];
  const timeComplexity = (elems.time_complexity as string) || "O(1) Constant Time";
  const proTip = (elems.pro_tip as string) || "Keep branch patterns predictable to maximize CPU instruction throughput.";

  const metricLabel = (elems.metric_label as string) || "SYSTEM THROUGHPUT";
  const metricVal = (elems.metric_val as string) || "0.35 ns (1 CYCLE)";

  const enterSpring = spring({
    frame,
    fps,
    config: { damping: 15, mass: 0.9, stiffness: 120 },
  });

  const headingFont = creativeDirection.typography?.heading || "Inter, sans-serif";
  const monoFont = creativeDirection.typography?.mono || "JetBrains Mono, monospace";

  // Animated pipeline progress
  const activeStage = Math.min(2, Math.floor(frame / 25));

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "flex-start",
        padding: "90px 50px 60px",
        textAlign: "center",
      }}
    >
      {/* Title Badge */}
      <div
        style={{
          fontFamily: monoFont,
          fontSize: 22,
          fontWeight: 700,
          letterSpacing: "0.2em",
          color: toRgba(palette.primary, 1),
          backgroundColor: toRgba(palette.surface, 0.92),
          border: `1.5px solid ${toRgba(palette.primary, 0.45)}`,
          padding: "8px 24px",
          borderRadius: 30,
          marginBottom: 16,
          opacity: enterSpring,
        }}
      >
        ✦ {title.toUpperCase()} ✦
      </div>

      {/* Subtitle / Hardware Reality */}
      <p
        style={{
          fontFamily: headingFont,
          fontSize: 28,
          lineHeight: 1.4,
          fontWeight: 600,
          color: toRgba(palette.text, 1),
          maxWidth: 900,
          margin: "0 0 36px 0",
          opacity: enterSpring,
        }}
      >
        {subtitle}
      </p>

      {/* 3-Stage Pipeline Flowchart Diagram */}
      <div
        style={{
          width: "100%",
          maxWidth: 920,
          display: "flex",
          flexDirection: "column",
          gap: 16,
          opacity: enterSpring,
        }}
      >
        {steps.map((stepText, idx) => {
          const isActive = idx === activeStage;
          const isDone = idx < activeStage;
          const stepSpring = spring({
            frame: frame - idx * 12,
            fps,
            config: { damping: 14, stiffness: 130 },
          });

          return (
            <div
              key={idx}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 20,
                backgroundColor: isActive
                  ? toRgba(palette.primary, 0.22)
                  : isDone
                  ? "rgba(16, 185, 129, 0.15)"
                  : toRgba(palette.surface, 0.8),
                border: `2px solid ${
                  isActive
                    ? toRgba(palette.primary, 0.95)
                    : isDone
                    ? "#10b981"
                    : toRgba(palette.primary, 0.3)
                }`,
                borderRadius: 18,
                padding: "18px 28px",
                boxShadow: isActive ? `0 0 35px ${toRgba(palette.primary, 0.3)}` : "none",
                transform: `translateX(${interpolate(stepSpring, [0, 1], [-25, 0])}px)`,
                opacity: stepSpring,
                textAlign: "left",
              }}
            >
              {/* Step Number Indicator */}
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: 12,
                  backgroundColor: isDone ? "#10b981" : isActive ? toRgba(palette.accent, 1) : "rgba(255,255,255,0.1)",
                  color: isDone || isActive ? "#000" : "#fff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontFamily: monoFont,
                  fontSize: 22,
                  fontWeight: 900,
                  flexShrink: 0,
                }}
              >
                {isDone ? "✓" : `0${idx + 1}`}
              </div>

              {/* Step Text Content */}
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: monoFont, fontSize: 13, color: toRgba(palette.subtext, 0.8), letterSpacing: "0.1em" }}>
                  PHASE {idx + 1}
                </div>
                <div style={{ fontFamily: headingFont, fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 2 }}>
                  {stepText}
                </div>
              </div>

              {/* Status Badge */}
              <div
                style={{
                  fontFamily: monoFont,
                  fontSize: 12,
                  fontWeight: 700,
                  color: isDone ? "#10b981" : isActive ? toRgba(palette.accent, 1) : "#64748b",
                  backgroundColor: "rgba(0,0,0,0.4)",
                  padding: "4px 10px",
                  borderRadius: 6,
                }}
              >
                {isDone ? "COMMITTED" : isActive ? "EXECUTING" : "QUEUED"}
              </div>
            </div>
          );
        })}
      </div>

      {/* Metrics & Telemetry Grid */}
      <div
        style={{
          marginTop: 28,
          width: "100%",
          maxWidth: 920,
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 16,
          opacity: enterSpring,
        }}
      >
        <div
          style={{
            backgroundColor: toRgba(palette.surface, 0.9),
            border: `1px solid ${toRgba(palette.primary, 0.35)}`,
            borderRadius: 16,
            padding: "16px 20px",
            textAlign: "left",
          }}
        >
          <div style={{ fontFamily: monoFont, fontSize: 13, color: toRgba(palette.subtext, 0.8) }}>
            TIME COMPLEXITY
          </div>
          <div style={{ fontFamily: monoFont, fontSize: 26, fontWeight: 800, color: toRgba(palette.accent, 1), marginTop: 4 }}>
            {timeComplexity}
          </div>
        </div>

        <div
          style={{
            backgroundColor: toRgba(palette.surface, 0.9),
            border: `1px solid ${toRgba(palette.primary, 0.35)}`,
            borderRadius: 16,
            padding: "16px 20px",
            textAlign: "left",
          }}
        >
          <div style={{ fontFamily: monoFont, fontSize: 13, color: toRgba(palette.subtext, 0.8) }}>
            {metricLabel.toUpperCase()}
          </div>
          <div style={{ fontFamily: monoFont, fontSize: 26, fontWeight: 800, color: "#10b981", marginTop: 4 }}>
            {metricVal}
          </div>
        </div>
      </div>

      {/* Pro Tip Card */}
      {proTip && (
        <div
          style={{
            marginTop: 20,
            width: "100%",
            maxWidth: 920,
            fontFamily: headingFont,
            fontSize: 20,
            fontWeight: 600,
            color: "#ffffff",
            backgroundColor: toRgba(palette.surface, 0.85),
            border: `1.5px solid ${toRgba(palette.accent, 0.5)}`,
            borderRadius: 16,
            padding: "14px 28px",
            boxShadow: `0 0 30px ${toRgba(palette.accent, 0.2)}`,
            textAlign: "left",
            display: "flex",
            alignItems: "center",
            gap: 12,
            opacity: spring({ frame: frame - 25, fps }),
          }}
        >
          <span style={{ fontSize: 24 }}>💡</span>
          <div>
            <span style={{ color: toRgba(palette.accent, 1), fontWeight: 700 }}>Pro Insight: </span>
            <span>{proTip}</span>
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};
