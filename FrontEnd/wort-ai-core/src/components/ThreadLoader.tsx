import React from "react";

export const ThreadLoader = () => {
    return (
        <div className="relative flex items-center justify-center w-5 h-5 shrink-0">
            <svg viewBox="0 0 100 100" className="w-full h-full overflow-visible">
                {/* Outer Circle - 12 dots. Moves clockwise */}
                <g className="origin-center">
                    {Array.from({ length: 12 }).map((_, i) => (
                        <circle
                            key={`outer-${i}`}
                            cx={50 + 35 * Math.cos((i * 30 * Math.PI) / 180)}
                            cy={50 + 35 * Math.sin((i * 30 * Math.PI) / 180)}
                            r="9"
                            className="dot-chase fill-[#3A3A38] opacity-20"
                            style={{ animationDelay: `${(i * 0.1) - 1.2}s` }}
                        />
                    ))}
                </g>

                {/* Inner Circle - 8 dots. Moves anticlockwise */}
                <g className="origin-center">
                    {Array.from({ length: 8 }).map((_, i) => (
                        <circle
                            key={`inner-${i}`}
                            cx={50 + 16 * Math.cos((i * 45 * Math.PI) / 180)}
                            cy={50 + 16 * Math.sin((i * 45 * Math.PI) / 180)}
                            r="7"
                            className="dot-chase fill-[#3A3A38] opacity-20"
                            style={{ animationDelay: `${(((8 - i) % 8) * 0.15) - 1.2}s` }}
                        />
                    ))}
                </g>
            </svg>
        </div>
    );
};
