import { Navigate } from "react-router-dom";
import { useAuth } from "@/lib/auth";

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center font-mono text-[10px] uppercase tracking-widest text-[#1A3C2B]/60">
        Loading...
      </div>
    );
  }

  if (!isAuthenticated) return <Navigate to="/" replace />;

  return <>{children}</>;
}
