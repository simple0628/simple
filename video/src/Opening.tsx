import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";

const lines = [
  { text: "每一款产品，都在要求你学习。", start: 15 },
  { text: "学习它的界面，学习它的逻辑，学习它的规则。", start: 75 },
  { text: "", start: 130 },
  { text: "如果有一款工具，不需要你学任何东西呢？", start: 140 },
  { text: "", start: 200 },
  { text: "你只需要说出你想做的事。", start: 210 },
];

const FINALE_TEXT = "对话——就是唯一的操作方式。";
const FINALE_START = 265;
const CHARS_PER_FRAME = 0.8;

export const Opening: React.FC = () => {
  const frame = useCurrentFrame();

  // After finale starts, push previous text up and fade it
  const finaleProgress = interpolate(
    frame,
    [FINALE_START - 10, FINALE_START + 15],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const previousOffset = finaleProgress * -60;
  const previousOpacity = interpolate(finaleProgress, [0, 1], [1, 0.3], {
    extrapolateRight: "clamp",
  });

  // Active line (for cursor)
  const activeLineIndex = lines.reduce((latest, line, i) => {
    if (frame >= line.start && line.text !== "") return i;
    return latest;
  }, -1);

  // Finale
  const finaleOpacity = interpolate(
    frame,
    [FINALE_START, FINALE_START + 20],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0a0a",
        justifyContent: "center",
        alignItems: "center",
        padding: 120,
      }}
    >
      {/* Previous lines (typewriter) */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 4,
          transform: `translateY(${previousOffset}px)`,
          opacity: previousOpacity,
          transition: "none",
        }}
      >
        {lines.map((line, i) => {
          if (line.text === "") return <div key={i} style={{ height: 30 }} />;

          const localFrame = frame - line.start;
          const charsToShow = Math.floor(localFrame * CHARS_PER_FRAME);
          const isDone = charsToShow >= line.text.length;
          const isActive = i === activeLineIndex && finaleProgress === 0;

          return (
            <div
              key={i}
              style={{
                fontSize: 46,
                color: "#e0e0e0",
                fontFamily: "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
                fontWeight: 300,
                lineHeight: 2,
                textAlign: "center",
                visibility: localFrame >= 0 ? "visible" : "hidden",
              }}
            >
              {localFrame >= 0 ? line.text.slice(0, charsToShow) : ""}
              {isActive && (
                <span
                  style={{
                    display: "inline-block",
                    width: 2,
                    height: "0.9em",
                    backgroundColor: "#60a5fa",
                    marginLeft: 2,
                    verticalAlign: "middle",
                    opacity:
                      isDone && Math.floor(localFrame / 8) % 2 === 0 ? 1 : isDone ? 0 : 1,
                  }}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Finale: glow + scale in */}
      {frame >= FINALE_START && (
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: `translate(-50%, -50%) scale(${interpolate(
              frame,
              [FINALE_START, FINALE_START + 20],
              [0.85, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            )})`,
            opacity: finaleOpacity,
          }}
        >
          <div
            style={{
              fontSize: 60,
              fontFamily: "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
              fontWeight: 600,
              textAlign: "center",
              color: "#ffffff",
              textShadow: `0 0 20px rgba(96,165,250,0.8), 0 0 60px rgba(96,165,250,0.4)`,
            }}
          >
            {FINALE_TEXT}
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};
