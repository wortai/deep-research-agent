import { useState, useEffect, useCallback } from "react";
import ReactDOM from "react-dom";
import { Key, Eye, EyeOff, Check, X } from "lucide-react";

export type ApiKeys = {
  openai?: string;
  gemini?: string;
  anthropic?: string;
};

export type ModelSelections = {
  openai_model?: string;
  gemini_model?: string;
  anthropic_model?: string;
};

export const PROVIDERS: { key: keyof ApiKeys; label: string; color: string }[] = [
  { key: "openai", label: "OpenAI", color: "#10a37f" },
  { key: "gemini", label: "Gemini", color: "#4285f4" },
  { key: "anthropic", label: "Anthropic", color: "#d4a574" },
];

export const MODELS: Record<keyof ApiKeys, { value: string; label: string }[]> = {
  openai: [
    { value: "gpt-5.4", label: "GPT-5.4" },
    { value: "gpt-5.4-mini", label: "GPT-5.4 Mini" },
    { value: "gpt-5.4-nano", label: "GPT-5.4 Nano" },
    { value: "gpt-4.1", label: "GPT-4.1" },
    { value: "gpt-4.1-mini", label: "GPT-4.1 Mini" },
  ],
  gemini: [
    { value: "gemini-2.5-pro", label: "Gemini 2.5 Pro" },
    { value: "gemini-2.5-flash", label: "Gemini 2.5 Flash" },
    { value: "gemini-3.1-pro-preview", label: "Gemini 3.1 Pro" },
    { value: "gemini-3-flash-preview", label: "Gemini 3 Flash" },
    { value: "gemini-2.0-flash", label: "Gemini 2.0 Flash" },
  ],
  anthropic: [
    { value: "claude-opus-4-6", label: "Claude Opus 4.6" },
    { value: "claude-sonnet-4-6", label: "Claude Sonnet 4.6" },
    { value: "claude-haiku-4-5", label: "Claude Haiku 4.5" },
    { value: "claude-sonnet-4-5", label: "Claude Sonnet 4.5" },
    { value: "claude-sonnet-4-20250514", label: "Claude Sonnet 4" },
  ],
};

const API_KEYS_STORAGE = "wort_api_keys";
const MODELS_STORAGE = "wort_model_selections";

export const loadApiKeys = (): ApiKeys => {
  try {
    const raw = localStorage.getItem(API_KEYS_STORAGE);
    if (raw) return JSON.parse(raw);
  } catch {}
  return {};
};

export const saveApiKeys = (keys: ApiKeys) => {
  const cleaned: ApiKeys = {};
  for (const [k, v] of Object.entries(keys)) {
    if (v && v.trim()) cleaned[k as keyof ApiKeys] = v.trim();
  }
  if (Object.keys(cleaned).length > 0) {
    localStorage.setItem(API_KEYS_STORAGE, JSON.stringify(cleaned));
  } else {
    localStorage.removeItem(API_KEYS_STORAGE);
  }
};

export const loadModelSelections = (): ModelSelections => {
  try {
    const raw = localStorage.getItem(MODELS_STORAGE);
    if (raw) return JSON.parse(raw);
  } catch {}
  return {};
};

export const saveModelSelections = (s: ModelSelections) => {
  const cleaned: ModelSelections = {};
  for (const [k, v] of Object.entries(s)) {
    if (v) cleaned[k as keyof ModelSelections] = v;
  }
  if (Object.keys(cleaned).length > 0) {
    localStorage.setItem(MODELS_STORAGE, JSON.stringify(cleaned));
  } else {
    localStorage.removeItem(MODELS_STORAGE);
  }
};

interface ApiKeyPanelProps {
  apiKeys: ApiKeys;
  onApiKeysChange: (keys: ApiKeys) => void;
  disabled?: boolean;
}

const ApiKeyPanel = ({ apiKeys, onApiKeysChange, disabled }: ApiKeyPanelProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [draft, setDraft] = useState<ApiKeys>({ ...apiKeys });
  const [visibleKeys, setVisibleKeys] = useState<Record<string, boolean>>({});
  const [mounted, setMounted] = useState(false);

  // Trigger enter animation after mount
  useEffect(() => {
    if (isOpen) {
      requestAnimationFrame(() => setMounted(true));
    } else {
      setMounted(false);
    }
  }, [isOpen]);

  useEffect(() => {
    if (isOpen) setDraft({ ...apiKeys });
  }, [apiKeys, isOpen]);

  const close = useCallback(() => setIsOpen(false), []);

  // Escape key to close
  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") close();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [isOpen, close]);

  const handleSave = () => {
    const cleanedKeys: ApiKeys = {};
    for (const [k, v] of Object.entries(draft)) {
      if (v && v.trim()) cleanedKeys[k as keyof ApiKeys] = v.trim();
    }
    saveApiKeys(cleanedKeys);
    onApiKeysChange(cleanedKeys);
    close();
  };

  const handleClear = () => {
    setDraft({});
    saveApiKeys({});
    onApiKeysChange({});
    close();
  };

  const hasKeys = Object.values(apiKeys).some((v) => v && v.trim());
  const filledCount = PROVIDERS.filter(
    (p) => draft[p.key] && draft[p.key]!.trim()
  ).length;

  const overlay = isOpen ? (
    <>
      {/* Backdrop — tap/click to dismiss */}
      <div
        className="fixed inset-0 z-40"
        style={{
          transition: "opacity 160ms ease",
          opacity: mounted ? 1 : 0,
        }}
        onClick={close}
        aria-hidden
      />

      {/* Panel — compact, right-anchored above the input bar */}
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Provider API Keys"
        style={{
          transition: "opacity 150ms ease, transform 170ms cubic-bezier(0.16,1,0.3,1)",
          opacity: mounted ? 1 : 0,
          transform: mounted ? "translateY(0)" : "translateY(8px)",
          boxShadow: "0 4px 24px -4px rgba(26,60,43,0.12), 0 1px 4px -1px rgba(26,60,43,0.08)",
          // Compact width: 256px, clamps to viewport on very small screens
          width: "min(256px, calc(100vw - 1.5rem))",
        }}
        className="fixed z-50 right-3 bottom-[7.5rem] sm:right-5 sm:bottom-[7.5rem] bg-background border border-[#1A3C2B]/12 rounded-lg overflow-hidden"
      >
        {/* ── Header ────────────────────────────────────────── */}
        <div className="flex items-center justify-between px-3 py-2 border-b border-[#1A3C2B]/8">
          <div className="flex items-center gap-1.5">
            <Key size={10} strokeWidth={2} className="text-[#1A3C2B]/40" />
            <span className="font-mono text-[9px] uppercase tracking-[0.18em] text-[#1A3C2B]/60 font-semibold select-none">
              Provider_Keys
            </span>
          </div>
          <button
            type="button"
            onClick={close}
            className="p-0.5 text-[#1A3C2B]/20 hover:text-[#1A3C2B]/55 transition-colors"
            aria-label="Close"
          >
            <X size={11} strokeWidth={2.5} />
          </button>
        </div>

        {/* ── Provider Inputs ───────────────────────────────── */}
        <div className="px-3 pt-2.5 pb-2 space-y-2.5 bg-background">
          {PROVIDERS.map((provider) => {
            const isVisible = visibleKeys[provider.key] ?? false;
            const hasKey = !!(draft[provider.key] && draft[provider.key]!.trim());

            return (
              <div key={provider.key} className="space-y-1">
                {/* Label row */}
                <div className="flex items-center gap-1.5">
                  <span
                    className="w-[5px] h-[5px] rounded-full shrink-0"
                    style={{ backgroundColor: provider.color }}
                    aria-hidden
                  />
                  <span className="font-mono text-[8.5px] uppercase tracking-wider text-[#1A3C2B]/50 font-medium flex-1 select-none">
                    {provider.label}
                  </span>
                  {hasKey && (
                    <Check size={8} strokeWidth={2.5} className="text-emerald-600/50" />
                  )}
                </div>

                {/* Input */}
                <div className="relative">
                  <input
                    type={isVisible ? "text" : "password"}
                    value={draft[provider.key] ?? ""}
                    onChange={(e) =>
                      setDraft((prev) => ({ ...prev, [provider.key]: e.target.value }))
                    }
                    placeholder="sk-···"
                    autoComplete="off"
                    spellCheck={false}
                    className={[
                      "w-full bg-[#f9f9f6] border rounded-[2px]",
                      "px-2.5 py-1.5 pr-7",
                      "text-[10px] font-mono text-primary",
                      "placeholder-[#1A3C2B]/18",
                      "outline-none transition-all duration-150",
                      hasKey
                        ? "border-[#1A3C2B]/18 focus:border-[#1A3C2B]/38 focus:bg-white"
                        : "border-[#1A3C2B]/10 focus:border-[#1A3C2B]/28 focus:bg-white",
                    ].join(" ")}
                  />
                  <button
                    type="button"
                    tabIndex={-1}
                    onClick={() =>
                      setVisibleKeys((prev) => ({
                        ...prev,
                        [provider.key]: !prev[provider.key],
                      }))
                    }
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-[#1A3C2B]/18 hover:text-[#1A3C2B]/50 transition-colors"
                    aria-label={isVisible ? "Hide key" : "Reveal key"}
                  >
                    {isVisible ? <EyeOff size={10} /> : <Eye size={10} />}
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* ── Footer ────────────────────────────────────────── */}
        <div className="px-3 py-2 border-t border-[#1A3C2B]/8 bg-[#fffff8] flex items-center justify-between gap-2">
          <button
            type="button"
            onClick={handleClear}
            className="font-mono text-[8px] uppercase tracking-wider text-[#1A3C2B]/22 hover:text-red-400/70 transition-colors"
          >
            Clear
          </button>
          <div className="flex items-center gap-1.5">
            <button
              type="button"
              onClick={close}
              className="px-2.5 py-1 font-mono text-[8.5px] uppercase tracking-wider border border-[#1A3C2B]/10 rounded-[2px] text-[#1A3C2B]/38 hover:text-[#1A3C2B]/65 hover:border-[#1A3C2B]/22 transition-all"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              className="px-3 py-1 font-mono text-[8.5px] uppercase tracking-wider bg-[#1A3C2B] text-white rounded-[2px] hover:bg-[#1A3C2B]/88 transition-colors"
            >
              Save
            </button>
          </div>
        </div>
      </div>
    </>
  ) : null;

  return (
    <>
      {/* Trigger button — lives inside the input bar */}
      <button
        type="button"
        disabled={disabled}
        onClick={() => setIsOpen((v) => !v)}
        className={[
          "shrink-0 flex items-center gap-1 transition-all duration-200 rounded-[2px]",
          hasKeys
            ? "px-2 py-1 border border-[#1A3C2B]/22 bg-[#1A3C2B]/5"
            : "p-1.5",
          isOpen ? "bg-[#1A3C2B]/10 border-[#1A3C2B]/25" : "",
        ].join(" ")}
        aria-label="Manage API keys"
        aria-expanded={isOpen}
        aria-haspopup="dialog"
      >
        <Key
          size={13}
          strokeWidth={2}
          className={hasKeys ? "text-[#1A3C2B]/65" : "text-primary/28"}
        />
        {hasKeys && (
          <span className="font-mono text-[9px] text-[#1A3C2B]/45 uppercase tracking-wider tabular-nums">
            {filledCount}
          </span>
        )}
      </button>

      {/* Portal — renders the overlay at document body to avoid stacking-context issues */}
      {typeof document !== "undefined" &&
        ReactDOM.createPortal(overlay, document.body)}
    </>
  );
};

export default ApiKeyPanel;
