import { type LucideIcon } from "lucide-react";

interface ToolLogProps {
  icon: LucideIcon;
  task: string;
  status?: string;
}

/** Technical metadata row — JetBrains Mono, Paper/Forest/Grid per style.md */
const ToolLog = ({ icon: Icon, task, status = "COMPLETE" }: ToolLogProps) => {
  return (
    <div className="mb-1.5 flex items-center justify-between gap-3 border border-[#3A3A38]/20 bg-[#F7F7F5] px-3 py-2 rounded-none transition-colors duration-150 ease-out hover:border-[#3A3A38]/35">
      <div className="flex min-w-0 flex-1 items-center gap-2">
        <Icon
          size={12}
          strokeWidth={2}
          className="shrink-0 text-[#1A3C2B]/75"
          aria-hidden
        />
        <span className="min-w-0 truncate font-mono text-[11px] font-normal leading-snug tracking-[0.1em] text-[#1A3C2B]">
          {task}
        </span>
      </div>
      <span className="shrink-0 font-mono text-[10px] font-normal uppercase tracking-[0.1em] text-[#1A3C2B]/65">
        {status}
      </span>
    </div>
  );
};

export default ToolLog;
