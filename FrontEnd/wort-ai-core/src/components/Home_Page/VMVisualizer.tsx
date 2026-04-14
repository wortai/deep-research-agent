import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";

const forest = "#1A3C2B";
const mint = "#9EFFBF";
const coral = "#FF8C69";
const grid = "#3A3A38";

/* ─── Step 1: SPIN VM ─── */
function SpinVM() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="flex flex-col items-center justify-center h-full gap-5 w-full px-4"
    >
      {/* Server rack */}
      <div className="relative flex flex-col gap-2.5 w-full max-w-[240px]">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -14 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.15, duration: 0.3 }}
            className="flex items-center gap-3 px-4 py-2.5 border border-[#3A3A38]/15 bg-[#F7F7F5] w-full"
          >
            <motion.div
              className="w-2.5 h-2.5 rounded-full shrink-0"
              animate={{
                backgroundColor: [mint, `${mint}66`, mint],
                boxShadow: [`0 0 5px ${mint}66`, `0 0 10px ${mint}`, `0 0 5px ${mint}66`],
              }}
              transition={{ repeat: Infinity, duration: 1.2, delay: i * 0.3 }}
            />
            <div className="flex-1 flex gap-[3px]">
              {Array.from({ length: 10 }).map((_, j) => (
                <motion.div
                  key={j}
                  className="flex-1 h-[4px] rounded-full"
                  animate={{ opacity: [0.15, 0.75, 0.15] }}
                  transition={{ repeat: Infinity, duration: 0.8, delay: j * 0.07 + i * 0.2 }}
                  style={{ backgroundColor: mint }}
                />
              ))}
            </div>
            <span className="font-mono text-[9px] text-[#1A3C2B]/50 ml-1 shrink-0">
              {i === 0 ? "CPU" : i === 1 ? "MEM" : "NET"}
            </span>
          </motion.div>
        ))}
      </div>
      <motion.div
        animate={{ opacity: [0.4, 1, 0.4] }}
        transition={{ repeat: Infinity, duration: 1.5 }}
        className="font-mono text-[10px] uppercase tracking-widest text-[#1A3C2B]/50"
      >
        Booting secure microVM...
      </motion.div>
    </motion.div>
  );
}

/* ─── Step 2: RUN CODE ─── */
function RunCode() {
  const lines = [
    { indent: 0, text: "import analysis from './core';" },
    { indent: 0, text: "const data = await fetch(src);" },
    { indent: 0, text: "const result = analysis.run({" },
    { indent: 1, text: "depth: 'HIGH'," },
    { indent: 1, text: "sources: data.refs," },
    { indent: 0, text: "});" },
    { indent: 0, text: "export(result, 'pdf');" },
  ];

  const [activeLine, setActiveLine] = useState(0);
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveLine((prev) => (prev + 1) % lines.length);
    }, 420);
    return () => clearInterval(interval);
  }, [lines.length]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="flex flex-col h-full justify-center px-4 w-full"
    >
      <div className="border border-[#3A3A38]/12 bg-[#F7F7F5] px-4 py-3 font-mono text-[10px] leading-[1.9] overflow-hidden w-full">
        {lines.map((l, i) => (
          <div
            key={i}
            className="flex items-center gap-3 transition-colors duration-200"
            style={{ paddingLeft: l.indent * 16 }}
          >
            <span className="w-4 text-right text-[#1A3C2B]/20 select-none text-[9px] shrink-0">
              {i + 1}
            </span>
            <span className={i <= activeLine ? "text-[#1A3C2B]/80" : "text-[#1A3C2B]/25"}>
              {l.text}
            </span>
            {i === activeLine && (
              <motion.span
                className="inline-block w-[5px] h-[11px] ml-[1px]"
                style={{ backgroundColor: coral }}
                animate={{ opacity: [1, 0] }}
                transition={{ repeat: Infinity, duration: 0.6 }}
              />
            )}
          </div>
        ))}
      </div>
      <motion.div
        animate={{ opacity: [0.4, 1, 0.4] }}
        transition={{ repeat: Infinity, duration: 1.5 }}
        className="font-mono text-[10px] uppercase tracking-widest text-[#1A3C2B]/50 mt-3 text-center"
      >
        Executing analysis...
      </motion.div>
    </motion.div>
  );
}

/* ─── Step 3: WEB_CRAWL ─── */
function WebCrawl() {
  const cx = 110, cy = 90;
  const nodes = [
    { x: cx,      y: cy,      r: 16 },
    { x: cx - 66, y: cy - 44, r: 9 },
    { x: cx + 66, y: cy - 44, r: 9 },
    { x: cx - 80, y: cy + 20, r: 8 },
    { x: cx - 22, y: cy + 60, r: 8 },
    { x: cx + 44, y: cy + 56, r: 8 },
    { x: cx + 80, y: cy + 10, r: 8 },
  ];
  const edges = [
    [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [1, 3], [2, 6], [4, 5],
  ] as const;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="flex flex-col items-center justify-center h-full gap-4 w-full px-3"
    >
      <svg viewBox="0 10 220 160" className="w-full h-auto overflow-visible">
        {edges.map(([a, b], i) => (
          <motion.line
            key={i}
            x1={nodes[a].x} y1={nodes[a].y}
            x2={nodes[b].x} y2={nodes[b].y}
            stroke={mint}
            strokeWidth="1"
            strokeDasharray="4 3"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 0.5 }}
            transition={{ delay: 0.1 + i * 0.06, duration: 0.5 }}
          />
        ))}
        {nodes.map((n, i) => (
          <motion.circle
            key={i}
            cx={n.x} cy={n.y} r={n.r}
            fill={i === 0 ? `${forest}15` : `${mint}20`}
            stroke={i === 0 ? forest : mint}
            strokeWidth="1"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3 + i * 0.08, type: "spring", stiffness: 200 }}
          />
        ))}
        {/* Center label */}
        <text x={cx} y={cy + 5} textAnchor="middle" fontFamily="JetBrains Mono, monospace"
          fontSize="7" fontWeight="500" fill={forest}>WORT</text>
        {/* Data packets */}
        {[1, 3, 5].map((idx) => (
          <motion.circle
            key={`pulse-${idx}`}
            r={3}
            fill={coral}
            animate={{
              cx: [nodes[0].x, nodes[idx].x],
              cy: [nodes[0].y, nodes[idx].y],
              opacity: [1, 0],
            }}
            transition={{ repeat: Infinity, duration: 1.4, delay: idx * 0.3, ease: "easeOut" }}
          />
        ))}
      </svg>
      <motion.div
        animate={{ opacity: [0.4, 1, 0.4] }}
        transition={{ repeat: Infinity, duration: 1.5 }}
        className="font-mono text-[10px] uppercase tracking-widest text-[#1A3C2B]/50"
      >
        Crawling 14 sources...
      </motion.div>
    </motion.div>
  );
}

/* ─── Step 4: SPAWN AGENTS ─── */
function SpawnAgents() {
  const agentLabels = ["AGENT_01", "AGENT_02", "AGENT_03"];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="flex flex-col items-center justify-center h-full gap-4 w-full px-3"
    >
      <svg viewBox="0 0 220 120" className="w-full h-auto overflow-visible">
        {/* Orchestrator box */}
        <motion.rect
          x={70} y={4} width={80} height={28} rx={2}
          fill={`${forest}15`} stroke={forest} strokeWidth="1"
          initial={{ scale: 0 }} animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 200 }}
          style={{ transformOrigin: "110px 18px" }}
        />
        <text x={110} y={22} textAnchor="middle" fontFamily="JetBrains Mono, monospace"
          fontSize="8.5" fontWeight="500" fill={forest}>
          ORCHESTRATOR
        </text>

        {/* Lines to agents */}
        {agentLabels.map((_, i) => {
          const ax = 28 + i * 82;
          return (
            <motion.line
              key={`l-${i}`}
              x1={110} y1={32} x2={ax} y2={68}
              stroke={forest} strokeWidth="0.8" strokeDasharray="4 3"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ delay: 0.3 + i * 0.1, duration: 0.4 }}
            />
          );
        })}

        {/* Agent nodes */}
        {agentLabels.map((label, i) => {
          const ax = 28 + i * 82;
          return (
            <motion.g key={i}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.5 + i * 0.12, type: "spring", stiffness: 200 }}
              style={{ transformOrigin: `${ax}px 82px` }}
            >
              <rect x={ax - 34} y={68} width={68} height={28} rx={2}
                fill={`${mint}20`} stroke={mint} strokeWidth="1"
              />
              <text x={ax} y={86} textAnchor="middle" fontFamily="JetBrains Mono, monospace"
                fontSize="8" fontWeight="500" fill={forest}>
                {label}
              </text>
              <motion.circle
                cx={ax - 27} cy={82} r={2.5}
                fill={mint}
                animate={{ opacity: [1, 0.3, 1], r: [2.5, 3.5, 2.5] }}
                transition={{ repeat: Infinity, duration: 1, delay: i * 0.25 }}
              />
            </motion.g>
          );
        })}
      </svg>
      <motion.div
        animate={{ opacity: [0.4, 1, 0.4] }}
        transition={{ repeat: Infinity, duration: 1.5 }}
        className="font-mono text-[10px] uppercase tracking-widest text-[#1A3C2B]/50"
      >
        Delegating to sub-agents...
      </motion.div>
    </motion.div>
  );
}

/* ─── Step 5: SYNTHESIZE ─── */
function Synthesize() {
  const pageLines = 10;
  const [filled, setFilled] = useState(0);

  useEffect(() => {
    if (filled >= pageLines) return;
    const timer = setTimeout(() => setFilled((f) => f + 1), 240);
    return () => clearTimeout(timer);
  }, [filled]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="flex flex-col items-center justify-center h-full gap-4 w-full px-4"
    >
      {/* Document */}
      <div className="relative border border-[#3A3A38]/15 bg-[#F7F7F5] px-5 py-4 w-full max-w-[200px]">
        {/* Header bar */}
        <div className="flex items-center gap-2 mb-3 pb-2 border-b border-[#3A3A38]/10">
          <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: `${coral}35` }} />
          <div className="h-[4px] flex-1 rounded-full bg-[#1A3C2B]/10" />
        </div>
        {/* Lines filling in */}
        <div className="flex flex-col gap-[7px]">
          {Array.from({ length: pageLines }).map((_, i) => {
            const widths = [100, 82, 94, 68, 96, 58, 86, 72, 90, 44];
            return (
              <motion.div
                key={i}
                className="h-[4px] rounded-full"
                style={{
                  width: `${widths[i]}%`,
                  backgroundColor: i < filled ? `${forest}28` : `${grid}08`,
                }}
                animate={i === filled - 1 ? { opacity: [0.3, 1] } : {}}
                transition={{ duration: 0.25 }}
              />
            );
          })}
        </div>
        {/* PDF badge */}
        <motion.div
          className="absolute -bottom-3 -right-3 px-2 py-1 border border-[#3A3A38]/15 bg-[#F7F7F5]"
          initial={{ scale: 0 }}
          animate={{ scale: filled >= pageLines ? 1 : 0 }}
          transition={{ type: "spring", stiffness: 300, damping: 18 }}
        >
          <span className="font-mono text-[9px] font-bold text-[#FF8C69] uppercase tracking-wider">PDF</span>
        </motion.div>
      </div>
      <motion.div
        animate={{ opacity: [0.4, 1, 0.4] }}
        transition={{ repeat: Infinity, duration: 1.5 }}
        className="font-mono text-[10px] uppercase tracking-widest text-[#1A3C2B]/50"
      >
        {filled >= pageLines ? "Report ready" : "Synthesizing report..."}
      </motion.div>
    </motion.div>
  );
}

/* ─── Step 6 (Complete) ─── */
function CompletedState() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="flex flex-col items-center justify-center h-full gap-4"
    >
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", stiffness: 200, damping: 14 }}
        className="w-16 h-16 rounded-full flex items-center justify-center border border-[#9EFFBF]/40"
        style={{ background: `${mint}18` }}
      >
        <svg width="28" height="28" viewBox="0 0 18 18" fill="none">
          <motion.path
            d="M4 9.5L7.5 13L14 5"
            stroke={mint}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ delay: 0.2, duration: 0.5, ease: "easeOut" }}
          />
        </svg>
      </motion.div>
      <span className="font-mono text-[11px] uppercase tracking-widest text-[#9EFFBF]">
        All tasks complete
      </span>
    </motion.div>
  );
}

/* ─── Idle (Step 0) ─── */
function IdleState() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex flex-col items-center justify-center h-full gap-2"
    >
      <div className="w-8 h-8 rounded-full border border-[#3A3A38]/10 flex items-center justify-center">
        <div className="w-2 h-2 rounded-full bg-[#3A3A38]/10" />
      </div>
      <span className="font-mono text-[8px] uppercase tracking-widest text-[#1A3C2B]/30">
        Awaiting task...
      </span>
    </motion.div>
  );
}

/* ─── Main Export ─── */
export default function VMVisualizer({ step }: { step: number }) {
  return (
    <div className="w-full h-full flex items-center justify-center p-5 min-h-[240px]">
      <AnimatePresence mode="wait">
        {step === 0 && <IdleState key="idle" />}
        {step === 1 && <SpinVM key="spin" />}
        {step === 2 && <RunCode key="code" />}
        {step === 3 && <WebCrawl key="crawl" />}
        {step === 4 && <SpawnAgents key="agents" />}
        {step === 5 && <Synthesize key="synth" />}
        {step === 6 && <CompletedState key="done" />}
      </AnimatePresence>
    </div>
  );
}
