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
  const primaryGlow = toRgba(palette.primary, 0.16);
  const secondaryGlow = toRgba(palette.secondary, 0.10);

  const template = creativeDirection.motion_template || {};
  const bgStyle = template.background_style || "clean_canvas";

  // Subtle ambient pulse
  const glowX = interpolate(frame % 200, [0, 100, 200], [35, 65, 35]);
  const glowY = interpolate(frame % 260, [0, 130, 260], [30, 70, 30]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: bgColor,
        overflow: "hidden",
      }}
    >
      {/* ── 1. BLUEPRINT GRID (Precision CAD Engineering) ── */}
      {bgStyle === "blueprint_grid" && (
        <>
          <div
            style={{
              position: "absolute",
              inset: 0,
              backgroundImage: `linear-gradient(to right, ${toRgba(palette.primary, 0.12)} 1px, transparent 1px),
                                linear-gradient(to bottom, ${toRgba(palette.primary, 0.12)} 1px, transparent 1px)`,
              backgroundSize: "32px 32px",
              opacity: 0.8,
            }}
          />
          <div
            style={{
              position: "absolute",
              top: 24,
              left: 24,
              right: 24,
              height: 1,
              backgroundColor: toRgba(palette.primary, 0.3),
            }}
          />
          <div
            style={{
              position: "absolute",
              top: 14,
              left: 30,
              fontFamily: "JetBrains Mono, monospace",
              fontSize: 10,
              color: toRgba(palette.primary, 0.6),
              letterSpacing: "0.2em",
            }}
          >
            CAD-ISO • SPEC: 1080x1920 • 60 FPS
          </div>
        </>
      )}

      {/* ── 2. SWISS RULER (12-Column Typographic Modernism) ── */}
      {bgStyle === "swiss_ruler" && (
        <>
          <div
            style={{
              position: "absolute",
              inset: "0 60px",
              display: "flex",
              justifyContent: "space-between",
              pointerEvents: "none",
            }}
          >
            {Array.from({ length: 12 }).map((_, idx) => (
              <div
                key={idx}
                style={{
                  width: 1,
                  height: "100%",
                  backgroundColor: "rgba(255, 255, 255, 0.04)",
                }}
              />
            ))}
          </div>
          <div
            style={{
              position: "absolute",
              top: 40,
              left: 60,
              right: 60,
              height: 1,
              backgroundColor: "rgba(255, 255, 255, 0.08)",
            }}
          />
        </>
      )}

      {/* ── 3. BRUTALIST MONOCHROME PLANES ── */}
      {bgStyle === "monochrome_planes" && (
        <>
          <div
            style={{
              position: "absolute",
              top: 0,
              right: 0,
              width: "45%",
              height: "100%",
              backgroundColor: "rgba(255, 255, 255, 0.02)",
              borderLeft: "2px solid rgba(255, 255, 255, 0.08)",
            }}
          />
          <div
            style={{
              position: "absolute",
              bottom: 80,
              left: 0,
              right: 0,
              height: 2,
              backgroundColor: toRgba(palette.accent, 0.25),
            }}
          />
        </>
      )}

      {/* ── 4. 3D SPATIAL PERSPECTIVE FLOOR ── */}
      {bgStyle === "spatial_depth_grid" && (
        <div
          style={{
            position: "absolute",
            bottom: "-15%",
            left: "-30%",
            right: "-30%",
            height: "70%",
            perspective: 600,
            perspectiveOrigin: "50% 0%",
            opacity: 0.45,
          }}
        >
          <div
            style={{
              width: "100%",
              height: "100%",
              transform: "rotateX(68deg)",
              backgroundImage: `linear-gradient(to right, ${toRgba(palette.primary, 0.35)} 1.5px, transparent 1.5px),
                                linear-gradient(to bottom, ${toRgba(palette.primary, 0.35)} 1.5px, transparent 1.5px)`,
              backgroundSize: "60px 60px",
            }}
          />
        </div>
      )}

      {/* ── 5. TERMINAL WORKSPACE (CRT Scanline Phosphor) ── */}
      {bgStyle === "terminal_workspace" && (
        <>
          <div
            style={{
              position: "absolute",
              inset: 0,
              backgroundImage: `linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%)`,
              backgroundSize: "100% 4px",
              pointerEvents: "none",
              opacity: 0.6,
            }}
          />
          <div
            style={{
              position: "absolute",
              top: 20,
              left: 40,
              fontFamily: "JetBrains Mono, monospace",
              fontSize: 12,
              color: toRgba(palette.primary, 0.7),
            }}
          >
            [TTY: /dev/pts/0] • BUFFER READY
          </div>
        </>
      )}

      {/* ── 6. CLEAN AMBIENT GRADIENTS (Soft living aura) ── */}
      <div
        style={{
          position: "absolute",
          top: `${glowY}%`,
          left: `${glowX}%`,
          width: 800,
          height: 800,
          transform: "translate(-50%, -50%)",
          borderRadius: "50%",
          background: `radial-gradient(circle, ${primaryGlow} 0%, transparent 68%)`,
          filter: "blur(65px)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};
