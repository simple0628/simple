import { useCurrentFrame, interpolate } from "remotion";

interface ShimmerTextProps {
  text: string;
  startFrame: number;
  revealDuration?: number;
  shimmerDuration?: number;
  fontSize?: number;
}

export const ShimmerText: React.FC<ShimmerTextProps> = ({
  text,
  startFrame,
  revealDuration = 20,
  shimmerDuration = 40,
  fontSize = 56,
}) => {
  const frame = useCurrentFrame();
  const localFrame = frame - startFrame;

  if (localFrame < 0) return null;

  const opacity = interpolate(localFrame, [0, revealDuration], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Shimmer sweep position (moves left to right)
  const shimmerPos = interpolate(
    localFrame,
    [revealDuration * 0.5, revealDuration * 0.5 + shimmerDuration],
    [-100, 200],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <div
      style={{
        opacity,
        fontSize,
        fontFamily: "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        fontWeight: 600,
        textAlign: "center",
        background: `linear-gradient(
          90deg,
          #e0e0e0 0%,
          #e0e0e0 ${shimmerPos - 20}%,
          #ffffff ${shimmerPos}%,
          #60a5fa ${shimmerPos + 5}%,
          #e0e0e0 ${shimmerPos + 20}%,
          #e0e0e0 100%
        )`,
        WebkitBackgroundClip: "text",
        WebkitTextFillColor: "transparent",
        backgroundClip: "text",
      }}
    >
      {text}
    </div>
  );
};
