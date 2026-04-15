import { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { useWebSocket } from './useWebSocket';
import { useQueryClient } from '@tanstack/react-query';
import type { SectionEditProgressData } from '../components/Report_Viewer/types';

export type Message = {
    id: string;
    role: "user" | "assistant" | "system";
    content: string;
    type?: "text" | "plan" | "report" | "thinking";
    metadata?: any;
};

export type AgentLog = {
    id: string;
    type: "log" | "progress" | "phase";
    message: string;
    timestamp: string;
    data?: any;
};

export type AgentProgressData = {
    query_num: number;
    query: string;
    percentage: number;
    phase: string;
    current_step: string;
    status?: string;
    metadata?: any;
};

export type WriterProgressData = {
    percentage: number;
    current_step: string;
    phase: string;
    metadata?: any;
};

export type { SectionEditProgressData };

export const JWT_KEY = "wort_jwt";

export const useChat = (threadId: string, userId: string) => {
    const queryClient = useQueryClient();
    const [messages, setMessages] = useState<Message[]>([]);
    const [logs, setLogs] = useState<AgentLog[]>([]);
    const [agentProgress, setAgentProgress] = useState<Record<number, AgentProgressData>>({});
    const [writerProgress, setWriterProgress] = useState<WriterProgressData | null>(null);
    const [sectionEditProgress, setSectionEditProgress] = useState<SectionEditProgressData | null>(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [isRestoringSession, setIsRestoringSession] = useState(true);
    const [currentResponseId, setCurrentResponseId] = useState<string | null>(null);
    const [isInterrupted, setIsInterrupted] = useState(false);
    const [interruptData, setInterruptData] = useState<any>(null);
    const [isClarifying, setIsClarifying] = useState(false);
    const [clarificationData, setClarificationData] = useState<{ questions: string[], loop_number: number } | null>(null);
    const [skillSelection, setSkillSelection] = useState<{ skills: string[], skill_labels: string[], reasoning: string } | null>(null);
    const [agentError, setAgentError] = useState<any>(null);

    const lastSeenId = useRef<string>("0");

    const hostname = window.location.hostname;
    const jwt = localStorage.getItem(JWT_KEY) || "";
    const authHeaders = jwt ? { Authorization: `Bearer ${jwt}` } : {};
    const wsUrl = `ws://${hostname}:8000/ws/chat/${threadId}?token=${jwt}`;

    const historyLoaded = useRef(false);

    useEffect(() => {
        setMessages([]);
        setLogs([]);
        setAgentProgress({});
        setWriterProgress(null);
        setSectionEditProgress(null);
        setIsProcessing(false);
        setIsRestoringSession(true);
        setCurrentResponseId(null);
        setIsInterrupted(false);
        setInterruptData(null);
        setIsClarifying(false);
        setClarificationData(null);
        setSkillSelection(null);
        setAgentError(null);
        lastSeenId.current = "0";
        historyLoaded.current = false;

        const fetchHistory = async () => {
            try {
                const res = await fetch(`http://${hostname}:8000/sessions/${threadId}/events`, {
                    headers: authHeaders
                });
                if (res.ok) {
                    const data = await res.json();
                    if (data.events && data.events.length > 0) {
                        const historyMessages: Message[] = [];
                        let restoredClarification: { questions: string[], loop_number: number } | null = null;
                        let restoredInterrupt: any = null;
                        let pendingInterrupt = false;

                        const restoredAgentProgress: Record<number, AgentProgressData> = {};
                        let restoredWriterProgress: WriterProgressData | null = null;

                        data.events.forEach((ev: any) => {
                            switch (ev.event_type) {
                                case "user_query":
                                    // Reset any pending interrupt when user sends a new message
                                    pendingInterrupt = false;
                                    restoredClarification = null;
                                    restoredInterrupt = null;
                                    historyMessages.push({ id: ev.event_id, role: "user", content: ev.content || "" });
                                    break;

                                case "assistant_response":
                                    pendingInterrupt = false;
                                    historyMessages.push({ id: ev.event_id, role: "assistant", content: ev.content || "" });
                                    break;

                                case "router_thinking": {
                                    const reasoning = ev.content || "";
                                    if (reasoning) {
                                        historyMessages.push({
                                            id: ev.event_id,
                                            role: "assistant",
                                            content: reasoning,
                                            type: "thinking",
                                        });
                                    }
                                    break;
                                }

                                case "agent_progress": {
                                    const meta = ev.metadata || {};
                                    const qNum = meta.query_num ?? 0;
                                    restoredAgentProgress[qNum] = {
                                        query_num: qNum,
                                        query: meta.query || ev.content || "",
                                        percentage: meta.percentage ?? 100,
                                        phase: meta.phase || "completed",
                                        current_step: meta.current_step || "Complete",
                                    };
                                    break;
                                }

                                case "writer_progress": {
                                    const meta = ev.metadata || {};
                                    restoredWriterProgress = {
                                        percentage: meta.percentage ?? 100,
                                        current_step: meta.current_step || "Complete",
                                        phase: meta.phase || "writing",
                                    };
                                    break;
                                }

                                case "clarification":
                                    // This interrupt was never resolved — restore UI state
                                    try {
                                        const parsed = typeof ev.content === "string" ? JSON.parse(ev.content) : ev.content;
                                        restoredClarification = {
                                            questions: parsed.questions || [],
                                            loop_number: parsed.loop_number || 1,
                                        };
                                        pendingInterrupt = true;
                                    } catch { /* malformed stored interrupt, skip */ }
                                    break;

                                case "clarification_answer":
                                    restoredClarification = null;
                                    pendingInterrupt = false;
                                    break;

                                case "plan_feedback":
                                    restoredInterrupt = null;
                                    pendingInterrupt = false;
                                    break;

                                case "plan_review":
                                    try {
                                        const parsed = typeof ev.content === "string" ? JSON.parse(ev.content) : ev.content;
                                        restoredInterrupt = {
                                            interrupt_type: "plan_review",
                                            plan: parsed.plan_display || "",
                                        };
                                        pendingInterrupt = true;
                                    } catch { /* malformed stored interrupt, skip */ }
                                    break;
                            }
                        });

                        // Fetch reports separately since they're stored in checkpoints
                        try {
                            const r = await fetch(`http://${hostname}:8000/sessions/${threadId}/report`, {
                                headers: authHeaders
                            });
                            if (r.ok) {
                                const reportData = await r.json();
                                if (reportData?.reports && Array.isArray(reportData.reports)) {
                                    reportData.reports.forEach((report: any, index: number) => {
                                        historyMessages.push({
                                            id: `report-${report.run_id || index}-${threadId}`,
                                            role: "assistant",
                                            content: `Report Generated: ${report.query || 'Topic'}`,
                                            type: "report",
                                            metadata: report
                                        });
                                    });
                                }
                            }
                        } catch { /* report fetch is optional */ }

                        setMessages(historyMessages);
                        historyLoaded.current = true;

                        // Restore final progress bars from persisted COMPLETED events
                        if (Object.keys(restoredAgentProgress).length > 0) {
                            setAgentProgress(restoredAgentProgress);
                        }
                        if (restoredWriterProgress) {
                            setWriterProgress(restoredWriterProgress);
                        }

                        // Re-surface any unanswered interrupt prompts
                        if (pendingInterrupt) {
                            if (restoredClarification) {
                                setIsClarifying(true);
                                setClarificationData(restoredClarification);
                            } else if (restoredInterrupt) {
                                setIsInterrupted(true);
                                setInterruptData(restoredInterrupt);
                            }
                        }
                    }
                }
            } catch (e) {
                console.error("Failed to load history", e);
            }
            historyLoaded.current = true;

            // After history load, check if thread is actively processing
            // to recover isProcessing state after page refresh
            try {
                const statusRes = await fetch(`http://${hostname}:8000/sessions/${threadId}/status`, {
                    headers: authHeaders
                });
                if (statusRes.ok) {
                    const statusData = await statusRes.json();
                    if (statusData.is_processing) {
                        setIsProcessing(true);
                    } else {
                        setIsProcessing(false);
                    }
                }
            } catch { /* status check is optional */ }

            // Session restore complete — unlock input
            setIsRestoringSession(false);
        };
        fetchHistory();
    }, [threadId, hostname]);

    /**
     * Appends streamed token to the last assistant text message.
     * If last message is not assistant text (e.g. it's a 'thinking' message),
     * starts a new assistant text message.
     * No dependency on isProcessing — uses functional state update with prev array.
     */
    const handleToken = useCallback((token: string) => {
        setMessages((prev) => {
            const lastMsg = prev[prev.length - 1];
            if (lastMsg && lastMsg.role === "assistant" && lastMsg.type === "text") {
                return [
                    ...prev.slice(0, -1),
                    { ...lastMsg, content: lastMsg.content + token }
                ];
            }
            return [
                ...prev,
                { id: uuidv4(), role: "assistant" as const, content: token, type: "text" as const }
            ];
        });
    }, []);

    /**
     * Routes log events: agent_progress updates the progress bars,
     * router_log inserts a 'thinking' message into the messages array
     * for chronological inline rendering, other logs go to the logs array.
     */
    const handleLogEvent = useCallback((data: any) => {
        const eventType = data.event_type;

        if (eventType === "router_log") {
            const thinkingMsg: Message = {
                id: uuidv4(),
                role: "assistant",
                content: (data.message || "").replace(/^Router Logic: /, ""),
                type: "thinking",
            };
            setMessages(prev => [...prev, thinkingMsg]);
        } else {
            const displayMessage = data.message || `Event: ${eventType}`;
            const logEntry: AgentLog = {
                id: uuidv4(),
                type: "log",
                message: displayMessage,
                timestamp: new Date().toISOString(),
                data: data
            };
            setLogs(prev => [...prev, logEntry]);
        }
    }, []);

    /** Adds a plan message built from the plan steps array. */
    const handlePlan = useCallback((plan: any[]) => {
        const planContent = "Tasks:\n\n" + plan.map((p: any) => `Agent_${Math.floor(p.query_num / 10)}_${p.query_num % 10} Subagent's task: ${p.query}`).join("\n\n");
        const planMsg: Message = {
            id: uuidv4(),
            role: "assistant",
            content: planContent,
            type: "plan",
            metadata: { steps: plan }
        };
        setMessages(prev => [...prev, planMsg]);
    }, []);

    /** Adds a report message when structured report data is received. */
    const handleReport = useCallback((reportWrapper: any) => {
        // The backend writer_node now returns {"reports": [reportData]}
        const reports = reportWrapper.reports || [reportWrapper];

        let shouldUpdate = false;
        const newMessages: Message[] = [];

        reports.forEach((reportData: any) => {
            if (reportData.body_sections || reportData.md_path) {
                const runId = String(reportData.run_id || "");
                shouldUpdate = true;
                newMessages.push({
                    id: uuidv4(),
                    role: "assistant",
                    content: `Report Generated: ${reportData.query || 'Research'}`,
                    type: "report",
                    metadata: reportData
                });
            }
        });

        if (shouldUpdate) {
            setMessages(prev => {
                // Deduplicate: replace existing report with same run_id, otherwise append
                const result = [...prev];
                for (const newMsg of newMessages) {
                    const newRunId = String(newMsg.metadata?.run_id || "");
                    const existingIdx = newRunId ? result.findIndex(m => m.type === "report" && String(m.metadata?.run_id || "") === newRunId) : -1;
                    if (existingIdx >= 0) {
                        result[existingIdx] = { ...newMsg, id: result[existingIdx].id };
                    } else {
                        result.push(newMsg);
                    }
                }
                return result;
            });
        }
    }, []);

    /** Updates writer synthesis progress from WRITER_PROGRESS custom events. */
    const handleWriterProgress = useCallback((payload: any) => {
        setWriterProgress(prev => ({
            ...prev,
            ...payload
        }));
    }, []);

    /** Handles the final compiled response from the backend */
    const handleFinalResponse = useCallback((content: string) => {
        setMessages(prev => {
            const lastMsg = prev[prev.length - 1];
            // Tokens from handleToken already built this message — final_response
            // would create a duplicate. Return unchanged so nothing is added.
            if (lastMsg && lastMsg.role === "assistant" && lastMsg.type === "text") {
                return prev;
            }
            // No streaming buffer exists: update a typeless assistant message or append new.
            if (lastMsg && lastMsg.role === "assistant" && !lastMsg.type) {
                if (lastMsg.content === content) return prev;
                const updated = [...prev];
                updated[updated.length - 1] = { ...lastMsg, content: content };
                return updated;
            }
            return [...prev, { id: uuidv4(), role: "assistant", content: content }];
        });
    }, []);

    /**
     * Central WebSocket message dispatcher.
     * All handlers are stable useCallback refs — no stale closure issues.
     */
    const handleMessage = useCallback((event: MessageEvent) => {
        try {
            const data = JSON.parse(event.data);

            if (data._redis_id) {
                lastSeenId.current = data._redis_id;
            }

            switch (data.type) {
                case "agent_progress": {
                    const payload = data.data || {};
                    setAgentProgress(prev => ({
                        ...prev,
                        [payload.query_num]: {
                            ...prev[payload.query_num],
                            ...payload
                        }
                    }));
                    break;
                }
                case "log":
                    handleLogEvent(data.data);
                    break;
                case "writer_progress": {
                    const wp = data.data || {};
                    const meta = wp.metadata || {};
                    if (meta.mode === "edit") {
                        setWriterProgress(null);
                        setSectionEditProgress((prev) => {
                            const step = (wp.current_step as string) || "";
                            const isDelta = meta.stream_delta === true;
                            const mergedStep = isDelta
                                ? (prev?.current_step || "") + step
                                : step || prev?.current_step || "";
                            return {
                                section_id: String(meta.section_id || prev?.section_id || ""),
                                run_id: meta.run_id != null ? String(meta.run_id) : prev?.run_id,
                                chapter_heading: meta.chapter_heading ?? prev?.chapter_heading,
                                section_order: prev?.section_order,
                                percentage:
                                    typeof wp.percentage === "number" ? wp.percentage : prev?.percentage ?? 0,
                                current_step: mergedStep,
                                phase: wp.phase || "editing",
                                metadata: meta,
                            };
                        });
                        if (
                            wp.percentage === 100 &&
                            meta.status === "error"
                        ) {
                            window.setTimeout(() => setSectionEditProgress(null), 8000);
                        }
                    } else {
                        setSectionEditProgress(null);
                        handleWriterProgress(wp);
                    }
                    break;
                }
                case "token":
                    handleToken(data.content);
                    break;
                case "plan":
                    handlePlan(data.data);
                    break;
                case "report":
                    handleReport(data.data);
                    break;
                case "report_section_update": {
                    const upd = data.data || {};
                    const sectionId = String(upd.section_id || "");
                    const rawOrder = upd.section_order;
                    const sectionOrder = (typeof rawOrder === "number") ? rawOrder
                        : (typeof rawOrder === "string" && rawOrder !== "" && Number.isFinite(Number(rawOrder))) ? parseInt(rawOrder, 10)
                        : null;
                    const newHtml = String(upd.new_section_content || "");
                    const runId = String(upd.run_id || "");
                    if (!sectionId || !newHtml) {
                        console.warn("[report_section_update] Missing section_id or new_section_content", upd);
                        break;
                    }

                    setMessages(prev => {
                        let patched = false;

                        const result = prev.map(m => {
                            if (m.type !== "report" || !m.metadata) return m;
                            const report = m.metadata as any;
                            const sections = report.body_sections;
                            if (!Array.isArray(sections)) return m;

                            let touched = false;
                            const nextSections = sections.map((s: any) => {
                                const idMatch = s.section_id && String(s.section_id) === sectionId;
                                const orderMatch = sectionOrder !== null && typeof s.section_order === "number" && s.section_order === sectionOrder;

                                if (runId && report.run_id && String(report.run_id) === runId) {
                                    if (idMatch || orderMatch) {
                                        touched = true;
                                        return { ...s, section_content: newHtml };
                                    }
                                } else if (idMatch) {
                                    touched = true;
                                    return { ...s, section_content: newHtml };
                                }
                                return s;
                            });

                            if (!touched) return m;
                            patched = true;
                            return { ...m, metadata: { ...report, body_sections: nextSections } };
                        });

                        if (!patched) {
                            console.error(
                                "[report_section_update] No section matched! section_id=%s section_order=%s run_id=%s",
                                sectionId, sectionOrder, runId
                            );
                        }
                        return result;
                    });
                    setSectionEditProgress(null);
                    break;
                }
                case "final_response":
                    handleFinalResponse(data.data);
                    break;
                case "status":
                    if (data.status === "processing") setIsProcessing(true);
                    break;
                case "done":
                    setIsProcessing(false);
                    setCurrentResponseId(null);
                    setLogs([]);
                    setSkillSelection(null);
                    setSectionEditProgress(null);
                    setMessages(prev => prev.map(m =>
                        m.type === "text" ? { ...m, type: undefined } : m
                    ));
                    // Force the sidebar to fetch the latest "completed" status
                    queryClient.invalidateQueries({ queryKey: ['sessions'] });
                    break;
                case "error":
                    console.error("Agent Error:", data.message);
                    setIsProcessing(false);
                    setSectionEditProgress(null);
                    setAgentError({ message: data.message });
                    queryClient.invalidateQueries({ queryKey: ['sessions'] });
                    break;
                case "llm_error":
                    console.error("LLM Error Details:", data.error_data);
                    setIsProcessing(false);
                    setSectionEditProgress(null);
                    setAgentError(data.error_data);
                    queryClient.invalidateQueries({ queryKey: ['sessions'] });
                    break;
                case "interrupt":
                    if (data.interrupt_type === "clarification") {
                        setIsClarifying(true);
                        setClarificationData({
                            questions: data.questions || [],
                            loop_number: data.loop_number || 1,
                        });
                        setIsProcessing(false);
                    } else {
                        setIsInterrupted(true);
                        setInterruptData(data);
                        setIsProcessing(false);
                    }
                    break;
                case "clarification_progress": {
                    const clarMsg: Message = {
                        id: uuidv4(),
                        role: "assistant",
                        content: data.data?.message || "Understanding your research intent...",
                        type: "thinking",
                    };
                    setMessages(prev => [...prev, clarMsg]);
                    break;
                }
                case "skill_selection": {
                    const skillData = data.data || {};
                    setSkillSelection(skillData);
                    const skillMsg: Message = {
                        id: uuidv4(),
                        role: "assistant",
                        content: `Selected research skills: ${(skillData.skill_labels || []).join(", ")}`,
                        type: "thinking",
                    };
                    setMessages(prev => [...prev, skillMsg]);
                    break;
                }
                default:
                    console.log("Unknown event type:", data.type);
            }
        } catch (e) {
            console.error("Error parsing WebSocket message:", e);
        }
    }, [handleLogEvent, handleToken, handlePlan, handleReport, handleWriterProgress, handleFinalResponse]);

    const { sendMessage: wsSendMessage, isConnected, error: wsError } = useWebSocket({
        url: wsUrl,
        onMessage: handleMessage,
    });

    // Automatically rejoin active tracking streams seamlessly if the socket bounces
    useEffect(() => {
        if (isConnected && lastSeenId.current !== "0") {
            wsSendMessage({
                type: "join_stream",
                last_seen_id: lastSeenId.current
            });
        }
    }, [isConnected, wsSendMessage]);

    /** Sends user message via WebSocket and resets per-turn state. */
    const sendMessage = (content: string, mode: string = "websearch", apiKeys?: Record<string, string>, modelSelections?: Record<string, string>) => {
        if (isProcessing || isRestoringSession) return;
        const userMsg: Message = {
            id: uuidv4(),
            role: "user",
            content,
        };
        setMessages((prev) => [...prev, userMsg]);
        setLogs([]);
        setAgentProgress({});
        setWriterProgress(null);
        setSectionEditProgress(null);
        setAgentError(null);

        if (messages.length === 0) {
            queryClient.invalidateQueries({ queryKey: ['sessions'] });
        }

        const payload: Record<string, any> = {
            content,
            mode,
            user_id: userId
        };
        if (apiKeys && Object.keys(apiKeys).length > 0) {
            payload.api_keys = apiKeys;
        }
        if (modelSelections && Object.keys(modelSelections).length > 0) {
            payload.model_selections = modelSelections;
        }
        wsSendMessage(payload);

        setIsProcessing(true);
    };

    /** Resumes after a HITL interrupt with approval/rejection and optional feedback. */
    const resume = (approved: boolean, feedback: string = "") => {
        setIsInterrupted(false);
        setInterruptData(null);
        setIsProcessing(true);

        wsSendMessage({
            type: "resume",
            resume_data: {
                type: "plan_review",
                approved,
                feedback
            }
        });
    };

    const resumeClarification = (answers: Record<string, string>) => {
        setIsClarifying(false);
        setClarificationData(null);
        setIsProcessing(true);

        wsSendMessage({
            type: "resume",
            resume_data: {
                type: "clarification",
                answers
            }
        });
    };

    const editSection = (payload: {
        section_id: string;
        section_order?: number | null;
        chapter_heading?: string;
        old_html: string;
        feedback: string;
        edit_mode: "visual" | "research";
        run_id?: string;
    }) => {
        setIsProcessing(true);
        setWriterProgress(null);
        setSectionEditProgress({
            section_id: payload.section_id,
            run_id: payload.run_id != null ? String(payload.run_id) : undefined,
            chapter_heading: payload.chapter_heading,
            section_order: payload.section_order,
            percentage: 0,
            current_step: "Connecting to editor…",
            phase: "edit",
            metadata: { mode: "edit", status: "queued" },
        });
        wsSendMessage({
            type: "edit_section",
            edit_data: payload,
        });
    };

    /** Asks the backend to resume the graph from the last checkpoint after a runtime error. */
    const resumeFromError = () => {
        setIsProcessing(true);
        wsSendMessage({
            type: "resume_error",
        });
    };

    return {
        messages,
        logs,
        agentProgress,
        writerProgress,
        sectionEditProgress,
        sendMessage,
        isConnected,
        isProcessing,
        isRestoringSession,
        isInterrupted,
        interruptData,
        isClarifying,
        clarificationData,
        skillSelection,
        resume,
        resumeClarification,
        error: wsError,
        resumeFromError,
        agentError,
        editSection,
        allReports: useMemo(() => {
            return messages.filter(m => m.type === "report").map(m => m.metadata as import('../components/Report_Viewer/types').ReportData);
        }, [messages])
    };
};
