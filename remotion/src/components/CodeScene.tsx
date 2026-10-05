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

  const filename = (elems.filename as string) || "Main.java";
  const rawLines = (elems.lines as string[]) || [
    "public class Main {",
    "  public static void main(String[] args) {",
    "    int x = 10;",
    "    if (x > 5) {",
    "      System.out.println(\"x is greater than 5\");",
    "    }",
    "  }",
    "}",
  ];
  const highlightLine = ((elems.highlight_line as number) || 4) - 1;
  const annotation = (elems.annotation as string) || "CPU branch evaluated in 1 cycle";
  const outputText = (elems.output_text as string) || "> x is greater than 5";
  const varState = (elems.variable_state as { var_name?: string; var_value?: string; eval_result?: string }) || {
    var_name: "x",
    var_value: "10",
    eval_result: "TRUE (1)",
  };

  const windowSpring = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.9, stiffness: 120 },
  });

  const monoFont = creativeDirection.typography?.mono || "JetBrains Mono, monospace";
  const headingFont = creativeDirection.typography?.heading || "Inter, sans-serif";

  // Dynamic execution phase:
  // Phase 1 (frame 0-30): Editor enters and lines appear
  // Phase 2 (frame 30-65): Laser sweeps down to condition line, evaluating condition
  // Phase 3 (frame 65+): Variable state badge locks TRUE, terminal window pops up and types output
  const execCycle = Math.max(0, frame - 25);
  const activeLineIndex = Math.min(
    rawLines.length - 1,
    Math.floor(interpolate(execCycle, [0, 45], [0, highlightLine], { extrapolateRight: "clamp" }))
  );

  const evalProgress = spring({
    frame: frame - 45,
    fps,
    config: { damping: 12, stiffness: 150 },
  });

  const terminalSpring = spring({
    frame: frame - 55,
    fps,
    config: { damping: 14, mass: 0.9, stiffness: 130 },
  });

  // Typing effect for terminal output
  const typeCharCount = Math.floor(
    interpolate(frame - 65, [0, 25], [0, outputText.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );
  const typedOutput = outputText.slice(0, typeCharCount);

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
      {/* Code Editor Window */}
      <div
        style={{
          width: "100%",
          maxWidth: 980,
          backgroundColor: toRgba(palette.surface, 0.96),
          border: `1.5px solid ${toRgba(palette.primary, 0.45)}`,
          borderRadius: 24,
          boxShadow: `0 24px 70px rgba(0, 0, 0, 0.7), 0 0 50px ${toRgba(palette.primary, 0.2)}`,
          overflow: "hidden",
          transform: `scale(${interpolate(windowSpring, [0, 1], [0.94, 1])})`,
          opacity: windowSpring,
          position: "relative",
        }}
      >
        {/* Window Title Bar */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "16px 24px",
            backgroundColor: toRgba(palette.background, 0.75),
            borderBottom: `1px solid ${toRgba(palette.surface, 0.8)}`,
          }}
        >
          {/* Traffic Lights */}
          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#ff5f56" }} />
            <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#ffbd2e" }} />
            <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#27c93f" }} />
            <span
              style={{
                fontFamily: monoFont,
                fontSize: 14,
                color: toRgba(palette.subtext, 0.7),
                marginLeft: 12,
                letterSpacing: "0.08em",
              }}
            >
              EXEC: LIVE TRACE
            </span>
          </div>

          {/* Filename & Language */}
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span
              style={{
                fontFamily: monoFont,
                fontSize: 18,
                fontWeight: 700,
                color: toRgba(palette.accent, 1),
                letterSpacing: "0.05em",
              }}
            >
              {filename}
            </span>
          </div>

          {/* Live Variable State Telemetry */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              backgroundColor: toRgba(palette.background, 0.8),
              padding: "4px 12px",
              borderRadius: 8,
              border: `1px solid ${toRgba(palette.primary, 0.3)}`,
            }}
          >
            <span style={{ fontFamily: monoFont, fontSize: 13, color: toRgba(palette.subtext, 0.8) }}>
              {varState.var_name || "val"} =
            </span>
            <span style={{ fontFamily: monoFont, fontSize: 13, color: toRgba(palette.primary, 1), fontWeight: 700 }}>
              {varState.var_value || "10"}
            </span>
          </div>
        </div>

        {/* Code Content */}
        <div
          style={{
            padding: "28px 24px",
            fontFamily: monoFont,
            fontSize: 24,
            lineHeight: 1.65,
            position: "relative",
          }}
        >
          {rawLines.slice(0, 9).map((line, idx) => {
            const isHighlight = idx === highlightLine;
            const isCurrentlyActive = idx === activeLineIndex;

            const lineSpring = spring({
              frame: frame - (idx * 3 + 6),
              fps,
              config: { damping: 14, stiffness: 140 },
            });

            return (
              <div
                key={idx}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "4px 14px",
                  borderRadius: 8,
                  backgroundColor:
                    isCurrentlyActive
                      ? toRgba(palette.primary, 0.22)
                      : isHighlight
                      ? toRgba(palette.accent, 0.12)
                      : "transparent",
                  borderLeft: isCurrentlyActive
                    ? `4px solid ${toRgba(palette.primary, 1)}`
                    : isHighlight
                    ? `4px solid ${toRgba(palette.accent, 0.8)}`
                    : "4px solid transparent",
                  opacity: lineSpring,
                  transform: `translateX(${interpolate(lineSpring, [0, 1], [-15, 0])}px)`,
                  transition: "background-color 0.2s ease",
                  position: "relative",
                }}
              >
                <div style={{ display: "flex", alignItems: "center" }}>
                  {/* Line number */}
                  <span
                    style={{
                      width: 42,
                      color: isCurrentlyActive
                        ? toRgba(palette.primary, 1)
                        : isHighlight
                        ? toRgba(palette.accent, 0.9)
                        : toRgba(palette.subtext, 0.5),
                      fontWeight: isCurrentlyActive || isHighlight ? 700 : 500,
                      userSelect: "none",
                      fontSize: 20,
                    }}
                  >
                    {idx + 1}
                  </span>

                  {/* Line text */}
                  <span
                    style={{
                      color: isCurrentlyActive
                        ? "#ffffff"
                        : isHighlight
                        ? toRgba(palette.primary, 1)
                        : toRgba(palette.text, 0.9),
                      fontWeight: isCurrentlyActive || isHighlight ? 700 : 400,
                      textShadow: isCurrentlyActive ? `0 0 15px ${toRgba(palette.primary, 0.7)}` : "none",
                    }}
                  >
                    {line}
                  </span>
                </div>

                {/* Inline condition evaluation tag */}
                {isHighlight && frame > 45 && (
                  <div
                    style={{
                      opacity: evalProgress,
                      transform: `scale(${interpolate(evalProgress, [0, 1], [0.8, 1])})`,
                      display: "flex",
                      alignItems: "center",
                      gap: 6,
                      backgroundColor: "#10b98125",
                      border: "1px solid #10b981",
                      padding: "2px 10px",
                      borderRadius: 6,
                      fontFamily: monoFont,
                      fontSize: 13,
                      fontWeight: 700,
                      color: "#10b981",
                      boxShadow: "0 0 15px #10b98140",
                    }}
                  >
                    <span>✓</span>
                    <span>{varState.eval_result || "TRUE"}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Interactive Floating Terminal / Console Window */}
      <div
        style={{
          width: "100%",
          maxWidth: 980,
          backgroundColor: "#090d16fa",
          border: `1.5px solid ${toRgba(palette.accent, 0.45)}`,
          borderRadius: 20,
          boxShadow: `0 16px 45px rgba(0, 0, 0, 0.8), 0 0 35px ${toRgba(palette.accent, 0.2)}`,
          overflow: "hidden",
          opacity: terminalSpring,
          transform: `translateY(${interpolate(terminalSpring, [0, 1], [25, 0])}px)`,
        }}
      >
        {/* Terminal Header */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "10px 20px",
            backgroundColor: "#050810",
            borderBottom: "1px solid rgba(255,255,255,0.08)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ color: "#10b981", fontSize: 13 }}>●</span>
            <span style={{ fontFamily: monoFont, fontSize: 14, fontWeight: 700, color: "#e2e8f0" }}>
              TERMINAL OUTPUT
            </span>
          </div>
          <span style={{ fontFamily: monoFont, fontSize: 12, color: "#64748b" }}>
            bash — 80x24 (0.00s)
          </span>
        </div>

        {/* Terminal Body */}
        <div
          style={{
            padding: "16px 20px",
            fontFamily: monoFont,
            fontSize: 20,
            lineHeight: 1.6,
            color: "#38bdf8",
          }}
        >
          <div style={{ color: "#94a3b8", fontSize: 16 }}>
            $ javac {filename} && java {filename.replace(/\.[^.]+$/, "")}
          </div>
          <div style={{ marginTop: 6, display: "flex", alignItems: "center", gap: 4 }}>
            <span style={{ color: "#4ade80", fontWeight: 700 }}>{typedOutput}</span>
            {frame % 20 < 10 && <span style={{ color: "#38bdf8", fontWeight: 700 }}>_</span>}
          </div>
        </div>
      </div>

      {/* Note / Invariant Callout */}
      {annotation && (
        <div
          style={{
            fontFamily: headingFont,
            fontSize: 22,
            fontWeight: 600,
            color: toRgba(palette.accent, 1),
            backgroundColor: toRgba(palette.surface, 0.88),
            border: `1px solid ${toRgba(palette.accent, 0.4)}`,
            borderRadius: 14,
            padding: "10px 28px",
            boxShadow: `0 0 25px ${toRgba(palette.accent, 0.22)}`,
            opacity: spring({ frame: frame - 20, fps }),
          }}
        >
          ✦ Invariant: {annotation}
        </div>
      )}
    </AbsoluteFill>
  );
};
