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

  const badgeText = elems.badge || topic.toUpperCase();
  const headlineText = elems.headline || topic;
  const subtext = elems.subtext || "Watch what happens in execution.";

  // High-impact entrance spring animations
  const badgeSpring = spring({
    frame,
    fps,
    config: { damping: 12, mass: 0.7, stiffness: 160 },
  });

  const headlineSpring = spring({
    frame: frame - 6,
    fps,
    config: { damping: 13, mass: 0.9, stiffness: 150 },
  });

  const dividerSpring = spring({
    frame: frame - 12,
    fps,
    config: { damping: 15, mass: 0.8, stiffness: 130 },
  });

  const subtextSpring = spring({
    frame: frame - 16,
    fps,
    config: { damping: 14, mass: 1.0, stiffness: 120 },
  });

  const badgeOpacity = interpolate(badgeSpring, [0, 1], [0, 1]);
  const badgeTranslate = interpolate(badgeSpring, [0, 1], [40, 0]);

  const dividerWidth = interpolate(dividerSpring, [0, 1], [0, 720]);

  const headlineOpacity = interpolate(headlineSpring, [0, 1], [0, 1]);
  const headlineScale = interpolate(headlineSpring, [0, 1], [0.85, 1]);
  const headlineTranslate = interpolate(headlineSpring, [0, 1], [45, 0]);

  const subtextOpacity = interpolate(subtextSpring, [0, 1], [0, 1]);
  const subtextTranslate = interpolate(subtextSpring, [0, 1], [30, 0]);

  const monoFont = creativeDirection.typography?.mono || "JetBrains Mono, monospace";
  const headingFont = creativeDirection.typography?.heading || "Inter, system-ui, sans-serif";

  // Dynamic font sizing
  const headlineFontSize =
    headlineText.length > 55 ? 50 : headlineText.length > 35 ? 60 : headlineText.length > 20 ? 70 : 80;

  const subtextFontSize =
    subtext.length > 80 ? 28 : subtext.length > 50 ? 32 : 36;

  // Kinetic pulse & 3D grid scroll
  const gridOffset = (frame * 3) % 60;
  const pulse = interpolate((frame % 45) / 45, [0, 0.5, 1], [1, 1.04, 1]);

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
        overflow: "hidden",
      }}
    >
      {/* 3D Perspective Grid Background Floor */}
      <div
        style={{
          position: "absolute",
          bottom: "-10%",
          left: "-20%",
          right: "-20%",
          height: "60%",
          perspective: 600,
          perspectiveOrigin: "50% 0%",
          pointerEvents: "none",
          opacity: 0.35,
        }}
      >
        <div
          style={{
            width: "100%",
            height: "100%",
            transform: "rotateX(75deg)",
            transformOrigin: "50% 0%",
            backgroundImage: `
              linear-gradient(to right, ${toRgba(palette.primary, 0.4)} 1px, transparent 1px),
              linear-gradient(to bottom, ${toRgba(palette.primary, 0.4)} 1px, transparent 1px)
            `,
            backgroundSize: "60px 60px",
            backgroundPosition: `0px ${gridOffset}px`,
          }}
        />
      </div>

      {/* Floating Cyber Particle Dots */}
      {[
        { x: 15, y: 22, s: 6, delay: 0 },
        { x: 82, y: 18, s: 8, delay: 10 },
        { x: 25, y: 78, s: 7, delay: 5 },
        { x: 78, y: 72, s: 5, delay: 15 },
        { x: 50, y: 12, s: 9, delay: 8 },
      ].map((p, idx) => {
        const pY = (p.y + (frame * 0.2 + p.delay)) % 100;
        return (
          <div
            key={idx}
            style={{
              position: "absolute",
              left: `${p.x}%`,
              top: `${pY}%`,
              width: p.s,
              height: p.s,
              borderRadius: "50%",
              backgroundColor: toRgba(palette.accent, 0.75),
              boxShadow: `0 0 20px ${toRgba(palette.accent, 1)}`,
              pointerEvents: "none",
            }}
          />
        );
      })}

      {/* Category / Topic Pill Badge */}
      <div
        style={{
          opacity: badgeOpacity,
          transform: `translateY(${badgeTranslate}px)`,
          fontFamily: monoFont,
          fontSize: 22,
          fontWeight: 800,
          letterSpacing: "0.22em",
          color: toRgba(palette.accent, 1),
          backgroundColor: toRgba(palette.surface, 0.9),
          border: `2px solid ${toRgba(palette.accent, 0.6)}`,
          padding: "12px 32px",
          borderRadius: 40,
          boxShadow: `0 0 35px ${toRgba(palette.accent, 0.35)}`,
          marginBottom: 36,
          maxWidth: 900,
          wordBreak: "break-word",
          textAlign: "center",
          textTransform: "uppercase",
        }}
      >
        [ {badgeText} ]
      </div>

      {/* Main Hook Headline */}
      <h1
        style={{
          opacity: headlineOpacity,
          transform: `translateY(${headlineTranslate}px) scale(${headlineScale * pulse})`,
          fontFamily: headingFont,
          fontSize: headlineFontSize,
          fontWeight: 900,
          lineHeight: 1.12,
          letterSpacing: "-0.03em",
          color: "#ffffff",
          textShadow: `
            0 0 30px ${toRgba(palette.primary, 0.6)},
            0 0 70px ${toRgba(palette.primary, 0.25)},
            0 4px 15px rgba(0, 0, 0, 0.9)
          `,
          margin: 0,
          maxWidth: 960,
          width: "100%",
          wordBreak: "break-word",
          overflowWrap: "break-word",
          textAlign: "center",
        }}
      >
        {headlineText}
      </h1>

      {/* Animated Glowing Accent Divider */}
      <div
        style={{
          width: dividerWidth,
          height: 4,
          background: `linear-gradient(90deg, transparent 0%, ${toRgba(palette.accent, 1)} 50%, transparent 100%)`,
          boxShadow: `0 0 25px ${toRgba(palette.accent, 0.8)}`,
          margin: "40px auto",
          borderRadius: 2,
        }}
      />

      {/* Subtext Insight Callout */}
      <p
        style={{
          opacity: subtextOpacity,
          transform: `translateY(${subtextTranslate}px)`,
          fontFamily: headingFont,
          fontSize: subtextFontSize,
          lineHeight: 1.45,
          fontWeight: 600,
          color: toRgba(palette.text, 0.92),
          margin: 0,
          maxWidth: 880,
          width: "100%",
          wordBreak: "break-word",
          overflowWrap: "break-word",
          textAlign: "center",
          textShadow: "0 2px 10px rgba(0, 0, 0, 0.8)",
        }}
      >
        {subtext}
      </p>
    </AbsoluteFill>
  );
};
