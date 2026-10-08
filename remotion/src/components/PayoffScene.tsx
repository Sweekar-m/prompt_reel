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
  const closingDna = creativeDirection.closing_dna;

  // Strategy and Layout resolution
  const compVariant = scene.composition_variant;
  const strategyId = (elems.closing_strategy as string) || closingDna?.strategy_id || "kinetic_statement";
  const layout = compVariant === "editorial_quote" 
    ? "centered_minimal" 
    : (compVariant === "split_benchmark" ? "split_before_after" : (compVariant || (elems.layout as string) || closingDna?.layout || "kinetic_words"));

  const headline = (elems.headline as string) || (elems.stat as string) || closingDna?.headline || "MASTER TAKEAWAY";
  const secondary = (elems.secondary_text as string) || (elems.subtitle as string) || closingDna?.secondary_text || "Deterministic system execution";
  const statCallout = (elems.stat_callout as string) || (elems.stat as string) || closingDna?.stat_callout || "O(1)";
  const callbackRef = (elems.callback_ref as string) || closingDna?.callback_ref || "Initial Question";
  const actionLabel = (elems.action_label as string) || closingDna?.action_label || "TEST IN PRODUCTION";
  const proTip = (elems.pro_tip as string) || "Mastering low-level execution invariants unlocks 10x engineering performance.";

  const headingFont = creativeDirection.typography?.heading || "Inter, sans-serif";
  const monoFont = creativeDirection.typography?.mono || "JetBrains Mono, monospace";

  // Enter animation spring
  const enterSpring = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.9, stiffness: 130 },
  });

  // Pulse & subtle breathing
  const pulse = interpolate((frame % 45) / 45, [0, 0.5, 1], [0.98, 1.04, 0.98]);

  // ── LAYOUT 1: KINETIC WORDS (Punchy multi-tier typography) ─────────────────
  if (layout === "kinetic_words" || strategyId === "kinetic_statement") {
    const words = headline.split(" ");
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
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 12,
            maxWidth: 960,
          }}
        >
          {words.map((word, wIdx) => {
            const wordSpring = spring({
              frame: Math.max(0, frame - wIdx * 4),
              fps,
              config: { damping: 12, mass: 0.7, stiffness: 180 },
            });
            const isAccent = wIdx === words.length - 1 || wIdx === 1;
            return (
              <div
                key={wIdx}
                style={{
                  fontFamily: headingFont,
                  fontSize: words.length > 5 ? 64 : 88,
                  fontWeight: 900,
                  letterSpacing: "-0.03em",
                  lineHeight: 1.05,
                  color: isAccent ? toRgba(palette.accent, 1) : "#ffffff",
                  textShadow: isAccent
                    ? `0 0 45px ${toRgba(palette.accent, 0.6)}`
                    : "0 4px 20px rgba(0,0,0,0.8)",
                  transform: `scale(${wordSpring}) translateY(${(1 - wordSpring) * 30}px)`,
                  opacity: wordSpring,
                }}
              >
                {word.toUpperCase()}
              </div>
            );
          })}
        </div>

        {/* Supporting Secondary Law */}
        <div
          style={{
            marginTop: 36,
            fontFamily: monoFont,
            fontSize: 24,
            fontWeight: 600,
            color: toRgba(palette.primary, 1),
            letterSpacing: "0.15em",
            opacity: enterSpring,
            borderTop: `2px solid ${toRgba(palette.primary, 0.3)}`,
            paddingTop: 18,
            maxWidth: 800,
          }}
        >
          ✦ {secondary.toUpperCase()}
        </div>
      </AbsoluteFill>
    );
  }

  // ── LAYOUT 2: CENTERED MINIMAL (Stark glowing sentence on dark void) ───────
  if (layout === "centered_minimal" || strategyId === "minimal" || strategyId === "cta") {
    const isCta = strategyId === "cta";
    return (
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "0 80px",
          textAlign: "center",
          boxSizing: "border-box",
        }}
      >
        {/* Subtle glowing singularity dot */}
        <div
          style={{
            width: 14,
            height: 14,
            borderRadius: "50%",
            backgroundColor: toRgba(palette.accent, 1),
            boxShadow: `0 0 30px ${toRgba(palette.accent, 0.9)}, 0 0 60px ${toRgba(palette.accent, 0.5)}`,
            marginBottom: 36,
            transform: `scale(${pulse})`,
          }}
        />

        <div
          style={{
            fontFamily: headingFont,
            fontSize: 48,
            fontWeight: 800,
            color: "#ffffff",
            lineHeight: 1.35,
            letterSpacing: "-0.01em",
            maxWidth: 880,
            opacity: enterSpring,
            textShadow: "0 0 35px rgba(255,255,255,0.25)",
          }}
        >
          {headline}
        </div>

        <div
          style={{
            marginTop: 24,
            fontFamily: monoFont,
            fontSize: 22,
            color: toRgba(palette.primary, 0.9),
            letterSpacing: "0.08em",
            maxWidth: 780,
            opacity: enterSpring,
          }}
        >
          {secondary}
        </div>

        {isCta && (
          <div
            style={{
              marginTop: 44,
              backgroundColor: toRgba(palette.surface, 0.95),
              border: `2px solid ${toRgba(palette.accent, 0.7)}`,
              padding: "14px 36px",
              borderRadius: 50,
              fontFamily: monoFont,
              fontSize: 20,
              fontWeight: 800,
              color: toRgba(palette.accent, 1),
              letterSpacing: "0.18em",
              boxShadow: `0 0 40px ${toRgba(palette.accent, 0.35)}`,
              opacity: spring({ frame: frame - 10, fps }),
            }}
          >
            ❯ {actionLabel}
          </div>
        )}
      </AbsoluteFill>
    );
  }

  // ── LAYOUT 3: SPLIT BEFORE & AFTER (Contrasting naive vs optimized) ────────
  if (layout === "split_before_after" || strategyId === "before_after") {
    return (
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "0 50px",
          boxSizing: "border-box",
        }}
      >
        <div
          style={{
            fontFamily: monoFont,
            fontSize: 20,
            fontWeight: 800,
            letterSpacing: "0.2em",
            color: toRgba(palette.primary, 1),
            marginBottom: 28,
            opacity: enterSpring,
          }}
        >
          ✦ SYSTEM TRANSFORMATION ✦
        </div>

        <div
          style={{
            display: "flex",
            width: "100%",
            maxWidth: 960,
            gap: 20,
            alignItems: "stretch",
          }}
        >
          {/* Naive / Left Card */}
          <div
            style={{
              flex: 1,
              backgroundColor: "rgba(30, 20, 25, 0.8)",
              border: "1.5px solid rgba(239, 68, 68, 0.4)",
              borderRadius: 20,
              padding: "32px 24px",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              textAlign: "center",
              opacity: enterSpring,
            }}
          >
            <div style={{ fontFamily: monoFont, fontSize: 16, color: "#ef4444", fontWeight: 800, marginBottom: 12 }}>
              ✕ NAIVE / UNOPTIMIZED
            </div>
            <div style={{ fontFamily: headingFont, fontSize: 26, color: "#e2e8f0", fontWeight: 600, lineHeight: 1.3 }}>
              {callbackRef || "Brute Force Traversal"}
            </div>
            <div style={{ marginTop: 14, fontFamily: monoFont, fontSize: 22, color: "#f87171", fontWeight: 800 }}>
              SLOW / O(N)
            </div>
          </div>

          {/* Optimized / Right Card */}
          <div
            style={{
              flex: 1.15,
              backgroundColor: toRgba(palette.surface, 0.95),
              border: `2px solid ${toRgba(palette.accent, 0.8)}`,
              borderRadius: 20,
              padding: "32px 28px",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              textAlign: "center",
              boxShadow: `0 0 50px ${toRgba(palette.accent, 0.35)}`,
              transform: `scale(${pulse})`,
              opacity: enterSpring,
            }}
          >
            <div style={{ fontFamily: monoFont, fontSize: 16, color: toRgba(palette.accent, 1), fontWeight: 800, marginBottom: 12 }}>
              ✓ OPTIMIZED INVARIANT
            </div>
            <div style={{ fontFamily: headingFont, fontSize: 32, color: "#ffffff", fontWeight: 800, lineHeight: 1.25 }}>
              {headline}
            </div>
            <div style={{ marginTop: 14, fontFamily: monoFont, fontSize: 30, color: toRgba(palette.accent, 1), fontWeight: 900 }}>
              {statCallout}
            </div>
          </div>
        </div>

        <div
          style={{
            marginTop: 28,
            fontFamily: headingFont,
            fontSize: 22,
            color: "#cbd5e1",
            textAlign: "center",
            maxWidth: 820,
            opacity: enterSpring,
          }}
        >
          {secondary}
        </div>
      </AbsoluteFill>
    );
  }

  // ── LAYOUT 4: CALLBACK ANCHOR / LOOP (Returns to opening question) ─────────
  if (layout === "callback_anchor" || strategyId === "callback" || strategyId === "loop") {
    const isLoop = strategyId === "loop";
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
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 10,
            fontFamily: monoFont,
            fontSize: 18,
            fontWeight: 800,
            letterSpacing: "0.2em",
            color: toRgba(palette.primary, 1),
            backgroundColor: toRgba(palette.surface, 0.9),
            border: `1.5px solid ${toRgba(palette.primary, 0.5)}`,
            padding: "8px 24px",
            borderRadius: 30,
            marginBottom: 28,
            opacity: enterSpring,
          }}
        >
          <span>{isLoop ? "↺" : "✓"}</span>
          <span>{isLoop ? "INFINITE EXECUTION LOOP" : "NARRATIVE CLOSURE"}</span>
        </div>

        <div
          style={{
            maxWidth: 900,
            backgroundColor: "rgba(12, 18, 30, 0.88)",
            border: `1.5px dashed ${toRgba(palette.primary, 0.4)}`,
            borderRadius: 18,
            padding: "20px 32px",
            marginBottom: 28,
            fontFamily: monoFont,
            fontSize: 22,
            color: "#94a3b8",
            opacity: enterSpring,
          }}
        >
          "{callbackRef}"
        </div>

        <div
          style={{
            fontFamily: headingFont,
            fontSize: 48,
            fontWeight: 900,
            color: toRgba(palette.accent, 1),
            lineHeight: 1.25,
            textShadow: `0 0 45px ${toRgba(palette.accent, 0.5)}`,
            maxWidth: 920,
            opacity: enterSpring,
          }}
        >
          {headline}
        </div>

        <div
          style={{
            marginTop: 20,
            fontFamily: headingFont,
            fontSize: 24,
            fontWeight: 500,
            color: "#e2e8f0",
            maxWidth: 820,
            opacity: enterSpring,
          }}
        >
          {secondary}
        </div>
      </AbsoluteFill>
    );
  }

  // ── LAYOUT 5: COMPRESSION SINGULARITY (Contracting orbital rings) ──────────
  if (layout === "compression_singularity" || strategyId === "compression") {
    const ringScale = interpolate(frame, [0, 30], [1.4, 1.0], { extrapolateRight: "clamp" });
    const ringRotate = interpolate(frame, [0, 90], [0, 180]);
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
        {/* Animated Concentric Singularities */}
        <div
          style={{
            position: "absolute",
            width: 520,
            height: 520,
            borderRadius: "50%",
            border: `2px dashed ${toRgba(palette.primary, 0.25)}`,
            transform: `scale(${ringScale}) rotate(${ringRotate}deg)`,
            pointerEvents: "none",
          }}
        />
        <div
          style={{
            position: "absolute",
            width: 400,
            height: 400,
            borderRadius: "50%",
            border: `1.5px solid ${toRgba(palette.accent, 0.35)}`,
            transform: `scale(${ringScale * 0.95}) rotate(${-ringRotate * 1.5}deg)`,
            pointerEvents: "none",
          }}
        />

        <div
          style={{
            fontFamily: monoFont,
            fontSize: 20,
            fontWeight: 800,
            letterSpacing: "0.25em",
            color: toRgba(palette.primary, 1),
            marginBottom: 24,
            opacity: enterSpring,
          }}
        >
          ✦ ONE-LINE PRINCIPLE ✦
        </div>

        <div
          style={{
            fontFamily: headingFont,
            fontSize: 54,
            fontWeight: 900,
            color: "#ffffff",
            maxWidth: 880,
            lineHeight: 1.25,
            letterSpacing: "-0.02em",
            opacity: enterSpring,
            textShadow: `0 0 40px ${toRgba(palette.accent, 0.5)}`,
          }}
        >
          {headline}
        </div>

        <div
          style={{
            marginTop: 24,
            fontFamily: monoFont,
            fontSize: 32,
            fontWeight: 900,
            color: toRgba(palette.accent, 1),
            opacity: enterSpring,
          }}
        >
          {statCallout}
        </div>

        <div
          style={{
            marginTop: 20,
            fontFamily: headingFont,
            fontSize: 22,
            color: "#94a3b8",
            maxWidth: 760,
            opacity: enterSpring,
          }}
        >
          {secondary}
        </div>
      </AbsoluteFill>
    );
  }

  // ── LAYOUT 6: OPEN QUESTION CARD (Provocative edge-case debate) ────────────
  if (layout === "question_card" || strategyId === "question") {
    const showCursor = Math.floor(frame / 12) % 2 === 0;
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
        <div
          style={{
            fontFamily: monoFont,
            fontSize: 18,
            fontWeight: 800,
            letterSpacing: "0.22em",
            color: "#f59e0b",
            backgroundColor: "rgba(245, 158, 11, 0.15)",
            border: "1.5px solid rgba(245, 158, 11, 0.6)",
            padding: "8px 24px",
            borderRadius: 30,
            marginBottom: 32,
            opacity: enterSpring,
          }}
        >
          ? UNRESOLVED EDGE CASE
        </div>

        <div
          style={{
            fontFamily: headingFont,
            fontSize: 48,
            fontWeight: 800,
            color: "#ffffff",
            lineHeight: 1.35,
            maxWidth: 920,
            opacity: enterSpring,
          }}
        >
          {headline}
          <span style={{ color: toRgba(palette.accent, 1), opacity: showCursor ? 1 : 0 }}>_</span>
        </div>

        <div
          style={{
            marginTop: 28,
            fontFamily: monoFont,
            fontSize: 22,
            color: toRgba(palette.primary, 0.9),
            maxWidth: 820,
            opacity: enterSpring,
          }}
        >
          {secondary}
        </div>

        <div
          style={{
            marginTop: 36,
            fontFamily: monoFont,
            fontSize: 16,
            letterSpacing: "0.15em",
            color: "#64748b",
            opacity: enterSpring,
          }}
        >
          DROP YOUR SOLUTION IN THE COMMENTS
        </div>
      </AbsoluteFill>
    );
  }

  // ── DEFAULT / HERO STAT BADGE LAYOUT ──────────────────────────────────────
  const statFontSize =
    headline.length > 28 ? 44 : headline.length > 18 ? 54 : headline.length > 10 ? 68 : 84;

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
          opacity: enterSpring,
          boxShadow: `0 0 30px ${toRgba(palette.primary, 0.25)}`,
        }}
      >
        ✦ {(elems.title as string || "SYSTEM RULE").toUpperCase()} ✦
      </div>

      {/* Hero Stat */}
      <div
        style={{
          fontFamily: monoFont,
          fontSize: statFontSize,
          fontWeight: 900,
          color: toRgba(palette.accent, 1),
          textShadow: `0 0 50px ${toRgba(palette.accent, 0.6)}, 0 0 90px ${toRgba(palette.accent, 0.3)}`,
          letterSpacing: headline.length > 15 ? "0.01em" : "-0.02em",
          lineHeight: 1.15,
          maxWidth: 960,
          marginBottom: 24,
          transform: `scale(${pulse})`,
        }}
      >
        {headline}
      </div>

      {/* Subtitle */}
      <h3
        style={{
          fontFamily: headingFont,
          fontSize: secondary.length > 60 ? 26 : 32,
          lineHeight: 1.4,
          fontWeight: 700,
          color: "#ffffff",
          maxWidth: 880,
          margin: "0 0 36px 0",
          opacity: enterSpring,
          textShadow: "0 2px 10px rgba(0, 0, 0, 0.8)",
        }}
      >
        {secondary}
      </h3>

      {/* Pro Tip Card */}
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
              SENIOR ARCHITECTURE INVARIANT
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
