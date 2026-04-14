import React, { useRef, useMemo, useEffect, useState, useCallback } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { ReportViewerProps } from './types';
import ReportToolbar from './ReportToolbar';
import './report-styles.css';

function assembleReportHtml(report: {
    table_of_contents?: string;
    body_sections?: { section_id: string; section_order: number; section_content: string }[];
}): string {
    const tocRaw = report.table_of_contents || '';
    const tocPage = tocRaw
        ? `<div class="report-page">${tocRaw}</div>`
        : '';
    const bodyHtml = (report.body_sections || [])
        .sort((a, b) => a.section_order - b.section_order)
        .map(s => {
            const safeId = String(s.section_id || "").replace(/"/g, "&quot;");
            const safeOrder = String(s.section_order ?? "");
            return `<div class="report-body-section" data-section-id="${safeId}" data-section-order="${safeOrder}">${s.section_content}</div>`;
        })
        .join('\n');

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Report</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=General+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/charts.css/dist/charts.min.css">
    <style>
        *, *::before, *::after { box-sizing: border-box; }
        html, body {
            margin: 0;
            padding: 0;
            background: #eef0f4;
            font-family: 'General Sans', 'Inter', sans-serif;
            font-size: 15px;
            line-height: 1.7;
            color: #2d3748;
            overflow-x: hidden;
            overflow-wrap: break-word;
        }
        body { padding: 1.5rem 0; }
        .report-container { width: 100%; max-width: 100%; padding: 0; overflow-x: hidden; }
        .report-page {
            width: 100%; max-width: 800px; min-height: 1056px;
            margin: 0 auto 1.5rem auto; padding: 3rem 3.5rem;
            background: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.05);
            border-radius: 2px; box-sizing: border-box; overflow: hidden;
        }
        .report-chapter { margin-bottom: 0; }
        .report-body-section {
            position: relative;
            transition: transform 160ms ease, box-shadow 160ms ease;
            outline: 2px solid transparent;
            outline-offset: 8px;
        }
        .report-body-section:hover {
            transform: translateY(-2px);
            outline-color: rgba(26, 60, 43, 0.28);
        }
        .report-body-section.is-selected {
            outline: 2px solid #FF8C69;
            outline-offset: 8px;
            animation: section-selected-shimmer 3.2s ease-in-out infinite;
        }
        .report-body-section.is-editing {
            outline: 2px solid rgba(34, 197, 94, 0.85);
            outline-offset: 8px;
            z-index: 1;
        }
        .report-body-section.is-editing::before {
            background: linear-gradient(135deg,
                rgba(34, 197, 94, 0.06) 0%,
                rgba(34, 197, 94, 0.14) 50%,
                rgba(34, 197, 94, 0.06) 100%);
            animation: none;
            opacity: 0.55;
        }
        /* Fade out section content while React stream panel overlays it */
        .report-body-section.is-streaming {
            outline: 2px solid rgba(137, 180, 250, 0.45);
            outline-offset: 8px;
        }
        .report-body-section.is-streaming > * {
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.35s ease-out;
        }
        .report-body-section.is-selected::before {
            content: '';
            position: absolute;
            inset: -12px;
            background: linear-gradient(135deg,
                rgba(255, 140, 105, 0.08) 0%,
                rgba(255, 140, 105, 0.25) 25%,
                rgba(255, 140, 105, 0.35) 50%,
                rgba(255, 140, 105, 0.25) 75%,
                rgba(255, 140, 105, 0.08) 100%);
            background-size: 200% 200%;
            background-position: 0% 50%;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            animation: section-shine-sweep 3.5s ease-in-out infinite alternate;
            pointer-events: none;
            border-radius: 4px;
        }
        @keyframes section-selected-shimmer {
            0%, 100% { box-shadow: 0 0 0 0 rgba(255, 140, 105, 0.2), 0 0 20px 0 rgba(255, 140, 105, 0.05); }
            50% { box-shadow: 0 0 0 4px rgba(255, 140, 105, 0.08), 0 0 30px 8px rgba(255, 140, 105, 0.12); }
        }
        @keyframes section-shine-sweep {
            0% { background-position: 0% 50%; opacity: 0.9; }
            100% { background-position: 100% 50%; opacity: 1; }
        }
        img, svg, video, iframe, canvas { max-width: 100% !important; height: auto; }
        pre, code { white-space: pre-wrap !important; word-break: break-all; }
        pre { overflow-x: auto; max-width: 100%; }
        table { table-layout: fixed; width: 100%; border-collapse: collapse; }
        td, th { word-wrap: break-word; overflow-wrap: break-word; }
        a { color: #2c5282; text-decoration: none; }
        a:hover { text-decoration: underline; }
        @media print {
            html, body { background: white; }
            .report-page { box-shadow: none; margin: 0; border-radius: 0; page-break-after: always; }
            .report-page:last-child { page-break-after: auto; }
        }
    </style>
</head>
<body>
<div class="report-container">
${tocPage}
${bodyHtml}
</div>
<script>
    var resizeTimer = null;
    function notifyHeight() {
        if (resizeTimer) clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            resizeTimer = null;
            var h = document.documentElement.scrollHeight;
            window.parent.postMessage({ type: 'report-iframe-resize', height: h }, '*');
        }, 400);
    }
    if (window.ResizeObserver) {
        try {
            var ro = new ResizeObserver(function() {
                if (typeof requestIdleCallback === 'function') {
                    requestIdleCallback(notifyHeight, { timeout: 600 });
                } else {
                    notifyHeight();
                }
            });
            ro.observe(document.body);
        } catch (e) {}
    }
    window.addEventListener('load', function() {
        var h = document.documentElement.scrollHeight;
        window.parent.postMessage({ type: 'report-iframe-resize', height: h }, '*');
    });
    document.addEventListener('DOMContentLoaded', function() {
        function clearSelected() {
            document.querySelectorAll('.report-body-section.is-selected').forEach(function(el) {
                el.classList.remove('is-selected');
            });
        }
        window.addEventListener('message', function(e) {
            if (e.data && e.data.type === 'report-section-deselect') clearSelected();
        });
        document.addEventListener('dblclick', function(e) {
            var el = e.target && e.target.closest ? e.target.closest('.report-body-section') : null;
            if (!el) return;
            var anchor = e.target.closest('a');
            if (anchor && anchor.href) return;

            var sectionId = el.getAttribute('data-section-id') || '';
            var sectionOrderRaw = el.getAttribute('data-section-order') || '';
            var sectionOrder = sectionOrderRaw ? parseInt(sectionOrderRaw, 10) : null;
            var h2 = el.querySelector && el.querySelector('h2') ? el.querySelector('h2') : null;
            var chapterHeading = h2 ? (h2.textContent || '').trim() : '';
            var rect = el.getBoundingClientRect();

            clearSelected();
            el.classList.add('is-selected');

            window.parent.postMessage({
                type: 'report-section-select',
                section_id: sectionId,
                section_order: sectionOrder,
                chapter_heading: chapterHeading,
                section_rect: { top: rect.top, left: rect.left, width: rect.width, height: rect.height }
            }, '*');
        });
        notifyHeight();
    });
    function findReportSectionById(sid) {
        var nodes = document.querySelectorAll('.report-body-section');
        for (var i = 0; i < nodes.length; i++) {
            if ((nodes[i].getAttribute('data-section-id') || '') === sid) return nodes[i];
        }
        return null;
    }
    window.addEventListener('message', function(e) {
        if (e.data && e.data.type === 'report-section-editor-stream') {
            var sid = e.data.section_id || '';
            document.querySelectorAll('.report-body-section.is-streaming').forEach(function(el) {
                el.classList.remove('is-streaming');
            });
            var host = sid ? findReportSectionById(sid) : null;
            if (host) {
                document.querySelectorAll('.report-body-section.is-selected').forEach(function(el) {
                    el.classList.remove('is-selected');
                });
                host.classList.add('is-streaming');
            }
            notifyHeight();
        }
        if (e.data && e.data.type === 'report-section-editor-clear') {
            document.querySelectorAll('.report-body-section.is-streaming').forEach(function(el) {
                el.classList.remove('is-streaming');
            });
            notifyHeight();
        }
    });
    document.addEventListener('click', function(e) {
        var anchor = e.target.closest('a');
        if (anchor && anchor.href) {
            e.preventDefault();
            window.open(anchor.href, '_blank', 'noopener,noreferrer');
        }
    });
</script>
</body>
</html>`;
}

const ReportViewer: React.FC<ReportViewerProps> = ({ content, reports = [], className = '', onEditSection, sectionEditProgress = null }) => {
    const iframeRef = useRef<HTMLIFrameElement>(null);
    const prevEditSectionRef = useRef<string | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const activeReportRef = useRef<{ body_sections?: Array<{ section_id: string; section_order: number; section_content: string }> } | undefined>(undefined);
    const [activeIndex, setActiveIndex] = React.useState<number>(Math.max(0, reports.length - 1));
    const [iframeHeight, setIframeHeight] = useState<number>(800);
    const [selectedSection, setSelectedSection] = useState<{
        section_id: string;
        section_order?: number | null;
        chapter_heading?: string;
        old_html: string;
        section_rect?: { top: number; left: number; width: number; height: number };
    } | null>(null);
    const [editPanelTop, setEditPanelTop] = useState<number | null>(null);
    const [editFeedback, setEditFeedback] = useState<string>("");
    const [editMode, setEditMode] = useState<"visual" | "research">("visual");
    const [streamSectionRect, setStreamSectionRect] = useState<{
        top: number; left: number; width: number; height: number;
    } | null>(null);

    React.useEffect(() => {
        if (reports.length > 0) {
            setActiveIndex(reports.length - 1);
        }
    }, [reports.length]);

    const activeReport = reports[activeIndex];
    activeReportRef.current = activeReport;

    const handleIframeMessage = useCallback((event: MessageEvent) => {
        if (event.data?.type === 'report-iframe-resize' && typeof event.data.height === 'number') {
            setIframeHeight(event.data.height + 32);
        }
        if (event.data?.type === 'report-section-select' && event.data.section_id) {
            const sectionId = String(event.data.section_id || "");
            const sectionOrder = (typeof event.data.section_order === "number" || event.data.section_order === null)
                ? event.data.section_order
                : undefined;
            const chapterHeading = String(event.data.chapter_heading || "");
            const sectionRect = event.data.section_rect;

            const report = activeReportRef.current;
            const sec = report?.body_sections?.find((s: { section_id: string; section_order: number }) => s.section_id === sectionId) ||
                (sectionOrder !== undefined ? report?.body_sections?.find((s: { section_order: number }) => s.section_order === sectionOrder) : undefined);
            if (sec) {
                setSelectedSection({
                    section_id: sec.section_id,
                    section_order: sec.section_order,
                    chapter_heading: chapterHeading,
                    old_html: sec.section_content,
                    section_rect: sectionRect,
                });
                setEditFeedback("");
                setEditMode("visual");

                if (sectionRect && iframeRef.current && containerRef.current) {
                    const iframeRect = iframeRef.current.getBoundingClientRect();
                    const containerRect = containerRef.current.getBoundingClientRect();
                    const top = (sectionRect.top + iframeRect.top) - containerRect.top;
                    setEditPanelTop(Math.max(16, top - 8));
                } else {
                    setEditPanelTop(16);
                }
            }
        }
    }, []);

    useEffect(() => {
        window.addEventListener('message', handleIframeMessage);
        return () => window.removeEventListener('message', handleIframeMessage);
    }, [handleIframeMessage]);

    const assembledHtml = useMemo(() => {
        if (!activeReport) return '';
        return assembleReportHtml(activeReport);
    }, [activeReport]);

    const syncEditorStreamToIframe = useCallback(() => {
        const w = iframeRef.current?.contentWindow;
        if (!w || !sectionEditProgress) return;
        w.postMessage(
            {
                type: 'report-section-editor-stream',
                section_id: sectionEditProgress.section_id,
                percentage: sectionEditProgress.percentage,
                current_step: sectionEditProgress.current_step,
                chapter_heading: sectionEditProgress.chapter_heading || '',
                run_id: sectionEditProgress.run_id || '',
            },
            '*'
        );
    }, [sectionEditProgress]);

    useEffect(() => {
        if (sectionEditProgress) {
            prevEditSectionRef.current = sectionEditProgress.section_id;
            syncEditorStreamToIframe();
            return;
        }
        const hadPending = prevEditSectionRef.current;
        prevEditSectionRef.current = null;
        setStreamSectionRect(null);
        if (!hadPending) return;
        const w = iframeRef.current?.contentWindow;
        w?.postMessage({ type: 'report-section-editor-clear' }, '*');
        w?.postMessage({ type: 'report-section-deselect' }, '*');
    }, [sectionEditProgress, assembledHtml, syncEditorStreamToIframe]);

    const handlePrint = () => {
        window.print();
    };

    const clearSectionSelection = useCallback(() => {
        setSelectedSection(null);
        iframeRef.current?.contentWindow?.postMessage({ type: 'report-section-deselect' }, '*');
    }, []);

    const fullContent = content || assembledHtml;

    /** Code shown in the stream panel — last 60 lines of HTML so the panel stays filled */
    const streamCode = useMemo(() => {
        if (!sectionEditProgress) return '';
        const step = (sectionEditProgress.current_step || '').trim();
        const ch = sectionEditProgress.chapter_heading || 'chapter';
        if (!step || step.length <= 180) {
            return `<!-- ${ch} -->\n<!-- → ${step || 'connecting…'} -->`;
        }
        const lines = step.split('\n');
        return lines.slice(-60).join('\n');
    }, [sectionEditProgress]);

    const streamStartLine = useMemo(() => {
        if (!sectionEditProgress) return 1;
        const step = (sectionEditProgress.current_step || '').trim();
        if (step.length <= 180) return 1;
        const totalLines = step.split('\n').length;
        return Math.max(1, totalLines - 59);
    }, [sectionEditProgress]);

    return (
        <div className={`report-viewer w-full max-w-4xl mx-auto ${className}`}>
            <ReportToolbar content={fullContent} onPrint={handlePrint} report={activeReport} />

            <div ref={containerRef} className="report-print-container bg-white dark:bg-background rounded-md border border-hairline shadow-[0_8px_30px_rgb(0,0,0,0.06)] relative my-4 overflow-hidden">
                {reports.length > 1 && (
                    <div className="flex items-center justify-between px-6 pt-6 pb-4 border-b border-border overflow-hidden">
                        <button
                            onClick={() => setActiveIndex(Math.max(0, activeIndex - 1))}
                            disabled={activeIndex === 0}
                            className="bg-secondary/50 p-2 rounded-full hover:bg-secondary disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                        >
                            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" /></svg>
                        </button>
                        <div className="flex flex-col items-center max-w-[80%]">
                            <span className="text-xs text-brand font-medium uppercase tracking-widest mb-1">
                                Report {activeIndex + 1} of {reports.length}
                            </span>
                            <h3 className="text-sm font-semibold truncate text-foreground/80">
                                {activeReport?.query || "Research Topic"}
                            </h3>
                        </div>
                        <button
                            onClick={() => setActiveIndex(Math.min(reports.length - 1, activeIndex + 1))}
                            disabled={activeIndex === reports.length - 1}
                            className="bg-secondary/50 p-2 rounded-full hover:bg-secondary disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                        >
                            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" /></svg>
                        </button>
                    </div>
                )}

                {activeReport ? (
                    <iframe
                        key={`${activeReport.run_id}-${assembledHtml.length}`}
                        ref={iframeRef}
                        srcDoc={assembledHtml}
                        title="Research Report"
                        onLoad={syncEditorStreamToIframe}
                        style={{
                            width: '100%',
                            height: `${iframeHeight}px`,
                            border: 'none',
                            display: 'block',
                            background: '#eef0f4',
                        }}
                        sandbox="allow-scripts allow-popups allow-popups-to-escape-sandbox"
                    />
                ) : content ? (
                    <div className="p-6 md:p-10 lg:p-12" dangerouslySetInnerHTML={{ __html: content }} />
                ) : (
                    <div className="p-6 md:p-10 lg:p-12 text-center text-foreground/50">
                        <p>No report content available.</p>
                    </div>
                )}

                {sectionEditProgress && (
                    <div
                        className="absolute z-20"
                        style={{
                            top: streamSectionRect?.top ?? (editPanelTop ?? 0),
                            left: streamSectionRect?.left ?? 0,
                            width: streamSectionRect?.width ?? '100%',
                            height: Math.max(streamSectionRect?.height ?? 0, 520),
                            background: '#1e1e2e',
                            boxShadow: '0 0 0 1px rgba(139,167,234,0.2), 0 8px 48px rgba(0,0,0,0.4)',
                            display: 'flex',
                            flexDirection: 'column',
                        }}
                    >
                        {/* Title bar */}
                        <div
                            style={{
                                flexShrink: 0,
                                display: 'flex',
                                alignItems: 'center',
                                gap: 10,
                                padding: '9px 14px',
                                background: '#181825',
                                borderBottom: '1px solid rgba(255,255,255,0.05)',
                            }}
                        >
                            <div style={{ display: 'flex', gap: 6 }}>
                                <span style={{ width: 11, height: 11, borderRadius: '50%', background: '#f38ba8', display: 'block' }} />
                                <span style={{ width: 11, height: 11, borderRadius: '50%', background: '#f9e2af', display: 'block' }} />
                                <span style={{ width: 11, height: 11, borderRadius: '50%', background: '#a6e3a1', display: 'block' }} />
                            </div>
                            <span style={{ flex: 1, textAlign: 'center', fontSize: 11, color: '#6c7086', fontFamily: 'monospace' }}>
                                chapter_update.wort
                            </span>
                            <span style={{ fontSize: 11, fontWeight: 600, color: '#89b4fa', fontVariantNumeric: 'tabular-nums' }}>
                                {sectionEditProgress.percentage}%
                            </span>
                        </div>

                        {/* Code body — flex-1 so it fills all remaining height */}
                        <div style={{ flex: 1, minHeight: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                            <SyntaxHighlighter
                                language="html"
                                style={vscDarkPlus}
                                showLineNumbers
                                startingLineNumber={streamStartLine}
                                customStyle={{
                                    margin: 0,
                                    padding: '14px 0',
                                    background: '#1e1e2e',
                                    fontSize: '12.5px',
                                    lineHeight: '1.65',
                                    flex: 1,
                                    minHeight: 0,
                                    overflow: 'hidden',
                                    borderRadius: 0,
                                    height: '100%',
                                }}
                                lineNumberStyle={{ color: '#45475a', minWidth: '3em', paddingRight: '1.2em' }}
                                wrapLongLines
                            >
                                {streamCode}
                            </SyntaxHighlighter>
                        </div>

                        {/* Progress bar pinned to bottom */}
                        <div style={{ flexShrink: 0, height: 4, background: '#313244' }}>
                            <div style={{
                                height: '100%',
                                width: `${sectionEditProgress.percentage}%`,
                                background: 'linear-gradient(90deg, #89b4fa 0%, #cba6f7 100%)',
                                transition: 'width 0.7s cubic-bezier(0.4,0,0.2,1)',
                            }} />
                        </div>
                    </div>
                )}

                {selectedSection && !sectionEditProgress && (
                    <div
                        className="absolute z-10 min-w-[320px] font-mono overflow-hidden"
                        style={{
                            top: (editPanelTop ?? 96) + 8,
                            right: 4,
                            backgroundColor: '#F2F2F0',
                            borderBottomLeftRadius: 8,
                        }}
                    >
                        <div className="px-3 py-2 border-b border-[#3A3A38]/20 flex items-center justify-between">
                            <div className="min-w-0">
                                <div className="text-[11px] uppercase tracking-[0.2em] text-[#3A3A38]/50">Edit_Section</div>
                                <div className="text-[13px] font-medium truncate text-[#1A3C2B]">{selectedSection.chapter_heading || `Section ${selectedSection.section_order}`}</div>
                            </div>
                            <button
                                onClick={clearSectionSelection}
                                className="px-1.5 py-0.5 text-[11px] uppercase tracking-[0.15em] text-[#3A3A38]/60 hover:text-[#3A3A38] hover:bg-[#9EFFBF]/30"
                            >
                                Close
                            </button>
                        </div>
                        <div className="p-2 space-y-2">
                            <div className="flex items-center gap-1.5 flex-wrap">
                                <button
                                    onClick={() => setEditMode("visual")}
                                    className={`px-2.5 py-1 text-[12px] uppercase tracking-[0.15em] border-0 whitespace-nowrap ${editMode === "visual" ? "bg-[#1A3C2B] text-white" : "border border-[#3A3A38]/20 text-[#3A3A38]/70 hover:bg-[#9EFFBF]/20"}`}
                                >
                                    Visual_Edit_Only
                                </button>
                                <button
                                    onClick={() => setEditMode("research")}
                                    className={`px-2.5 py-1 text-[12px] uppercase tracking-[0.15em] border-0 whitespace-nowrap ${editMode === "research" ? "bg-[#1A3C2B] text-white" : "border border-[#3A3A38]/20 text-[#3A3A38]/70 hover:bg-[#9EFFBF]/20"}`}
                                >
                                    Edit_With_More_Research
                                </button>
                            </div>
                            <textarea
                                value={editFeedback}
                                onChange={(e) => setEditFeedback(e.target.value)}
                                placeholder="This will change the whole chapter. If you want to keep existing content, mention it in your feedback. Describe what to change/add."
                                className="w-full min-h-[64px] resize-y border border-[#3A3A38]/15 px-2.5 py-1.5 text-[12px] outline-none focus:border-[#1A3C2B]/40 placeholder:text-[#3A3A38]/45 bg-[#FAFAFA]"
                            />
                            <div className="flex items-center justify-end gap-1 pt-0.5">
                                <button
                                    onClick={clearSectionSelection}
                                    className="px-2.5 py-1.5 text-[12px] uppercase tracking-[0.15em] border border-[#3A3A38]/15 text-[#3A3A38]/70 hover:bg-[#3A3A38]/5"
                                >
                                    Cancel
                                </button>
                                <button
                                    disabled={!editFeedback.trim() || !onEditSection}
                                    onClick={() => {
                                        if (!onEditSection) return;
                                        /* Always capture geometry — section_rect if available, full iframe width as fallback */
                                        if (iframeRef.current && containerRef.current) {
                                            const iframeRect = iframeRef.current.getBoundingClientRect();
                                            const containerRect = containerRef.current.getBoundingClientRect();
                                            const sr = selectedSection.section_rect;
                                            setStreamSectionRect(sr ? {
                                                top: sr.top + iframeRect.top - containerRect.top,
                                                left: sr.left + iframeRect.left - containerRect.left,
                                                width: sr.width,
                                                height: sr.height,
                                            } : {
                                                top: iframeRect.top - containerRect.top,
                                                left: iframeRect.left - containerRect.left,
                                                width: iframeRef.current.offsetWidth,
                                                height: 520,
                                            });
                                        }
                                        iframeRef.current?.contentWindow?.postMessage({ type: 'report-section-deselect' }, '*');
                                        onEditSection({
                                            section_id: selectedSection.section_id,
                                            section_order: selectedSection.section_order,
                                            chapter_heading: selectedSection.chapter_heading,
                                            old_html: selectedSection.old_html,
                                            feedback: editFeedback.trim(),
                                            edit_mode: editMode,
                                            run_id: activeReport?.run_id,
                                        });
                                        setSelectedSection(null);
                                    }}
                                    className="px-2.5 py-1.5 text-[12px] uppercase tracking-[0.15em] bg-[#1A3C2B] text-white hover:bg-[#122A1E] disabled:opacity-40 disabled:cursor-not-allowed"
                                >
                                    Submit_Edit
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default React.memo(ReportViewer);
