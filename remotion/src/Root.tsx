import React from "react";
import { Composition } from "remotion";
import { ReelVideo } from "./ReelVideo";
import { defaultMotionPlan } from "./defaultProps";
import { ReelCompositionProps } from "./types";

export const Root: React.FC = () => {
  return (
    <>
      <Composition
        id="ReelComposition"
        component={ReelVideo as React.FC<any>}
        durationInFrames={450}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          motionPlan: defaultMotionPlan,
        }}
        calculateMetadata={async ({ props }) => {
          const typedProps = props as unknown as ReelCompositionProps;
          const fps = typedProps.motionPlan?.fps || 30;
          const duration = typedProps.motionPlan?.duration || 15;
          const durationInFrames = Math.max(1, Math.round(duration * fps));

          return {
            durationInFrames,
            fps,
            width: 1080,
            height: 1920,
          };
        }}
      />
    </>
  );
};
