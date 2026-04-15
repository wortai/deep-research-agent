import { useState, useRef, useEffect, KeyboardEvent } from "react";
import { ArrowUp, ChevronDown, Cpu } from "lucide-react";
import ApiKeyPanel, {
  ApiKeys,
  ModelSelections,
  PROVIDERS,
  MODELS,
  loadApiKeys,
  loadModelSelections,
  saveApiKeys,
  saveModelSelections,
} from "./ApiKeyPopover";

const TEXTAREA_MAX_HEIGHT_PX = 160;

type Mode = "web" | "deep" | "extreme";
type DeepLevel = "low" | "mid" | "high";

export interface ChatInputProps {
  onSendMessage: (
    message: string,
    mode: string,
    apiKeys?: ApiKeys,
    modelSelections?: ModelSelections
  ) => void;
  disabled?: boolean;
  onResumeError?: () => void;
  hasError?: boolean;
}

const DEEP_LEVELS: DeepLevel[] = ["low", "mid", "high"];
const DEEP_LEVELS_MENU_TOP_FIRST: DeepLevel[] = [...DEEP_LEVELS].reverse();

function deepLevelDotClass(level: DeepLevel, selected: boolean): string {
  if (selected) {
    switch (level) {
      case "high":
        return "bg-amber-400 shadow-[0_0_6px_3px_rgba(251,191,36,0.55)]";
      case "mid":
        return "bg-cyan-400 shadow-[0_0_6px_3px_rgba(34,211,238,0.5)]";
      case "low":
      default:
        return "bg-emerald-400 shadow-[0_0_6px_3px_rgba(52,211,153,0.45)]";
    }
  }
  switch (level) {
    case "high":
      return "border border-amber-400/55 bg-white";
    case "mid":
      return "border border-cyan-400/55 bg-white";
    case "low":
    default:
      return "border border-emerald-400/55 bg-white";
  }
}

const ChatInput = ({
  onSendMessage,
  disabled,
  onResumeError,
  hasError,
}: ChatInputProps) => {
  const [activeMode, setActiveMode] = useState<Mode>("deep");
  const [deepLevel, setDeepLevel] = useState<DeepLevel>("low");
  const [deepMenuOpen, setDeepMenuOpen] = useState(false);
  const [input, setInput] = useState("");
  const [apiKeys, setApiKeys] = useState<ApiKeys>(loadApiKeys);
  const [modelSelections, setModelSelections] =
    useState<ModelSelections>(loadModelSelections);
  const [modelDropdownOpen, setModelDropdownOpen] = useState(false);
  const [mobileModeMenuOpen, setMobileModeMenuOpen] = useState(false);
  /** Mobile only: Deep_Analysis row expanded to pick HIGH / MID / LOW (commit happens on level tap). */
  const [mobileDeepExpanded, setMobileDeepExpanded] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const modelDropdownRef = useRef<HTMLDivElement>(null);
  const mobileModeMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, TEXTAREA_MAX_HEIGHT_PX)}px`;
  }, [input]);

  useEffect(() => {
    if (!modelDropdownOpen) return;
    const handleClick = (e: MouseEvent) => {
      if (modelDropdownRef.current && !modelDropdownRef.current.contains(e.target as Node)) {
        setModelDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [modelDropdownOpen]);

  useEffect(() => {
    if (!mobileModeMenuOpen) return;
    const handleClick = (e: MouseEvent) => {
      if (mobileModeMenuRef.current && !mobileModeMenuRef.current.contains(e.target as Node)) {
        setMobileModeMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [mobileModeMenuOpen]);

  useEffect(() => {
    if (!mobileModeMenuOpen) setMobileDeepExpanded(false);
  }, [mobileModeMenuOpen]);

  const modes: { id: Mode; label: string }[] = [
    { id: "web", label: "Web_Search" },
    { id: "deep", label: "Deep_Research" },
    { id: "extreme", label: "XtremeResearch" },
  ];

  const handleSend = () => {
    if (input.trim() && !disabled) {
      let backendMode: string;
      if (activeMode === "web") {
        backendMode = "websearch";
      } else if (activeMode === "deep") {
        backendMode = `deepsearch_${deepLevel}`;
      } else {
        backendMode = "extremesearch";
      }
      const hasKeys = Object.values(apiKeys).some((v) => v && v.trim());
      onSendMessage(
        input,
        backendMode,
        hasKeys ? apiKeys : undefined,
        hasKeys ? modelSelections : undefined
      );
      setInput("");
      requestAnimationFrame(() => {
        if (textareaRef.current) textareaRef.current.style.height = "auto";
      });
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const availableProviders = PROVIDERS.filter(
    (p) => apiKeys[p.key]?.trim()
  );

  /** Label shown on the mobile mode trigger button */
  const mobileModeTriggerLabel =
    activeMode === "web"
      ? "Web_Search"
      : activeMode === "extreme"
        ? "XtremeResearch"
        : `Deep_Research[${deepLevel}]`;

  const handleModelSelect = (providerKey: string, modelValue: string) => {
    const modelKey = `${providerKey}_model` as keyof ModelSelections;
    const next = { ...modelSelections };
    if (modelValue) {
      next[modelKey] = modelValue;
    } else {
      delete next[modelKey];
    }
    setModelSelections(next);
    saveModelSelections(next);
    setModelDropdownOpen(false);
  };

  return (
    <div className="absolute bottom-0 left-0 right-0 bg-background pt-8 pb-8 px-4">
      <div className="w-full max-w-4xl mx-auto">
        <div className="border border-[#1A3C2B]/20 rounded-lg shadow-sm bg-background">
          {/* Input Field */}
          <div className="flex items-end gap-3 px-4 py-2.5 bg-transparent">
            <textarea
              ref={textareaRef}
              rows={1}
              placeholder="."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={disabled}
              className="w-full min-h-[44px] resize-none overflow-y-auto bg-transparent border-none outline-none text-base font-mono text-primary placeholder-muted-foreground/40 py-2.5 leading-relaxed"
              style={{ maxHeight: TEXTAREA_MAX_HEIGHT_PX }}
            />
            <button
              type="button"
              onClick={handleSend}
              disabled={disabled || !input.trim()}
              className={`shrink-0 w-8 h-8 mb-0.5 flex items-center justify-center transition-all duration-200 border rounded-[2px] ${
                input.trim() && !disabled
                  ? "bg-[#1A3C2B] border-[#1A3C2B] text-white hover:bg-[#1A3C2B]/90"
                  : "bg-secondary text-primary/20"
              }`}
              aria-label="Send"
            >
              <ArrowUp size={18} />
            </button>
            <ApiKeyPanel
              apiKeys={apiKeys}
              onApiKeysChange={(keys) => {
                setApiKeys(keys);
                saveApiKeys(keys);
                const next: ModelSelections = {};
                for (const [k, v] of Object.entries(modelSelections)) {
                  const pk = k.replace("_model", "") as keyof ApiKeys;
                  if (keys[pk]?.trim()) {
                    (next as any)[k] = v;
                  }
                }
                setModelSelections(next);
                saveModelSelections(next);
              }}
              disabled={disabled}
            />
          </div>

          {/* Mode Selection + Model Dropdowns + Error Resume */}
          <div className="bg-[#fffff8] border-t border-[#1A3C2B]/10 px-3 sm:px-4 py-2 sm:py-3 pb-3.5 sm:pb-5 flex flex-wrap items-center gap-2 overflow-visible scrollbar-hide rounded-b-lg">
            {/* —— Mobile: compact mode control + dropdown (md+: hidden) —— */}
            <div
              ref={mobileModeMenuRef}
              className="relative z-[60] w-[8.75rem] max-w-[calc(100vw-5rem)] shrink md:hidden"
            >
              <button
                type="button"
                disabled={disabled}
                onClick={() => setMobileModeMenuOpen((o) => !o)}
                aria-expanded={mobileModeMenuOpen}
                aria-haspopup="listbox"
                className={`flex w-full items-center justify-between gap-1 px-2 py-1 font-mono text-[8px] uppercase tracking-[0.14em] border transition-all ${
                  mobileModeMenuOpen
                    ? "rounded-t-none rounded-b-[3px] border-t-0 border-[#1A3C2B]/35 bg-[#1A3C2B] text-white shadow-sm"
                    : "rounded-[3px] border-[#1A3C2B]/15 bg-white/90 text-[#1A3C2B]/90 shadow-[inset_0_1px_0_rgba(255,255,255,0.7)] hover:border-[#1A3C2B]/28"
                }`}
              >
                <span className="min-w-0 truncate text-left leading-tight">{mobileModeTriggerLabel}</span>
                <ChevronDown
                  size={10}
                  strokeWidth={2}
                  className={`shrink-0 opacity-75 transition-transform ${mobileModeMenuOpen ? "rotate-180" : ""}`}
                />
              </button>

              {mobileModeMenuOpen && (
                <div
                  className="absolute bottom-full left-0 z-[70] mb-0 w-full overflow-hidden rounded-t-[6px] rounded-b-none border border-b-0 border-[#1A3C2B]/10 bg-[#fffff8] p-1 shadow-[0_-2px_18px_-4px_rgba(26,60,43,0.1),0_-1px_3px_rgba(26,60,43,0.04)]"
                  role="listbox"
                  aria-label="Search mode"
                >
                  {/* Web */}
                  <button
                    type="button"
                    role="option"
                    aria-selected={activeMode === "web"}
                    onClick={() => {
                      setActiveMode("web");
                      setMobileDeepExpanded(false);
                      setMobileModeMenuOpen(false);
                    }}
                    disabled={disabled}
                    className={`w-full rounded-[4px] px-2 py-[0.35rem] text-left font-mono text-[8px] uppercase tracking-[0.12em] leading-snug transition-all ${
                      activeMode === "web"
                        ? "bg-[#1A3C2B] font-medium text-white shadow-sm"
                        : "text-[#1A3C2B]/55 hover:bg-white/80 hover:text-[#1A3C2B]/85"
                    }`}
                  >
                    Web_Search
                  </button>

                  {/* Deep: expand → pick intensity */}
                  <div className="mt-0.5">
                    <button
                      type="button"
                      role="option"
                      aria-expanded={mobileDeepExpanded}
                      aria-selected={activeMode === "deep"}
                      onClick={() => setMobileDeepExpanded((e) => !e)}
                      disabled={disabled}
                      className={`flex w-full items-center justify-between gap-0.5 rounded-[4px] px-2 py-[0.35rem] text-left font-mono text-[8px] uppercase tracking-[0.12em] leading-snug transition-all ${
                        activeMode === "deep"
                          ? "bg-[#1A3C2B] font-medium text-white shadow-sm"
                          : mobileDeepExpanded
                            ? "bg-white/70 text-[#1A3C2B]"
                            : "text-[#1A3C2B]/55 hover:bg-white/80 hover:text-[#1A3C2B]/85"
                      }`}
                    >
                      <span className="min-w-0">Deep</span>
                      <ChevronDown
                        size={10}
                        strokeWidth={2}
                        className={`shrink-0 opacity-60 transition-transform ${mobileDeepExpanded ? "rotate-180" : ""}`}
                      />
                    </button>
                    {mobileDeepExpanded && (
                      <div
                        className="mt-0.5 grid grid-cols-3 gap-0.5 rounded-[4px] bg-[#1A3C2B]/[0.04] p-1"
                        role="group"
                        aria-label="Deep research intensity"
                      >
                        {DEEP_LEVELS_MENU_TOP_FIRST.map((level) => {
                          const sel = activeMode === "deep" && deepLevel === level;
                          return (
                            <button
                              key={level}
                              type="button"
                              role="option"
                              aria-selected={sel}
                              onClick={() => {
                                setActiveMode("deep");
                                setDeepLevel(level);
                                setMobileDeepExpanded(false);
                                setMobileModeMenuOpen(false);
                              }}
                              disabled={disabled}
                              className={`flex flex-col items-center justify-center gap-px rounded-[3px] py-1 font-mono text-[7px] uppercase tracking-tight transition-all ${
                                sel
                                  ? level === "high"
                                    ? "bg-amber-100/90 text-[#1A3C2B] shadow-sm ring-1 ring-amber-200/60"
                                    : level === "mid"
                                      ? "bg-cyan-100/80 text-[#1A3C2B] shadow-sm ring-1 ring-cyan-200/50"
                                      : "bg-emerald-100/90 text-[#1A3C2B] shadow-sm ring-1 ring-emerald-200/60"
                                  : "bg-white/90 text-[#1A3C2B]/45 hover:bg-white hover:text-[#1A3C2B]/75"
                              }`}
                            >
                              <span
                                className={`h-1 w-1 rounded-full ${deepLevelDotClass(level, sel)}`}
                                aria-hidden
                              />
                              {level}
                            </button>
                          );
                        })}
                      </div>
                    )}
                  </div>

                  <div className="group relative mt-0.5 w-full">
                    <button
                      type="button"
                      role="option"
                      aria-selected={false}
                      onClick={(e) => e.preventDefault()}
                      className="w-full rounded-[4px] px-2 py-[0.35rem] text-left font-mono text-[8px] uppercase tracking-[0.12em] leading-snug opacity-40 cursor-not-allowed text-[#6B7280]"
                    >
                      XtremeResearch
                    </button>
                    <div className="absolute right-0 bottom-full mb-1 hidden group-hover:block w-[190px] p-2 bg-[#F7F7F5] text-[#1A3C2B] border border-[#1A3C2B]/15 text-[9px] font-mono leading-relaxed rounded-[4px] shadow-sm pointer-events-none z-[80] whitespace-normal normal-case tracking-normal">
                      Feature still in progress, will be live soon
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* —— Desktop / tablet: three separate mode buttons —— */}
            <div className="hidden md:contents">
            {modes.map((mode) => {
              const isActive = activeMode === mode.id;
              const isDeep = mode.id === "deep";

              const baseClasses =
                "px-2 md:px-3 py-1 font-mono text-[11px] uppercase tracking-widest transition-all cursor-pointer whitespace-nowrap border rounded-[2px]";
              const activeClasses = " bg-[#1A3C2B] border-[#1A3C2B] text-white font-thin";
              const inactiveClasses = " opacity-60 hover:opacity-100 border-[#1A3C2B]/20 hover:border-[#1A3C2B] text-[#1A3C2B]";

              const deepWrap = "relative z-[60] inline-block min-w-[10rem]";
              const deepMenuBox =
                "flex w-[5.5rem] flex-col divide-y divide-[#1A3C2B]/25 border border-b-0 border-[#1A3C2B]/30 bg-white rounded-t-[3px] rounded-b-none shadow-sm";
              const deepMenuStack =
                "absolute bottom-full left-0 z-[60] mb-0 flex w-[5.5rem] flex-col items-stretch gap-0";
              const deepLevelRow = (level: DeepLevel, selected: boolean) => {
                const base =
                  "m-0 flex min-h-0 w-full items-center gap-1 px-1.5 py-0.5 text-left font-mono text-[9px] uppercase leading-tight tracking-wide transition-colors rounded-none border-0 text-[#1A3C2B]";
                const bg = selected
                  ? level === "high"
                    ? "bg-amber-50/60"
                    : level === "mid"
                      ? "bg-cyan-50/50"
                      : "bg-emerald-50/50"
                  : "bg-white hover:bg-[#fbfefc]";
                return `${base} ${bg}`;
              };

              if (isDeep) {
                return (
                  <div
                    key={mode.id}
                    className={deepWrap}
                    onMouseEnter={() => {
                      if (!disabled) setDeepMenuOpen(true);
                    }}
                    onMouseLeave={() => setDeepMenuOpen(false)}
                  >
                    {deepMenuOpen && (
                      <div className={deepMenuStack}>
                        <div className={deepMenuBox} role="listbox" aria-label="Deep research intensity">
                          {DEEP_LEVELS_MENU_TOP_FIRST.map((level) => {
                            const isSelectedLevel = deepLevel === level;
                            return (
                              <button
                                key={level}
                                type="button"
                                role="option"
                                aria-selected={isSelectedLevel}
                                onClick={() => {
                                  setActiveMode("deep");
                                  setDeepLevel(level);
                                  setDeepMenuOpen(false);
                                }}
                                disabled={disabled}
                                className={deepLevelRow(level, isSelectedLevel)}
                              >
                                <span
                                  className={`h-1.5 w-1.5 shrink-0 rounded-full ${deepLevelDotClass(level, isSelectedLevel)}`}
                                  aria-hidden
                                />
                                {level}
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    )}
                    <button
                      type="button"
                      onClick={() => {
                        if (disabled) return;
                        setDeepMenuOpen((o) => !o);
                      }}
                      disabled={disabled}
                      aria-expanded={deepMenuOpen}
                      aria-haspopup="listbox"
                      className={
                        baseClasses +
                        " inline-flex min-w-[9.5rem] items-center justify-center " +
                        (isActive ? activeClasses : inactiveClasses) +
                        (deepMenuOpen ? " rounded-t-none rounded-b-[2px] border-t-0" : "")
                      }
                    >
                      {`Deep_Research[${deepLevel}]`}
                    </button>
                  </div>
                );
              }

              if (mode.id === "extreme") {
                return (
                  <div key={mode.id} className="relative group inline-flex">
                    <button
                      type="button"
                      onClick={(e) => e.preventDefault()}
                      className={baseClasses + " opacity-40 cursor-not-allowed border-[#9CA3AF]/30 text-[#6B7280] bg-[#F3F4F6]/50"}
                    >
                      {mode.label}
                    </button>
                    <div className="absolute bottom-full left-1/2 w-[240px] -translate-x-1/2 mb-1.5 hidden group-hover:block p-2.5 bg-[#F7F7F5] text-[#1A3C2B] border border-[#1A3C2B]/15 text-[10px] font-mono leading-relaxed rounded-[4px] shadow-sm pointer-events-none z-[80] text-center whitespace-normal normal-case tracking-normal">
                      Feature still in progress, will be live soon
                      <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-[#1A3C2B]/20" />
                    </div>
                  </div>
                );
              }

              return (
                <button
                  key={mode.id}
                  onClick={() => setActiveMode(mode.id)}
                  disabled={disabled}
                  className={baseClasses + (isActive ? activeClasses : inactiveClasses)}
                >
                  {mode.label}
                </button>
              );
            })}
            </div>

            <div className="ml-auto flex items-center gap-2 pl-2">
              {availableProviders.length > 0 && (
                <div ref={modelDropdownRef} className="relative">
                  <button
                    type="button"
                    disabled={disabled}
                    onClick={() => setModelDropdownOpen((v) => !v)}
                    className={`inline-flex items-center gap-1 px-2 py-1 font-mono text-[11px] tracking-wider border rounded-[2px] transition-all whitespace-nowrap ${
                      (() => {
                        for (const p of availableProviders) {
                          const mv = modelSelections[`${p.key}_model` as keyof ModelSelections];
                          if (mv) return false;
                        }
                        return true;
                      })()
                        ? "border-[#1A3C2B]/20 bg-white text-[#1A3C2B]/50 hover:border-[#1A3C2B]/30"
                        : "border-[#1A3C2B]/30 bg-white text-[#1A3C2B]"
                    }`}
                    style={{
                      borderLeftWidth: "3px",
                      borderLeftColor: (() => {
                        for (const p of availableProviders) {
                          const mv = modelSelections[`${p.key}_model` as keyof ModelSelections];
                          if (mv) return p.color;
                        }
                        return undefined;
                      })(),
                    }}
                  >
                    <Cpu size={13} />
                    <span className="truncate max-w-[120px]">
                      {(() => {
                        for (const p of availableProviders) {
                          const mv = modelSelections[`${p.key}_model` as keyof ModelSelections];
                          if (mv) return MODELS[p.key].find((m) => m.value === mv)?.label || mv;
                        }
                        return "Model";
                      })()}
                    </span>
                    <ChevronDown
                      size={10}
                      className={`shrink-0 text-[#1A3C2B]/40 transition-transform ${modelDropdownOpen ? "rotate-180" : ""}`}
                    />
                  </button>
                  {modelDropdownOpen && (
                    <div className="absolute bottom-full right-0 mb-1 min-w-[200px] max-h-[280px] overflow-y-auto bg-white border border-[#1A3C2B]/12 rounded-md shadow-lg z-[70]">
                      {availableProviders.map((provider) => {
                        const cm = modelSelections[`${provider.key}_model` as keyof ModelSelections] || "";
                        return (
                          <div key={provider.key}>
                            <div className="flex items-center gap-1.5 px-3 py-1.5 border-b border-[#1A3C2B]/8">
                              <span
                                className="w-2 h-2 rounded-full shrink-0"
                                style={{ backgroundColor: provider.color }}
                              />
                              <span className="font-mono text-[10px] uppercase tracking-wider text-[#1A3C2B]/70 font-medium">
                                {provider.label}
                              </span>
                            </div>
                            {MODELS[provider.key].map((model) => (
                              <button
                                key={model.value}
                                type="button"
                                onClick={() => handleModelSelect(provider.key, model.value)}
                                className={`w-full text-left px-3 py-1.5 font-mono text-[10px] transition-colors ${
                                  cm === model.value
                                    ? "bg-[#1A3C2B]/5 text-[#1A3C2B] font-medium"
                                    : "text-[#1A3C2B]/60 hover:bg-[#f9f9f6]"
                                }`}
                              >
                                {model.label}
                              </button>
                            ))}
                          </div>
                        );
                      })}
                      {availableProviders.some(
                        (p) => modelSelections[`${p.key}_model` as keyof ModelSelections]
                      ) && (
                        <button
                          type="button"
                          onClick={() => {
                            setModelSelections({});
                            saveModelSelections({});
                            setModelDropdownOpen(false);
                          }}
                          className="w-full text-left px-3 py-1.5 font-mono text-[10px] text-red-400/70 hover:bg-[#f9f9f6] transition-colors border-t border-[#1A3C2B]/8"
                        >
                          Clear
                        </button>
                      )}
                    </div>
                  )}
                </div>
              )}
              {onResumeError && hasError && (
                <button
                  type="button"
                  onClick={() => onResumeError()}
                  disabled={disabled}
                  className="px-2 py-1 border border-red-300 text-red-500 bg-white/60 hover:bg-red-50 rounded-[2px] font-mono text-[9px] uppercase tracking-[0.15em] whitespace-nowrap disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Retry_Last_Run
                </button>
              )}
              <div className="flex items-center gap-1">
                <div className={`w-1 h-1 rounded-full shrink-0 ${disabled ? "bg-yellow-500" : "bg-green-500"}`} />
                <span className="font-mono text-[9px] opacity-30 uppercase whitespace-nowrap hidden sm:inline-block">
                  {disabled ? "Processing..." : "System_Ready"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;