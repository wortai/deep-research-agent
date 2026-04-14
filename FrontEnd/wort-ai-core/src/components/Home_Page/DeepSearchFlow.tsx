import { useRef, memo } from "react";
import { motion } from "framer-motion";
import { C } from "./tokens";
import { AnimatedDotMatrix } from "./AnimatedDotMatrix";

const AGENTS = [
  { name: "AGENT_01: RESEARCH THE DEFINITION AND FUNDAMENTAL", status: "RESEARCHING", step: "cross-referencing 12 sources", mode: "LOW" },
  { name: "AGENT_02: RESEARCH THE CORE COMPONENTS AND BUILDIN", status: "RESEARCHING", step: "analyzing architecture patterns", mode: "MID" },
  { name: "AGENT_03: RESEARCH SIMPLE REAL-WORLD EXAMPLES OF S", status: "REVIEWING", step: "validating 8 case studies", mode: "HIGH" },
];

const ORCH = { x: 160, y: 22 };
const AGENT_SVG = [
  { x: 52,  y: 82, label: "AGENT_01", role: "Definition",  mode: "LOW" },
  { x: 160, y: 82, label: "AGENT_02", role: "Components",  mode: "MID" },
  { x: 268, y: 82, label: "AGENT_03", role: "Examples",    mode: "HIGH" },
];
const WRITER = { x: 160, y: 148 };

function DeepSearchFlowInner() {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useRef(false);

  const svgFg = C.forest;
  const svgFgMuted = C.forestMuted;

  return (
    <div ref={ref} className="flex flex-col gap-3 w-full min-w-0">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
        className="w-full border border-[#3A3A38]/20 bg-[#F7F7F5] p-3 sm:p-4 lg:p-5 flex flex-col gap-1"
      >
        <div className="flex items-center gap-4 mb-3">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-[#9EFFBF]" style={{ boxShadow: C.mintGlow }} />
            <span className="font-mono text-[10px] uppercase tracking-widest text-[#1A3C2B]/70">Researching [100%]</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-[#F4D35E]" />
            <span className="font-mono text-[10px] uppercase tracking-widest text-[#1A3C2B]/70">Reviewing [100%]</span>
          </div>
        </div>

        {AGENTS.map((a, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -12 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.15 + i * 0.12, duration: 0.35 }}
            className="border border-[#2D7A4F]/30 p-2 sm:p-3 flex flex-col gap-2"
          >
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 sm:gap-2.5 min-w-0">
                <div className="w-4 h-4 sm:w-5 sm:h-5 flex items-center justify-center border border-[#2D7A4F]/35 shrink-0">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#2D7A4F]/25" />
                </div>
                <span className="font-mono text-[9px] sm:text-[10px] font-bold uppercase tracking-widest text-[#1A3C2B]/90 truncate">
                  {a.name}
                </span>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className="font-mono text-[8px] uppercase tracking-widest px-1.5 py-0.5 border border-[#2D7A4F]/30 text-[#1A3C2B]/50">
                  DEPTH: {a.mode}
                </span>
              </div>
            </div>
            <AnimatedDotMatrix
              targetFilled={15}
              total={15}
              color={a.status === "REVIEWING" ? C.gold : C.mint}
              delay={i * 180}
            />
          </motion.div>
        ))}

        <motion.div
          initial={{ opacity: 0, x: -12 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.55, duration: 0.35 }}
          className="border border-[#7DD3FC]/30 p-2 sm:p-3 flex flex-col gap-2 mt-1"
        >
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 sm:gap-2.5 min-w-0">
              <div className="w-4 h-4 sm:w-5 sm:h-5 flex items-center justify-center border border-[#7DD3FC]/35 shrink-0">
                <div className="w-1.5 h-1.5 rounded-full bg-[#7DD3FC] animate-pulse" />
              </div>
              <span className="font-mono text-[9px] sm:text-[10px] font-bold uppercase tracking-widest text-[#1A3C2B]/90 truncate">
                WRITER_SYNTHESIS_ENGINE
              </span>
            </div>
          </div>
          <AnimatedDotMatrix targetFilled={12} total={15} color="#7DD3FC" flickerLast delay={540} />
        </motion.div>
      </motion.div>

      <div className="w-full shrink-0 flex items-center justify-center overflow-hidden py-1">
        <svg
          viewBox="-4 -6 328 222"
          preserveAspectRatio="xMidYMid meet"
          className="block h-auto w-full max-w-full"
          aria-hidden
        >
          {AGENT_SVG.map((a, i) => (
            <motion.line
              key={`oa-${i}`}
              x1={ORCH.x} y1={ORCH.y + 13}
              x2={a.x}    y2={a.y - 13}
              stroke={C.forest}
              strokeWidth="0.8"
              strokeDasharray="2 5"
              initial={{ pathLength: 0, opacity: 0 }}
              whileInView={{ pathLength: 1, opacity: 0.35 }}
              viewport={{ once: true }}
              transition={{ delay: 0.6 + i * 0.1, duration: 0.5, ease: "easeOut" }}
            />
          ))}
          {AGENT_SVG.map((a, i) => (
            <motion.line
              key={`aw-${i}`}
              x1={a.x}
              y1={a.y + 15 + 11 + 1}
              x2={WRITER.x}
              y2={WRITER.y - 13}
              stroke={C.forestGreen}
              strokeWidth="0.8"
              strokeDasharray="2 5"
              initial={{ pathLength: 0, opacity: 0 }}
              whileInView={{ pathLength: 1, opacity: 0.45 }}
              viewport={{ once: true }}
              transition={{ delay: 0.9 + i * 0.1, duration: 0.5, ease: "easeOut" }}
            />
          ))}

          <motion.g
            initial={{ scale: 0, opacity: 0 }}
            whileInView={{ scale: 1, opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.5, type: "spring", stiffness: 280, damping: 22 }}
            style={{ transformOrigin: `${ORCH.x}px ${ORCH.y}px` }}
          >
            <rect x={ORCH.x - 40} y={ORCH.y - 13} width={80} height={26} fill="none" stroke={C.forest} strokeWidth="1" rx="0" />
            <text x={ORCH.x} y={ORCH.y + 4} textAnchor="middle" fontFamily="JetBrains Mono, monospace" fontSize="8" fontWeight="500" fill={svgFg}>ORCHESTRATOR</text>
          </motion.g>

          {AGENT_SVG.map((a, i) => (
            <motion.g
              key={`an-${i}`}
              initial={{ scale: 0, opacity: 0 }}
              whileInView={{ scale: 1, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.65 + i * 0.12, type: "spring", stiffness: 260, damping: 20 }}
              style={{ transformOrigin: `${a.x}px ${a.y}px` }}
            >
              <rect x={a.x - 36} y={a.y - 13} width={72} height={26} fill="none" stroke={C.forestGreen} strokeWidth="1" rx="0" />
              <text x={a.x} y={a.y + 1} textAnchor="middle" fontFamily="JetBrains Mono, monospace" fontSize="7.5" fontWeight="500" fill={svgFg}>{a.label}</text>
              <text x={a.x} y={a.y + 10} textAnchor="middle" fontFamily="JetBrains Mono, monospace" fontSize="6" fontWeight="400" fill={svgFgMuted}>{a.role}</text>
              <rect x={a.x - 22} y={a.y + 15} width={44} height={11} fill="none" stroke={C.forestGreen} strokeWidth="0.6" rx="0" />
              <text x={a.x} y={a.y + 22.5} textAnchor="middle" fontFamily="JetBrains Mono, monospace" fontSize="5.5" fontWeight="500" fill={svgFg}>DEPTH: {a.mode}</text>
            </motion.g>
          ))}

          <motion.g
            initial={{ scale: 0, opacity: 0 }}
            whileInView={{ scale: 1, opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 1.05, type: "spring", stiffness: 260, damping: 20 }}
            style={{ transformOrigin: `${WRITER.x}px ${WRITER.y}px` }}
          >
            <rect x={WRITER.x - 52} y={WRITER.y - 13} width={104} height={26} fill={C.blueFill} stroke={C.blue} strokeWidth="1" rx="0" />
            <text x={WRITER.x} y={WRITER.y + 5} textAnchor="middle" fontFamily="JetBrains Mono, monospace" fontSize="8" fontWeight="500" fill={svgFg}>WRITER_SYNTHESIS</text>
          </motion.g>

          <motion.line
            x1={WRITER.x} y1={WRITER.y + 13}
            x2={WRITER.x} y2={WRITER.y + 28}
            stroke={C.pdfBorder}
            strokeWidth="0.8"
            strokeDasharray="2 5"
            initial={{ pathLength: 0, opacity: 0 }}
            whileInView={{ pathLength: 1, opacity: 0.7 }}
            viewport={{ once: true }}
            transition={{ delay: 1.2, duration: 0.3 }}
          />
          <motion.g
            initial={{ opacity: 0, scale: 0 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 1.3, type: "spring", stiffness: 260, damping: 20 }}
            style={{ transformOrigin: `${WRITER.x}px ${WRITER.y + 36}px` }}
          >
            <rect x={WRITER.x - 22} y={WRITER.y + 28} width={44} height={16} fill={C.pdfFill} stroke={C.pdfBorder} strokeWidth="1" rx="0" />
            <text x={WRITER.x} y={WRITER.y + 39} textAnchor="middle" fontFamily="JetBrains Mono, monospace" fontSize="7" fontWeight="500" fill={C.coral}>PDF OUT</text>
          </motion.g>
        </svg>
      </div>
    </div>
  );
}

export const DeepSearchFlow = memo(DeepSearchFlowInner);
