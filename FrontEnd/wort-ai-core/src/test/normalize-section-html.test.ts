/**
 * Tests for normalizeSectionHtml — validates and fixes LLM-generated
 * chapter HTML to ensure proper report-chapter > report-page structure.
 */
import { describe, it, expect } from 'vitest';

function normalizeSectionHtml(raw: string): string {
    if (!raw || !raw.trim()) return raw;
    let html = raw.trim();

    if (html.startsWith('```')) {
        html = html.replace(/^```(?:html)?\s*\n?/, '').replace(/\n?```\s*$/, '');
    }

    if (!/class=["'][^"']*report-page/.test(html)) {
        return `<div class="report-chapter"><div class="report-page">${html}</div></div>`;
    }

    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const body = doc.body;
    if (!body || !body.innerHTML.trim()) {
        return `<div class="report-chapter"><div class="report-page">${html}</div></div>`;
    }

    const chapter = body.querySelector('.report-chapter');
    const container = chapter || body;

    const children = Array.from(container.childNodes).filter(
        (n): n is Element => n.nodeType === Node.ELEMENT_NODE
    );

    if (children.length === 0) {
        return `<div class="report-chapter"><div class="report-page">${html}</div></div>`;
    }

    const pages = children.filter(el => el.classList.contains('report-page'));
    const orphans = children.filter(el => !el.classList.contains('report-page'));

    if (orphans.length === 0 && pages.length > 0) {
        return chapter
            ? chapter.outerHTML
            : `<div class="report-chapter">${pages.map(p => p.outerHTML).join('\n')}</div>`;
    }

    const result: string[] = [];
    let buf: string[] = [];

    const flush = () => {
        if (buf.length) {
            result.push(`<div class="report-page">${buf.join('\n')}</div>`);
            buf = [];
        }
    };

    for (const child of children) {
        if (child.classList.contains('report-page')) {
            flush();
            result.push(child.outerHTML);
        } else {
            buf.push(child.outerHTML);
        }
    }
    flush();

    return result.length > 0
        ? `<div class="report-chapter">${result.join('\n')}</div>`
        : `<div class="report-chapter"><div class="report-page">${html}</div></div>`;
}

function hasReportChapter(html: string) {
    return html.startsWith('<div class="report-chapter">') && html.endsWith('</div>');
}

function getPageCount(html: string) {
    const matches = html.match(/class="report-page"/g);
    return matches ? matches.length : 0;
}

function allContentInsidePages(html: string) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const chapter = doc.body.querySelector('.report-chapter');
    if (!chapter) return false;
    const children = Array.from(chapter.children);
    return children.length > 0 && children.every(el => el.classList.contains('report-page'));
}

describe('normalizeSectionHtml', () => {
    it('returns empty string as-is', () => {
        expect(normalizeSectionHtml('')).toBe('');
    });

    it('returns whitespace-only string as-is', () => {
        expect(normalizeSectionHtml('   ')).toBe('   ');
    });

    it('wraps bare HTML (no report-page) in chapter > page', () => {
        const input = '<h2>Chapter Title</h2><p>Some content here.</p>';
        const result = normalizeSectionHtml(input);
        expect(hasReportChapter(result)).toBe(true);
        expect(getPageCount(result)).toBe(1);
        expect(result).toContain('<h2>Chapter Title</h2>');
        expect(result).toContain('<p>Some content here.</p>');
    });

    it('wraps long bare HTML with multiple elements in one page', () => {
        const input = '<h2>Title</h2><p>Para 1</p><p>Para 2</p><h3>Sub</h3><p>Para 3</p>';
        const result = normalizeSectionHtml(input);
        expect(hasReportChapter(result)).toBe(true);
        expect(getPageCount(result)).toBe(1);
    });

    it('adds chapter wrapper when pages exist but no chapter', () => {
        const input = '<div class="report-page"><h2>Title</h2><p>Content</p></div>';
        const result = normalizeSectionHtml(input);
        expect(hasReportChapter(result)).toBe(true);
        expect(getPageCount(result)).toBe(1);
        expect(result).toContain('<h2>Title</h2>');
    });

    it('preserves valid chapter > pages structure', () => {
        const input = '<div class="report-chapter"><div class="report-page"><h2>Title</h2><p>Content A</p></div><div class="report-page"><p>Content B</p></div></div>';
        const result = normalizeSectionHtml(input);
        expect(hasReportChapter(result)).toBe(true);
        expect(getPageCount(result)).toBe(2);
        expect(allContentInsidePages(result)).toBe(true);
    });

    it('wraps orphan elements before a report-page into their own page', () => {
        const input = '<div class="report-chapter"><p>Orphan paragraph</p><div class="report-page"><h2>Title</h2><p>Content</p></div></div>';
        const result = normalizeSectionHtml(input);
        expect(hasReportChapter(result)).toBe(true);
        expect(getPageCount(result)).toBe(2);
        expect(allContentInsidePages(result)).toBe(true);
        expect(result).toContain('Orphan paragraph');
    });

    it('wraps orphan elements after a report-page into their own page', () => {
        const input = '<div class="report-chapter"><div class="report-page"><h2>Title</h2></div><p>Trailing orphan</p></div>';
        const result = normalizeSectionHtml(input);
        expect(hasReportChapter(result)).toBe(true);
        expect(getPageCount(result)).toBe(2);
        expect(allContentInsidePages(result)).toBe(true);
        expect(result).toContain('Trailing orphan');
    });

    it('wraps orphan elements between two report-pages', () => {
        const input = '<div class="report-chapter"><div class="report-page"><h2>Title</h2></div><p>Orphan in middle</p><div class="report-page"><p>Content</p></div></div>';
        const result = normalizeSectionHtml(input);
        expect(hasReportChapter(result)).toBe(true);
        expect(getPageCount(result)).toBe(3);
        expect(allContentInsidePages(result)).toBe(true);
        expect(result).toContain('Orphan in middle');
    });

    it('handles multiple pages without chapter wrapper', () => {
        const input = '<div class="report-page"><h2>Title</h2><p>Page 1</p></div><div class="report-page"><p>Page 2</p></div>';
        const result = normalizeSectionHtml(input);
        expect(hasReportChapter(result)).toBe(true);
        expect(getPageCount(result)).toBe(2);
        expect(allContentInsidePages(result)).toBe(true);
    });

    it('strips markdown code fences before processing', () => {
        const input = '```html\n<h2>Title</h2><p>Content</p>\n```';
        const result = normalizeSectionHtml(input);
        expect(hasReportChapter(result)).toBe(true);
        expect(getPageCount(result)).toBe(1);
        expect(result).toContain('<h2>Title</h2>');
        expect(result).not.toContain('```');
    });

    it('strips code fences without language tag', () => {
        const input = '```\n<h2>Title</h2><p>Content</p>\n```';
        const result = normalizeSectionHtml(input);
        expect(hasReportChapter(result)).toBe(true);
        expect(result).not.toContain('```');
    });

    it('preserves inline styles on elements', () => {
        const input = '<h2 style="color: #1a365d; font-size: 1.8rem;">Styled Title</h2><p>Content</p>';
        const result = normalizeSectionHtml(input);
        expect(result).toContain('color: #1a365d');
        expect(result).toContain('Styled Title');
    });

    it('preserves tables inside pages', () => {
        const input = '<div class="report-chapter"><div class="report-page"><h2>Data</h2><table><tr><td>Value</td></tr></table></div></div>';
        const result = normalizeSectionHtml(input);
        expect(result).toContain('<table>');
        expect(result).toContain('<td>Value</td>');
    });

    it('preserves SVG content inside pages', () => {
        const input = '<div class="report-chapter"><div class="report-page"><h2>Chart</h2><svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg" width="100%"><title>Chart</title><circle cx="200" cy="200" r="80" fill="none" stroke="#3182CE" stroke-width="40"/></svg></div></div>';
        const result = normalizeSectionHtml(input);
        expect(result).toContain('viewBox="0 0 800 400"');
        expect(result).toContain('stroke="#3182CE"');
    });

    it('handles HTML with unclosed divs via DOMParser', () => {
        const input = '<div class="report-chapter"><div class="report-page"><h2>Title</h2><p>Unclosed content';
        const result = normalizeSectionHtml(input);
        expect(hasReportChapter(result)).toBe(true);
        expect(getPageCount(result)).toBeGreaterThanOrEqual(1);
        expect(result).toContain('Title');
    });

    it('handles only orphan content with no pages or chapter', () => {
        const input = '<h2>Just a heading</h2><p>And a paragraph</p><ul><li>Item</li></ul>';
        const result = normalizeSectionHtml(input);
        expect(hasReportChapter(result)).toBe(true);
        expect(getPageCount(result)).toBe(1);
        expect(result).toContain('<h2>Just a heading</h2>');
        expect(result).toContain('<li>Item</li>');
    });

    it('handles single quotes in class attribute', () => {
        const input = "<div class='report-page'><h2>Title</h2></div>";
        const result = normalizeSectionHtml(input);
        expect(hasReportChapter(result)).toBe(true);
        expect(getPageCount(result)).toBe(1);
    });

    it('preserves content with links and citations', () => {
        const input = '<div class="report-chapter"><div class="report-page"><h2>Research</h2><p>According to <a href="https://example.com">Smith (2023)</a>, the data shows growth.</p></div></div>';
        const result = normalizeSectionHtml(input);
        expect(result).toContain('href="https://example.com"');
        expect(result).toContain('Smith (2023)');
    });

    it('handles multiple consecutive orphan elements between pages', () => {
        const input = '<div class="report-chapter"><div class="report-page"><h2>Title</h2></div><p>Orphan 1</p><p>Orphan 2</p><p>Orphan 3</p><div class="report-page"><p>Page content</p></div></div>';
        const result = normalizeSectionHtml(input);
        expect(hasReportChapter(result)).toBe(true);
        expect(getPageCount(result)).toBe(3);
        expect(allContentInsidePages(result)).toBe(true);
    });

    it('preserves details/summary elements', () => {
        const input = '<div class="report-chapter"><div class="report-page"><h2>FAQ</h2><details><summary>Question 1</summary><p>Answer 1</p></details></div></div>';
        const result = normalizeSectionHtml(input);
        expect(result).toContain('<details>');
        expect(result).toContain('<summary>Question 1</summary>');
    });
});
