import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { SceneSchema, CreativeDirectionSchema } from "../types";
import { toRgba } from "../utils/colors";

export const CodeScene: React.FC<{
  scene: SceneSchema;
  creativeDirection: CreativeDirectionSchema;
}> = ({ scene, creativeDirection }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const palette = creativeDirection.palette;
  const elems = scene.elements || {};
  const variant = scene.composition_variant || (scene.visual_recipe?.layout_grammar?.composition_variant) || "centered_window";

  const filename = (elems.filename as string) || "main.py";
  const rawLines = (elems.lines as string[]) || [
    "function execute_pipeline() {",
    "  const state = allocate_buffer();",
    "  if (state.valid) {",
    "    commit_transaction(state);",
    "  }",
    "}",
  ];
  const highlightLine = Math.max(0, ((elems.highlight_line as number) || 3) - 1);
  const annotation = (elems.annotation as string) || "CPU branch evaluated in 1 cycle";
  const outputText = (elems.output_text as string) || "> Transaction committed [OK]";
  const varState = (elems.variable_state as { var_name?: string; var_value?: string; eval_result?: string }) || {
    var_name: "state",
    var_value: "0x7FA1",
    eval_result: "COMMITTED",
  };

  const windowSpring = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.9, stiffness: 120 },
  });

  const monoFont = creativeDirection.typography?.mono || "'JetBrains Mono', monospace";
  const headingFont = creativeDirection.typography?.heading || "Inter, sans-serif";

  // Typing effect
  const typeCharCount = Math.floor(
    interpolate(frame - 40, [0, 25], [0, outputText.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );
  const typedOutput = outputText.slice(0, typeCharCount);

  // ── VARIANT 1: SPLIT EXECUTION (Code on Left, Live Telemetry on Right) ──────
  if (variant === "split_execution") {
    return (
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "center",
          padding: "0 60px",
          gap: 36,
          boxSizing: "border-box",
        }}
      >
        {/* Left: Code Block */}
        <div
          style={{
            flex: 1.2,
            backgroundColor: toRgba(palette.surface, 0.95),
            border: `1.5px solid ${toRgba(palette.primary, 0.4)}`,
            borderRadius: 20,
            overflow: "hidden",
            boxShadow: `0 20px 60px rgba(0,0,0,0.7)`,
            transform: `scale(${windowSpring})`,
          }}
        >
          <div style={{ padding: "14px 20px", backgroundColor: "rgba(0,0,0,0.3)", borderBottom: `1px solid ${toRgba(palette.primary, 0.2)}`, display: "flex", justifyContent: "space-between" }}>
            <span style={{ fontFamily: monoFont, fontSize: 14, color: "#94a3b8" }}>{filename}</span>
            <span style={{ fontFamily: monoFont, fontSize: 13, color: toRgba(palette.accent, 1) }}>LIVE EXECUTION</span>
          </div>
          <div style={{ padding: "24px 28px", fontFamily: monoFont, fontSize: 18, lineHeight: 1.6 }}>
            {rawLines.slice(0, 7).map((line, lIdx) => {
              const isHighlight = lIdx === highlightLine;
              return (
                <div key={lIdx} style={{ display: "flex", gap: 16, backgroundColor: isHighlight ? toRgba(palette.primary, 0.15) : "transparent", padding: "4px 8px", borderRadius: 6 }}>
                  <span style={{ color: "#64748b", userSelect: "none", width: 24 }}>{lIdx + 1}</span>
                  <span style={{ color: isHighlight ? toRgba(palette.accent, 1) : "#ffffff", fontWeight: isHighlight ? 700 : 400 }}>{line}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Variable & Telemetry Inspector */}
        <div
          style={{
            flex: 0.8,
            display: "flex",
            flexDirection: "column",
            gap: 20,
            transform: `scale(${windowSpring})`,
          }}
        >
          <div style={{ backgroundColor: toRgba(palette.surface, 0.9), border: `1.5px solid ${toRgba(palette.accent, 0.6)}`, borderRadius: 20, padding: "24px 28px" }}>
            <div style={{ fontFamily: monoFont, fontSize: 14, color: toRgba(palette.accent, 1), fontWeight: 800, marginBottom: 8 }}>
              RUNTIME VARIABLE STATE
            </div>
            <div style={{ fontFamily: monoFont, fontSize: 26, fontWeight: 900, color: "#ffffff" }}>
              {varState.var_name}: <span style={{ color: toRgba(palette.primary, 1) }}>{varState.var_value}</span>
            </div>
            <div style={{ marginTop: 12, display: "inline-block", backgroundColor: "rgba(34, 211, 165, 0.15)", border: "1px solid #22D3A5", borderRadius: 8, padding: "4px 12px", fontFamily: monoFont, fontSize: 14, color: "#22D3A5" }}>
              ● {varState.eval_result}
            </div>
          </div>

          <div style={{ backgroundColor: "rgba(10, 14, 23, 0.95)", border: `1.5px solid ${toRgba(palette.primary, 0.3)}`, borderRadius: 20, padding: "20px 24px" }}>
            <div style={{ fontFamily: monoFont, fontSize: 13, color: "#64748b", marginBottom: 6 }}>
              CONSOLE STDOUT
            </div>
            <div style={{ fontFamily: monoFont, fontSize: 17, color: "#22D3A5" }}>
              {typedOutput}
            </div>
          </div>
        </div>
      </AbsoluteFill>
    );
  }

  // ── VARIANT 2: TERMINAL STREAM ──────────────────────────────────────────────
  if (variant === "terminal_stream") {
    return (
      <AbsoluteFill
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          padding: "0 60px",
          boxSizing: "border-box",
        }}
      >
        <div
          style={{
            width: "100%",
            maxWidth: 960,
            backgroundColor: "rgba(8, 12, 18, 0.98)",
            border: `2px solid ${toRgba(palette.primary, 0.7)}`,
            borderRadius: 20,
            padding: "36px 44px",
            boxShadow: `0 30px 80px rgba(0,0,0,0.85), 0 0 50px ${toRgba(palette.primary, 0.2)}`,
            transform: `scale(${windowSpring})`,
          }}
        >
          <div style={{ fontFamily: monoFont, fontSize: 18, color: toRgba(palette.primary, 1), marginBottom: 20 }}>
            $ gdb --batch -ex "disassemble" ./{filename}
          </div>
          <div style={{ fontFamily: monoFont, fontSize: 18, lineHeight: 1.6, color: "#e2e8f0" }}>
            {rawLines.slice(0, 6).map((l, idx) => (
              <div key={idx} style={{ color: idx === highlightLine ? toRgba(palette.accent, 1) : "#94a3b8" }}>
                0x0040{idx * 4}: {l} {idx === highlightLine ? `\t// ${annotation}` : ""}
              </div>
            ))}
          </div>
          <div style={{ marginTop: 24, paddingTop: 18, borderTop: "1px dashed rgba(255,255,255,0.15)", fontFamily: monoFont, fontSize: 18, color: "#22D3A5" }}>
            {typedOutput}
          </div>
        </div>
      </AbsoluteFill>
    );
  }

  // ── VARIANT 3: DIFF COMPARISON (Inefficient vs Optimized) ───────────────────
  if (variant === "diff_comparison") {
    const leftLines = (elems.left_code as string[]) || rawLines.slice(0, 4);
    const rightLines = (elems.right_code as string[]) || rawLines.slice(2, 6);

    return (
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "center",
          padding: "0 50px",
          gap: 28,
          boxSizing: "border-box",
        }}
      >
        <div style={{ flex: 1, backgroundColor: "rgba(244, 63, 94, 0.08)", border: "2px solid #F43F5E", borderRadius: 20, padding: "28px 24px", transform: `scale(${windowSpring})` }}>
          <div style={{ fontFamily: monoFont, fontSize: 15, color: "#F43F5E", fontWeight: 800, marginBottom: 12 }}>
            ✕ INEFFICIENT BEFORE (O(N))
          </div>
          <div style={{ fontFamily: monoFont, fontSize: 16, lineHeight: 1.5, color: "#e2e8f0" }}>
            {leftLines.map((l, idx) => (
              <div key={idx}>- {l}</div>
            ))}
          </div>
        </div>

        <div style={{ flex: 1, backgroundColor: "rgba(34, 211, 165, 0.08)", border: "2px solid #22D3A5", borderRadius: 20, padding: "28px 24px", transform: `scale(${windowSpring})` }}>
          <div style={{ fontFamily: monoFont, fontSize: 15, color: "#22D3A5", fontWeight: 800, marginBottom: 12 }}>
            ✓ OPTIMIZED AFTER (O(1))
          </div>
          <div style={{ fontFamily: monoFont, fontSize: 16, lineHeight: 1.5, color: "#ffffff" }}>
            {rightLines.map((l, idx) => (
              <div key={idx}>+ {l}</div>
            ))}
          </div>
        </div>
      </AbsoluteFill>
    );
  }

  // ── VARIANT 4: MINIMAL FLOATING / CENTERED WINDOW (Default) ─────────────────
  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 50px",
        gap: 20,
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: 960,
          backgroundColor: toRgba(palette.surface, 0.96),
          border: `1.5px solid ${toRgba(palette.primary, 0.45)}`,
          borderRadius: 24,
          boxShadow: `0 24px 70px rgba(0, 0, 0, 0.7), 0 0 50px ${toRgba(palette.primary, 0.2)}`,
          overflow: "hidden",
          transform: `scale(${windowSpring})`,
        }}
      >
        <div style={{ padding: "16px 24px", backgroundColor: "rgba(0,0,0,0.3)", borderBottom: `1px solid ${toRgba(palette.primary, 0.2)}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", gap: 8 }}>
            <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: "#EF4444" }} />
            <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: "#F59E0B" }} />
            <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: "#22D3A5" }} />
          </div>
          <div style={{ fontFamily: monoFont, fontSize: 14, color: "#94a3b8" }}>{filename}</div>
          <div style={{ width: 40 }} />
        </div>

        <div style={{ padding: "28px 36px", fontFamily: monoFont, fontSize: 20, lineHeight: 1.6 }}>
          {rawLines.slice(0, 7).map((line, lIdx) => {
            const isHighlight = lIdx === highlightLine;
            return (
              <div key={lIdx} style={{ display: "flex", gap: 16, backgroundColor: isHighlight ? toRgba(palette.primary, 0.15) : "transparent", padding: "4px 8px", borderRadius: 6 }}>
                <span style={{ color: "#64748b", userSelect: "none", width: 28 }}>{lIdx + 1}</span>
                <span style={{ color: isHighlight ? toRgba(palette.accent, 1) : "#ffffff", fontWeight: isHighlight ? 800 : 400 }}>{line}</span>
              </div>
            );
          })}
        </div>
      </div>

      <div style={{ width: "100%", maxWidth: 960, display: "flex", justifyContent: "space-between", gap: 20 }}>
        <div style={{ flex: 1, backgroundColor: "rgba(0,0,0,0.4)", border: `1px solid ${toRgba(palette.primary, 0.3)}`, borderRadius: 16, padding: "14px 20px", fontFamily: monoFont, fontSize: 16, color: "#22D3A5" }}>
          {typedOutput}
        </div>
        <div style={{ backgroundColor: toRgba(palette.surface, 0.9), border: `1.5px solid ${toRgba(palette.accent, 0.6)}`, borderRadius: 16, padding: "14px 24px", fontFamily: monoFont, fontSize: 16, color: "#ffffff", fontWeight: 700 }}>
          {varState.var_name} = {varState.var_value} ({varState.eval_result})
        </div>
      </div>
    </AbsoluteFill>
  );
};
