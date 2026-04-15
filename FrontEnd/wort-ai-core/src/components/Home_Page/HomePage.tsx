import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useGoogleLogin } from "@react-oauth/google";
import { ROUTES } from "@/lib/routes";
import { useAuth } from "@/lib/auth";
import { PENGUIN_URL } from "./tokens";
import { ScrollProgressBar } from "./ScrollProgressBar";
import { HeroSection } from "./HeroSection";
import { AnimatedTerminal } from "./AnimatedTerminal";
import { TiltCard } from "./TiltCard";
import { DeepSearchFlow } from "./DeepSearchFlow";
import { VMDisplay } from "./VMDisplay";
import "./home-page.css";

const hasGoogleClientId = Boolean((import.meta.env.VITE_GOOGLE_CLIENT_ID ?? "").trim());

/** Must only render when `GoogleOAuthProvider` is mounted (requires `VITE_GOOGLE_CLIENT_ID`). */
function HomeGoogleSignInButton() {
  const { loginWithAccessToken } = useAuth();
  const navigate = useNavigate();
  const [authenticating, setAuthenticating] = useState(false);

  const googleLogin = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      try {
        setAuthenticating(true);
        if (!tokenResponse.access_token) {
          console.error("No access_token received from Google");
          return;
        }
        await loginWithAccessToken(tokenResponse.access_token);
        navigate(ROUTES.chat);
      } catch (err) {
        console.error("Login failed:", err);
      } finally {
        setAuthenticating(false);
      }
    },
    onError: () => {
      console.error("Google Sign-In failed");
      setAuthenticating(false);
    },
  });

  return (
    <button
      type="button"
      onClick={() => googleLogin()}
      disabled={authenticating}
      className="px-4 py-2 border border-[#1A3C2B]/25 font-mono text-[10px] uppercase tracking-widest text-[#1A3C2B] hover:bg-[#9EFFBF]/20 transition-colors inline-flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <svg className="w-3.5 h-3.5 flex-shrink-0" viewBox="0 0 24 24">
        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4" />
        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
      </svg>
      <span>{authenticating ? "Signing in..." : "Sign in with Google"}</span>
    </button>
  );
}

export default function HomePage() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="home-page min-h-screen overflow-x-hidden relative flex flex-col">
      <div className="mosaic-overlay" aria-hidden />
      <ScrollProgressBar />

      {/* NAV */}
      <motion.nav
        initial={{ y: -64, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        className="fixed top-0 w-full z-50 bg-[#F7F7F5]/90 backdrop-blur-sm border-b border-[#3A3A38]/15 flex items-center justify-between px-4 sm:px-6 h-14 sm:h-16 shrink-0"
      >
        <div className="flex items-center gap-2 sm:gap-3">
          <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-sm overflow-hidden border border-[#1A3C2B]/20 flex items-center justify-center bg-white">
            <img
              src={PENGUIN_URL}
              alt="WORT Penguin"
              className="w-full h-full object-contain"
            />
          </div>
          <span className="font-mono text-[9px] sm:text-[10px] uppercase tracking-widest text-[#1A3C2B]">
            WORT RESEARCH AGENT
          </span>
        </div>

        <div className="hidden md:flex gap-10">
          {[
            { href: "#features", label: "Features", idx: "01." },
            { href: "#intelligence", label: "Modes", idx: "02." },
          ].map((link) => (
            <a
              key={link.href}
              href={link.href}
              data-index={link.idx}
              className="header-link font-mono text-[10px] uppercase tracking-widest hover:text-[#2D7A4F] transition-colors"
            >
              {link.label}
            </a>
          ))}
          <Link
            to={ROUTES.about}
            data-index="03."
            className="header-link font-mono text-[10px] uppercase tracking-widest hover:text-[#2D7A4F] transition-colors"
          >
            About
          </Link>
        </div>

        <div className="flex items-center gap-2 sm:gap-4">
          <Link
            to={ROUTES.about}
            className="md:hidden font-mono text-[9px] uppercase tracking-widest text-[#1A3C2B]/75 hover:text-[#2D7A4F] transition-colors shrink-0"
          >
            About
          </Link>

          {/* Authenticated: show user avatar + name + logout */}
          {isAuthenticated && user ? (
            <div className="hidden sm:flex items-center gap-2">
              <div className="flex items-center gap-2 px-3 py-1.5 border border-[#1A3C2B]/15">
                {user.avatar_url ? (
                  <img
                    src={user.avatar_url}
                    alt={user.full_name || user.username || ""}
                    className="w-5 h-5 rounded-full object-cover"
                    referrerPolicy="no-referrer"
                  />
                ) : (
                  <span className="w-5 h-5 rounded-full bg-[#1A3C2B]/10 flex items-center justify-center text-[8px] font-mono text-[#1A3C2B]">
                    {(user.full_name || user.username || "U").charAt(0).toUpperCase()}
                  </span>
                )}
                <span className="font-mono text-[9px] uppercase tracking-widest text-[#1A3C2B]/70 max-w-[120px] truncate">
                  {user.full_name || user.username || ""}
                </span>
              </div>
              <button
                type="button"
                onClick={logout}
                className="px-3 py-1.5 border border-[#1A3C2B]/25 font-mono text-[9px] uppercase tracking-widest hover:bg-[#9EFFBF]/20 transition-colors"
              >
                Logout
              </button>
            </div>
          ) : null}

          {!isAuthenticated ? (
            hasGoogleClientId ? (
              <HomeGoogleSignInButton />
            ) : (
              <span
                className="max-w-[200px] text-right font-mono text-[8px] sm:text-[9px] uppercase tracking-widest text-[#1A3C2B]/45 leading-snug"
                title="Set VITE_GOOGLE_CLIENT_ID in Vercel (Preview/Production) and redeploy."
              >
                Sign-in disabled — add Google client ID to env
              </span>
            )
          ) : (
            <button
              type="button"
              onClick={() => navigate(ROUTES.chat)}
              className="px-3 sm:px-5 py-2 bg-[#FF8C69] text-black font-mono text-[10px] uppercase tracking-widest font-normal no-underline hover:no-underline focus-visible:no-underline hover:brightness-[0.97] transition-[filter] inline-flex items-center"
            >
              Try Agent
            </button>
          )}
        </div>
      </motion.nav>

      {/* HERO — isolated component owns its own useScroll */}
      <HeroSection />

      {/* FEATURES */}
      <section id="features" className="py-4">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 0.45 }}
          className="px-6 sm:px-10 md:px-20 py-10 flex items-center gap-4"
        >
          <div className="w-4 h-[1px] bg-[#1A3C2B]/30" />
          <span className="font-mono text-[9px] uppercase tracking-[0.35em] text-[#1A3C2B]/45">
            Intelligence Layers
          </span>
        </motion.div>

        <div id="intelligence" className="flex flex-col w-full border-t border-[#3A3A38]/15">
          {/* 01 — Web Search */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.15 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="min-h-[70vh] flex flex-col lg:flex-row bg-[#F7F7F5] border-b border-[#3A3A38]/15"
          >
            <div className="flex-1 flex flex-col justify-center gap-6 sm:gap-8 p-6 sm:p-10 md:p-20 xl:px-32 xl:py-24">
              <motion.div
                initial={{ scaleX: 0 }}
                whileInView={{ scaleX: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                style={{ originX: 0 }}
                className="border-l-4 border-[#9EFFBF] pl-4"
              >
                <span className="font-mono text-[10px] uppercase tracking-widest opacity-60">01. Fast Intel</span>
              </motion.div>
              <h3 className="font-grotesk text-4xl sm:text-5xl lg:text-7xl font-bold tracking-tight">Web_Search</h3>
              <p className="font-mono text-sm uppercase tracking-widest text-[#1A3C2B]/55 max-w-xl leading-relaxed">
                Searches articles and cross-references data in real-time. Understands images, parses products, and comprehends user intent while maintaining perfect memory of the context. Never answers cold.
              </p>
              <div className="flex items-center gap-2 mt-2">
                <div className="w-1.5 h-1.5 rounded-full bg-[#9EFFBF]" style={{ boxShadow: "0 0 6px #9EFFBF88" }} />
                <span className="font-mono text-[9px] uppercase tracking-widest text-[#1A3C2B]/50">Research-first · Always-on · Zero stale data</span>
              </div>
            </div>
            <div className="flex-1 min-h-0 p-4 sm:p-6 md:p-10 lg:p-12 flex items-stretch justify-center border-t lg:border-t-0 lg:border-l border-[#3A3A38]/15 bg-[#3A3A38]/[0.02]">
              <TiltCard className="w-full h-full max-w-none flex flex-col">
                <AnimatedTerminal />
              </TiltCard>
            </div>
          </motion.div>

          {/* 02 — Deep Research */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.15 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="min-h-0 flex flex-col gap-4 sm:gap-6 lg:flex-row-reverse lg:items-stretch lg:gap-8 xl:gap-10 bg-[#F7F7F5] border-b border-[#3A3A38]/15"
          >
            <div className="flex min-h-0 min-w-0 w-full flex-col justify-center gap-4 sm:gap-5 p-5 sm:p-6 md:p-8 lg:flex-1 lg:py-10 lg:pl-6 lg:pr-8 xl:pl-8 xl:pr-14 xl:py-12">
              <motion.div
                initial={{ scaleX: 0 }}
                whileInView={{ scaleX: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                style={{ originX: 0 }}
                className="border-l-4 border-[#F4D35E] pl-4"
              >
                <span className="font-mono text-[10px] uppercase tracking-widest opacity-60">02. Synthesis</span>
              </motion.div>
              <h3 className="font-grotesk text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold tracking-tight max-w-full">
                Deep_Research
              </h3>
              <p className="font-mono text-sm uppercase tracking-widest text-[#1A3C2B]/55 max-w-xl leading-relaxed">
                Uses advanced algorithms to research the internet. Spawns dynamic sub-agents configurable to low, mid, or high depth modes. Each agent researches independently while understanding the full picture. After your report is ready, seamlessly edit and continue researching directly on the document using AI. Built for exam cheatsheets, business analysis, and comprehensive learning.
              </p>
              <div className="flex flex-wrap gap-2 mt-2">
                {["Exam Cheatsheets", "Business Analysis", "Investment Reports", "System Design", "Market Research", "Art & Culture"].map((tag) => (
                  <span key={tag} className="font-mono text-[9px] uppercase tracking-widest px-3 py-1 border border-[#3A3A38]/20 text-[#1A3C2B]/60">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
            <div className="min-h-0 w-full min-w-0 flex-[1.15] lg:flex-[1.2] px-3 sm:px-4 py-4 sm:px-5 md:px-6 lg:pl-5 lg:pr-4 xl:pl-6 xl:pr-5 flex items-start justify-stretch border-t lg:border-t-0 lg:border-r border-[#3A3A38]/15 bg-[#3A3A38]/[0.02] overflow-visible">
              <TiltCard className="w-full max-w-none flex flex-col overflow-visible">
                <DeepSearchFlow />
              </TiltCard>
            </div>
          </motion.div>

          {/* 03 — Extreme Search */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.15 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="min-h-[70vh] flex flex-col lg:flex-row bg-[#F7F7F5]"
          >
            <div className="flex-1 flex flex-col justify-center gap-6 sm:gap-8 p-6 sm:p-10 md:p-20 xl:px-32 xl:py-24">
              <motion.div
                initial={{ scaleX: 0 }}
                whileInView={{ scaleX: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                style={{ originX: 0 }}
                className="border-l-4 border-[#FF8C69] pl-4"
              >
                <span className="font-mono text-[10px] uppercase tracking-widest opacity-60">03. Autonomous</span>
              </motion.div>
              <h3 className="font-grotesk text-4xl sm:text-5xl lg:text-7xl font-bold tracking-tight">Xtreme_Research</h3>
              <p className="font-mono text-sm uppercase tracking-widest text-[#1A3C2B]/55 max-w-xl leading-relaxed">
                Spins up a live Virtual Machine to run code, browse the web like a human, and analyze deep technical research. Creates dynamic simulations directly in chat. Performs complex analysis in a secure VM environment and can output any file format, from PDFs to PPT presentations.
              </p>
              <div className="flex items-center gap-2 mt-2">
                <div className="w-1.5 h-1.5 rounded-full bg-[#FF8C69]" style={{ boxShadow: "0 0 6px #FF8C6988" }} />
                <span className="font-mono text-[9px] uppercase tracking-widest text-[#1A3C2B]/50">VM + Code + Delegate · Full Autonomy</span>
              </div>
            </div>
            <div className="flex-1 min-h-0 p-4 sm:p-6 md:p-10 lg:p-12 flex items-stretch justify-center border-t lg:border-t-0 lg:border-l border-[#3A3A38]/15 bg-[#3A3A38]/[0.02]">
              <TiltCard className="w-full h-full max-w-none flex flex-col">
                <VMDisplay />
              </TiltCard>
            </div>
          </motion.div>

        </div>
      </section>

      {/* FOOTER */}
      <footer className="bg-[#F7F7F5] py-8 sm:py-10 px-6 sm:px-10">
        <div className="max-w-7xl mx-auto flex flex-col items-center gap-4 sm:gap-6">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 rounded-sm overflow-hidden border border-[#1A3C2B]/20">
              <img src={PENGUIN_URL} alt="WORT" className="w-full h-full object-contain" />
            </div>
            <span className="font-mono text-[10px] uppercase tracking-widest text-[#1A3C2B]">WORT Research</span>
          </div>

          <div className="flex items-center gap-6 sm:gap-8">
            {["Privacy", "Terms", "Contact"].map((l) => (
              <span
                key={l}
                className="font-mono text-[10px] uppercase tracking-widest text-[#1A3C2B]/45 cursor-default"
              >
                {l}
              </span>
            ))}
          </div>

          <span className="font-mono text-[9px] uppercase tracking-widest text-[#3A3A38]/30">
            © 2026 WORT Research Agent
          </span>
        </div>
      </footer>
    </div>
  );
}
