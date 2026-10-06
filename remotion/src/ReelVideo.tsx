import React from "react";
import { AbsoluteFill, Sequence, useVideoConfig, useCurrentFrame, interpolate } from "remotion";
import { ReelCompositionProps, SceneSchema } from "./types";
import { Background } from "./components/Background";
import { HookScene } from "./components/HookScene";
import { MetaphorScene } from "./components/MetaphorScene";
import { Math3DScene } from "./components/Math3DScene";
import { CodeScene } from "./components/CodeScene";
import { BenchmarkScene } from "./components/BenchmarkScene";
import { DiagramScene } from "./components/DiagramScene";
import { PayoffScene } from "./components/PayoffScene";
import { ContinuityBridgeLayer } from "./components/ContinuityBridgeLayer";

import { VisualRecipeScene } from "./components/VisualRecipeScene";

export const ReelVideo: React.FC<ReelCompositionProps> = ({ motionPlan }) => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const fallbackPalette = {
    background: [10, 14, 23] as [number, number, number],
    primary: [0, 240, 255] as [number, number, number],
    secondary: [255, 0, 128] as [number, number, number],
    accent: [255, 230, 0] as [number, number, number],
    surface: [18, 24, 38] as [number, number, number],
    text: [240, 245, 255] as [number, number, number],
  };
  const cd = motionPlan?.creative_direction || { palette: fallbackPalette };
  const palette = cd.palette || fallbackPalette;
  const scenes = motionPlan?.scenes || [];
  const bridges = motionPlan?.continuity_bridges || [];

  const totalFrames = Math.max(1, Math.round((motionPlan.duration || 50) * fps));

  // Base slow cinematic drift
  let cameraScale = interpolate(frame, [0, totalFrames], [1.0, 1.05], {
    extrapolateRight: "clamp",
  });
  let cameraTranslateX = 0;
  let cameraTranslateY = 0;
  let cameraRotate = 0;

  // Dynamic Camera Continuity: Apply impulse across scene boundary bridges
  for (let i = 0; i < scenes.length - 1; i++) {
    const nextScene = scenes[i + 1];
    const boundaryFrame = Math.round(nextScene.start * fps);
    const bridge =
      bridges.find(
        (b) => b.from_scene === scenes[i].id && b.to_scene === nextScene.id
      ) || bridges[i];

    const overlap = bridge ? bridge.overlap_frames || 14 : 14;
    const halfOverlap = Math.floor(overlap / 2);
    const startWindow = boundaryFrame - halfOverlap;
    const endWindow = boundaryFrame + (overlap - halfOverlap);

    if (frame >= startWindow && frame <= endWindow) {
      const t = interpolate(frame, [startWindow, endWindow], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      const bell = Math.sin(t * Math.PI);
      const camMode = bridge?.camera_continuity || "punch_z";

      if (camMode === "punch_z") {
        cameraScale += bell * 0.08;
      } else if (camMode === "whip") {
        cameraTranslateX += (t - 0.5) * -70;
        cameraRotate += (t - 0.5) * -1.8;
      } else if (camMode === "orbit_continue") {
        cameraRotate += Math.sin((t - 0.5) * Math.PI) * 2.2;
        cameraScale += bell * 0.04;
      } else if (camMode === "travel_y") {
        cameraTranslateY += (t - 0.5) * -50;
      }
      break;
    }
  }

  const renderSceneContent = (scene: SceneSchema) => {
    // 1. Universal Shot Designer Visual Recipe (High-end dynamic motion graphics)
    if (scene.visual_recipe) {
      return (
        <VisualRecipeScene
          scene={scene}
          creativeDirection={cd}
          recipe={scene.visual_recipe}
        />
      );
    }

    // 2. Legacy Fallback
    switch (scene.visual_type) {
      case "hook":
        return (
          <HookScene
            scene={scene}
            creativeDirection={cd}
            topic={motionPlan.topic}
          />
        );
      case "math_3d":
        return (
          <Math3DScene
            scene={scene}
            creativeDirection={cd}
          />
        );
      case "metaphor":
        return (
          <MetaphorScene
            scene={scene}
            creativeDirection={cd}
          />
        );
      case "code":
        return (
          <CodeScene
            scene={scene}
            creativeDirection={cd}
          />
        );
      case "benchmark":
      case "split":
        return (
          <BenchmarkScene
            scene={scene}
            creativeDirection={cd}
          />
        );
      case "diagram":
        return (
          <DiagramScene
            scene={scene}
            creativeDirection={cd}
          />
        );
      case "payoff":
      default:
        return (
          <PayoffScene
            scene={scene}
            creativeDirection={cd}
          />
        );
    }
  };

  return (
    <AbsoluteFill
      style={{
        transform: `scale(${cameraScale}) translate3d(${cameraTranslateX}px, ${cameraTranslateY}px, 0) rotate(${cameraRotate}deg)`,
        transformOrigin: "center center",
      }}
    >
      {/* Background layer spanning full video */}
      <Background creativeDirection={cd} />

      {/* Sequential scenes timed strictly by Motion Plan */}
      {scenes.map((scene, idx) => {
        const fromFrame = Math.max(0, Math.round(scene.start * fps));
        const durationFrames = Math.max(1, Math.round(scene.duration * fps));

        return (
          <Sequence
            key={scene.id || `scene_${idx}`}
            from={fromFrame}
            durationInFrames={durationFrames}
            name={`${idx + 1}. ${scene.visual_type.toUpperCase()}`}
          >
            {renderSceneContent(scene)}
          </Sequence>
        );
      })}

      {/* Continuity Bridge Layer: Renders continuous visual carry & motion blur across cuts */}
      <ContinuityBridgeLayer
        bridges={bridges}
        scenes={scenes}
        palette={palette}
      />
    </AbsoluteFill>
  );
};
