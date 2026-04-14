import React from 'react';
import { ReportSectionProps } from './types';
import { cn } from "@/lib/utils"; 

// Assuming shadcn utils exist, or we can use clsx/tailwind-merge directly if not. 
// Note: User's package.json has 'clsx' and 'tailwind-merge'. 
// I'll assume @/lib/utils exists as is standard in shadcn projects. If not, I'll fallback to simple string concatenation or define cn locally.
// Let's check if @/lib/utils exists first? safely, I'll allow it to fail if it doesn't and fix it. 
// Actually, I can just use className prop directly for now to be safe.

const ReportSection: React.FC<ReportSectionProps> = ({
    children,
    className,
    id
}) => {
    return (
        <section
            id={id}
            className={`report-section group relative border-l-2 border-transparent hover:border-sidebar-accent transition-colors pl-4 -ml-4 ${className || ''}`}
        >
            {/* Future: Add hover actions/buttons here for "Edit Section" */}
            <div className={`
                absolute right-0 top-0 opacity-0 group-hover:opacity-100 transition-opacity
                translate-x-full pr-2
            `}>
                {/* Placeholder for future edit button */}
            </div>

            {children}
        </section>
    );
};

export default ReportSection;