import { useCurrentFrame, interpolate } from "remotion";

interface BlurRevealProps {
  text: string;
  startFrame: number;
  duration?: number;
  fontSize?: number;
  color?: string;
}

export const BlurReveal: React.FC<BlurRevealProps> = ({
  text,
  startFrame,
  duration = 20,
  fontSize = 48,
  color = "#e0e0e0",
}) => {
  const frame = useCurrentFrame();
  const localFrame = frame - startFrame;

  if (localFrame < 0) return null;

  const opacity = interpolate(localFrame, [0, duration], [0, 1], {
    extrapolateRight: "clamp",
  });

  const blur = interpolate(localFrame, [0, duration], [12, 0], {
    extrapolateRight: "clamp",
  });

  const scale = interpolate(localFrame, [0, duration], [0.95, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        opacity,
        filter: `blur(${blur}px)`,
        transform: `scale(${scale})`,
        fontSize,
        color,
        fontFamily: "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        fontWeight: 300,
        lineHeight: 1.8,
        textAlign: "center",
      }}
    >
      {text}
    </div>
  );
};
