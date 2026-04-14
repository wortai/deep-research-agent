import { memo } from "react";

function DotMatrixInner({ filled, total, color, flickerLast }: {
  filled: number; total: number; color: string; flickerLast?: boolean;
}) {
  return (
    <div className="flex gap-1 w-full overflow-hidden">
      {Array.from({ length: total }).map((_, i) => {
        const active = i < filled;
        const isLast = i === filled - 1;
        return (
          <div key={i} className="flex flex-col gap-[1px]">
            {[0, 1].map((row) => (
              <div key={row} className="flex gap-[1px]">
                 {[0, 1, 2].map((d) => (
                   <div
                     key={d}
                     className="w-[4px] h-[4px] sm:w-[5px] sm:h-[5px] rounded-full transition-all duration-200"
                    style={{
                      background: active ? color : "rgba(26,60,43,0.08)",
                      opacity: active ? (isLast && flickerLast ? 1 : row === 1 ? 0.6 : 1) : 1,
                      animation:
                        active && isLast && flickerLast
                          ? `dot-flicker 2.2s ease-in-out infinite ${(row * 3 + d) * 85}ms`
                          : undefined,
                    }}
                  />
                ))}
              </div>
            ))}
          </div>
        );
      })}
    </div>
  );
}

export const DotMatrix = memo(DotMatrixInner);
