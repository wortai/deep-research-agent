import { useRef, memo } from "react";
import { Link } from "react-router-dom";
import { motion, useScroll, useTransform } from "framer-motion";
import { ROUTES } from "@/lib/routes";
import { C, PENGUIN_URL } from "./tokens";
import { SolarSystemO } from "./SolarSystemO";
import { FloatingDots } from "./FloatingDots";

const FADE_UP = {
  hidden: { opacity: 0, y: 28 },
  show: { opacity: 1, y: 0, transition: { duration: 0.55, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] } },
};
const STAGGER = { show: { transition: { staggerChildren: 0.12 } } };

function HeroSectionInner() {
  const heroRef = useRef<HTMLElement>(null);
  const { scrollY } = useScroll();
  const heroY = useTransform(scrollY, [0, 400], [0, -60]);

  return (
    <motion.header
      ref={heroRef}
      style={{ y: heroY }}
      className="relative flex flex-col items-center justify-center text-center px-6 sm:px-10 md:px-20 pt-36 sm:pt-44 pb-20 sm:pb-28 border-b border-[#3A3A38]/10 overflow-hidden min-h-[85vh]"
    >
      <FloatingDots />

      <motion.div
        variants={STAGGER}
        initial="hidden"
        animate="show"
        className="flex flex-col items-center gap-6 max-w-3xl relative z-10"
      >
        <motion.div variants={FADE_UP} className="flex items-center gap-3">
          <div className="hidden sm:block w-[1px] h-10 bg-[#9EFFBF]" />
          <span className="font-mono text-[9px] sm:text-[10px] uppercase tracking-[0.2em] sm:tracking-[0.3em] text-[#1A3C2B]/60">
            Research Agent v3.0 · Always Researches First · Never Answers Cold
          </span>
          <div className="hidden sm:block w-[1px] h-10 bg-[#9EFFBF]" />
        </motion.div>

        <motion.h1
          variants={FADE_UP}
          className="font-grotesk text-5xl sm:text-7xl md:text-[9rem] font-bold tracking-tighter flex items-center gap-2 sm:gap-3 leading-none text-[#1A3C2B] no-underline decoration-none"
          style={{ textDecoration: "none" }}
        >
          W<SolarSystemO />RT
        </motion.h1>

        <motion.p
          variants={FADE_UP}
          className="font-mono text-xs sm:text-sm uppercase tracking-widest text-[#1A3C2B]/55 max-w-lg leading-relaxed"
        >
          A research agent that investigates before it speaks. You ask — WORT researches, spawns agents, synthesizes,
          and delivers. From quick lookups to full autonomous PDF reports.
        </motion.p>

        <motion.div variants={FADE_UP} className="flex flex-col sm:flex-row gap-3 sm:gap-4 mt-2">
          <Link
            to={ROUTES.chat}
            className="no-underline decoration-none px-5 sm:px-6 py-3 bg-[#1A3C2B] text-white font-mono text-[10px] uppercase tracking-[0.2em] hover:bg-[#2D7A4F] hover:no-underline transition-colors text-center"
            style={{ textDecoration: "none" }}
          >
            Start Researching
          </Link>
          <a
            href="#features"
            className="no-underline decoration-none px-5 sm:px-6 py-3 border border-[#1A3C2B]/25 font-mono text-[10px] uppercase tracking-[0.2em] hover:bg-[#9EFFBF]/20 hover:no-underline transition-colors text-center"
            style={{ textDecoration: "none" }}
          >
            See How It Works
          </a>
        </motion.div>
      </motion.div>

      <span className="hidden sm:absolute sm:bottom-6 sm:left-6 font-mono text-[8px] text-[#1A3C2B]/25 uppercase tracking-widest">
        WORT_RESEARCH_AGENT · v3.0
      </span>
      <span className="hidden sm:absolute sm:bottom-6 sm:right-6 font-mono text-[8px] text-[#1A3C2B]/25 uppercase tracking-widest">
        POWERED_BY_SUBAGENTS
      </span>
    </motion.header>
  );
}

export const HeroSection = memo(HeroSectionInner);
