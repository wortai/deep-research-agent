import { useState } from "react";
import { useParams } from "react-router-dom";
import WortHeader from "@/components/WortHeader";
import ThreadSidebar from "@/components/ThreadSidebar";
import ChatWorkspace from "@/components/ChatWorkspace";
import { ProcessingStateProvider } from "@/hooks/useProcessingState";
import { useAuth } from "@/lib/auth";

const Index = () => {
  const { id } = useParams<{ id: string }>();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const { user } = useAuth();
  const userId = user?.user_id ?? "";

  return (
    <ProcessingStateProvider>
      <div className="h-screen w-full flex flex-col overflow-hidden">
        <WortHeader />
        <main className="flex-grow flex overflow-hidden relative">
          <ThreadSidebar isOpen={isSidebarOpen} onToggle={() => setIsSidebarOpen(!isSidebarOpen)} />
          <ChatWorkspace key={id || 'new'} userId={userId} />
        </main>
      </div>
    </ProcessingStateProvider>
  );
};

export default Index;
