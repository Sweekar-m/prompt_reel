import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { SceneSchema, CreativeDirectionSchema } from "../types";
import { toRgba } from "../utils/colors";

export const MetaphorScene: React.FC<{
  scene: SceneSchema;
  creativeDirection: CreativeDirectionSchema;
}> = ({ scene, creativeDirection }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const palette = creativeDirection.palette;
  const elems = scene.elements || {};

  const label = (elems.label as string) || scene.beat_name || "UNDER THE HOOD";
  const description = (elems.description as string) || "Hardware execution and mental model simulation.";
  const simulationType = (elems.simulation_type as string) || (elems.metaphor_id as string) || "decision_gate";
  const hardwareReality = (elems.hardware_reality as string) || "Instruction pipeline branches in 1 CPU cycle.";

  const enterSpring = spring({
    frame,
    fps,
    config: { damping: 15, mass: 0.9, stiffness: 120 },
  });

  const headingFont = creativeDirection.typography?.heading || "Inter, sans-serif";
  const monoFont = creativeDirection.typography?.mono || "JetBrains Mono, monospace";

  // Render specific interactive simulation based on topic
  const renderSimulation = () => {
    if (simulationType.includes("stack") || simulationType.includes("recur") || simulationType.includes("memory")) {
      // ─────────────────────────────────────────────────────────────
      // SIMULATION 1: 3D CALL STACK / MEMORY ALLOCATION
      // ─────────────────────────────────────────────────────────────
      return (
        <div style={{ display: "flex", flexDirection: "column-reverse", gap: 14, width: "88%", alignItems: "center" }}>
          {[1, 2, 3, 4].map((idx) => {
            const frameDelay = idx * 10;
            const frameActive = frame > frameDelay;
            const frameProg = spring({ frame: frame - frameDelay, fps, config: { damping: 14, stiffness: 140 } });
            const isTop = idx === 4;

            return (
              <div
                key={idx}
                style={{
                  width: `${88 - idx * 5}%`,
                  height: 80,
                  backgroundColor: isTop ? toRgba(palette.primary, 0.28) : toRgba(palette.surface, 0.88),
                  border: `2px solid ${isTop ? toRgba(palette.accent, 0.95) : toRgba(palette.primary, 0.5)}`,
                  borderRadius: 16,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "0 28px",
                  boxShadow: isTop ? `0 0 35px ${toRgba(palette.accent, 0.45)}` : "none",
                  opacity: frameActive ? frameProg : 0,
                  transform: `scale(${frameActive ? frameProg : 0.8})`,
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <span style={{ fontFamily: monoFont, fontSize: 16, color: toRgba(palette.accent, 1), fontWeight: 700 }}>
                    0x7FFF{idx * 16}
                  </span>
                  <span style={{ fontFamily: monoFont, fontSize: 22, color: "#fff", fontWeight: 700 }}>
                    Frame #{idx}: recurse(n={5 - idx})
                  </span>
                </div>
                <span
                  style={{
                    fontFamily: monoFont,
                    fontSize: 15,
                    color: isTop ? "#10b981" : toRgba(palette.subtext, 1),
                    fontWeight: 700,
                    backgroundColor: isTop ? "#10b98125" : "rgba(255,255,255,0.06)",
                    padding: "4px 12px",
                    borderRadius: 8,
                  }}
                >
                  {isTop ? "● ACTIVE PC" : "STACKED"}
                </span>
              </div>
            );
          })}
        </div>
      );
    } else if (simulationType.includes("array") || simulationType.includes("search") || simulationType.includes("sort")) {
      // ─────────────────────────────────────────────────────────────
      // SIMULATION 2: HOLOGRAPHIC ARRAY SEARCH & HALVING
      // ─────────────────────────────────────────────────────────────
      const items = [4, 9, 15, 23, 42, 58, 77, 91];
      const midIdx = 4;
      const targetIdx = 5;

      return (
        <div style={{ width: "90%", display: "flex", flexDirection: "column", alignItems: "center", gap: 24 }}>
          {/* Array Cell Grid */}
          <div style={{ display: "flex", gap: 10, justifyContent: "center", width: "100%" }}>
            {items.map((val, i) => {
              const isDiscarded = frame > 35 && i < midIdx;
              const isTarget = i === targetIdx && frame > 55;
              const isMid = i === midIdx && frame > 20 && frame <= 55;

              return (
                <div
                  key={i}
                  style={{
                    flex: 1,
                    maxWidth: 100,
                    height: 105,
                    backgroundColor: isTarget
                      ? "#10b98135"
                      : isMid
                      ? toRgba(palette.accent, 0.3)
                      : isDiscarded
                      ? "rgba(20,20,30,0.4)"
                      : toRgba(palette.surface, 0.85),
                    border: `2px solid ${
                      isTarget
                        ? "#10b981"
                        : isMid
                        ? toRgba(palette.accent, 0.9)
                        : isDiscarded
                        ? "rgba(255,255,255,0.1)"
                        : toRgba(palette.primary, 0.5)
                    }`,
                    borderRadius: 14,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    position: "relative",
                    opacity: isDiscarded ? 0.35 : 1,
                    boxShadow: isTarget
                      ? "0 0 35px #10b98160"
                      : isMid
                      ? `0 0 30px ${toRgba(palette.accent, 0.4)}`
                      : "none",
                    transform: isTarget ? "scale(1.08)" : "scale(1)",
                  }}
                >
                  <span style={{ fontFamily: monoFont, fontSize: 13, color: toRgba(palette.subtext, 0.7), marginBottom: 4 }}>
                    [{i}]
                  </span>
                  <span
                    style={{
                      fontFamily: monoFont,
                      fontSize: 26,
                      fontWeight: 800,
                      color: isTarget ? "#10b981" : isDiscarded ? "#64748b" : "#ffffff",
                    }}
                  >
                    {val}
                  </span>
                  {isMid && (
                    <span
                      style={{
                        position: "absolute",
                        bottom: -22,
                        fontFamily: monoFont,
                        fontSize: 11,
                        fontWeight: 700,
                        color: toRgba(palette.accent, 1),
                      }}
                    >
                      MID
                    </span>
                  )}
                  {isTarget && (
                    <span
                      style={{
                        position: "absolute",
                        bottom: -22,
                        fontFamily: monoFont,
                        fontSize: 11,
                        fontWeight: 700,
                        color: "#10b981",
                      }}
                    >
                      MATCH
                    </span>
                  )}
                </div>
              );
            })}
          </div>

          {/* Search telemetry */}
          <div
            style={{
              display: "flex",
              gap: 20,
              backgroundColor: toRgba(palette.surface, 0.9),
              padding: "12px 28px",
              borderRadius: 16,
              border: `1px solid ${toRgba(palette.primary, 0.3)}`,
              fontFamily: monoFont,
              fontSize: 18,
            }}
          >
            <span style={{ color: toRgba(palette.subtext, 0.8) }}>Search Space:</span>
            <span style={{ color: toRgba(palette.primary, 1), fontWeight: 700 }}>
              {frame > 35 ? "N / 2 (4 items)" : "N (8 items)"}
            </span>
            <span style={{ color: toRgba(palette.accent, 1), fontWeight: 700 }}>➔ O(log N) Steps: 3</span>
          </div>
        </div>
      );
    } else if (simulationType.includes("loop") || simulationType.includes("turbine")) {
      // ─────────────────────────────────────────────────────────────
      // SIMULATION 3: HIGH-SPEED LOOP TURBINE
      // ─────────────────────────────────────────────────────────────
      const rotation = (frame * 6) % 360;
      const iteration = Math.floor(frame / 6);

      return (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 24 }}>
          <div style={{ position: "relative", width: 340, height: 340, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <div
              style={{
                position: "absolute",
                inset: 0,
                borderRadius: "50%",
                border: `3px dashed ${toRgba(palette.primary, 0.6)}`,
                transform: `rotate(${rotation}deg)`,
              }}
            />
            <div
              style={{
                position: "absolute",
                inset: 24,
                borderRadius: "50%",
                border: `2px solid ${toRgba(palette.accent, 0.7)}`,
                boxShadow: `0 0 35px ${toRgba(palette.accent, 0.3)}`,
              }}
            />
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                textAlign: "center",
              }}
            >
              <span style={{ fontFamily: monoFont, fontSize: 16, color: toRgba(palette.subtext, 0.8) }}>ITERATION</span>
              <span style={{ fontFamily: monoFont, fontSize: 56, fontWeight: 900, color: "#fff" }}>i = {iteration}</span>
              <span style={{ fontFamily: monoFont, fontSize: 15, color: "#10b981", fontWeight: 700 }}>UNROLL OPTIMAL</span>
            </div>
          </div>
        </div>
      );
    } else if (simulationType.includes("heap") || simulationType.includes("object") || simulationType.includes("class")) {
      // ─────────────────────────────────────────────────────────────
      // SIMULATION 4: 3D HEAP OBJECT ALLOCATION & VTABLE
      // ─────────────────────────────────────────────────────────────
      const allocProgress = spring({ frame: frame - 15, fps, config: { damping: 14, stiffness: 120 } });
      const obj2Progress = spring({ frame: frame - 35, fps, config: { damping: 14, stiffness: 120 } });

      return (
        <div style={{ width: "92%", display: "flex", flexDirection: "column", alignItems: "center", gap: 20 }}>
          {/* Class Blueprint */}
          <div
            style={{
              width: "100%",
              maxWidth: 780,
              backgroundColor: "rgba(15, 20, 32, 0.9)",
              border: `2px dashed ${toRgba(palette.primary, 0.6)}`,
              borderRadius: 16,
              padding: "16px 24px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              boxShadow: `0 0 30px ${toRgba(palette.primary, 0.2)}`,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
              <span style={{ fontSize: 24 }}>🏛️</span>
              <div>
                <span style={{ fontFamily: monoFont, fontSize: 13, color: toRgba(palette.accent, 1), fontWeight: 700 }}>
                  BLUEPRINT (METASPACE)
                </span>
                <div style={{ fontFamily: monoFont, fontSize: 20, fontWeight: 800, color: "#fff" }}>
                  class User &#123; id, name, vtable &#125;
                </div>
              </div>
            </div>
            <span
              style={{
                fontFamily: monoFont,
                fontSize: 12,
                color: "#10b981",
                backgroundColor: "rgba(16, 185, 129, 0.15)",
                padding: "6px 14px",
                borderRadius: 8,
                border: "1px solid rgba(16, 185, 129, 0.3)",
                fontWeight: 700,
              }}
            >
              TYPE LOADED
            </span>
          </div>

          {/* Allocation Conduit Arrow */}
          <div style={{ display: "flex", alignItems: "center", gap: 8, fontFamily: monoFont, fontSize: 13, color: toRgba(palette.subtext, 0.8) }}>
            <span>▼ new User("Alice")</span>
            <span style={{ color: toRgba(palette.primary, 1) }}>➔ HEAP ALLOCATOR (16B Header) ➔</span>
          </div>

          {/* Heap Memory Instances */}
          <div style={{ display: "flex", gap: 18, width: "100%", maxWidth: 780 }}>
            {/* Instance 1 */}
            <div
              style={{
                flex: 1,
                backgroundColor: toRgba(palette.surface, 0.92),
                border: `2px solid ${toRgba(palette.primary, 0.8)}`,
                borderRadius: 18,
                padding: "20px 22px",
                opacity: allocProgress,
                transform: `scale(${allocProgress})`,
                boxShadow: `0 10px 40px ${toRgba(palette.primary, 0.25)}`,
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <span style={{ fontFamily: monoFont, fontSize: 14, color: toRgba(palette.accent, 1), fontWeight: 700 }}>
                  0x7FA3A010
                </span>
                <span style={{ fontFamily: monoFont, fontSize: 12, color: "#10b981", fontWeight: 700 }}>
                  LIVE HEAP
                </span>
              </div>
              <div style={{ fontFamily: monoFont, fontSize: 22, fontWeight: 800, color: "#fff", marginBottom: 8 }}>
                User #1
              </div>
              <div style={{ fontFamily: monoFont, fontSize: 13, color: toRgba(palette.subtext, 0.9), lineHeight: 1.6 }}>
                <div>• MarkWord: 0x01 (Unlocked)</div>
                <div>• KlassPtr: ➔ User.class</div>
                <div>• Field [id]: "usr_981"</div>
              </div>
            </div>

            {/* Instance 2 */}
            <div
              style={{
                flex: 1,
                backgroundColor: toRgba(palette.surface, 0.92),
                border: `2px solid ${toRgba(palette.accent, 0.8)}`,
                borderRadius: 18,
                padding: "20px 22px",
                opacity: obj2Progress,
                transform: `scale(${obj2Progress})`,
                boxShadow: `0 10px 40px ${toRgba(palette.accent, 0.25)}`,
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <span style={{ fontFamily: monoFont, fontSize: 14, color: toRgba(palette.accent, 1), fontWeight: 700 }}>
                  0x7FA3B048
                </span>
                <span style={{ fontFamily: monoFont, fontSize: 12, color: "#10b981", fontWeight: 700 }}>
                  LIVE HEAP
                </span>
              </div>
              <div style={{ fontFamily: monoFont, fontSize: 22, fontWeight: 800, color: "#fff", marginBottom: 8 }}>
                User #2
              </div>
              <div style={{ fontFamily: monoFont, fontSize: 13, color: toRgba(palette.subtext, 0.9), lineHeight: 1.6 }}>
                <div>• MarkWord: 0x01 (Unlocked)</div>
                <div>• KlassPtr: ➔ User.class</div>
                <div>• Field [id]: "usr_982"</div>
              </div>
            </div>
          </div>

          {/* Vtable & Reference Telemetry */}
          <div
            style={{
              width: "100%",
              maxWidth: 780,
              backgroundColor: "rgba(0,0,0,0.45)",
              border: `1px solid ${toRgba(palette.primary, 0.3)}`,
              borderRadius: 14,
              padding: "12px 24px",
              display: "flex",
              justifyContent: "space-between",
              fontFamily: monoFont,
              fontSize: 16,
            }}
          >
            <span style={{ color: toRgba(palette.subtext, 0.9) }}>VTable Dynamic Dispatch:</span>
            <span style={{ color: "#10b981", fontWeight: 700 }}>RESOLVED (O(1) Direct Offset)</span>
            <span style={{ color: toRgba(palette.accent, 1), fontWeight: 700 }}>Refs: 2 Active</span>
          </div>
        </div>
      );
    } else if (simulationType.includes("pipeline") || simulationType.includes("network") || simulationType.includes("api") || simulationType.includes("stream")) {
      // ─────────────────────────────────────────────────────────────
      // SIMULATION 5: ASYNC DATA PIPELINE & EVENT QUEUE
      // ─────────────────────────────────────────────────────────────
      const streamX = interpolate(frame % 50, [0, 50], [50, 720]);
      const reqCount = 1000 + Math.floor(frame * 12);

      return (
        <div style={{ width: "92%", display: "flex", flexDirection: "column", alignItems: "center", gap: 20 }}>
          {/* Main Pipeline Track */}
          <div
            style={{
              position: "relative",
              width: "100%",
              maxWidth: 780,
              height: 220,
              backgroundColor: "rgba(10, 15, 26, 0.8)",
              border: `2px solid ${toRgba(palette.primary, 0.4)}`,
              borderRadius: 20,
              overflow: "hidden",
              padding: "24px",
              boxShadow: `0 0 40px ${toRgba(palette.primary, 0.15)}`,
            }}
          >
            {/* 3 Pipeline Stages */}
            <div style={{ display: "flex", justifyContent: "space-between", height: "100%", position: "relative", zIndex: 2 }}>
              <div style={{ width: 180, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", backgroundColor: toRgba(palette.surface, 0.85), borderRadius: 14, border: `1px solid ${toRgba(palette.primary, 0.4)}` }}>
                <span style={{ fontFamily: monoFont, fontSize: 12, color: toRgba(palette.subtext, 0.8) }}>CLIENT REQ</span>
                <span style={{ fontFamily: monoFont, fontSize: 18, fontWeight: 800, color: "#fff", marginTop: 4 }}>HTTP GET</span>
                <span style={{ fontFamily: monoFont, fontSize: 11, color: "#10b981", marginTop: 2 }}>SOCKET READY</span>
              </div>

              <div style={{ width: 220, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", backgroundColor: toRgba(palette.surface, 0.9), borderRadius: 14, border: `2px solid ${toRgba(palette.accent, 0.8)}`, boxShadow: `0 0 25px ${toRgba(palette.accent, 0.3)}` }}>
                <span style={{ fontFamily: monoFont, fontSize: 12, color: toRgba(palette.accent, 1), fontWeight: 700 }}>EVENT LOOP</span>
                <span style={{ fontFamily: monoFont, fontSize: 20, fontWeight: 900, color: "#fff", marginTop: 4 }}>NON-BLOCKING</span>
                <span style={{ fontFamily: monoFont, fontSize: 11, color: "#38bdf8", marginTop: 2 }}>ASYNC YIELD (0ms)</span>
              </div>

              <div style={{ width: 180, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", backgroundColor: toRgba(palette.surface, 0.85), borderRadius: 14, border: `1px solid ${toRgba(palette.primary, 0.4)}` }}>
                <span style={{ fontFamily: monoFont, fontSize: 12, color: toRgba(palette.subtext, 0.8) }}>WORKER POOL</span>
                <span style={{ fontFamily: monoFont, fontSize: 18, fontWeight: 800, color: "#fff", marginTop: 4 }}>HTTP 200</span>
                <span style={{ fontFamily: monoFont, fontSize: 11, color: "#10b981", marginTop: 2 }}>RESOLVED</span>
              </div>
            </div>

            {/* Glowing moving packet */}
            <div
              style={{
                position: "absolute",
                top: 100,
                left: streamX,
                width: 24,
                height: 24,
                borderRadius: "50%",
                backgroundColor: "#38bdf8",
                boxShadow: "0 0 25px #38bdf8, 0 0 50px #38bdf8",
                zIndex: 3,
              }}
            />
          </div>

          {/* Telemetry Bar */}
          <div
            style={{
              width: "100%",
              maxWidth: 780,
              backgroundColor: "rgba(0,0,0,0.5)",
              border: `1px solid ${toRgba(palette.primary, 0.3)}`,
              borderRadius: 14,
              padding: "14px 24px",
              display: "flex",
              justifyContent: "space-between",
              fontFamily: monoFont,
              fontSize: 16,
            }}
          >
            <span style={{ color: toRgba(palette.subtext, 0.9) }}>Requests Handled:</span>
            <span style={{ color: "#fff", fontWeight: 800 }}>{reqCount.toLocaleString()} req/s</span>
            <span style={{ color: "#10b981", fontWeight: 700 }}>Throughput: OPTIMAL</span>
          </div>
        </div>
      );
    } else if (simulationType.includes("tree") || simulationType.includes("graph")) {
      // ─────────────────────────────────────────────────────────────
      // SIMULATION 6: B-TREE / HIERARCHICAL GRAPH TRAVERSAL
      // ─────────────────────────────────────────────────────────────
      const level1Active = frame > 10;
      const level2Active = frame > 30;
      const level3Active = frame > 50;

      return (
        <div style={{ width: "92%", display: "flex", flexDirection: "column", alignItems: "center", gap: 20 }}>
          {/* Tree Canvas */}
          <div
            style={{
              width: "100%",
              maxWidth: 780,
              height: 270,
              backgroundColor: "rgba(10, 15, 26, 0.8)",
              border: `2px solid ${toRgba(palette.primary, 0.4)}`,
              borderRadius: 20,
              position: "relative",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              padding: "24px 30px",
              boxShadow: `0 0 40px ${toRgba(palette.primary, 0.15)}`,
            }}
          >
            {/* Root Node */}
            <div style={{ display: "flex", justifyContent: "center" }}>
              <div
                style={{
                  padding: "10px 24px",
                  borderRadius: 14,
                  backgroundColor: level1Active ? toRgba(palette.primary, 0.3) : toRgba(palette.surface, 0.8),
                  border: `2px solid ${level1Active ? toRgba(palette.accent, 1) : toRgba(palette.primary, 0.4)}`,
                  fontFamily: monoFont,
                  fontSize: 18,
                  fontWeight: 800,
                  color: "#fff",
                  boxShadow: level1Active ? `0 0 25px ${toRgba(palette.accent, 0.4)}` : "none",
                }}
              >
                ROOT: [50] (Key Seeker)
              </div>
            </div>

            {/* Level 2 Nodes */}
            <div style={{ display: "flex", justifyContent: "space-around" }}>
              <div
                style={{
                  padding: "8px 20px",
                  borderRadius: 12,
                  backgroundColor: "rgba(20,20,30,0.4)",
                  border: "1px dashed rgba(255,255,255,0.15)",
                  fontFamily: monoFont,
                  fontSize: 16,
                  color: "#64748b",
                  opacity: 0.5,
                }}
              >
                [25] (Skipped)
              </div>
              <div
                style={{
                  padding: "8px 24px",
                  borderRadius: 12,
                  backgroundColor: level2Active ? toRgba(palette.primary, 0.35) : toRgba(palette.surface, 0.8),
                  border: `2px solid ${level2Active ? toRgba(palette.primary, 0.95) : toRgba(palette.primary, 0.4)}`,
                  fontFamily: monoFont,
                  fontSize: 16,
                  fontWeight: 800,
                  color: "#fff",
                  boxShadow: level2Active ? `0 0 25px ${toRgba(palette.primary, 0.35)}` : "none",
                }}
              >
                ➔ BRANCH [75] (Traversing)
              </div>
            </div>

            {/* Level 3 Leaf Nodes */}
            <div style={{ display: "flex", justifyContent: "flex-end", paddingRight: 60 }}>
              <div
                style={{
                  padding: "10px 28px",
                  borderRadius: 14,
                  backgroundColor: level3Active ? "rgba(16, 185, 129, 0.25)" : toRgba(palette.surface, 0.8),
                  border: `2px solid ${level3Active ? "#10b981" : toRgba(palette.primary, 0.4)}`,
                  fontFamily: monoFont,
                  fontSize: 18,
                  fontWeight: 900,
                  color: level3Active ? "#10b981" : "#fff",
                  boxShadow: level3Active ? "0 0 35px rgba(16, 185, 129, 0.5)" : "none",
                  transform: level3Active ? "scale(1.06)" : "scale(1)",
                }}
              >
                ★ LEAF [85] TARGET FOUND (0.12ms)
              </div>
            </div>
          </div>

          {/* Telemetry Bar */}
          <div
            style={{
              width: "100%",
              maxWidth: 780,
              backgroundColor: "rgba(0,0,0,0.5)",
              border: `1px solid ${toRgba(palette.primary, 0.3)}`,
              borderRadius: 14,
              padding: "12px 24px",
              display: "flex",
              justifyContent: "space-between",
              fontFamily: monoFont,
              fontSize: 16,
            }}
          >
            <span style={{ color: toRgba(palette.subtext, 0.9) }}>Tree Height:</span>
            <span style={{ color: toRgba(palette.accent, 1), fontWeight: 700 }}>Depth = 3 Levels</span>
            <span style={{ color: "#10b981", fontWeight: 700 }}>Disk Seeks: O(log N)</span>
          </div>
        </div>
      );
    } else {
      // ─────────────────────────────────────────────────────────────
      // SIMULATION 4 (DEFAULT / CONDITIONALS):
      // ELECTRIC NEON DECISION GATE & CPU BRANCH PREDICTOR
      // ─────────────────────────────────────────────────────────────
      const packetY = interpolate(frame % 75, [0, 25, 45, 75], [20, 160, 160, 290], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      const packetX = interpolate(frame % 75, [0, 25, 45, 75], [0, 0, -140, -220], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      const gateEvaluated = (frame % 75) > 28;

      return (
        <div style={{ width: "100%", maxWidth: 920, display: "flex", flexDirection: "column", alignItems: "center", position: "relative" }}>
          {/* Circuit Visual Canvas */}
          <div
            style={{
              position: "relative",
              width: 800,
              height: 380,
              backgroundColor: "rgba(10, 14, 24, 0.65)",
              border: `1.5px solid ${toRgba(palette.primary, 0.35)}`,
              borderRadius: 24,
              overflow: "hidden",
              boxShadow: `0 20px 50px rgba(0, 0, 0, 0.6), inset 0 0 30px ${toRgba(palette.primary, 0.1)}`,
            }}
          >
            {/* Top Input Bus Line */}
            <div
              style={{
                position: "absolute",
                top: 0,
                left: 400,
                width: 4,
                height: 140,
                backgroundColor: toRgba(palette.primary, 0.7),
                boxShadow: `0 0 15px ${toRgba(palette.primary, 0.8)}`,
              }}
            />

            {/* Moving Electrical Data Packet */}
            <div
              style={{
                position: "absolute",
                top: packetY,
                left: 382 + packetX,
                width: 40,
                height: 40,
                borderRadius: "50%",
                backgroundColor: gateEvaluated ? "#10b981" : toRgba(palette.accent, 1),
                boxShadow: `0 0 25px ${gateEvaluated ? "#10b981" : toRgba(palette.accent, 1)}`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                zIndex: 10,
                transition: "background-color 0.2s ease",
              }}
            >
              <span style={{ fontFamily: monoFont, fontSize: 13, fontWeight: 900, color: "#000" }}>10</span>
            </div>

            {/* Central Decision Gate Diamond */}
            <div
              style={{
                position: "absolute",
                top: 140,
                left: 330,
                width: 140,
                height: 100,
                backgroundColor: toRgba(palette.surface, 0.95),
                border: `2px solid ${gateEvaluated ? "#10b981" : toRgba(palette.accent, 0.9)}`,
                borderRadius: 16,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: `0 0 30px ${gateEvaluated ? "#10b98145" : toRgba(palette.accent, 0.35)}`,
                zIndex: 5,
              }}
            >
              <span style={{ fontFamily: monoFont, fontSize: 13, color: toRgba(palette.subtext, 0.8), letterSpacing: "0.08em" }}>
                CONDITION
              </span>
              <span style={{ fontFamily: monoFont, fontSize: 24, fontWeight: 900, color: "#fff" }}>x &gt; 5</span>
              <span
                style={{
                  fontFamily: monoFont,
                  fontSize: 12,
                  fontWeight: 700,
                  color: gateEvaluated ? "#10b981" : "#f59e0b",
                  marginTop: 2,
                }}
              >
                {gateEvaluated ? "● TRUE" : "○ EVAL"}
              </span>
            </div>

            {/* Left Branch Line (TRUE - Laser) */}
            <svg
              style={{ position: "absolute", top: 190, left: 160, width: 200, height: 160, pointerEvents: "none" }}
            >
              <path
                d="M 180 0 L 60 120"
                stroke={gateEvaluated ? "#10b981" : "rgba(255,255,255,0.15)"}
                strokeWidth={gateEvaluated ? "5" : "2"}
                fill="none"
                style={{ filter: gateEvaluated ? "drop-shadow(0 0 10px #10b981)" : "none" }}
              />
            </svg>

            {/* Right Branch Line (FALSE - Bypassed) */}
            <svg
              style={{ position: "absolute", top: 190, left: 440, width: 200, height: 160, pointerEvents: "none" }}
            >
              <path
                d="M 20 0 L 140 120"
                stroke="rgba(255,255,255,0.15)"
                strokeWidth="2"
                strokeDasharray="6 6"
                fill="none"
              />
            </svg>

            {/* Left Branch Node: TRUE */}
            <div
              style={{
                position: "absolute",
                bottom: 24,
                left: 140,
                padding: "10px 24px",
                backgroundColor: gateEvaluated ? "#10b98125" : "rgba(20,20,30,0.5)",
                border: `2px solid ${gateEvaluated ? "#10b981" : "rgba(255,255,255,0.15)"}`,
                borderRadius: 14,
                display: "flex",
                alignItems: "center",
                gap: 10,
                boxShadow: gateEvaluated ? "0 0 25px #10b98140" : "none",
              }}
            >
              <span style={{ color: "#10b981", fontSize: 18, fontWeight: 900 }}>✓</span>
              <div>
                <div style={{ fontFamily: monoFont, fontSize: 16, fontWeight: 800, color: "#fff" }}>BRANCH: TAKEN</div>
                <div style={{ fontFamily: monoFont, fontSize: 12, color: "#10b981" }}>EXECUTE BLOCK (0 CYCLES)</div>
              </div>
            </div>

            {/* Right Branch Node: FALSE */}
            <div
              style={{
                position: "absolute",
                bottom: 24,
                right: 140,
                padding: "10px 24px",
                backgroundColor: "rgba(20,20,30,0.5)",
                border: "2px solid rgba(255,255,255,0.15)",
                borderRadius: 14,
                display: "flex",
                alignItems: "center",
                gap: 10,
                opacity: 0.5,
              }}
            >
              <span style={{ color: "#ef4444", fontSize: 18 }}>✕</span>
              <div>
                <div style={{ fontFamily: monoFont, fontSize: 16, fontWeight: 800, color: "#94a3b8" }}>BRANCH: SKIPPED</div>
                <div style={{ fontFamily: monoFont, fontSize: 12, color: "#64748b" }}>BYPASSED IN HARDWARE</div>
              </div>
            </div>
          </div>

          {/* Telemetry Bar Underneath */}
          <div
            style={{
              marginTop: 20,
              width: "100%",
              maxWidth: 800,
              display: "flex",
              justifyContent: "space-between",
              backgroundColor: toRgba(palette.surface, 0.9),
              padding: "12px 24px",
              borderRadius: 16,
              border: `1px solid ${toRgba(palette.primary, 0.3)}`,
              fontFamily: monoFont,
              fontSize: 16,
            }}
          >
            <div>
              <span style={{ color: toRgba(palette.subtext, 0.7) }}>CPU INSTRUCTION: </span>
              <span style={{ color: toRgba(palette.accent, 1), fontWeight: 700 }}>if_icmple / bne</span>
            </div>
            <div>
              <span style={{ color: toRgba(palette.subtext, 0.7) }}>PREDICTOR ACCURACY: </span>
              <span style={{ color: "#10b981", fontWeight: 700 }}>99.4% (NO FLUSH)</span>
            </div>
          </div>
        </div>
      );
    }
  };

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "flex-start",
        padding: "100px 50px 60px",
        textAlign: "center",
      }}
    >
      {/* Category / Beat Label Badge */}
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
        ✦ {label.replace(/_/g, " ").toUpperCase()} ✦
      </div>

      {/* Description / Mental Model Subheading */}
      <p
        style={{
          fontFamily: headingFont,
          fontSize: description.length > 70 ? 26 : 32,
          lineHeight: 1.35,
          fontWeight: 600,
          color: toRgba(palette.text, 1),
          maxWidth: 900,
          width: "100%",
          wordBreak: "break-word",
          margin: "0 0 32px 0",
          opacity: enterSpring,
        }}
      >
        {description}
      </p>

      {/* Interactive Simulation Graphic */}
      <div
        style={{
          flex: 1,
          width: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          opacity: enterSpring,
        }}
      >
        {renderSimulation()}
      </div>

      {/* Hardware Reality Footer */}
      {hardwareReality && (
        <div
          style={{
            marginTop: 16,
            fontFamily: monoFont,
            fontSize: 16,
            color: toRgba(palette.accent, 0.9),
            backgroundColor: toRgba(palette.surface, 0.8),
            padding: "8px 22px",
            borderRadius: 12,
            border: `1px solid ${toRgba(palette.accent, 0.3)}`,
          }}
        >
          ⚡ {hardwareReality}
        </div>
      )}
    </AbsoluteFill>
  );
};
