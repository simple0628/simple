import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

// Each line is its own "scene" — one sentence per screen
const scenes = [
  { text: "每一款产品，都在要求你学习。", start: 0, end: 80 },
  { text: "学习它的界面，学习它的逻辑，学习它的规则。", start: 85, end: 175, staggerWords: true },
  // Black pause
  { text: "", start: 175, end: 195 },
  { text: "如果有一款工具，不需要你学任何东西呢？", start: 195, end: 285, apple: true },
  // Short black
  { text: "", start: 285, end: 300 },
  { text: "你只需要说出你想做的事。", start: 300, end: 375 },
  { text: "对话——就是唯一的操作方式。", start: 380, end: 480, finale: true },
];

// Slide up + fade in
const SlideIn: React.FC<{ children: React.ReactNode; start: number; end: number }> = ({
  children,
  start,
  end,
}) => {
  const frame = useCurrentFrame();
  const localFrame = frame - start;

  if (frame < start || frame >= end) return null;

  const opacity = interpolate(localFrame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });
  const translateY = interpolate(localFrame, [0, 15], [40, 0], {
    extrapolateRight: "clamp",
  });

  // Fade out at end
  const fadeOut = interpolate(frame, [end - 10, end], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        opacity: opacity * fadeOut,
        transform: `translateY(${translateY}px)`,
      }}
    >
      {children}
    </div>
  );
};

// Staggered words (三个"学习"依次出现)
const StaggerWords: React.FC<{ text: string; start: number; end: number }> = ({
  text,
  start,
  end,
}) => {
  const frame = useCurrentFrame();
  if (frame < start || frame >= end) return null;

  // Split by Chinese comma
  const parts = text.split("，");

  // Fade out at end
  const fadeOut = interpolate(frame, [end - 10, end], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div style={{ opacity: fadeOut, textAlign: "center" }}>
      {parts.map((part, i) => {
        const partStart = start + i * 20;
        const localFrame = frame - partStart;

        const opacity = interpolate(localFrame, [0, 12], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const translateY = interpolate(localFrame, [0, 12], [25, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

        return (
          <span
            key={i}
            style={{
              opacity,
              display: "inline-block",
              transform: `translateY(${translateY}px)`,
              fontSize: 46,
              color: "#d0d0d0",
              fontFamily: "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
              fontWeight: 300,
            }}
          >
            {part}
            {i < parts.length - 1 ? "，" : "。"}
          </span>
        );
      })}
    </div>
  );
};

// Apple style: scale down + blur clear
const AppleReveal: React.FC<{ text: string; start: number; end: number }> = ({
  text,
  start,
  end,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (frame < start || frame >= end) return null;

  const localFrame = frame - start;

  const scale = interpolate(localFrame, [0, 18], [1.08, 1], {
    extrapolateRight: "clamp",
  });
  const blur = interpolate(localFrame, [0, 18], [8, 0], {
    extrapolateRight: "clamp",
  });
  const opacity = interpolate(localFrame, [0, 12], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Fade out
  const fadeOut = interpolate(frame, [end - 10, end], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        opacity: opacity * fadeOut,
        transform: `scale(${scale})`,
        filter: `blur(${blur}px)`,
        fontSize: 52,
        color: "#ffffff",
        fontFamily: "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        fontWeight: 500,
        textAlign: "center",
      }}
    >
      {text}
    </div>
  );
};

// Finale: burst scale + glow
const Finale: React.FC<{ text: string; start: number; end: number }> = ({
  text,
  start,
  end,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (frame < start || frame >= end) return null;

  const localFrame = frame - start;

  // Spring for natural bounce
  const scaleSpring = spring({
    frame: localFrame,
    fps,
    config: { damping: 12, stiffness: 80, mass: 0.8 },
  });

  const scale = interpolate(scaleSpring, [0, 1], [0.7, 1]);

  const opacity = interpolate(localFrame, [0, 8], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Glow intensity pulses subtly
  const glowIntensity = interpolate(
    Math.sin(localFrame * 0.08),
    [-1, 1],
    [0.6, 1]
  );

  return (
    <div
      style={{
        opacity,
        transform: `scale(${scale})`,
        fontSize: 64,
        color: "#ffffff",
        fontFamily: "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        fontWeight: 700,
        textAlign: "center",
        textShadow: `0 0 ${20 * glowIntensity}px rgba(96,165,250,0.9), 0 0 ${60 * glowIntensity}px rgba(96,165,250,0.4), 0 0 ${100 * glowIntensity}px rgba(96,165,250,0.2)`,
      }}
    >
      {text}
    </div>
  );
};

export const Opening: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0a0a",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {scenes.map((scene, i) => {
        if (scene.text === "") return null;

        if ((scene as any).staggerWords) {
          return (
            <AbsoluteFill
              key={i}
              style={{ justifyContent: "center", alignItems: "center" }}
            >
              <StaggerWords text={scene.text} start={scene.start} end={scene.end} />
            </AbsoluteFill>
          );
        }

        if ((scene as any).apple) {
          return (
            <AbsoluteFill
              key={i}
              style={{ justifyContent: "center", alignItems: "center" }}
            >
              <AppleReveal text={scene.text} start={scene.start} end={scene.end} />
            </AbsoluteFill>
          );
        }

        if ((scene as any).finale) {
          return (
            <AbsoluteFill
              key={i}
              style={{ justifyContent: "center", alignItems: "center" }}
            >
              <Finale text={scene.text} start={scene.start} end={scene.end} />
            </AbsoluteFill>
          );
        }

        // Default: slide in
        return (
          <AbsoluteFill
            key={i}
            style={{ justifyContent: "center", alignItems: "center" }}
          >
            <SlideIn start={scene.start} end={scene.end}>
              <div
                style={{
                  fontSize: 46,
                  color: "#e0e0e0",
                  fontFamily: "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
                  fontWeight: 300,
                  textAlign: "center",
                }}
              >
                {scene.text}
              </div>
            </SlideIn>
          </AbsoluteFill>
        );
      })}
    </AbsoluteFill>
  );
};
