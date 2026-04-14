import { memo } from "react";
import { motion, useScroll, useSpring } from "framer-motion";

function ScrollProgressBarInner() {
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, { stiffness: 100, damping: 30 });
  return (
    <motion.div
      className="fixed top-0 left-0 right-0 h-[2px] z-[100] origin-left"
      style={{ scaleX, background: "#9EFFBF" }}
    />
  );
}

export const ScrollProgressBar = memo(ScrollProgressBarInner);
