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

export const ReelVideo: React.FC<ReelCompositionProps> = ({ motionPlan }) => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const cd = motionPlan.creative_direction;
  const scenes = motionPlan.scenes || [];

  const totalFrames = Math.max(1, Math.round((motionPlan.duration || 50) * fps));
  const cameraScale = interpolate(frame, [0, totalFrames], [1.0, 1.04], {
    extrapolateRight: "clamp",
  });

  const renderSceneContent = (scene: SceneSchema) => {
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
    <AbsoluteFill style={{ transform: `scale(${cameraScale})`, transformOrigin: "center center" }}>
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
    </AbsoluteFill>
  );
};
