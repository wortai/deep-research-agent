import React, { useState } from 'react';
import { getApiOrigin } from '@/apiConfig';
import { Printer, Copy, Check, Download, Loader2 } from "lucide-react";
import { ReportToolbarProps } from './types';

const ReportToolbar: React.FC<ReportToolbarProps> = ({ content, onPrint, report }) => {
    const [copied, setCopied] = useState(false);
    const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(content);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error("Failed to copy:", err);
        }
    };

    const handleDownloadHtml = () => {
        const blob = new Blob([content], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = report?.query ? `${report.query.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_report.html` : 'research_report.html';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const handleDownloadPdf = async () => {
        if (!report) {
            alert("Report data is not available for PDF generation yet.");
            return;
        }

        try {
            setIsDownloadingPdf(true);
            const response = await fetch(`${getApiOrigin()}/publish/pdf`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(report),
            });

            if (!response.ok) {
                throw new Error('Failed to generate PDF on the server');
            }

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = report.query ? `${report.query.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_report.pdf` : 'research_report.pdf';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (err) {
            console.error("Failed to download PDF:", err);
            alert("There was an error generating the PDF. Please try using the Print option.");
            onPrint(); // Fallback to window.print() if server generation fails
        } finally {
            setIsDownloadingPdf(false);
        }
    };

    return (
        <div className="report-toolbar flex items-center gap-2 mb-4 p-2 bg-secondary/30 rounded-md border border-hairline w-fit">
            <button
                onClick={handleDownloadPdf}
                disabled={isDownloadingPdf}
                className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-primary/80 hover:text-primary hover:bg-background rounded-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title="Download High-Quality PDF"
            >
                {isDownloadingPdf ? <Loader2 size={14} className="animate-spin" /> : <Printer size={14} />}
                <span>{isDownloadingPdf ? "Generating PDF..." : "Download PDF"}</span>
            </button>
            <div className="w-[1px] h-4 bg-primary/20" />
            <button
                onClick={handleDownloadHtml}
                className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-primary/80 hover:text-primary hover:bg-background rounded-sm transition-colors"
                title="Download HTML"
            >
                <Download size={14} />
                <span>Download HTML</span>
            </button>
            <div className="w-[1px] h-4 bg-primary/20" />
            <button
                onClick={handleCopy}
                className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-primary/80 hover:text-primary hover:bg-background rounded-sm transition-colors"
                title="Copy HTML"
            >
                {copied ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
                <span>{copied ? "Copied" : "Copy"}</span>
            </button>
        </div>
    );
};

export default ReportToolbar;