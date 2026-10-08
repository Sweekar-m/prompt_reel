import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { SceneSchema, CreativeDirectionSchema } from "../types";
import { toRgba } from "../utils/colors";

export const HookScene: React.FC<{
  scene: SceneSchema;
  creativeDirection: CreativeDirectionSchema;
  topic: string;
}> = ({ scene, creativeDirection, topic }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const palette = creativeDirection.palette;
  const elems = scene.elements || {};
  const variant = scene.composition_variant || (scene.visual_recipe?.layout_grammar?.composition_variant) || "centered";

  const badgeText = elems.badge || topic.toUpperCase();
  const headlineText = elems.headline || topic;
  const subtext = elems.subtext || "Watch what happens in execution.";

  const monoFont = creativeDirection.typography?.mono || "'JetBrains Mono', monospace";
  const headingFont = creativeDirection.typography?.heading || "Inter, sans-serif";

  // Spring animations
  const enterSpring = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.85, stiffness: 150 },
  });

  const secondarySpring = spring({
    frame: Math.max(0, frame - 8),
    fps,
    config: { damping: 16, mass: 1.0, stiffness: 130 },
  });

  const pulse = interpolate((frame % 45) / 45, [0, 0.5, 1], [1, 1.04, 1]);

  // ── VARIANT 1: EDITORIAL LEFT ───────────────────────────────────────────────
  if (variant === "editorial_left") {
    return (
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "flex-start",
          padding: "0 100px",
          boxSizing: "border-box",
        }}
      >
        <div
          style={{
            borderLeft: `5px solid ${toRgba(palette.primary, 1)}`,
            paddingLeft: 36,
            transform: `translateX(${interpolate(enterSpring, [0, 1], [-40, 0])}px)`,
            opacity: enterSpring,
          }}
        >
          <div
            style={{
              fontFamily: monoFont,
              fontSize: 22,
              fontWeight: 800,
              color: toRgba(palette.accent, 1),
              letterSpacing: "0.2em",
              textTransform: "uppercase",
              marginBottom: 20,
            }}
          >
            ✦ {badgeText}
          </div>
          <h1
            style={{
              fontFamily: headingFont,
              fontSize: 72,
              fontWeight: 900,
              lineHeight: 1.1,
              color: toRgba(palette.text, 1),
              margin: "0 0 28px 0",
              maxWidth: 900,
            }}
          >
            {headlineText}
          </h1>
          <p
            style={{
              fontFamily: headingFont,
              fontSize: 32,
              color: toRgba(palette.subtext, 1),
              lineHeight: 1.4,
              maxWidth: 780,
              margin: 0,
              opacity: secondarySpring,
            }}
          >
            {subtext}
          </p>
        </div>
      </AbsoluteFill>
    );
  }

  // ── VARIANT 2: GIANT TYPE ───────────────────────────────────────────────────
  if (variant === "giant_type") {
    const words = headlineText.split(" ");
    return (
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: "0 50px",
          textAlign: "center",
          boxSizing: "border-box",
        }}
      >
        <div
          style={{
            fontFamily: monoFont,
            fontSize: 20,
            fontWeight: 800,
            color: toRgba(palette.primary, 1),
            letterSpacing: "0.3em",
            marginBottom: 24,
            opacity: enterSpring,
          }}
        >
          [ {badgeText} ]
        </div>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 12,
            alignItems: "center",
            maxWidth: 1000,
          }}
        >
          {words.map((w, idx) => {
            const wordSpring = spring({
              frame: Math.max(0, frame - idx * 4),
              fps,
              config: { damping: 13, stiffness: 180 },
            });
            const isHighlight = idx === 1 || idx === words.length - 1;
            return (
              <span
                key={idx}
                style={{
                  fontFamily: headingFont,
                  fontSize: words.length > 5 ? 70 : 86,
                  fontWeight: 950,
                  lineHeight: 0.95,
                  letterSpacing: "-0.03em",
                  color: isHighlight ? toRgba(palette.accent, 1) : toRgba(palette.text, 1),
                  transform: `scale(${interpolate(wordSpring, [0, 1], [0.8, 1])}) translateY(${interpolate(wordSpring, [0, 1], [30, 0])}px)`,
                  opacity: wordSpring,
                }}
              >
                {w.toUpperCase()}
              </span>
            );
          })}
        </div>
        <div
          style={{
            fontFamily: monoFont,
            fontSize: 24,
            color: toRgba(palette.subtext, 1),
            marginTop: 36,
            opacity: secondarySpring,
          }}
        >
          // {subtext}
        </div>
      </AbsoluteFill>
    );
  }

  // ── VARIANT 3: TERMINAL ─────────────────────────────────────────────────────
  if (variant === "terminal") {
    const charCount = Math.floor(interpolate(frame, [5, 40], [0, headlineText.length], { extrapolateRight: "clamp" }));
    return (
      <AbsoluteFill
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          padding: "0 80px",
          boxSizing: "border-box",
        }}
      >
        <div
          style={{
            width: "100%",
            maxWidth: 960,
            backgroundColor: toRgba(palette.surface, 0.96),
            border: `2px solid ${toRgba(palette.primary, 0.6)}`,
            borderRadius: 18,
            boxShadow: `0 30px 80px rgba(0,0,0,0.8), 0 0 50px ${toRgba(palette.primary, 0.25)}`,
            overflow: "hidden",
            transform: `scale(${enterSpring})`,
          }}
        >
          <div
            style={{
              padding: "16px 24px",
              backgroundColor: "rgba(0,0,0,0.4)",
              borderBottom: `1px solid ${toRgba(palette.primary, 0.25)}`,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <div style={{ display: "flex", gap: 10 }}>
              <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#EF4444" }} />
              <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#F59E0B" }} />
              <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#22D3A5" }} />
            </div>
            <div style={{ fontFamily: monoFont, fontSize: 16, color: toRgba(palette.primary, 1), fontWeight: 700 }}>
              KERNEL BOOT // {badgeText}
            </div>
            <div style={{ width: 40 }} />
          </div>
          <div style={{ padding: "40px 48px", fontFamily: monoFont }}>
            <div style={{ color: "#22D3A5", fontSize: 20, marginBottom: 16 }}>
              $ ./inspect --trace --eval
            </div>
            <div style={{ color: "#ffffff", fontSize: 44, fontWeight: 900, lineHeight: 1.3, minHeight: 120 }}>
              {headlineText.slice(0, charCount)}
              <span style={{ opacity: frame % 16 < 8 ? 1 : 0, color: toRgba(palette.accent, 1) }}>█</span>
            </div>
            <div style={{ marginTop: 24, color: toRgba(palette.subtext, 1), fontSize: 22, borderTop: "1px dashed rgba(255,255,255,0.15)", paddingTop: 20 }}>
              &gt; {subtext}
            </div>
          </div>
        </div>
      </AbsoluteFill>
    );
  }

  // ── VARIANT 4: SPLIT ────────────────────────────────────────────────────────
  if (variant === "split") {
    return (
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "row",
          justifyContent: "center",
          alignItems: "center",
          padding: "0 60px",
          gap: 36,
          boxSizing: "border-box",
        }}
      >
        <div
          style={{
            flex: 1,
            backgroundColor: toRgba(palette.surface, 0.9),
            border: `2px solid ${toRgba(palette.primary, 0.5)}`,
            borderRadius: 24,
            padding: "48px 36px",
            boxShadow: `0 20px 50px rgba(0,0,0,0.6)`,
            transform: `translateX(${interpolate(enterSpring, [0, 1], [-50, 0])}px)`,
            opacity: enterSpring,
          }}
        >
          <div style={{ fontFamily: monoFont, fontSize: 16, color: toRgba(palette.primary, 1), fontWeight: 800, marginBottom: 12 }}>
            CONVENTIONAL ASSUMPTION
          </div>
          <div style={{ fontFamily: headingFont, fontSize: 36, fontWeight: 800, color: "#ffffff", lineHeight: 1.25 }}>
            {badgeText}
          </div>
          <div style={{ marginTop: 20, fontFamily: monoFont, fontSize: 18, color: "#EF4444" }}>
            ✕ High latency &amp; overhead
          </div>
        </div>

        <div
          style={{
            flex: 1,
            backgroundColor: toRgba(palette.surface, 0.95),
            border: `2px solid ${toRgba(palette.accent, 0.8)}`,
            borderRadius: 24,
            padding: "48px 36px",
            boxShadow: `0 20px 50px rgba(0,0,0,0.6), 0 0 40px ${toRgba(palette.accent, 0.3)}`,
            transform: `translateX(${interpolate(secondarySpring, [0, 1], [50, 0])}px)`,
            opacity: secondarySpring,
          }}
        >
          <div style={{ fontFamily: monoFont, fontSize: 16, color: toRgba(palette.accent, 1), fontWeight: 800, marginBottom: 12 }}>
            HARDWARE REALITY
          </div>
          <div style={{ fontFamily: headingFont, fontSize: 36, fontWeight: 800, color: "#ffffff", lineHeight: 1.25 }}>
            {headlineText}
          </div>
          <div style={{ marginTop: 20, fontFamily: monoFont, fontSize: 18, color: "#22D3A5" }}>
            ✓ 1 CPU Instruction Cycle
          </div>
        </div>
      </AbsoluteFill>
    );
  }

  // ── VARIANT 5: CINEMATIC / VISUAL FIRST / CENTERED (Classic fallback) ──────
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
          opacity: enterSpring,
          transform: `translateY(${interpolate(enterSpring, [0, 1], [30, 0])}px)`,
          fontFamily: monoFont,
          fontSize: 22,
          fontWeight: 800,
          letterSpacing: "0.22em",
          color: toRgba(palette.accent, 1),
          backgroundColor: toRgba(palette.surface, 0.92),
          border: `2px solid ${toRgba(palette.accent, 0.6)}`,
          padding: "12px 32px",
          borderRadius: 40,
          boxShadow: `0 0 35px ${toRgba(palette.accent, 0.35)}`,
          marginBottom: 36,
          textTransform: "uppercase",
        }}
      >
        ✦ {badgeText} ✦
      </div>

      <h1
        style={{
          opacity: enterSpring,
          transform: `scale(${interpolate(enterSpring, [0, 1], [0.88, 1])})`,
          fontFamily: headingFont,
          fontSize: headlineText.length > 40 ? 54 : 68,
          lineHeight: 1.15,
          fontWeight: 900,
          color: toRgba(palette.text, 1),
          maxWidth: 960,
          margin: "0 0 28px 0",
          textShadow: `0 0 40px ${toRgba(palette.primary, 0.35)}`,
        }}
      >
        {headlineText}
      </h1>

      <div
        style={{
          width: interpolate(secondarySpring, [0, 1], [0, 500]),
          height: 3,
          backgroundColor: toRgba(palette.primary, 0.8),
          boxShadow: `0 0 20px ${toRgba(palette.primary, 1)}`,
          marginBottom: 28,
        }}
      />

      <p
        style={{
          opacity: secondarySpring,
          transform: `translateY(${interpolate(secondarySpring, [0, 1], [20, 0])}px)`,
          fontFamily: headingFont,
          fontSize: 32,
          lineHeight: 1.4,
          color: toRgba(palette.subtext, 1),
          maxWidth: 820,
          margin: 0,
        }}
      >
        {subtext}
      </p>
    </AbsoluteFill>
  );
};
