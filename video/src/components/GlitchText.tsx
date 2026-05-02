import { useCurrentFrame, interpolate } from "remotion";

interface GlitchTextProps {
  text: string;
  startFrame: number;
  glitchDuration?: number;
  fontSize?: number;
  color?: string;
}

export const GlitchText: React.FC<GlitchTextProps> = ({
  text,
  startFrame,
  glitchDuration = 25,
  fontSize = 52,
  color = "#ffffff",
}) => {
  const frame = useCurrentFrame();
  const localFrame = frame - startFrame;

  if (localFrame < 0) return null;

  const progress = interpolate(localFrame, [0, glitchDuration], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Glitch intensity decreases as text stabilizes
  const glitchIntensity = interpolate(progress, [0, 0.7, 1], [1, 0.3, 0], {
    extrapolateRight: "clamp",
  });

  const offsetR = Math.sin(localFrame * 1.5) * 4 * glitchIntensity;
  const offsetG = Math.cos(localFrame * 2.1) * 4 * glitchIntensity;
  const offsetB = Math.sin(localFrame * 0.9) * 4 * glitchIntensity;

  const opacity = interpolate(localFrame, [0, 5], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Random clip for scan line effect
  const clipTop = Math.random() * 100 * glitchIntensity;
  const clipBottom = clipTop + 5 + Math.random() * 10;

  return (
    <div
      style={{
        position: "relative",
        fontSize,
        fontFamily: "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        fontWeight: 500,
        textAlign: "center",
        opacity,
      }}
    >
      {/* Red channel */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          color: "#ff0000",
          mixBlendMode: "screen",
          transform: `translate(${offsetR}px, ${-offsetR * 0.5}px)`,
          opacity: glitchIntensity > 0 ? 0.8 : 0,
        }}
      >
        {text}
      </div>
      {/* Green channel */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          color: "#00ff00",
          mixBlendMode: "screen",
          transform: `translate(${offsetG}px, ${offsetG * 0.5}px)`,
          opacity: glitchIntensity > 0 ? 0.8 : 0,
        }}
      >
        {text}
      </div>
      {/* Blue channel */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          color: "#0088ff",
          mixBlendMode: "screen",
          transform: `translate(${offsetB}px, ${-offsetB * 0.3}px)`,
          opacity: glitchIntensity > 0 ? 0.8 : 0,
        }}
      >
        {text}
      </div>
      {/* Main text */}
      <div style={{ position: "relative", color }}>{text}</div>
    </div>
  );
};
