import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ROUTES } from "@/lib/routes";
import { PENGUIN_URL } from "@/components/Home_Page/tokens";
import "./about.css";

const FOUNDER_IMG = "/founder2.png";

const About = () => {
  return (
    /*
     * Grid lives as background-image on the root div.
     * Sections that set bg-[#1A3C2B] paint over it (dark sections).
     * Sections with no background let it show through (light sections).
     */
    <div className="about-page min-h-screen about-grid-bg">
      {/* ── NAV ─────────────────────────────────────────────── */}
      <motion.nav
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4, delay: 0.05 }}
        className="fixed top-0 w-full z-50 bg-[#F7F7F5]/92 backdrop-blur-sm border-b border-[#3A3A38]/15 flex items-center justify-between px-4 sm:px-6 h-14 sm:h-16"
      >
        <Link to={ROUTES.home} className="flex items-center gap-2 sm:gap-3">
          <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-sm overflow-hidden border border-[#1A3C2B]/20 bg-white flex items-center justify-center">
            <img src={PENGUIN_URL} alt="WORT" className="w-full h-full object-contain" />
          </div>
          <span className="font-mono text-[9px] sm:text-[10px] uppercase tracking-widest text-[#1A3C2B]">
            WORT RESEARCH AGENT
          </span>
        </Link>

        <div className="flex items-center gap-3 sm:gap-5">
          <Link
            to={ROUTES.home}
            className="font-mono text-[9px] sm:text-[10px] uppercase tracking-widest text-[#1A3C2B]/55 hover:text-[#1A3C2B] transition-colors"
          >
            ← Home
          </Link>
          <Link
            to={ROUTES.chat}
            className="px-3 sm:px-5 py-2 bg-[#FF8C69] text-black font-mono text-[10px] uppercase tracking-widest hover:brightness-[0.93] transition-[filter] inline-flex items-center"
          >
            Try Agent
          </Link>
        </div>
      </motion.nav>

      <main className="pt-14 sm:pt-16">
        {/* ── HERO ──────────────────────────────────────────── */}
        <section className="border-b border-[#3A3A38]/15 min-h-[80vh] flex items-center">
          <div className="max-w-7xl mx-auto px-6 sm:px-10 md:px-20 py-28 w-full">
            <motion.div
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.45, delay: 0.1 }}
              className="flex items-center gap-3 mb-10"
            >
              <div className="w-4 h-[1px] bg-[#1A3C2B]/30" />
              <span className="font-mono text-[10px] uppercase tracking-[0.35em] text-[#1A3C2B]/40">
                Open Source · Solo · 3 Months · NYC
              </span>
            </motion.div>

            {/* Display heading — factual, not a personal boast */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: "easeOut", delay: 0.2 }}
              className="font-display text-5xl md:text-6xl lg:text-7xl font-bold text-[#1A3C2B] leading-[1.05] tracking-tight max-w-3xl"
            >
              Parallel research. Editable output. Open source.
            </motion.h1>

            {/* Mono technical description */}
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.7, delay: 0.4 }}
              className="mt-8 font-mono text-xs uppercase tracking-widest text-[#1A3C2B]/50 max-w-xl leading-loose"
            >
              BFS search engine · Parallel sub-agents · Reviewer-evaluated depth ·
              Runs on cheap models · Reports you keep editing · Built in 3 months
            </motion.p>

            <motion.div
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ duration: 0.7, ease: "easeOut", delay: 0.6 }}
              style={{ originX: 0 }}
              className="mt-12 h-[2px] bg-[#9EFFBF] w-24"
            />

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8, duration: 0.4 }}
              className="mt-8 inline-flex items-center gap-2 border border-[#3A3A38]/15 px-4 py-2"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-[#9EFFBF]" />
              <span className="font-mono text-[9px] uppercase tracking-widest text-[#1A3C2B]/45">
                Open Source · Built Solo · Still Growing
              </span>
            </motion.div>
          </div>
        </section>

        {/* ── WHY IT EXISTS ─────────────────────────────────── */}
        <section className="border-b border-[#3A3A38]/15">
          <div className="max-w-7xl mx-auto px-6 sm:px-10 md:px-20 py-24">
            {/* Section header */}
            <div className="flex items-center gap-4 mb-16">
              <span className="font-mono text-[10px] uppercase tracking-[0.3em] text-[#1A3C2B]/35">WHY_IT_EXISTS</span>
              <div className="flex-1 h-[1px] bg-[#3A3A38]/12" />
            </div>

            {/* Alternating cards: 01 left · 02 right · 03 left */}
            <div className="space-y-8">
              {[
                {
                  num: "01",
                  accent: "#9EFFBF",
                  label: "The Frustration",
                  heading: "One shot. Locked out. No iteration.",
                  body: "Every tool I tried returned one output and closed the door. No way to say 'dig deeper here', no refinement loop, no going back. You were stuck with whatever it first produced. Research is iterative — the tools weren't. WORT was built to stay in the room with you until the output is actually right.",
                },
                {
                  num: "02",
                  accent: "#F4D35E",
                  label: "The Technical Gap",
                  heading: "BFS. Parallel agents. Each one reviewed.",
                  body: "A market analysis is not a medical breakdown is not a system design doc. Generic agents flatten everything. WORT spawns parallel sub-agents using a BFS-style traversal across the internet — each researching independently while a reviewer agent continuously evaluates quality and reroutes depth. Separate machines, junior researcher model, each accountable to the whole.",
                },
                {
                  num: "03",
                  accent: "#FF8C69",
                  label: "The Build",
                  heading: "3 months. Cheap models. Maximum output.",
                  body: "Working on RLVR training loops using GRPO for open-source LLMs when I kept needing this tool and it didn't exist. Built WORT from scratch — nights and weekends, 3 months straight. Core constraint was fixed: extract maximum quality from the cheapest available models. That tradeoff forced better architecture at every layer.",
                },
              ].map((item, i) => {
                const isRight = i % 2 === 1;
                return (
                  <motion.div
                    key={item.num}
                    initial={{ opacity: 0, x: isRight ? 20 : -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true, amount: 0.15 }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                    className={`bg-[#F7F7F5] border border-[#3A3A38]/12 p-8 md:p-10 w-full md:max-w-[78%] ${isRight ? "md:ml-auto" : ""}`}
                  >
                    {/* Number + label row */}
                    <div className="flex items-center gap-3 mb-5">
                      <span
                        className="font-mono text-[10px] font-bold tracking-widest"
                        style={{ color: item.accent }}
                      >
                        {item.num}
                      </span>
                      <div className="h-[1px] w-6 opacity-30" style={{ backgroundColor: item.accent }} />
                      <span className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#1A3C2B]/40">
                        {item.label}
                      </span>
                    </div>

                    {/* Heading — darker, display font */}
                    <h2 className="font-display text-xl md:text-2xl font-bold text-[#1A3C2B] tracking-tight leading-snug mb-5">
                      {item.heading}
                    </h2>

                    {/* Body — mono, consistent with rest of site labels */}
                    <p className="font-mono text-xs text-[#1A3C2B]/55 leading-loose tracking-wide">
                      {item.body}
                    </p>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </section>

        {/* ── VISION — solid dark green ──────────────────────── */}
        <section className="border-b border-[#3A3A38]/15 bg-[#1A3C2B] text-[#F7F7F5] overflow-hidden relative">
          {/* VISION watermark — top area, behind content, visible */}
          <div
            className="absolute top-0 right-0 font-display font-bold leading-none pointer-events-none select-none text-right pr-10 pt-4 opacity-[0.07]"
            style={{ fontSize: "clamp(80px, 14vw, 180px)" }}
          >
            VISION
          </div>

          <div className="max-w-7xl mx-auto px-6 sm:px-10 md:px-20 pt-20 pb-24 relative z-10">
            {/* Label + heading */}
            <div className="mb-16">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-4 h-[1px] bg-[#9EFFBF]/40" />
                <span className="font-mono text-[10px] uppercase tracking-[0.35em] text-[#9EFFBF]/60">
                  The Vision
                </span>
              </div>

              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.2 }}
                transition={{ duration: 0.6, ease: "easeOut" }}
                className="font-display text-4xl md:text-5xl lg:text-6xl font-bold leading-[1.1] tracking-tight max-w-3xl"
              >
                Extreme search means everyone gets a tiny junior researcher.
              </motion.h2>
            </div>

            {/* Cards — each with a top color accent bar */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-[#F7F7F5]/8 border border-[#F7F7F5]/8">
              {[
                {
                  idx: "01",
                  color: "#9EFFBF",
                  title: "For Exams",
                  body: "Generate precise cheatsheets and study guides tailored to exactly what you need — not generic summaries.",
                },
                {
                  idx: "02",
                  color: "#F4D35E",
                  title: "For Prep",
                  body: "Interview, presentation, deep dive into a new domain — WORT builds real context so you walk in ready.",
                },
                {
                  idx: "03",
                  color: "#FF8C69",
                  title: "For Anything",
                  body: "Every curious person deserves research at scale with beautiful, editable reports that match the vibe of the query.",
                },
              ].map((card, i) => (
                <motion.div
                  key={card.idx}
                  initial={{ opacity: 0, y: 16 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, amount: 0.2 }}
                  transition={{ duration: 0.5, delay: i * 0.1, ease: "easeOut" }}
                  className="bg-[#1A3C2B] p-8 md:p-10"
                >
                  {/* Color accent bar at top of each card */}
                  <div className="h-[2px] w-8 mb-6" style={{ backgroundColor: card.color }} />
                  <div className="font-mono text-[10px] uppercase tracking-widest mb-4 opacity-40">
                    {card.idx}
                  </div>
                  <h3 className="font-display text-xl font-bold text-[#F7F7F5] mb-3">{card.title}</h3>
                  <p className="font-sans text-sm text-[#F7F7F5]/50 leading-relaxed">{card.body}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* ── THE BUILDER ───────────────────────────────────── */}
        <section className="border-b border-[#3A3A38]/15">
          <div className="max-w-7xl mx-auto px-6 sm:px-10 md:px-20 py-24">
            <div className="flex items-center gap-4 mb-16">
              <span className="font-mono text-[10px] uppercase tracking-[0.3em] text-[#1A3C2B]/40">THE_BUILDER</span>
              <div className="flex-1 h-[1px] bg-[#3A3A38]/15" />
            </div>

            {/*
             * Founder card — constrained width, fixed-size image, all mono text.
             * portrait-container triggers grayscale → color hover on .portrait-filter child.
             */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.1 }}
              transition={{ duration: 0.55, ease: "easeOut" }}
              className="max-w-3xl mx-auto bg-[#F7F7F5] border border-[#3A3A38]/15 relative portrait-container"
            >
              {/* L-brackets */}
              <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-[#1A3C2B] z-10" />
              <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-[#1A3C2B] z-10" />
              <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-[#1A3C2B] z-10" />
              <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-[#1A3C2B] z-10" />

              {/* ── Top identity row: image + name/meta ── */}
              {/*
               * No fixed height on image container — it uses self-stretch (flex default)
               * so the image always fills exactly the same height as the info column.
               * That makes the image bottom flush with the horizontal divider below.
               */}
              <div className="flex flex-col sm:flex-row border-b border-[#3A3A38]/12">
                {/* Portrait — fills full row height, no distortion */}
                <div className="shrink-0 w-full sm:w-80 self-stretch border-b sm:border-b-0 sm:border-r border-[#3A3A38]/12 p-1.5">
                  <img
                    src={FOUNDER_IMG}
                    alt="Madhvan Tyagi"
                    className="w-full h-full object-contain object-center portrait-filter"
                  />
                </div>

                {/* Identity metadata — content-height only, no justify-between gap */}
                <div className="flex-1 flex flex-col gap-0 justify-center pl-14 pr-8 py-8">
                  <div className="font-mono text-[9px] uppercase tracking-widest text-[#FF8C69] mb-4">
                    Founder · Engineer · Builder
                  </div>

                  {/* Name — darkest element in the card */}
                  <h3 className="font-display text-3xl font-bold text-[#1A3C2B] tracking-tight leading-tight mb-6">
                    Madhvan Tyagi
                  </h3>

                  {/* Metadata lines */}
                  <div className="space-y-2 mb-7">
                    <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-[#1A3C2B]/40">
                      New York City
                    </div>
                    <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-[#1A3C2B]/40">
                      Queens College, CUNY — BS
                    </div>
                    <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-[#1A3C2B]/40">
                      RLVR · GRPO · Open-Source LLMs
                    </div>
                  </div>

                  {/* Social */}
                  <div className="flex gap-3">
                    <a
                      href="https://github.com/madhvantyagi"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 border border-[#1A3C2B]/40 font-mono text-[9px] uppercase tracking-widest px-3 py-1.5 hover:bg-[#1A3C2B] hover:text-[#F7F7F5] hover:border-[#1A3C2B] transition-all duration-200 text-[#1A3C2B]"
                    >
                      <GithubIcon />
                      GitHub
                    </a>
                    <a
                      href="https://www.linkedin.com/in/madhvan-tyagi-10a44a222/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 border border-[#1A3C2B]/40 font-mono text-[9px] uppercase tracking-widest px-3 py-1.5 hover:bg-[#1A3C2B] hover:text-[#F7F7F5] hover:border-[#1A3C2B] transition-all duration-200 text-[#1A3C2B]"
                    >
                      <LinkedinIcon />
                      LinkedIn
                    </a>
                  </div>
                </div>
              </div>

              {/* ── Bio rows — all mono, hairline-divided ── */}
              {[
                {
                  label: "/ Background",
                  text: "Into AI — not just using it, but how it learns. Working on RLVR training loops with GRPO for open-source LLMs when I kept running into the same wall: the research tool I needed didn't exist. WORT became that tool.",
                },
                {
                  label: "/ The Goal",
                  text: "Research that parallelizes across sources, produces reports in the depth and format you actually need, and lets you keep iterating until the output is exactly right. Not a search wrapper. A thinking partner.",
                },
                {
                  label: "/ The Constraint",
                  text: "Built to run on cheap models. Not a limitation — the design goal. Squeezing maximum quality out of minimal compute forced better architecture, better prompting, and a smarter agent evaluation loop.",
                },
              ].map((item) => (
                <div
                  key={item.label}
                  className="px-6 py-5 flex flex-col sm:flex-row gap-3 sm:gap-6 border-b border-[#3A3A38]/12 last:border-b-0"
                >
                  {/* Label — mono, muted */}
                  <div className="font-mono text-[10px] uppercase tracking-widest text-[#1A3C2B]/35 shrink-0 w-32 pt-0.5">
                    {item.label}
                  </div>
                  {/* Body — mono, slightly darker */}
                  <p className="font-mono text-xs text-[#1A3C2B]/70 leading-relaxed tracking-wide flex-1">
                    {item.text}
                  </p>
                </div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* ── OPEN SOURCE CTA — solid dark ──────────────────── */}
        <section className="bg-[#1A3C2B] text-[#F7F7F5] relative overflow-hidden">
          <div className="max-w-7xl mx-auto px-6 sm:px-10 md:px-20 py-28 relative z-10">
            <div className="flex items-center gap-3 mb-8">
              <div className="w-4 h-[1px] bg-[#9EFFBF]/40" />
              <span className="font-mono text-[10px] uppercase tracking-[0.35em] text-[#9EFFBF]/60">
                Open Source
              </span>
            </div>

            <motion.h2
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              className="font-display text-4xl md:text-6xl font-bold leading-tight tracking-tight max-w-3xl mb-6"
            >
              Intelligence should be transparent. WORT is.
            </motion.h2>

            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="font-sans text-base opacity-60 mb-12 leading-relaxed max-w-2xl"
            >
              The core research engine, the agent logic, the prompt architecture — all public, verifiable, and
              improvable. Built to be seen, forked, and made better by anyone who cares about research as much as I do.
            </motion.p>

            <div className="flex flex-col sm:flex-row gap-4">
              <a
                href="https://github.com/madhvantyagi"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 border border-[#9EFFBF] text-[#9EFFBF] font-mono text-xs uppercase tracking-widest px-8 py-4 hover:bg-[#9EFFBF]/10 transition-all duration-200"
              >
                <GithubIcon className="w-4 h-4" />
                View_Source_Code
              </a>
              <Link
                to={ROUTES.chat}
                className="inline-flex items-center justify-center bg-[#FF8C69] text-[#1A3C2B] font-mono text-xs uppercase tracking-widest px-8 py-4 hover:brightness-[0.92] transition-all duration-200"
              >
                Try_Agent_Now →
              </Link>
            </div>
          </div>

          <div className="absolute bottom-0 right-0 p-12 opacity-[0.04] pointer-events-none select-none">
            <span className="font-display text-[15vw] font-bold leading-none">WORT</span>
          </div>
        </section>
      </main>

      {/* ── FOOTER ────────────────────────────────────────── */}
      <footer className="border-t border-[#3A3A38]/15 py-8 sm:py-10 px-6 sm:px-10">
        <div className="max-w-7xl mx-auto flex flex-col items-center gap-4 sm:gap-6">
          <Link
            to={ROUTES.home}
            className="block rounded-sm overflow-hidden border border-[#1A3C2B]/20 bg-white w-10 h-10 sm:w-11 sm:h-11 flex items-center justify-center hover:opacity-90 transition-opacity"
            aria-label="WORT Research home"
          >
            <img src={PENGUIN_URL} alt="" className="w-full h-full object-contain" />
          </Link>

          <div className="flex items-center gap-6 sm:gap-8">
            <Link
              to={ROUTES.home}
              className="font-mono text-[10px] uppercase tracking-widest text-[#1A3C2B]/45 hover:text-[#1A3C2B] transition-colors"
            >
              Home
            </Link>
            <a
              href="https://github.com/madhvantyagi"
              target="_blank"
              rel="noopener noreferrer"
              className="font-mono text-[10px] uppercase tracking-widest text-[#1A3C2B]/45 hover:text-[#1A3C2B] transition-colors"
            >
              GitHub
            </a>
            <a
              href="https://www.linkedin.com/in/madhvan-tyagi-10a44a222/"
              target="_blank"
              rel="noopener noreferrer"
              className="font-mono text-[10px] uppercase tracking-widest text-[#1A3C2B]/45 hover:text-[#1A3C2B] transition-colors"
            >
              LinkedIn
            </a>
            <Link
              to={ROUTES.chat}
              className="font-mono text-[10px] uppercase tracking-widest text-[#1A3C2B]/45 hover:text-[#1A3C2B] transition-colors"
            >
              Try Agent
            </Link>
          </div>

          <span className="font-mono text-[9px] uppercase tracking-widest text-[#3A3A38]/30">
            © 2026 WORT Research Agent
          </span>
        </div>
      </footer>
    </div>
  );
};

function GithubIcon({ className = "w-3.5 h-3.5" }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path
        fillRule="evenodd"
        d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
        clipRule="evenodd"
      />
    </svg>
  );
}

function LinkedinIcon({ className = "w-3.5 h-3.5" }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
    </svg>
  );
}

export default About;
