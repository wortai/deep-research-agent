import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
  type ReactNode,
} from "react";
import { getApiOrigin } from "@/apiConfig";

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

/**
 * Shape returned by both `POST /api/auth/google` and `GET /api/auth/me`.
 * Field names match the backend's snake_case DB column names exactly.
 */
export interface AuthUser {
  user_id: string;
  email: string;
  username: string | null;
  full_name: string | null;
  avatar_url: string | null;
  provider: string;
  credits: number;
  created_at: string | null;
  last_login: string | null;
}

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (googleIdToken: string) => Promise<void>;
  loginWithAccessToken: (accessToken: string) => Promise<void>;
  logout: () => void;
}

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

const JWT_KEY = "wort_jwt";

/* ------------------------------------------------------------------ */
/*  Context                                                            */
/* ------------------------------------------------------------------ */

const AuthContext = createContext<AuthContextValue | null>(null);

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

/** Remove JWT from localStorage and reset state. */
function clearSession(): void {
  localStorage.removeItem(JWT_KEY);
}

/* ------------------------------------------------------------------ */
/*  Provider                                                           */
/* ------------------------------------------------------------------ */

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const mountRef = useRef(false);

  /* ---------- restore session on mount ---------- */
  useEffect(() => {
    if (mountRef.current) return;
    mountRef.current = true;

    const jwt = localStorage.getItem(JWT_KEY);
    if (!jwt) {
      setLoading(false);
      return;
    }

    let cancelled = false;

    (async () => {
      try {
        const res = await fetch(`${getApiOrigin()}/api/auth/me`, {
          headers: { Authorization: `Bearer ${jwt}` },
        });

        if (!res.ok) {
          // JWT is invalid or expired — auto-logout
          clearSession();
          return;
        }

        const data: AuthUser = await res.json();
        if (!cancelled) setUser(data);
      } catch {
        // Network error — keep JWT for next attempt, but don't set user
        console.error("Failed to validate session");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  /* ---------- login with id_token (legacy) ---------- */
  const login = useCallback(async (googleIdToken: string) => {
    const res = await fetch(`${getApiOrigin()}/api/auth/google`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id_token: googleIdToken }),
    });

    if (!res.ok) {
      const text = await res.text().catch(() => "Authentication failed");
      throw new Error(text);
    }

    const data: { jwt: string; user: AuthUser } = await res.json();
    localStorage.setItem(JWT_KEY, data.jwt);
    setUser(data.user);
  }, []);

  /* ---------- login with access_token ---------- */
  const loginWithAccessToken = useCallback(async (accessToken: string) => {
    const res = await fetch(`${getApiOrigin()}/api/auth/google`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ access_token: accessToken }),
    });

    if (!res.ok) {
      const text = await res.text().catch(() => "Authentication failed");
      throw new Error(text);
    }

    const data: { jwt: string; user: AuthUser } = await res.json();
    localStorage.setItem(JWT_KEY, data.jwt);
    setUser(data.user);
  }, []);

  /* ---------- logout ---------- */
  const logout = useCallback(() => {
    clearSession();
    setUser(null);
  }, []);

  /* ---------- context value ---------- */
  const value: AuthContextValue = {
    user,
    loading,
    isAuthenticated: user !== null,
    login,
    loginWithAccessToken,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/* ------------------------------------------------------------------ */
/*  Hook                                                               */
/* ------------------------------------------------------------------ */

/**
 * Access the current auth state anywhere inside `<AuthProvider>`.
 *
 * ```ts
 * const { user, isAuthenticated, login, logout, loading } = useAuth();
 * ```
 */
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an <AuthProvider>");
  }
  return ctx;
}
