import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { SceneSchema, CreativeDirectionSchema, VisualRecipeSchema } from "../types";
import { toRgba } from "../utils/colors";

export const VisualRecipeScene: React.FC<{
  scene: SceneSchema;
  creativeDirection: CreativeDirectionSchema;
  recipe: VisualRecipeSchema;
}> = ({ scene, creativeDirection, recipe }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const palette = creativeDirection.palette;

  const headingFont = creativeDirection.typography?.heading || "Outfit, sans-serif";
  const monoFont = creativeDirection.typography?.mono || "JetBrains Mono, monospace";

  const durationFrames = Math.max(1, Math.round(recipe.duration_sec * fps));
  const progress = Math.min(1, Math.max(0, frame / durationFrames));

  // ── 1. Enter and Primitive Motion Calculations ──────────────────────────────
  const enterSpring = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.85, stiffness: 150 },
  });

  const settleSpring = spring({
    frame: Math.max(0, frame - 8),
    fps,
    config: { damping: 16, mass: 1.0, stiffness: 130 },
  });

  // ── 2. Camera Coordinates for this Shot ────────────────────────────────────
  const camStart = recipe.camera.start;
  const camEnd = recipe.camera.end;
  const camT = interpolate(frame, [0, durationFrames], [0, 1], {
    extrapolateRight: "clamp",
  });

  const shotCamX = interpolate(camT, [0, 1], [camStart.x, camEnd.x]);
  const shotCamY = interpolate(camT, [0, 1], [camStart.y, camEnd.y]);
  const shotCamZ = interpolate(camT, [0, 1], [camStart.z, camEnd.z]);
  const shotCamPitch = interpolate(camT, [0, 1], [camStart.pitch, camEnd.pitch]);
  const shotCamYaw = interpolate(camT, [0, 1], [camStart.yaw, camEnd.yaw]);
  const shotCamRoll = interpolate(camT, [0, 1], [camStart.roll, camEnd.roll]);
  const shotScale = interpolate(camT, [0, 1], [camStart.scale || 1.0, camEnd.scale || 1.0]);

  // Motion Blur calculation based on velocity
  const blurMagnitude = recipe.camera.motion_blur || 0.0;
  const activeBlurPx = Math.sin(camT * Math.PI) * (blurMagnitude * 12);

  // ── 3. Typography Calculations ─────────────────────────────────────────────
  const typo = recipe.typography;
  const words = (typo.headline || "").split(" ");
  const isUppercase = typo.case === "uppercase";

  // ── 4. Composition Styles ──────────────────────────────────────────────────
  const comp = recipe.composition;
  const isLeftWeighted = comp === "asymmetric_left" || comp === "stacked" || comp === "edge_anchored";
  const isSplit = comp === "split_contrast";
  const isSpatialDepth = comp === "spatial_depth";

  // ── 5. Render Primary Subject Component ────────────────────────────────────
  const renderPrimarySubject = () => {
    const subj = recipe.primary_subject;
    const props = subj.properties || {};

    // ── A. Branching Logic (e.g. Java if-else) ───────────────────────────────
    if (subj.type === "branching_logic") {
      const conditionExpr = props.condition_expr || "x > 10";
      const activePath = props.active_path || "TRUE";
      const pulseT = (frame % 30) / 30;
      const pulsePos = interpolate(pulseT, [0, 1], [0, 100]);

      return (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: isLeftWeighted ? "flex-start" : "center",
            gap: 20,
            width: "100%",
            maxWidth: 860,
          }}
        >
          {/* Top Decision Gate Pill */}
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 12,
              padding: "14px 28px",
              borderRadius: 40,
              backgroundColor: toRgba(palette.surface, 0.95),
              border: `2px solid ${toRgba(palette.primary, 0.8)}`,
              boxShadow: `0 0 30px ${toRgba(palette.primary, 0.35)}`,
              transform: `scale(${enterSpring})`,
            }}
          >
            <span style={{ fontFamily: monoFont, fontSize: 16, color: toRgba(palette.primary, 1), fontWeight: 800 }}>
              BRANCH GATE
            </span>
            <span style={{ fontFamily: monoFont, fontSize: 26, color: "#ffffff", fontWeight: 900 }}>
              {conditionExpr}
            </span>
          </div>

          {/* Branch Fork Network */}
          <div
            style={{
              display: "flex",
              gap: 24,
              width: "100%",
              justifyContent: isLeftWeighted ? "flex-start" : "center",
            }}
          >
            {/* TRUE Branch */}
            <div
              style={{
                flex: 1,
                maxWidth: 400,
                padding: "24px 20px",
                borderRadius: 20,
                backgroundColor: activePath === "TRUE" ? "rgba(34, 211, 165, 0.12)" : "rgba(18, 24, 38, 0.6)",
                border: activePath === "TRUE" ? "2px solid #22D3A5" : "1.5px solid rgba(255,255,255,0.1)",
                boxShadow: activePath === "TRUE" ? "0 0 40px rgba(34, 211, 165, 0.3)" : "none",
                transform: `scale(${settleSpring})`,
              }}
            >
              <div style={{ fontFamily: monoFont, fontSize: 15, color: "#22D3A5", fontWeight: 800, marginBottom: 8 }}>
                ✓ TRUE BRANCH (TAKEN)
              </div>
              <div style={{ fontFamily: headingFont, fontSize: 22, color: "#ffffff", fontWeight: 700, lineHeight: 1.3 }}>
                {props.left_branch || "Execute target block"}
              </div>
              <div style={{ marginTop: 12, fontFamily: monoFont, fontSize: 14, color: "#94a3b8" }}>
                CPU: 1 branch cycle
              </div>
            </div>

            {/* FALSE Branch */}
            <div
              style={{
                flex: 1,
                maxWidth: 400,
                padding: "24px 20px",
                borderRadius: 20,
                backgroundColor: activePath === "FALSE" ? "rgba(244, 63, 94, 0.12)" : "rgba(18, 24, 38, 0.4)",
                border: activePath === "FALSE" ? "2px solid #F43F5E" : "1.5px dashed rgba(255,255,255,0.08)",
                opacity: activePath === "FALSE" ? 1 : 0.45,
                transform: `scale(${settleSpring})`,
              }}
            >
              <div style={{ fontFamily: monoFont, fontSize: 15, color: "#F43F5E", fontWeight: 800, marginBottom: 8 }}>
                ✕ FALSE BRANCH (BYPASS)
              </div>
              <div style={{ fontFamily: headingFont, fontSize: 22, color: "#e2e8f0", fontWeight: 600, lineHeight: 1.3 }}>
                {props.right_branch || "Jump to else"}
              </div>
              <div style={{ marginTop: 12, fontFamily: monoFont, fontSize: 14, color: "#64748b" }}>
                Bypassed in instruction cache
              </div>
            </div>
          </div>
        </div>
      );
    }

    // ── B. 3D Spatial Stack (e.g. Docker Container Layers, Memory Heap) ───────
    if (subj.type === "spatial_3d_mesh") {
      const layers = (props.layers as string[]) || ["Layer 1", "Layer 2", "Layer 3"];
      const activeLayerIdx = props.active_layer_index || 0;

      return (
        <div
          style={{
            perspective: 1000,
            transformStyle: "preserve-3d",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 16,
            width: "100%",
            maxWidth: 820,
          }}
        >
          <div
            style={{
              fontFamily: monoFont,
              fontSize: 16,
              color: toRgba(palette.primary, 1),
              fontWeight: 800,
              letterSpacing: "0.2em",
              marginBottom: 8,
            }}
          >
            ✦ VOLUMETRIC CONTAINER STACK ✦
          </div>

          <div
            style={{
              transform: `rotateX(48deg) rotateZ(-32deg) scale(${enterSpring})`,
              display: "flex",
              flexDirection: "column-reverse",
              gap: 20,
              width: "100%",
              maxWidth: 620,
            }}
          >
            {layers.map((layerName, lIdx) => {
              const isSelected = lIdx === activeLayerIdx;
              const liftY = isSelected ? interpolate((frame % 45) / 45, [0, 0.5, 1], [-12, -28, -12]) : 0;

              return (
                <div
                  key={lIdx}
                  style={{
                    backgroundColor: isSelected
                      ? toRgba(palette.surface, 0.95)
                      : "rgba(18, 24, 38, 0.75)",
                    border: isSelected
                      ? `2px solid ${toRgba(palette.accent, 1)}`
                      : `1.5px solid ${toRgba(palette.primary, 0.35)}`,
                    borderRadius: 16,
                    padding: "24px 28px",
                    boxShadow: isSelected
                      ? `0 20px 50px rgba(0,0,0,0.8), 0 0 45px ${toRgba(palette.accent, 0.4)}`
                      : "0 10px 30px rgba(0,0,0,0.5)",
                    transform: `translate3d(0, ${liftY}px, ${lIdx * 35}px)`,
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <div>
                    <div style={{ fontFamily: monoFont, fontSize: 13, color: isSelected ? toRgba(palette.accent, 1) : "#94a3b8", fontWeight: 800 }}>
                      LAYER 0{lIdx + 1}
                    </div>
                    <div style={{ fontFamily: headingFont, fontSize: 24, fontWeight: 700, color: "#ffffff", marginTop: 4 }}>
                      {layerName}
                    </div>
                  </div>
                  <div
                    style={{
                      fontFamily: monoFont,
                      fontSize: 14,
                      color: isSelected ? toRgba(palette.accent, 1) : "#64748b",
                      padding: "6px 14px",
                      borderRadius: 20,
                      backgroundColor: "rgba(0,0,0,0.4)",
                    }}
                  >
                    {isSelected ? "MOUNTED READ-WRITE" : "IMMUTABLE RO"}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      );
    }

    // ── C. Data Flow / Spatial Search (e.g. Binary Search Partition) ──────────
    if (subj.type === "data_flow") {
      const arr = (props.array_elements as number[]) || [2, 7, 12, 19, 24, 38, 45, 56, 71, 88];
      const midIdx = props.mid_idx || Math.floor(arr.length / 2);
      const targetVal = props.target_val || 45;

      return (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: isLeftWeighted ? "flex-start" : "center",
            gap: 20,
            width: "100%",
            maxWidth: 920,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", width: "100%", alignItems: "center" }}>
            <span style={{ fontFamily: monoFont, fontSize: 16, color: toRgba(palette.primary, 1), fontWeight: 800, letterSpacing: "0.15em" }}>
              TARGET: {targetVal}
            </span>
            <span style={{ fontFamily: monoFont, fontSize: 16, color: toRgba(palette.accent, 1), fontWeight: 800 }}>
              {props.complexity_stat || "O(log N) SEARCH"}
            </span>
          </div>

          {/* Partition Array Grid */}
          <div
            style={{
              display: "flex",
              gap: 10,
              width: "100%",
              overflowX: "hidden",
              padding: "16px 0",
              transform: `scale(${enterSpring})`,
            }}
          >
            {arr.map((val, aIdx) => {
              const isMid = aIdx === midIdx;
              const isEliminated = aIdx < midIdx;
              return (
                <div
                  key={aIdx}
                  style={{
                    flex: 1,
                    minWidth: 60,
                    height: 80,
                    borderRadius: 14,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    backgroundColor: isMid
                      ? toRgba(palette.accent, 0.25)
                      : isEliminated
                      ? "rgba(18, 24, 38, 0.25)"
                      : toRgba(palette.surface, 0.9),
                    border: isMid
                      ? `2px solid ${toRgba(palette.accent, 1)}`
                      : isEliminated
                      ? "1px dashed rgba(255,255,255,0.1)"
                      : `1.5px solid ${toRgba(palette.primary, 0.4)}`,
                    boxShadow: isMid ? `0 0 35px ${toRgba(palette.accent, 0.4)}` : "none",
                    opacity: isEliminated ? 0.35 : 1,
                    transform: isMid ? "translateY(-10px) scale(1.08)" : "none",
                  }}
                >
                  <span style={{ fontFamily: monoFont, fontSize: 24, fontWeight: 900, color: isMid ? toRgba(palette.accent, 1) : "#ffffff" }}>
                    {val}
                  </span>
                  <span style={{ fontFamily: monoFont, fontSize: 11, color: "#64748b", marginTop: 4 }}>
                    [{aIdx}]
                  </span>
                </div>
              );
            })}
          </div>

          <div style={{ fontFamily: monoFont, fontSize: 18, color: "#94a3b8" }}>
            Midpoint index [{midIdx}] evaluates: {arr[midIdx]} {'<'} {targetVal} → Eliminate left partition
          </div>
        </div>
      );
    }

    // ── D. Dynamic Product UI / API Pipeline ──────────────────────────────────
    if (subj.type === "ui_panel") {
      const endpoint = props.endpoint || "/api/v1/resource";
      const method = props.method || "GET";
      const latency = props.latency_ms || 14.2;

      return (
        <div
          style={{
            width: "100%",
            maxWidth: 880,
            backgroundColor: toRgba(palette.surface, 0.96),
            border: `1.5px solid ${toRgba(palette.primary, 0.45)}`,
            borderRadius: 22,
            boxShadow: `0 24px 70px rgba(0, 0, 0, 0.75), 0 0 45px ${toRgba(palette.primary, 0.2)}`,
            overflow: "hidden",
            transform: `scale(${enterSpring})`,
          }}
        >
          {/* OS Window Header */}
          <div
            style={{
              padding: "16px 24px",
              borderBottom: `1px solid ${toRgba(palette.primary, 0.2)}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              backgroundColor: "rgba(0,0,0,0.3)",
            }}
          >
            <div style={{ display: "flex", gap: 8 }}>
              <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: "#EF4444" }} />
              <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: "#F59E0B" }} />
              <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: "#22D3A5" }} />
            </div>
            <div style={{ fontFamily: monoFont, fontSize: 14, color: "#94a3b8" }}>
              HTTP/2 TELEMETRY TRACE
            </div>
            <div style={{ fontFamily: monoFont, fontSize: 13, color: "#22D3A5", fontWeight: 700 }}>
              200 OK • {latency}ms
            </div>
          </div>

          {/* URL & Method Row */}
          <div style={{ padding: "24px 28px", display: "flex", alignItems: "center", gap: 16 }}>
            <span
              style={{
                fontFamily: monoFont,
                fontSize: 16,
                fontWeight: 800,
                color: method === "GET" ? "#22D3A5" : toRgba(palette.accent, 1),
                backgroundColor: "rgba(0,0,0,0.5)",
                padding: "8px 18px",
                borderRadius: 10,
                border: "1px solid rgba(255,255,255,0.1)",
              }}
            >
              {method}
            </span>
            <span style={{ fontFamily: monoFont, fontSize: 22, color: "#ffffff", fontWeight: 700 }}>
              {endpoint}
            </span>
          </div>
        </div>
      );
    }

    // ── Default Graphic Subject ──────────────────────────────────────────────
    return (
      <div
        style={{
          display: "flex",
          gap: 16,
          alignItems: "center",
          transform: `scale(${enterSpring})`,
        }}
      >
        <div
          style={{
            fontFamily: monoFont,
            fontSize: 20,
            fontWeight: 800,
            color: toRgba(palette.primary, 1),
            padding: "10px 24px",
            borderRadius: 30,
            border: `1.5px solid ${toRgba(palette.primary, 0.4)}`,
            backgroundColor: toRgba(palette.surface, 0.9),
          }}
        >
          ✦ SYSTEM CORE: {recipe.beat_name.toUpperCase()}
        </div>
      </div>
    );
  };

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: isLeftWeighted ? "flex-start" : "center",
        justifyContent: "center",
        padding: isLeftWeighted ? "0 80px" : "0 60px",
        textAlign: isLeftWeighted ? "left" : "center",
        boxSizing: "border-box",
        overflow: "hidden",
        transform: `translate3d(${shotCamX}px, ${shotCamY}px, ${shotCamZ}px) rotateX(${shotCamPitch}deg) rotateY(${shotCamYaw}deg) rotateZ(${shotCamRoll}deg) scale(${shotScale})`,
        filter: activeBlurPx > 1.5 ? `blur(${activeBlurPx.toFixed(1)}px)` : "none",
      }}
    >
      {/* ── TOP BADGE & CATEGORY ANCHOR ── */}
      {typo.badge && (
        <div
          style={{
            fontFamily: monoFont,
            fontSize: 16,
            fontWeight: 800,
            letterSpacing: "0.22em",
            color: toRgba(palette.primary, 1),
            backgroundColor: toRgba(palette.surface, 0.9),
            border: `1.5px solid ${toRgba(palette.primary, 0.4)}`,
            padding: "8px 22px",
            borderRadius: 30,
            marginBottom: 24,
            transform: `scale(${enterSpring})`,
          }}
        >
          ✦ {typo.badge.toUpperCase()} ✦
        </div>
      )}

      {/* ── KINETIC HEADLINE (WORD-BY-WORD REVEAL WITH STAGGER) ── */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: isLeftWeighted ? "flex-start" : "center",
          gap: 14,
          maxWidth: 960,
          marginBottom: 28,
        }}
      >
        {words.map((word, wIdx) => {
          const wordSpring = spring({
            frame: Math.max(0, frame - wIdx * (typo.stagger_frames || 3)),
            fps,
            config: { damping: 13, mass: 0.8, stiffness: 170 },
          });
          const isAccent = (typo.highlight_word_indices || []).includes(wIdx) || wIdx === words.length - 1;

          return (
            <span
              key={wIdx}
              style={{
                fontFamily: headingFont,
                fontSize: words.length > 5 ? 58 : 78,
                fontWeight: 900,
                letterSpacing: typo.letter_spacing || "-0.02em",
                color: isAccent ? toRgba(palette.accent, 1) : "#ffffff",
                textShadow: isAccent
                  ? `0 0 45px ${toRgba(palette.accent, 0.6)}`
                  : "0 4px 20px rgba(0,0,0,0.8)",
                transform: `scale(${wordSpring}) translateY(${(1 - wordSpring) * 25}px)`,
                opacity: wordSpring,
                display: "inline-block",
              }}
            >
              {isUppercase ? word.toUpperCase() : word}
            </span>
          );
        })}
      </div>

      {/* ── PRIMARY SUBJECT VISUALIZATION ── */}
      <div style={{ marginTop: 12, marginBottom: 28, width: "100%", display: "flex", justifyContent: isLeftWeighted ? "flex-start" : "center" }}>
        {renderPrimarySubject()}
      </div>

      {/* ── SUBTEXT NARRATIVE STATEMENT ── */}
      {typo.subtext && (
        <div
          style={{
            fontFamily: headingFont,
            fontSize: 24,
            fontWeight: 500,
            color: "#cbd5e1",
            maxWidth: 820,
            lineHeight: 1.4,
            opacity: settleSpring,
            textShadow: "0 2px 10px rgba(0,0,0,0.8)",
          }}
        >
          {typo.subtext}
        </div>
      )}

      {/* ── SECONDARY HUD TELEMETRY LAYER ── */}
      {recipe.secondary_subjects && recipe.secondary_subjects.length > 0 && (
        <div
          style={{
            position: "absolute",
            bottom: 30,
            left: 40,
            right: 40,
            display: "flex",
            justifyContent: "space-between",
            fontFamily: monoFont,
            fontSize: 13,
            color: "#64748b",
            letterSpacing: "0.1em",
            opacity: settleSpring,
          }}
        >
          <span>TEMPLATE: {recipe.template_id.toUpperCase()}</span>
          <span>COMPOSITION: {recipe.composition.toUpperCase()}</span>
          <span>PACE: {recipe.pacing_style.toUpperCase()}</span>
        </div>
      )}
    </AbsoluteFill>
  );
};
