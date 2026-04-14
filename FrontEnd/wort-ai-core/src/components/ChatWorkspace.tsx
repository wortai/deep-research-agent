import { Search, BarChart, Brain, Sparkles, MessageCircleQuestion, CheckCircle2, XCircle, Send } from "lucide-react";
import { useParams, useNavigate } from "react-router-dom";
import ToolLog from "./ToolLog";
import AgentProgress from "./AgentProgress";
import ChatInput from "./ChatInput";
import { LLMCatchError } from "./LLMCatchError";
import ReportViewer from "./Report_Viewer/ReportViewer";
import { useChat } from "@/hooks/useChat";
import { useProcessingState } from "@/hooks/useProcessingState";
import React, { useEffect, useRef, useState } from "react";
import { v4 as uuidv4 } from 'uuid';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

/**
 * Renders a syntax-highlighted code block with a one-click copy button.
 * Uses navigator.clipboard with a textarea fallback for non-HTTPS dev servers.
 */
const CodeBlock = ({ language, code }: { language: string; code: string }) => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = () => {
    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(code).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }).catch(() => fallbackCopy());
    } else {
      fallbackCopy();
    }
  };

  const fallbackCopy = () => {
    const textarea = document.createElement('textarea');
    textarea.value = code;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group">
      {language ? (
        <div className="flex items-center justify-between px-4 py-1.5 bg-[#1A3C2B]">
          <span className="text-[11px] font-mono text-[#F7F7F5] uppercase tracking-wider font-semibold opacity-90">{language}</span>
          <button onClick={copyToClipboard} className={`text-[11px] font-mono transition-colors px-2 py-0.5 rounded ${copied ? 'text-emerald-300' : 'text-[#F7F7F5]/60 hover:text-[#F7F7F5] hover:bg-white/10'}`}>
            {copied ? '✓ Copied!' : 'Copy'}
          </button>
        </div>
      ) : (
        <button onClick={copyToClipboard} className={`absolute top-2 right-2 text-[11px] font-mono transition-colors px-2 py-0.5 rounded z-10 ${copied ? 'text-emerald-300 opacity-100' : 'text-[#d4d4d4]/40 hover:text-[#d4d4d4] hover:bg-white/10 opacity-0 group-hover:opacity-100'}`}>
          {copied ? '✓ Copied!' : 'Copy'}
        </button>
      )}
      <SyntaxHighlighter
        style={vscDarkPlus}
        language={language || 'text'}
        PreTag="div"
        customStyle={{ margin: 0, padding: "16px 20px", background: 'transparent', fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace" }}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
};

/**
 * Pre-processes markdown content before passing it to ReactMarkdown.
 *
 * remark-math v6 only understands $...$ and $$...$$ delimiters — it does NOT
 * handle \(...\) or \[...\].  Many LLMs emit the LaTeX-style delimiters, so
 * this function normalises everything to dollar notation before remarkMath
 * ever sees the content.
 *
 * Pipeline:
 *   0. Protect code blocks, images, and links with placeholders.
 *   1. Escape currency dollar signs ($50, $1,000) so remarkMath ignores them.
 *   2. [non-streaming] Auto-close unclosed \(, \[, and $$ delimiters.
 *   3. Convert \(...\) → $...$  and  \[...\] → $$...$$ .
 *   4. [non-streaming] Auto-close unclosed $$ after conversion.
 *   5. Restore placeholders.
 *
 * When isStreaming=true steps 2 & 4 are skipped to prevent layout shifts.
 *
 * Hoisted to module scope — pure function with no closure dependencies.
 */
const preprocessContent = (raw: string, isStreaming: boolean = false): string => {
  let result = raw;
  const codeBlocks: string[] = [];
  const imageLinks: string[] = [];
  const textLinks: string[] = [];

  // ── Step 0: Protect non-math constructs with placeholders ─────────────

  result = result.replace(/```[\s\S]*?```/g, (m) => {
    codeBlocks.push(m);
    return `%%CB_${codeBlocks.length - 1}%%`;
  });
  result = result.replace(/`[^`]+`/g, (m) => {
    codeBlocks.push(m);
    return `%%CB_${codeBlocks.length - 1}%%`;
  });

  result = result.replace(/!\[([^\]]*)\]\([^)]*\)/g, (m) => {
    imageLinks.push(m);
    return `%%IMG_${imageLinks.length - 1}%%`;
  });

  result = result.replace(/\(\s*(!?\[[^\]]*\]\([^)]*\))\s*\)/g, '$1');

  result = result.replace(/(?<!!)\[([^\]]*)\]\([^)]*\)/g, (m) => {
    textLinks.push(m);
    return `%%LINK_${textLinks.length - 1}%%`;
  });

  // ── Step 1: Escape standalone currency dollar signs ───────────────────
  // $50, $1,000, $100.50 etc. — a lone $ followed by a digit that is NOT
  // part of a $$ display-math fence.  Escaping to \$ makes markdown render
  // a literal "$" while keeping remarkMath from treating it as math.
  result = result.replace(/(?<!\$)\$(?=\d)/g, '\\$');

  // ── Step 2: Auto-close unclosed LaTeX-style delimiters (final only) ───
  if (!isStreaming) {
    const openInline  = (result.match(/\\\(/g) || []).length;
    const closeInline = (result.match(/\\\)/g) || []).length;
    if (openInline > closeInline) result += '\\)';

    const openDisplay  = (result.match(/\\\[/g) || []).length;
    const closeDisplay = (result.match(/\\\]/g) || []).length;
    if (openDisplay > closeDisplay) result += '\\]';
  }

  // ── Step 3: Normalise LaTeX delimiters → dollar notation ──────────────
  // \(...\) → $...$   (inline math)
  result = result.replace(/\\\(([\s\S]*?)\\\)/g, (_, math) => `$${math}$`);
  // \[...\] → $$...$$ (display math)
  result = result.replace(/\\\[([\s\S]*?)\\\]/g, (_, math) => `$$${math}$$`);

  // ── Step 4: Auto-close unclosed $$ fences (final only) ────────────────
  if (!isStreaming) {
    const ddCount = (result.match(/(?<!\$)\$\$(?!\$)/g) || []).length;
    if (ddCount % 2 !== 0) result += '$$';
  }

  // ── Step 5: Restore protected constructs ──────────────────────────────
  result = result.replace(/%%LINK_(\d+)%%/g, (_, i) => {
    const idx = parseInt(i, 10);
    return idx < textLinks.length ? textLinks[idx] : `%%LINK_${i}%%`;
  });
  result = result.replace(/%%IMG_(\d+)%%/g, (_, i) => {
    const idx = parseInt(i, 10);
    return idx < imageLinks.length ? imageLinks[idx] : `%%IMG_${i}%%`;
  });
  result = result.replace(/%%CB_(\d+)%%/g, (_, i) => {
    const idx = parseInt(i, 10);
    return idx < codeBlocks.length ? codeBlocks[idx] : `%%CB_${i}%%`;
  });

  return result;
};

/**
 * Strips citation-style parentheses from React children arrays.
 * Only matches citation patterns like [1], [2,3], etc. — not arbitrary parenthetical text.
 * Hoisted to module scope to avoid re-creation on every render.
 */
const stripCitationParentheses = (children: React.ReactNode): React.ReactNode => {
  const arr = React.Children.toArray(children);
  return arr.map((child, i) => {
    if (typeof child !== 'string') return child;
    let cleaned = child;
    const nextSibling = arr[i + 1];
    const prevSibling = arr[i - 1];
    const nextIsElement = nextSibling != null && typeof nextSibling !== 'string';
    const prevIsElement = prevSibling != null && typeof prevSibling !== 'string';
    if (nextIsElement) cleaned = cleaned.replace(/\(\s*\[\d+(?:,\s*\d+)*\]\s*\)\s*$/, '');
    if (prevIsElement) cleaned = cleaned.replace(/^\s*\(\s*\[\d+(?:,\s*\d+)*\]\s*\)/, '');
    return cleaned;
  });
};

/**
 * ReactMarkdown components map defined at module scope so the object reference
 * is stable across renders. Passing a new object every render forces ReactMarkdown
 * to re-parse the entire AST even when content hasn't changed.
 */
const markdownComponents = {
  a: ({ node, href, children, ...props }: any) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      title={href}
      style={{ textDecoration: "none", border: "none" }}
      className="inline-flex items-center gap-1 px-1.5 py-[1px] rounded-[3px] bg-[#1A3C2B] text-white/90 border border-[#1A3C2B]/80 font-medium text-[11.5px] hover:bg-[#0d1f17] hover:text-white hover:underline transition-all group mx-0.5"
      {...props}
    >
      <span className="truncate max-w-[200px]">{children}</span>
      <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="opacity-60 group-hover:opacity-100 shrink-0"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
    </a>
  ),
  p: ({ children }: any) => (
    <p className="my-[6px]">{stripCitationParentheses(children)}</p>
  ),
  li: ({ children, ...props }: any) => (
    <li {...props}>{stripCitationParentheses(children)}</li>
  ),
  blockquote: ({ children }: any) => (
    <blockquote className="pl-5 py-1 my-4 text-primary/70 italic" style={{ borderLeft: 'none', background: 'none', backgroundColor: 'transparent' }}>
      {children}
    </blockquote>
  ),
  img: ({ node, src, alt, ...props }: any) => (
    <figure className="my-4">
      <img
        src={src}
        alt={alt || ""}
        loading="lazy"
        onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
        className="rounded-md max-w-full max-h-[400px] w-auto object-contain border border-hairline bg-secondary/20"
        {...props}
      />
      {alt && alt !== "image" && (
        <figcaption className="font-mono text-[10px] text-primary/40 mt-1.5 tracking-wide">
          {alt}
        </figcaption>
      )}
    </figure>
  ),
  h1: ({ children }: any) => <h1 className="font-display font-semibold tracking-tight text-primary mt-5 mb-2 text-2xl">{children}</h1>,
  h2: ({ children }: any) => <h2 className="font-display font-semibold tracking-tight text-primary mt-5 mb-2 text-xl">{children}</h2>,
  h3: ({ children }: any) => <h3 className="font-display font-semibold tracking-tight text-primary mt-5 mb-2 text-lg">{children}</h3>,
  h4: ({ children }: any) => <h4 className="font-display font-semibold tracking-tight text-primary mt-5 mb-2 text-base">{children}</h4>,
  h5: ({ children }: any) => <h5 className="font-display font-semibold tracking-tight text-primary mt-5 mb-2 text-sm">{children}</h5>,
  h6: ({ children }: any) => <h6 className="font-display font-semibold tracking-tight text-primary mt-5 mb-2 text-xs">{children}</h6>,
  table: ({ children }: any) => <div className="overflow-x-auto my-8 border border-hairline rounded-sm"><table className="w-full text-left border-collapse">{children}</table></div>,
  thead: ({ children }: any) => <thead className="bg-[#1A3C2B] text-[#F7F7F5] font-mono text-xs uppercase tracking-wider">{children}</thead>,
  tbody: ({ children }: any) => <tbody className="divide-y divide-hairline bg-primary/5">{children}</tbody>,
  tr: ({ children }: any) => <tr className="hover:bg-primary/10 transition-colors">{children}</tr>,
  th: ({ children }: any) => <th className="px-4 py-3 font-semibold whitespace-nowrap">{children}</th>,
  td: ({ children }: any) => <td className="px-4 py-3 text-sm text-primary/90">{stripCitationParentheses(children)}</td>,
  code: ({ node, className, children, ...props }: any) => {
    const match = /language-(\w+)/.exec(className || "");
    const codeString = String(children).replace(/\n$/, '');
    const isBlock = match || codeString.includes('\n');
    if (isBlock) {
      return <CodeBlock language={match ? match[1] : ''} code={codeString} />;
    }
    return (
      <code
        className={className}
        style={{ fontFamily: "'JetBrains Mono', 'Fira Code', Consolas, monospace", backgroundColor: "rgba(26,60,43,0.08)", border: "1px solid rgba(26,60,43,0.12)", padding: "2px 6px", borderRadius: "4px", fontSize: "0.85em", color: "#1A3C2B", fontWeight: 600 }}
        {...props}
      >
        {children}
      </code>
    );
  },
};

const MARKDOWN_STYLES = `
.markdown-content pre {
  background: #1e1e1e !important;
  padding: 0 !important;
  border-radius: 8px;
  overflow: hidden;
  margin: 1.5em 0;
  border: 1px solid rgba(0,0,0,0.1);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
.markdown-content pre code {
  background: transparent !important;
  color: #d4d4d4 !important;
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important;
  font-size: 13.5px;
  line-height: 1.6;
}
.markdown-content pre span { background: transparent !important; }
.markdown-content .katex { font-size: 1em !important; }
.markdown-content .katex-display { margin: 0.8em 0; overflow-x: auto; overflow-y: hidden; }
.markdown-content .katex-display > .katex { white-space: normal; }
`;

/**
 * Renders markdown content.
 *
 * isStreaming=true  → uses only remarkGfm (fast); skips preprocessContent and
 *                     the expensive remarkMath/rehypeKatex pipeline entirely.
 *                     This runs on every token during streaming.
 *
 * isStreaming=false → full pipeline: preprocessContent normalises all math
 *                     delimiters (\(...\), \[...\], $...$) into dollar notation,
 *                     then remarkMath (singleDollarTextMath=true) + rehypeKatex
 *                     renders both inline ($...$) and display ($$...$$) math.
 */
const Markdown = React.memo(({ content, className = "", isStreaming = false }: { content: string, className?: string, isStreaming?: boolean }) => {
  return (
    <div
      className={`markdown-content text-[15.5px] text-primary/95 leading-[1.75] font-medium [&_ul]:list-disc [&_ul]:pl-5 [&_ol]:list-decimal [&_ol]:pl-5 [&_li]:my-0.5 ${className}`}
      style={{ fontFamily: "'Space Grotesk', sans-serif", fontOpticalSizing: "auto", fontStyle: "normal" }}
    >
      <style>{MARKDOWN_STYLES}</style>
      {isStreaming ? (
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={markdownComponents}
        >
          {content}
        </ReactMarkdown>
      ) : (
        <ReactMarkdown
          remarkPlugins={[remarkGfm, remarkMath]}
          rehypePlugins={[rehypeKatex]}
          components={markdownComponents}
        >
          {preprocessContent(content)}
        </ReactMarkdown>
      )}
    </div>
  );
});

/**
 * Report glyph: simple page (no dog-ear bleed). Coral strokes sit inset from Forest outline.
 * Colors: Forest #1A3C2B, Coral #FF8C69
 */
function ReportLogoMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden
    >
      {/* Outer page — single stroke, predictable bounds */}
      <rect
        x="4.75"
        y="3.5"
        width="14.5"
        height="17"
        rx="1.25"
        stroke="#1A3C2B"
        strokeWidth="1.25"
      />
      {/* Coral body lines — inset ≥2px from rect inner edge so caps never cross Forest */}
      <path
        d="M7.5 8.5h8.5M7.5 11.5h6.5M7.5 14.5h5"
        stroke="#FF8C69"
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Ready dot — bottom-right quadrant, inside page only */}
      <circle cx="15.85" cy="17.35" r="1.35" fill="#FF8C69" />
    </svg>
  );
}

/** Deep-research report CTA — Forest border, Coral logo mark, Paper base */
function ReportReadyBanner({
  label,
  onOpen,
}: {
  label: string;
  onOpen: () => void;
}) {
  const topic = label.replace(/^Report Generated:\s*/i, "").trim() || "Research";
  const truncated = topic.length > 72 ? `${topic.slice(0, 69)}…` : topic;
  return (
    <button
      type="button"
      onClick={onOpen}
      className="group w-full max-w-sm border border-[#1A3C2B] bg-[#F7F7F5] rounded-none px-3 py-2.5 text-left transition-colors duration-150 ease-out hover:bg-[#F7F7F5]/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#1A3C2B]/40"
    >
      <div className="flex items-start gap-3">
        <div
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-none border border-[#1A3C2B]/25 bg-[#F7F7F5] transition-colors group-hover:border-[#1A3C2B]/45"
          aria-hidden
        >
          <ReportLogoMark className="h-9 w-9" />
        </div>
        <div className="min-w-0 flex-1 pt-0.5">
          <div className="font-mono text-[10px] uppercase tracking-[0.1em] text-[#1A3C2B]/70">
            Report ready
          </div>
          <div className="mt-1 font-mono text-[11px] font-normal leading-snug tracking-[0.06em] text-[#1A3C2B]">
            {truncated}
          </div>
          <div className="mt-1.5 font-mono text-[10px] tracking-[0.08em] text-[#1A3C2B]/55">
            Open in panel →
          </div>
        </div>
      </div>
    </button>
  );
}

interface ChatWorkspaceProps {
  userId: string;
}

const ChatWorkspace = ({ userId }: ChatWorkspaceProps) => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const threadId = id || '';

  const { messages, logs, agentProgress, writerProgress, sectionEditProgress, sendMessage, isProcessing, isConnected, error, isInterrupted, interruptData, isClarifying, clarificationData, skillSelection, resume, resumeClarification, allReports, resumeFromError, agentError, editSection } = useChat(threadId, userId);

  const hasReports = allReports && allReports.length > 0;

  // Sync processing state to context for WortHeader's WortLoader
  const { updateProcessingState } = useProcessingState();
  const hasAgents = Object.keys(agentProgress).length > 0;
  const hasWriter = !!writerProgress;

  useEffect(() => {
    updateProcessingState({ isProcessing, hasAgents, hasWriter });
  }, [isProcessing, hasAgents, hasWriter, updateProcessingState]);

  const [isReportOpen, setIsReportOpen] = useState(false);

  useEffect(() => {
    if (hasReports) setIsReportOpen(true);
  }, [hasReports]);

  const scrollRef = useRef<HTMLDivElement>(null);
  const [feedback, setFeedback] = useState("");
  const [showRejectInput, setShowRejectInput] = useState(false);
  const [clarificationAnswers, setClarificationAnswers] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!id) {
      navigate(`/chat/${uuidv4()}`, { replace: true });
    }
  }, [id, navigate]);

  const handleNewThread = () => {
    const newId = uuidv4();
    navigate(`/chat/${newId}`);
    console.log("Started new thread:", newId);
  };

  // Auto-scroll only when user is genuinely at the bottom (tighter threshold)
  // This prevents the UI from fighting the user when they try to scroll up during rapid agentProgress updates.
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    if (distanceFromBottom < 80) {
      el.scrollTop = el.scrollHeight;
    }
  }, [messages, logs, agentProgress, writerProgress]);

  return (
    <div className="flex-grow relative flex flex-col overflow-hidden bg-background">
      {/* Main Layout Container */}
      <div className="flex-grow relative h-full overflow-hidden">

        {/* Left Pane: Chat (Margin right if report is open) */}
        <div
          className="absolute top-0 bottom-0 left-0 transition-all duration-300 ease-in-out flex flex-col border-hairline"
          style={{
            right: (hasReports && isReportOpen) ? 'clamp(350px, 55vw, 1200px)' : '0px',
            borderRightWidth: (hasReports && isReportOpen) ? '1px' : '0px'
          }}
        >
          {/* Chat Messages Area */}
          <div ref={scrollRef} className="flex-grow overflow-y-auto px-4 md:px-12 py-8 space-y-6 pb-64 scrollbar-hide">
            {(() => {
              // Find the last text-type assistant message to render after progress UI,
              // but only if it appears AFTER the last user message (i.e. it's the current response, not a historical one)
              const lastTextMsg = [...messages].reverse().find(m => m.role === "assistant" && (!m.type || m.type === "text"));
              const lastUserMsgIndex = messages.map(m => m.role).lastIndexOf("user");
              const lastTextMsgIndex = lastTextMsg ? messages.findIndex(m => m.id === lastTextMsg.id) : -1;
              const hasTerminalOutput = Object.keys(agentProgress).length > 0 || writerProgress || logs.length > 0 || skillSelection;
              const shouldRenderLastMsgAtBottom = lastTextMsg && hasTerminalOutput && lastTextMsgIndex > lastUserMsgIndex;

              return (
                <>
                  {messages.map((msg, msgIdx) => {
                    // Skip the final text message if we need to render it below the progress UI
                    if (shouldRenderLastMsgAtBottom && msg.id === lastTextMsg.id) return null;
                    // Defer "report" messages in the current reply to after progress + final text (deep research)
                    if (msg.type === "report" && msgIdx > lastUserMsgIndex) return null;

                    return (
                      <div key={msg.id} className="max-w-4xl mx-auto w-full group">
                        {msg.role === "user" ? (
                          <div className="flex justify-end">
                            <div className="w-[65%] min-w-0 rounded-tl-md rounded-bl-md rounded-br-md bg-[#1A3C2B] text-white font-mono text-base leading-relaxed px-4 py-3 border border-[#3A3A38]/20 transition-[border-color] duration-150 ease-out group-hover:border-[#3A3A38]/35">
                              {msg.content}
                            </div>
                          </div>
                        ) : msg.type === "thinking" ? (
                          /* Router thinking — rendered as a collapsible dropdown */
                          <div className="pl-2 md:pl-16 py-2 thinking-fade-in -ml-2.5">
                            <details className="group marker:content-['']">
                              <summary className="inline-flex items-center gap-2.5 cursor-pointer select-none outline-none px-2.5 py-1.5 rounded-full hover:bg-primary/5 transition-colors">
                                <div className="p-1 bg-secondary/60 rounded-full group-open:bg-secondary/40 transition-colors">
                                  <Brain size={14} className="text-primary/40 animate-pulse group-open:animate-none" />
                                </div>
                                <div className="font-mono text-[10px] uppercase tracking-[0.15em] text-primary/40 hover:text-primary/60 transition-colors flex items-center gap-2">
                                  Thinking Process
                                  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="opacity-50 transition-transform duration-200 group-open:rotate-90"><polyline points="9 18 15 12 9 6"></polyline></svg>
                                </div>
                              </summary>
                              <div className="mt-2 text-sm text-primary/50 leading-relaxed italic border-l-2 border-primary/10 pl-6 py-1 ml-[18px]">
                                {msg.content}
                              </div>
                            </details>
                          </div>
                        ) : msg.type === "plan" ? (
                          <div className="bg-secondary/30 p-4 rounded-[2px] border border-[#1A3C2B]/20">
                            <div className="flex items-center gap-2 mb-3 text-[#1A3C2B] opacity-60">
                              <BarChart size={14} />
                              <span className="font-mono text-[10px] uppercase tracking-widest">Tasks</span>
                            </div>
                            <div className="max-h-[300px] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-[#1A3C2B]/10 scrollbar-track-transparent">
                              <Markdown content={msg.content} />
                            </div>
                          </div>
                        ) : msg.type === "report" ? (
                          <ReportReadyBanner
                            label={msg.content}
                            onOpen={() => setIsReportOpen(true)}
                          />
                        ) : (
                          /* Standard assistant text message — isStreaming while type==="text" */
                          <div className="pl-2 md:pl-16">
                            <Markdown content={msg.content} isStreaming={msg.type === "text"} />
                          </div>
                        )}
                      </div>
                    );
                  })}

                  {/* Agent Progress Bars */}
                  {Object.keys(agentProgress).length > 0 && (
                    <div className="max-w-4xl mx-auto w-full">
                      <div className="pl-2 md:pl-16 space-y-3">
                        {/* Phase Distribution */}
                        <div className="flex items-center gap-4 font-mono text-[10px] tracking-wider">
                          {(['RESEARCHING', 'REVIEWING'].map(phase => {
                            const agents = Object.values(agentProgress);
                            let sum = 0;
                            agents.forEach(a => {
                              const p = a.phase?.toUpperCase() || '';
                              if (phase === 'RESEARCHING') {
                                if (p === 'RESEARCHING') sum += a.percentage || 0;
                                else if (p === 'REVIEWING' || p === 'WRITING' || p === 'PUBLISHING' || p === 'RESPONDING' || p === 'COMPLETED') sum += 100;
                              } else if (phase === 'REVIEWING') {
                                if (p === 'REVIEWING') sum += a.percentage || 0;
                                else if (p === 'WRITING' || p === 'PUBLISHING' || p === 'RESPONDING' || p === 'COMPLETED') sum += 100;
                              }
                            });
                            const pct = agents.length ? Math.round(sum / agents.length) : 0;
                            const isActivePhase = pct > 0 && pct < 100;
                            const isFinished = pct === 100;
                            const activeColor = phase === 'REVIEWING' ? 'bg-amber-400' : 'bg-emerald-400';
                            return (
                              <span key={phase} className="flex items-center gap-1.5 text-primary/60">
                                <span className={`w-1.5 h-1.5 rounded-full ${isActivePhase ? `${activeColor} animate-pulse` : (isFinished ? activeColor : 'bg-primary/10')}`} />
                                {phase} [{pct}%]
                              </span>
                            );
                          }))}
                        </div>
                        {Object.values(agentProgress).map((agent) => (
                          <AgentProgress
                            key={agent.query_num}
                            name={`AGENT_${String(agent.query_num).padStart(2, '0')}: ${agent.query?.substring(0, 40) || agent.phase}`}
                            percentage={agent.percentage}
                            active={agent.phase !== "completed"}
                            status={agent.phase?.toUpperCase()}
                            currentStep={agent.current_step}
                            query={agent.query}
                            fullCurrentStep={agent.current_step}
                            phase={agent.phase}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Writer Synthesis Progress (section edits use ReportViewer terminal overlay instead) */}
                  {writerProgress && writerProgress.metadata?.mode !== 'edit' && (
                    <div className="max-w-4xl mx-auto w-full">
                      <div className="pl-16">
                        <AgentProgress
                          name="Writer_Synthesis_Engine"
                          percentage={writerProgress.percentage}
                          currentStep={writerProgress.current_step}
                          active={writerProgress.percentage < 100}
                          status={writerProgress.percentage < 100 ? 'COMPOSING' : 'COMPLETE'}
                          variant="writer"
                        />
                      </div>
                    </div>
                  )}


                  {/* Non-router logs (generic tool logs) */}
                  {logs.length > 0 && (
                    <div className="max-w-4xl mx-auto w-full">
                      <div className="pl-16 space-y-2">
                        {logs.slice(-5).map((log) => (
                          <ToolLog
                            key={log.id}
                            icon={Search}
                            task={log.message}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Skill Selection Chips */}
                  {skillSelection && (
                    <div className="max-w-4xl mx-auto w-full animate-in fade-in duration-300">
                      <div className="pl-16">
                        <div className="flex items-center gap-2 flex-wrap">
                          <Sparkles size={14} className="text-amber-500/70" />
                          <span className="font-mono text-[10px] uppercase tracking-wider text-primary/40">Skills Active</span>
                          {skillSelection.skill_labels.map((label: string, i: number) => (
                            <span
                              key={i}
                              className="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-mono tracking-wide bg-primary/5 border border-primary/10 text-primary/70"
                            >
                              {label}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Final assistant text message rendered below progress UI */}
                  {shouldRenderLastMsgAtBottom && (
                    <div className="max-w-4xl mx-auto w-full group animate-in fade-in duration-300">
                      <div className="pl-16">
                        <Markdown content={lastTextMsg.content} isStreaming={lastTextMsg.type === "text"} />
                      </div>
                    </div>
                  )}

                  {/* Deep research: report CTA after agents + final reply (not inline in message stream) */}
                  {messages
                    .map((msg, idx) => ({ msg, idx }))
                    .filter(
                      ({ msg, idx }) =>
                        msg.type === "report" && idx > lastUserMsgIndex
                    )
                    .map(({ msg }) => (
                      <div key={msg.id} className="max-w-4xl mx-auto w-full animate-in fade-in duration-300">
                        <div className="pl-16 pt-1">
                          <ReportReadyBanner
                            label={msg.content}
                            onOpen={() => setIsReportOpen(true)}
                          />
                        </div>
                      </div>
                    ))}
                </>
              );
            })()}
            {/* Clarification Q&A UI */}
            {isClarifying && clarificationData && (
              <div className="max-w-4xl mx-auto w-full pt-6 pb-4 animate-in slide-in-from-bottom-4 duration-500">
                <div className="border border-[#1A3C2B]/20 bg-background/50 backdrop-blur-md rounded-[2px] p-6">
                  <div className="flex items-center gap-2.5 mb-5">
                    <MessageCircleQuestion size={16} className="text-[#1A3C2B]" />
                    <span className="font-mono text-xs uppercase tracking-[0.2em] font-semibold text-[#1A3C2B]">
                      Clarification // Round {clarificationData.loop_number}/3
                    </span>
                  </div>

                  <div className="space-y-4">
                    {clarificationData.questions.map((q: string, i: number) => (
                      <div key={i} className="space-y-2">
                        <label className="block text-[13px] text-[#1A3C2B] leading-relaxed font-medium">
                          {q}
                        </label>
                        <input
                          type="text"
                          value={clarificationAnswers[q] || ""}
                          onChange={(e) => setClarificationAnswers(prev => ({ ...prev, [q]: e.target.value }))}
                          placeholder="Your answer..."
                          className="w-full bg-transparent border-b border-[#1A3C2B]/20 py-2 text-sm outline-none focus:border-[#1A3C2B] transition-colors placeholder:text-[#1A3C2B]/30"
                          onKeyDown={(e) => {
                            if (e.key === "Enter" && !e.shiftKey) {
                              e.preventDefault();
                              const allAnswered = clarificationData.questions.every((q: string) => clarificationAnswers[q]?.trim());
                              if (allAnswered) {
                                resumeClarification(clarificationAnswers);
                                setClarificationAnswers({});
                              }
                            }
                          }}
                        />
                      </div>
                    ))}
                  </div>

                  <div className="flex items-center justify-end gap-3 mt-6">
                    <button
                      onClick={() => {
                        resumeClarification({});
                        setClarificationAnswers({});
                      }}
                      className="px-6 py-2.5 bg-transparent border border-[#1A3C2B]/30 text-[#1A3C2B] font-mono text-[11px] uppercase tracking-[0.15em] rounded-[2px] hover:bg-[#1A3C2B]/5 transition-all"
                    >
                      Skip_Clarification
                    </button>
                    <button
                      onClick={() => {
                        resumeClarification(clarificationAnswers);
                        setClarificationAnswers({});
                      }}
                      disabled={!clarificationData.questions.every((q: string) => clarificationAnswers[q]?.trim())}
                      className="px-6 py-2.5 bg-[#1A3C2B] text-white font-mono text-[11px] uppercase tracking-[0.15em] rounded-[2px] hover:bg-[#1A3C2B]/90 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                    >
                      Submit_Answers
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Plan Review UI */}
            {isInterrupted && interruptData && (
              <div className="max-w-4xl mx-auto w-full pt-8 pb-4 animate-in slide-in-from-bottom-6 duration-500">
                <div className="bg-background border border-[#1A3C2B]/20 rounded-[2px] p-4 md:p-6">

                  {/* Header */}
                  <div className="flex items-center gap-3 mb-8">
                    <div className="h-3 w-3 bg-[#4ade80] rounded-[2px]" />
                    <span className="font-mono text-[11px] md:text-xs uppercase tracking-[0.2em] font-bold text-[#1A3C2B]">
                      QUERY_PLAN_REVIEW // STAGE_02
                    </span>
                  </div>

                  {/* Plan Steps List */}
                  <div className="space-y-6 mb-10 pl-2">
                    {(() => {
                      const planSteps = (typeof interruptData.plan === 'string')
                        ? interruptData.plan.split('\n').filter(s => s.trim() !== '')
                        : interruptData.plan;

                      if (Array.isArray(planSteps)) {
                        return planSteps.map((step: any, index: number) => {
                          const stepString = typeof step === 'string' ? step : JSON.stringify(step);
                          // Strip leading text like "1. " or "Step 1:"
                          let cleanStep = stepString.replace(/^\d+\.\s*/, '');
                          try {
                            if (cleanStep.startsWith('{')) {
                              const parsed = JSON.parse(cleanStep);
                              if (parsed.query) cleanStep = parsed.query;
                            }
                          } catch (e) { /* ignore parse error */ }

                          return (
                            <div key={index} className="flex flex-col md:flex-row gap-2 md:gap-4 font-inter text-sm md:text-[15px] text-[#1A3C2B]/80 hover:text-[#1A3C2B] transition-colors leading-relaxed">
                              <div className="font-mono text-xs md:text-sm font-bold text-[#1A3C2B] whitespace-nowrap shrink-0 pt-[2px]">
                                _{String(index + 1).padStart(2, '0')}:
                              </div>
                              <div className="flex-1">{cleanStep}</div>
                            </div>
                          );
                        });
                      }
                      return <div className="text-sm font-mono text-[#1A3C2B]/70">{interruptData.plan}</div>;
                    })()}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-col md:flex-row gap-4 mb-6">
                    <button
                      onClick={() => { setShowRejectInput(false); setFeedback(""); resume(true, feedback); }}
                      className="flex-1 text-center py-4 bg-[#1A3C2B] text-white font-mono text-[12px] uppercase tracking-[0.2em] font-semibold hover:bg-[#122A1E] transition-colors rounded-[2px] shadow-sm"
                    >
                      APPROVE_PLAN
                    </button>
                    <button
                      onClick={() => {
                        if (showRejectInput && feedback) {
                          resume(false, feedback);
                          setFeedback("");
                          setShowRejectInput(false);
                        } else {
                          setShowRejectInput(true);
                        }
                      }}
                      className="flex-1 text-center py-4 bg-transparent border border-red-400 text-red-500 font-mono text-[12px] uppercase tracking-[0.2em] font-semibold hover:bg-red-50 transition-colors rounded-[2px]"
                    >
                      {showRejectInput ? (feedback ? "SUBMIT_MODIFICATION" : "CANCEL_MODIFY") : "REJECT_AND_MODIFY"}
                    </button>
                  </div>

                  {/* Feedback Input (Conditional) */}
                  {showRejectInput && (
                    <div className="animate-in fade-in slide-in-from-top-2 duration-300">
                      <input
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                        placeholder="Add feedback for query optimization..."
                        className="w-full bg-transparent border border-[#1A3C2B]/20 px-5 py-4 text-sm font-inter outline-none focus:border-[#1A3C2B]/60 transition-colors rounded-[2px] placeholder:text-[#1A3C2B]/40"
                        autoFocus
                        onKeyDown={(e) => {
                          if (e.key === "Enter" && !e.shiftKey && feedback) {
                            e.preventDefault();
                            resume(false, feedback);
                            setFeedback("");
                            setShowRejectInput(false);
                          }
                        }}
                      />
                    </div>
                  )}

                </div>
              </div>
            )}
          </div>

          {/* Agent Error Recovery UI */}
          {agentError && (
             <LLMCatchError 
               errorData={agentError} 
               onRetry={() => {
                 // LangGraph checkpointer allows us to natively resume execution exactly from the last saved node.
                 resumeFromError();
               }} 
             />
          )}

          {/* Input Bar is Always Visible Unless Hard Error Occurs */}
          {!agentError && (
            <ChatInput
              onSendMessage={sendMessage}
              disabled={isProcessing || isInterrupted || isClarifying}
              onResumeError={resumeFromError}
              hasError={!!error}
            />
          )}
        </div>

        {/* Right Pane: Report Viewer (Absolute Positioning prevents layout thrashing) */}
        <div
          className={`absolute top-0 bottom-0 right-0 bg-background transition-transform duration-300 ease-in-out border-l border-hairline flex flex-col p-6 z-10 ${hasReports && isReportOpen ? 'translate-x-0' : 'translate-x-full'
            }`}
          style={{
            width: 'clamp(350px, 55vw, 1200px)',
            visibility: hasReports && isReportOpen ? 'visible' : 'hidden'
          }}
        >
          <div className="h-full flex flex-col bg-[#F7F7F5] rounded-xl shadow-sm border border-hairline overflow-hidden relative group">
            <div className="flex items-center justify-between px-6 py-4 bg-[#1A3C2B] text-white z-10 sticky top-0 rounded-t-xl">
              <div className="font-mono text-sm uppercase tracking-[0.15em] font-semibold flex items-center gap-3">
                <div className="w-2 h-2 rounded-sm bg-white opacity-80" />
                DOCUMENT_VIEWER
              </div>
              <button
                onClick={() => setIsReportOpen(false)}
                className="text-white/70 hover:text-white hover:bg-white/10 p-1.5 rounded-full transition-colors"
              >
                <XCircle size={18} />
              </button>
            </div>
            <div className="flex-grow overflow-y-auto p-4 md:p-8 custom-scrollbar bg-black/5 dark:bg-white/5 mx-[-1px]">
              <ReportViewer content="" reports={allReports} sectionEditProgress={sectionEditProgress} onEditSection={editSection} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default React.memo(ChatWorkspace);
