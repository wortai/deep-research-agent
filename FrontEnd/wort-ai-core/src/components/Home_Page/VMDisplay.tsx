import { useRef, useState, useEffect, memo } from "react";
import { C } from "./tokens";
import VMVisualizer from "./VMVisualizer";

const TASKS = [
  { id: 1, label: "SPIN VM", logs: ["Allocating secure microVM...", "Network interface up", "System boot OK"] },
  { id: 2, label: "RUN CODE", logs: ["Pulling environment...", "Executing python analysis.py...", "Exit 0: Analysis complete"] },
  { id: 3, label: "WEB_CRAWL", logs: ["Init headless browser...", "Bypassing captchas...", "Scraping 14 sources..."] },
  { id: 4, label: "SPAWN AGENTS", logs: ["Orchestrating sub-agents...", "Delegating context chunks...", "Consensus reached"] },
  { id: 5, label: "SYNTHESIZE", logs: ["Aggregating findings...", "Drafting markdown report...", "Exporting PDF format..."] },
];

const STEP_DELAYS = [800, 2400, 2600, 2800, 3000, 2800, 6000];

function VMDisplayInner() {
  const ref = useRef<HTMLDivElement>(null);
  const [step, setStep] = useState(0);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    let cancelled = false;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          cancelled = false;
          const runSequence = async () => {
            const delay = (ms: number) => new Promise<void>(res => {
              const id = setTimeout(res, ms);
            });
            while (!cancelled) {
              for (let s = 0; s < STEP_DELAYS.length; s++) {
                if (cancelled) return;
                await delay(STEP_DELAYS[s]);
                if (cancelled) return;
                setStep(s + 1);
              }
              if (!cancelled) {
                await delay(STEP_DELAYS[STEP_DELAYS.length - 1]);
              }
            }
          };
          setStep(0);
          runSequence();
        } else {
          cancelled = true;
          setStep(0);
        }
      },
      { threshold: 0.4 },
    );

    observer.observe(el);
    return () => {
      cancelled = true;
      observer.disconnect();
    };
  }, []);

  return (
    <div ref={ref} className="w-full h-full flex flex-col bg-[#F7F7F5] border border-[#3A3A38]/10 overflow-hidden">
      <div className="flex items-center justify-between px-3 sm:px-4 lg:px-6 py-2 sm:py-3 border-b border-[#3A3A38]/10">
        <div className="flex items-center gap-3">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-[#FF5F56]/20 flex items-center justify-center"><div className="w-1 h-1 rounded-full bg-[#FF5F56]" /></div>
            <div className="w-2.5 h-2.5 rounded-full bg-[#FFBD2E]/20 flex items-center justify-center"><div className="w-1 h-1 rounded-full bg-[#FFBD2E]" /></div>
            <div className="w-2.5 h-2.5 rounded-full bg-[#27C93F]/20 flex items-center justify-center"><div className="w-1 h-1 rounded-full bg-[#27C93F]" /></div>
          </div>
          <span className="font-mono text-[9px] sm:text-[10px] text-[#1A3C2B]/60 uppercase tracking-widest ml-1 sm:ml-2">
            wort-xtreme-session
          </span>
        </div>
        <div className="flex items-center gap-2">
          {step > 0 && step < 6 && (
            <>
              <div className="w-1.5 h-1.5 rounded-full bg-[#FF8C69] animate-pulse" style={{ boxShadow: C.coralGlow }} />
              <span className="font-mono text-[9px] text-[#FF8C69] uppercase tracking-widest font-bold">RUNNING</span>
            </>
          )}
          {step === 6 && (
            <>
              <div className="w-1.5 h-1.5 rounded-full bg-[#9EFFBF]" style={{ boxShadow: C.mintGlow }} />
              <span className="font-mono text-[9px] text-[#1A3C2B]/60 uppercase tracking-widest">COMPLETED</span>
            </>
          )}
        </div>
      </div>

      <div className="flex flex-1 min-h-0">
        <div className="flex flex-col flex-1 min-w-0 px-3 sm:px-4 lg:px-6 py-3 sm:py-4">
          <div className="flex flex-col gap-1 flex-1">
            {TASKS.map((t) => {
              const isPast = step > t.id;
              const isActive = step === t.id;
              const isFuture = step < t.id;

              return (
                <div key={t.id} className={`flex flex-col transition-all duration-500 ${isFuture ? "opacity-40" : "opacity-100"}`}>
                  <div className="flex items-center gap-3 py-1.5">
                    <div className="w-4 h-4 flex items-center justify-center shrink-0">
                      {isActive ? (
                        <div className="w-2.5 h-2.5 rounded-full border-2 border-[#FF8C69] border-t-transparent animate-spin" />
                      ) : isPast ? (
                        <div className="w-1.5 h-1.5 rounded-full bg-[#9EFFBF]" />
                      ) : (
                        <div className="w-1 h-1 rounded-full bg-[#1A3C2B]/20" />
                      )}
                    </div>
                    <span className={`font-mono text-[10px] sm:text-[11px] uppercase tracking-wider ${isActive ? "text-[#FF8C69] font-bold" : isPast ? "text-[#1A3C2B]" : "text-[#1A3C2B]/60"}`}>
                      {t.label}
                    </span>
                  </div>

                  <div
                    className="overflow-hidden transition-all duration-500 ease-in-out"
                    style={{
                      maxHeight: isActive ? '100px' : isPast ? '24px' : '0px',
                      opacity: isActive || isPast ? 1 : 0,
                    }}
                  >
                    <div className="pl-7 pb-2 flex flex-col gap-1">
                      {isActive && <VMLogLines lines={t.logs} />}
                      {isPast && (
                        <span className="font-mono text-[9px] text-[#1A3C2B]/40">
                          ✓ {t.logs[t.logs.length - 1]}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="hidden md:flex flex-1 min-w-0 border-l border-[#3A3A38]/10 bg-[#3A3A38]/[0.02]">
          <VMVisualizer step={step} />
        </div>
      </div>

      <div className="px-3 sm:px-4 lg:px-6 py-2 sm:py-3 border-t border-[#3A3A38]/10 flex justify-between items-center">
        <span className="font-mono text-[9px] text-[#1A3C2B]/40 uppercase tracking-widest">
          ENVIRONMENT: SECURE_VM
        </span>
        <span className="font-mono text-[9px] text-[#1A3C2B]/40 uppercase tracking-widest">
          {step === 6 ? "100% DONE" : `${Math.floor(((step > 0 ? step - 1 : 0) / 5) * 100)}%`}
        </span>
      </div>
    </div>
  );
}

function VMLogLines({ lines }: { lines: string[] }) {
  const [visibleCount, setVisibleCount] = useState(1);

  useEffect(() => {
    if (visibleCount >= lines.length) return;
    const timer = setTimeout(() => {
      setVisibleCount(c => c + 1);
    }, 700);
    return () => clearTimeout(timer);
  }, [visibleCount, lines.length]);

  return (
    <>
      {lines.slice(0, visibleCount).map((l, i) => {
        const isLatest = i === visibleCount - 1;
        return (
          <span key={i} className={`font-mono text-[8px] sm:text-[9px] flex items-center gap-2 ${isLatest ? "text-[#1A3C2B]/70" : "text-[#1A3C2B]/40"}`}>
            <span className={isLatest ? "text-[#FF8C69] animate-pulse" : "text-[#1A3C2B]/30"}>
              {isLatest ? "❯" : "·"}
            </span>
            {l}
          </span>
        );
      })}
    </>
  );
}

export const VMDisplay = memo(VMDisplayInner);
