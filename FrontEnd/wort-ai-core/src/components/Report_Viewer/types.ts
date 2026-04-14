export interface ReportSectionData {
    section_id: string;
    section_order: number;
    section_content: string;
}

export interface ReportData {
    run_id?: string;
    query?: string;
    body_sections?: ReportSectionData[];
    table_of_contents?: string;
    design_instructions?: string;
    timestamp?: string;
}

/** Live section edit streaming from editor_node (writer_progress with metadata.mode === "edit"). */
export interface SectionEditProgressData {
    section_id: string;
    run_id?: string;
    chapter_heading?: string | null;
    section_order?: number | null;
    percentage: number;
    current_step: string;
    phase?: string;
    metadata?: Record<string, unknown>;
}

export interface ReportViewerProps {
    content?: string; // Fallback or concatenated string
    reports?: ReportData[]; // Array of structured data reports
    className?: string;
    /** Live progress from editor_node (WebSocket writer_progress with metadata.mode === "edit"). */
    sectionEditProgress?: SectionEditProgressData | null;
    onEditSection?: (payload: {
        section_id: string;
        section_order?: number | null;
        chapter_heading?: string;
        old_html: string;
        feedback: string;
        edit_mode: "visual" | "research";
        run_id?: string;  // Target report when multiple exist
    }) => void;
}

export interface ReportSectionProps {
    children: React.ReactNode;
    id?: string;
    title?: string;
    className?: string;
    // Future-proofing for editing/actions
    isEditable?: boolean;
    onEdit?: (content: string) => void;
}

export interface ReportToolbarProps {
    content: string; // For copy/download - we might need to generate this from reportData if content is missing
    onPrint: () => void;
    report?: ReportData; // Needed for PDF Generation endpoint
}