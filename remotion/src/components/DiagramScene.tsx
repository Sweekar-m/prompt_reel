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
  const variant = scene.composition_variant || (scene.visual_recipe?.layout_grammar?.composition_variant) || "vertical_pipeline";

  const title = (elems.title as string) || "SYSTEM ARCHITECTURE & PIPELINE";
  const subtitle = (elems.subtitle as string) || "Instruction execution through hardware registers";
  const steps = (elems.steps as string[]) || [
    "Fetch instruction from cache into pipeline",
    "Evaluate operational invariants and data boundaries",
    "Commit zero-latency state transition",
  ];
  const metricLabel = (elems.metric_label as string) || "SYSTEM THROUGHPUT";
  const metricVal = (elems.metric_val as string) || "0.35 ns (1 CYCLE)";
  const proTip = (elems.pro_tip as string) || "Keep branch patterns predictable to maximize CPU instruction throughput.";

  const enterSpring = spring({
    frame,
    fps,
    config: { damping: 15, mass: 0.9, stiffness: 120 },
  });

  const headingFont = creativeDirection.typography?.heading || "Inter, sans-serif";
  const monoFont = creativeDirection.typography?.mono || "'JetBrains Mono', monospace";
  const activeStage = Math.min(steps.length - 1, Math.floor(frame / 22));

  // ── VARIANT 1: RADIAL SYSTEM (Hub & Spoke Network) ──────────────────────────
  if (variant === "radial_system") {
    const hubScale = spring({ frame, fps, config: { damping: 14, stiffness: 140 } });
    const satellites = steps.slice(0, 4);

    return (
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "60px",
          boxSizing: "border-box",
        }}
      >
        <div style={{ fontFamily: monoFont, fontSize: 18, color: toRgba(palette.primary, 1), fontWeight: 800, letterSpacing: "0.2em", marginBottom: 30 }}>
          ✦ {title.toUpperCase()} ✦
        </div>

        <div style={{ position: "relative", width: 800, height: 500, display: "flex", alignItems: "center", justifyContent: "center" }}>
          {/* Central Hub */}
          <div
            style={{
              width: 220,
              height: 220,
              borderRadius: "50%",
              backgroundColor: toRgba(palette.surface, 0.95),
              border: `3px solid ${toRgba(palette.accent, 0.9)}`,
              boxShadow: `0 0 60px ${toRgba(palette.accent, 0.4)}`,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              textAlign: "center",
              padding: 20,
              zIndex: 2,
              transform: `scale(${hubScale})`,
            }}
          >
            <span style={{ fontFamily: monoFont, fontSize: 13, color: toRgba(palette.accent, 1), fontWeight: 800 }}>CORE HUB</span>
            <span style={{ fontFamily: headingFont, fontSize: 22, fontWeight: 900, color: "#ffffff", marginTop: 4 }}>{metricVal}</span>
            <span style={{ fontFamily: monoFont, fontSize: 12, color: "#94a3b8", marginTop: 4 }}>{metricLabel}</span>
          </div>

          {/* Satellite Nodes */}
          {satellites.map((satText, sIdx) => {
            const angle = (sIdx * (360 / satellites.length)) * (Math.PI / 180);
            const radius = 280;
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius;
            const satSpring = spring({ frame: Math.max(0, frame - sIdx * 6), fps, config: { damping: 14, stiffness: 130 } });

            return (
              <div
                key={sIdx}
                style={{
                  position: "absolute",
                  left: `calc(50% + ${x}px - 140px)`,
                  top: `calc(50% + ${y}px - 50px)`,
                  width: 280,
                  padding: "16px 20px",
                  borderRadius: 16,
                  backgroundColor: toRgba(palette.surface, 0.9),
                  border: `1.5px solid ${toRgba(palette.primary, 0.5)}`,
                  boxShadow: `0 10px 30px rgba(0,0,0,0.6)`,
                  transform: `scale(${satSpring})`,
                }}
              >
                <div style={{ fontFamily: monoFont, fontSize: 12, color: toRgba(palette.primary, 1), fontWeight: 800 }}>NODE 0{sIdx + 1}</div>
                <div style={{ fontFamily: headingFont, fontSize: 16, fontWeight: 700, color: "#ffffff", marginTop: 4 }}>{satText}</div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    );
  }

  // ── VARIANT 2: HORIZONTAL FLOW (Left to Right Architecture Trace) ───────────
  if (variant === "horizontal_flow") {
    return (
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "60px 40px",
          boxSizing: "border-box",
        }}
      >
        <div style={{ fontFamily: monoFont, fontSize: 18, color: toRgba(palette.primary, 1), fontWeight: 800, letterSpacing: "0.2em", marginBottom: 12 }}>
          {title.toUpperCase()}
        </div>
        <p style={{ fontFamily: headingFont, fontSize: 26, color: toRgba(palette.text, 1), maxWidth: 860, textAlign: "center", marginBottom: 40 }}>
          {subtitle}
        </p>

        <div style={{ display: "flex", alignItems: "center", gap: 16, width: "100%", maxWidth: 1000, overflowX: "hidden" }}>
          {steps.map((st, idx) => {
            const isCur = idx === activeStage;
            const stSpring = spring({ frame: Math.max(0, frame - idx * 7), fps, config: { damping: 14, stiffness: 140 } });
            return (
              <React.Fragment key={idx}>
                <div
                  style={{
                    flex: 1,
                    backgroundColor: isCur ? toRgba(palette.primary, 0.2) : toRgba(palette.surface, 0.9),
                    border: isCur ? `2px solid ${toRgba(palette.accent, 1)}` : `1.5px solid ${toRgba(palette.primary, 0.4)}`,
                    borderRadius: 20,
                    padding: "24px 20px",
                    boxShadow: isCur ? `0 0 40px ${toRgba(palette.accent, 0.35)}` : "none",
                    transform: `scale(${stSpring})`,
                  }}
                >
                  <div style={{ fontFamily: monoFont, fontSize: 14, color: isCur ? toRgba(palette.accent, 1) : "#64748b", fontWeight: 800, marginBottom: 8 }}>
                    STAGE 0{idx + 1}
                  </div>
                  <div style={{ fontFamily: headingFont, fontSize: 20, fontWeight: 700, color: "#ffffff", lineHeight: 1.3 }}>
                    {st}
                  </div>
                </div>
                {idx < steps.length - 1 && (
                  <div style={{ color: toRgba(palette.primary, 0.8), fontSize: 24, fontWeight: 900 }}>
                    →
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>

        <div style={{ marginTop: 40, fontFamily: monoFont, fontSize: 16, color: "#22D3A5", backgroundColor: "rgba(34, 211, 165, 0.1)", padding: "10px 24px", borderRadius: 30, border: "1px solid #22D3A5" }}>
          TELEMETRY: {metricLabel} = {metricVal}
        </div>
      </AbsoluteFill>
    );
  }

  // ── VARIANT 3: METRIC BREAKDOWN (Central Stat with Radiating Cards) ──────────
  if (variant === "metric_breakdown") {
    return (
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "60px",
          boxSizing: "border-box",
        }}
      >
        <div style={{ backgroundColor: toRgba(palette.surface, 0.95), border: `2px solid ${toRgba(palette.accent, 0.8)}`, borderRadius: 30, padding: "36px 60px", textAlign: "center", boxShadow: `0 0 60px ${toRgba(palette.accent, 0.3)}`, transform: `scale(${enterSpring})`, marginBottom: 36 }}>
          <div style={{ fontFamily: monoFont, fontSize: 16, color: toRgba(palette.accent, 1), fontWeight: 800, letterSpacing: "0.2em", marginBottom: 8 }}>
            {metricLabel}
          </div>
          <div style={{ fontFamily: headingFont, fontSize: 68, fontWeight: 950, color: "#ffffff", lineHeight: 1 }}>
            {metricVal}
          </div>
          <div style={{ fontFamily: headingFont, fontSize: 22, color: toRgba(palette.subtext, 1), marginTop: 12 }}>
            {title}
          </div>
        </div>

        <div style={{ display: "flex", gap: 20, width: "100%", maxWidth: 960 }}>
          {steps.slice(0, 3).map((st, idx) => (
            <div key={idx} style={{ flex: 1, backgroundColor: toRgba(palette.surface, 0.9), border: `1.5px solid ${toRgba(palette.primary, 0.4)}`, borderRadius: 18, padding: "20px 24px" }}>
              <div style={{ fontFamily: monoFont, fontSize: 13, color: toRgba(palette.primary, 1), fontWeight: 800, marginBottom: 6 }}>
                INVARIANT 0{idx + 1}
              </div>
              <div style={{ fontFamily: headingFont, fontSize: 17, color: "#e2e8f0", fontWeight: 600, lineHeight: 1.3 }}>
                {st}
              </div>
            </div>
          ))}
        </div>
      </AbsoluteFill>
    );
  }

  // ── VARIANT 4: GRID MATRIX / VERTICAL PIPELINE (Default) ────────────────────
  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "flex-start",
        padding: "80px 50px 60px",
        textAlign: "center",
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          fontFamily: monoFont,
          fontSize: 20,
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

      <p style={{ fontFamily: headingFont, fontSize: 26, lineHeight: 1.4, fontWeight: 600, color: toRgba(palette.text, 1), maxWidth: 900, margin: "0 0 32px 0", opacity: enterSpring }}>
        {subtitle}
      </p>

      <div style={{ width: "100%", maxWidth: 920, display: "flex", flexDirection: "column", gap: 16, opacity: enterSpring }}>
        {steps.map((stepText, idx) => {
          const isActive = idx === activeStage;
          const isDone = idx < activeStage;
          const stepSpring = spring({ frame: Math.max(0, frame - idx * 6), fps, config: { damping: 14, stiffness: 140 } });

          return (
            <div
              key={idx}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 20,
                padding: "20px 24px",
                borderRadius: 18,
                backgroundColor: isActive ? toRgba(palette.primary, 0.16) : toRgba(palette.surface, 0.9),
                border: isActive ? `2px solid ${toRgba(palette.accent, 0.95)}` : `1.5px solid ${toRgba(palette.primary, 0.35)}`,
                boxShadow: isActive ? `0 0 35px ${toRgba(palette.accent, 0.3)}` : "none",
                transform: `scale(${stepSpring})`,
                textAlign: "left",
              }}
            >
              <div style={{ width: 42, height: 42, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: isDone ? "#22D3A5" : isActive ? toRgba(palette.accent, 1) : "rgba(255,255,255,0.1)", color: "#000", fontWeight: 900, fontFamily: monoFont }}>
                {isDone ? "✓" : idx + 1}
              </div>
              <div style={{ flex: 1, fontFamily: headingFont, fontSize: 22, fontWeight: 700, color: "#ffffff" }}>
                {stepText}
              </div>
            </div>
          );
        })}
      </div>

      <div style={{ marginTop: 28, display: "flex", gap: 16, opacity: enterSpring }}>
        <div style={{ backgroundColor: toRgba(palette.surface, 0.9), border: `1px solid ${toRgba(palette.primary, 0.4)}`, padding: "10px 22px", borderRadius: 20, fontFamily: monoFont, fontSize: 16, color: toRgba(palette.accent, 1) }}>
          {metricLabel}: {metricVal}
        </div>
      </div>
    </AbsoluteFill>
  );
};
