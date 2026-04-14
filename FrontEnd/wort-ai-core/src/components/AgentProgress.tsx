import { useState } from 'react';

interface AgentProgressProps {
  name: string;
  percentage: number;
  active?: boolean;
  status?: string;
  currentStep?: string;
  variant?: "research" | "writer";
  query?: string;
  fullCurrentStep?: string;
  phase?: string;
}

const AgentProgress = ({ name, percentage, active = false, status, currentStep, variant = "research", query, fullCurrentStep, phase: agentPhase }: AgentProgressProps) => {
  const [expanded, setExpanded] = useState(false);

  const totalChunks = 15; // Number of "matrix blocks"
  const activeChunks = Math.max(0, Math.min(totalChunks, Math.floor((percentage / 100) * totalChunks)));

  const isReviewing = status?.toUpperCase() === 'REVIEWING';
  const isWriter = variant === "writer";

  // Color palette: writer uses cyan, research uses green/amber
  const themeColor = isWriter ? 'text-cyan-400' : (isReviewing ? 'text-amber-400' : 'text-emerald-400');
  const pulseColor = isWriter ? 'bg-cyan-400' : (isReviewing ? 'bg-amber-400' : 'bg-emerald-400');
  const borderColor = isWriter ? 'border-cyan-400/20' : (isReviewing ? 'border-amber-400/20' : 'border-emerald-400/20');

  return (
    <div
      className={`bg-background/50 border ${active ? borderColor : 'border-white/5'} p-3 rounded-sm transition-all duration-300 cursor-pointer ${expanded ? 'ring-1 ring-primary/5' : ''}`}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-3">
          {/* Status Icon Box */}
          <div className={`w-6 h-6 rounded-[2px] flex items-center justify-center border ${active ? borderColor : 'border-white/5'} bg-background`}>
            <div className={`w-1.5 h-1.5 rounded-full ${active ? `${pulseColor} animate-pulse` : 'bg-primary/10'}`} />
          </div>

          <div className="flex flex-col">
            <div className="flex items-center gap-1.5">
              <span className="font-mono text-[10px] uppercase tracking-widest text-primary/90 font-bold">
                {name}
              </span>
              {/* Chevron indicator */}
              <span
                className="font-mono text-[8px] text-primary/30 transition-transform duration-200 inline-block"
                style={{ transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)' }}
              >
                ▼
              </span>
            </div>

            {/* Collapsed: show truncated currentStep (existing behavior) */}
            {!expanded && currentStep && active && (
              <div className="flex items-center gap-2 mt-0.5">
                <span className="font-mono text-[10px] text-primary/40">»</span>
                <span className={`font-mono text-[9px] ${themeColor} opacity-90 truncate max-w-[280px] tracking-wide`}>
                  "{currentStep}"
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Percentage Badge */}
        <div className={`font-mono text-[10px] ${active ? themeColor : 'text-primary/20'} tracking-wider bg-secondary/50 px-1.5 py-0.5 rounded-[1px]`}>
          {active ? status : 'IDLE'} {percentage}%
        </div>
      </div>

      {/* EXPANDED: Full details section */}
      {expanded && (
        <div className="mt-2 mb-2 pl-9 border-l border-primary/10 space-y-1.5 animate-in fade-in duration-200">
          {query && (
            <div>
              <span className="font-mono text-[8px] uppercase tracking-wider text-primary/30">Query</span>
              <p className="font-mono text-[10px] text-primary/70 leading-relaxed break-all">{query}</p>
            </div>
          )}
          {fullCurrentStep && active && (
            <div>
              <span className="font-mono text-[8px] uppercase tracking-wider text-primary/30">Current Step</span>
              <p className={`font-mono text-[10px] ${themeColor} opacity-80 leading-relaxed`}>{fullCurrentStep}</p>
            </div>
          )}
          {agentPhase && (
            <div className="flex items-center gap-2">
              <span className="font-mono text-[8px] uppercase tracking-wider text-primary/30">Phase</span>
              <span className={`font-mono text-[9px] ${themeColor}`}>{agentPhase}</span>
            </div>
          )}
        </div>
      )}

      {/* Progress Matrix Track */}
      <div className="flex gap-1.5 w-full mt-2 overflow-hidden">
        {Array.from({ length: totalChunks }).map((_, i) => {
          const isActive = i < activeChunks;
          const isHead = i === activeChunks - 1; // The actively processing chunk

          return (
            <div
              key={i}
              className="flex flex-col gap-[1px]"
            >
              {/* Top Row (3 dots) */}
              <div className="flex gap-[1px]">
                {[0, 1, 2].map(d => (
                  <div
                    key={`t-${d}`}
                    className={`w-1 h-1 rounded-full transition-all duration-300 
                            ${isActive
                        ? (isHead && active ? `${pulseColor} animate-pulse` : pulseColor)
                        : 'bg-primary/5'} 
                        `}
                  />
                ))}
              </div>
              {/* Bottom Row (3 dots) */}
              <div className="flex gap-[1px]">
                {[0, 1, 2].map(d => (
                  <div
                    key={`b-${d}`}
                    className={`w-1 h-1 rounded-full transition-all duration-300
                            ${isActive
                        ? (isHead && active ? `${pulseColor} animate-pulse` : `${pulseColor} opacity-60`)
                        : 'bg-primary/5'} 
                        `}
                    style={isHead && active ? { animationDelay: '500ms' } : {}}
                  />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AgentProgress;
