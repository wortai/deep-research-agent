import { useRef, useState, useEffect, memo } from "react";
import { motion } from "framer-motion";
import { C } from "./tokens";

const TERMINAL_LINES = [
  { tag: "[EXEC]", text: "QUERYING: arxiv.org, pubmed, scholar...", color: C.mint },
  { tag: "[IMG]",  text: "VISION: extracted 3 diagrams, 2 charts...", color: C.mint },
  { tag: "[DATA]", text: "Parsed 18.7kb — 94% relevance score...", color: "rgba(26,60,43,0.5)" },
  { tag: "[FACT]", text: "Cross-referencing 7 sources...", color: "rgba(26,60,43,0.5)" },
  { tag: "[RES]",  text: "Verified. Response generated in 1.2s.", color: C.gold },
];

function AnimatedTerminalInner() {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useRef(false);
  const [visible, setVisible] = useState(0);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !isInView.current) {
          isInView.current = true;
          setVisible(0);
          const timers: ReturnType<typeof setTimeout>[] = [];
          TERMINAL_LINES.forEach((_, i) => {
            timers.push(setTimeout(() => setVisible(i + 1), i * 480 + 300));
          });
        }
      },
      { rootMargin: "-80px" },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className="bg-white border border-[#1A3C2B]/10 p-3 sm:p-4 font-mono text-[9px] sm:text-[10px] space-y-1 mt-4 overflow-hidden"
    >
      {TERMINAL_LINES.map((line, i) => (
        <motion.div
          key={i}
          className="flex gap-2"
          initial={{ opacity: 0, x: -10 }}
          animate={i < visible ? { opacity: 1, x: 0 } : { opacity: 0, x: -10 }}
          transition={{ duration: 0.25, ease: "easeOut" }}
        >
          <span style={{ color: line.color }}>{line.tag}</span>
          <span style={{ color: line.color === C.gold ? C.gold : "rgba(26,60,43,0.6)" }}>{line.text}</span>
        </motion.div>
      ))}
    </div>
  );
}

export const AnimatedTerminal = memo(AnimatedTerminalInner);
