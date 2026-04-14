import { memo } from "react";
import { motion } from "framer-motion";

const DOTS = Array.from({ length: 12 }, (_, i) => ({
  id: i,
  cx: `${8 + (i % 4) * 28}%`,
  cy: `${15 + Math.floor(i / 4) * 35}%`,
  delay: i * 0.25,
  duration: 4 + i * 0.3,
}));

function FloatingDotsInner() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden>
      {DOTS.map((d) => (
        <motion.div
          key={d.id}
          className="absolute w-1 h-1 rounded-full bg-[#1A3C2B]"
          style={{ left: d.cx, top: d.cy, opacity: 0.06 }}
          animate={{ y: [0, -10, 0], opacity: [0.06, 0.15, 0.06] }}
          transition={{ delay: d.delay, duration: d.duration, repeat: Infinity, ease: "easeInOut" }}
        />
      ))}
    </div>
  );
}

export const FloatingDots = memo(FloatingDotsInner);
