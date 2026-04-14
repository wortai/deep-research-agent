import { useRef, useState, useEffect, memo } from "react";
import { DotMatrix } from "./DotMatrix";

function AnimatedDotMatrixInner({ targetFilled, total, color, flickerLast, delay = 0 }: {
  targetFilled: number; total: number; color: string; flickerLast?: boolean; delay?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useRef(false);
  const [filled, setFilled] = useState(0);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !isInView.current) {
          isInView.current = true;
          let raf: number;
          const startAt = Date.now() + delay;
          const duration = 1400;
          const tick = () => {
            const now = Date.now();
            if (now < startAt) { raf = requestAnimationFrame(tick); return; }
            const progress = Math.min((now - startAt) / duration, 1);
            setFilled(Math.round(progress * targetFilled));
            if (progress < 1) raf = requestAnimationFrame(tick);
          };
          raf = requestAnimationFrame(tick);
        }
      },
      { rootMargin: "-40px" },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [targetFilled, delay]);

  return (
    <div ref={ref}>
      <DotMatrix filled={filled} total={total} color={color} flickerLast={flickerLast} />
    </div>
  );
}

export const AnimatedDotMatrix = memo(AnimatedDotMatrixInner);
