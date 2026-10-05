import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";
import { CreativeDirectionSchema } from "../types";
import { toRgba } from "../utils/colors";

export const Background: React.FC<{
  creativeDirection: CreativeDirectionSchema;
}> = ({ creativeDirection }) => {
  const frame = useCurrentFrame();
  const palette = creativeDirection.palette;

  const bgColor = toRgba(palette.background, 1);
  const primaryGlow = toRgba(palette.primary, 0.18);
  const secondaryGlow = toRgba(palette.secondary, 0.12);

  // Subtle ambient breathing/pulsing
  const glowX = interpolate(frame % 180, [0, 90, 180], [30, 70, 30]);
  const glowY = interpolate(frame % 240, [0, 120, 240], [25, 65, 25]);
  const glowScale = interpolate(frame % 120, [0, 60, 120], [0.95, 1.1, 0.95]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: bgColor,
        overflow: "hidden",
      }}
    >
      {/* Dynamic Ambient Glow 1 */}
      <div
        style={{
          position: "absolute",
          top: `${glowY}%`,
          left: `${glowX}%`,
          width: 900,
          height: 900,
          transform: `translate(-50%, -50%) scale(${glowScale})`,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${primaryGlow} 0%, transparent 70%)`,
          filter: "blur(60px)",
          pointerEvents: "none",
        }}
      />

      {/* Dynamic Ambient Glow 2 */}
      <div
        style={{
          position: "absolute",
          bottom: "15%",
          right: "20%",
          width: 750,
          height: 750,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${secondaryGlow} 0%, transparent 65%)`,
          filter: "blur(70px)",
          pointerEvents: "none",
        }}
      />

      {/* Cyber/Tech Grid Overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `linear-gradient(to right, ${toRgba(palette.surface, 0.25)} 1px, transparent 1px),
                            linear-gradient(to bottom, ${toRgba(palette.surface, 0.25)} 1px, transparent 1px)`,
          backgroundSize: "60px 60px",
          opacity: 0.35,
          pointerEvents: "none",
        }}
      />

      {/* Top & Bottom Vignette Gradient */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(ellipse at center, transparent 40%, rgba(0, 0, 0, 0.75) 100%)`,
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};
