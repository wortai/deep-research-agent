import { ChevronLeft, ChevronRight, Plus } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate, useParams } from "react-router-dom";
import { v4 as uuidv4 } from "uuid";
import { useAuth } from "@/lib/auth";
import { ThreadLoader } from "./ThreadLoader";

export interface Session {
  session_id: string;
  title: string;
  search_mode: string;
  status: string;
  created_at: string;
  updated_at?: string;
}

interface ThreadSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const ThreadSidebar = ({ isOpen, onToggle }: ThreadSidebarProps) => {
  const navigate = useNavigate();
  const { id: currentThreadId } = useParams<{ id: string }>();
  const { user } = useAuth();

  const hostname = window.location.hostname;
  const jwt = localStorage.getItem("wort_jwt") || "";

  const { data, isLoading } = useQuery({
    queryKey: ['sessions'],
    queryFn: async () => {
      const res = await fetch(`http://${hostname}:8000/sessions`, {
        headers: { Authorization: `Bearer ${jwt}` }
      });
      if (!res.ok) throw new Error('Failed to fetch sessions');
      const json = await res.json();
      return json.sessions as Session[];
    }
  });

  const threads = data || [];
  return (
    <aside
      className={`${isOpen ? 'w-[260px]' : 'w-[60px]'} border-r border-hairline bg-background flex flex-col flex-shrink-0 transition-all duration-300 ease-in-out`}
    >
      <div className={`p-4 flex-shrink-0 flex flex-col gap-4 ${!isOpen && 'items-center'}`}>
        <div className={`flex items-center justify-between ${!isOpen && 'justify-center w-full'}`}>
          {isOpen && (
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-accent" />
              <span className="font-mono text-[10px] uppercase tracking-wider text-primary opacity-60">
                Thread_Archive
              </span>
            </div>
          )}
          <button
            onClick={onToggle}
            className="text-primary/60 hover:text-primary transition-colors p-1"
          >
            {isOpen ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
          </button>
        </div>

        <button
          onClick={() => navigate(`/chat/${uuidv4()}`)}
          className={`bg-primary text-primary-foreground font-mono text-[10px] uppercase py-3 tracking-wider hover:bg-primary/80 transition-colors duration-200 flex items-center justify-center gap-2 w-full`}
        >
          {isOpen ? "+ New Research" : <Plus size={14} />}
        </button>
      </div>

      <nav className="flex-grow overflow-y-auto scrollbar-hide px-4 pb-6 mt-2">
        <div className="space-y-0">
          {isLoading ? (
            <div className="text-center text-primary/40 font-mono text-[10px] py-4">Loading...</div>
          ) : threads.length === 0 ? (
            <div className="text-center text-primary/40 font-mono text-[10px] py-4">No history</div>
          ) : (
            threads.map((thread) => {
              const active = thread.session_id === currentThreadId;
              const isStale = new Date().getTime() - new Date(thread.updated_at || thread.created_at || Date.now()).getTime() > 24 * 60 * 60 * 1000;
              const isProcessing = ['processing', 'in_progress', 'running'].includes(thread.status?.toLowerCase() || "") ||
                (thread.status?.toLowerCase() === 'active' && !isStale);

              // Only apply heavier primary styling if the thread is active
              const titleColorClass = active ? "text-primary font-medium" : "text-primary/60";

              return (
                <button
                  key={thread.session_id}
                  onClick={() => navigate(`/chat/${thread.session_id}`)}
                  className="block group w-full text-left"
                >
                  <div
                    className={`font-mono text-[11px] py-3 border-b border-hairline tracking-wide flex justify-between items-center ${!active ? "opacity-40 group-hover:opacity-100 transition-opacity" : ""} ${!isOpen && 'justify-center border-none'} ${titleColorClass}`}
                  >
                    {isOpen ? (
                      <>
                        <span className="truncate flex-1 pr-2">{thread.title || "New Research"}</span>
                        {isProcessing && <ThreadLoader />}
                      </>
                    ) : (
                      <div className={`w-6 h-6 flex items-center justify-center rounded-sm transition-colors ${active ? "bg-primary/20 text-primary font-medium" : "bg-secondary group-hover:bg-primary/10"}`}>
                        {isProcessing ? (
                          <ThreadLoader />
                        ) : (
                          <span className="text-[9px]">{thread.title ? thread.title.substring(0, 2).toUpperCase() : "NR"}</span>
                        )}
                      </div>
                    )}
                  </div>
                </button>
              );
            })
          )}
        </div>
      </nav>
    </aside>
  );
};

export default ThreadSidebar;
