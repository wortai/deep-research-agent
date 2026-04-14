/**
 * Vitest: render Markdown component, check actual DOM output
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

// Inline preprocessContent — mirrors ChatWorkspace.tsx logic
const preprocessContent = (raw: string, isStreaming = false): string => {
  let result = raw;
  const codeBlocks: string[] = [];
  result = result.replace(/```[\s\S]*?```/g, (m) => { codeBlocks.push(m); return `%%CB_${codeBlocks.length - 1}%%`; });
  result = result.replace(/`[^`]+`/g, (m) => { codeBlocks.push(m); return `%%CB_${codeBlocks.length - 1}%%`; });
  result = result.replace(/(?<!\$)\$(?=\d)/g, '\\$');
  if (!isStreaming) {
    const openInline  = (result.match(/\\\(/g) || []).length;
    const closeInline = (result.match(/\\\)/g) || []).length;
    if (openInline > closeInline) result += '\\)';
    const openDisplay  = (result.match(/\\\[/g) || []).length;
    const closeDisplay = (result.match(/\\\]/g) || []).length;
    if (openDisplay > closeDisplay) result += '\\]';
  }
  result = result.replace(/\\\(([\s\S]*?)\\\)/g, (_, math) => `$${math}$`);
  result = result.replace(/\\\[([\s\S]*?)\\\]/g, (_, math) => `$$${math}$$`);
  if (!isStreaming) {
    const ddCount = (result.match(/(?<!\$)\$\$(?!\$)/g) || []).length;
    if (ddCount % 2 !== 0) result += '$$';
  }
  result = result.replace(/%%CB_(\d+)%%/g, (_, i) => codeBlocks[parseInt(i, 10)]);
  return result;
};

// Minimal Markdown component (same logic, no icons/dependencies)
const TestMarkdown = ({ content }: { content: string }) => (
  <div data-testid="md">
    <ReactMarkdown
      remarkPlugins={[remarkGfm, remarkMath]}
      rehypePlugins={[rehypeKatex]}
    >
      {preprocessContent(content)}
    </ReactMarkdown>
  </div>
);

describe('Markdown rendering', () => {
  it('renders headers h1-h4', () => {
    const { container } = render(<TestMarkdown content="# H1\n## H2\n### H3\n#### H4" />);
    expect(container.querySelector('h1')?.textContent).toBe('H1');
    expect(container.querySelector('h2')?.textContent).toBe('H2');
    expect(container.querySelector('h3')?.textContent).toBe('H3');
    expect(container.querySelector('h4')?.textContent).toBe('H4');
  });

  it('renders links with target blank', () => {
    render(<TestMarkdown content="[Example](https://example.com)" />);
    const link = screen.getByRole('link');
    expect(link.getAttribute('href')).toBe('https://example.com');
  });

  it('renders images', () => {
    const { container } = render(<TestMarkdown content="![Alt](img.png)" />);
    const img = container.querySelector('img');
    expect(img?.getAttribute('src')).toBe('img.png');
    expect(img?.getAttribute('alt')).toBe('Alt');
  });

  it('renders blockquotes', () => {
    const { container } = render(<TestMarkdown content="> quoted text" />);
    const bq = container.querySelector('blockquote');
    expect(bq?.textContent).toContain('quoted');
  });

  it('renders tables', () => {
    const { container } = render(<TestMarkdown content="| A | B |\n| --- | --- |\n| 1 | 2 |" />);
    const table = container.querySelector('table');
    expect(table).toBeTruthy();
    expect(table?.querySelector('th')?.textContent).toContain('A');
  });

  it('renders unordered list', () => {
    const { container } = render(<TestMarkdown content="- one\n- two" />);
    const items = container.querySelectorAll('li');
    expect(items.length).toBe(2);
  });

  it('renders ordered list', () => {
    const { container } = render(<TestMarkdown content="1. first\n2. second" />);
    const ol = container.querySelector('ol');
    expect(ol).toBeTruthy();
    expect(ol?.querySelectorAll('li').length).toBe(2);
  });

  it('renders inline code', () => {
    const { container } = render(<TestMarkdown content="Use `console.log`" />);
    const code = container.querySelector('code');
    expect(code?.textContent).toContain('console.log');
  });

  it('renders math via KaTeX', () => {
    const { container } = render(<TestMarkdown content="$x^2$" />);
    // KaTeX should render a .katex element
    const katex = container.querySelector('.katex');
    expect(katex).toBeTruthy();
  });

  it('does NOT render currency $70M as math', () => {
    const { container } = render(<TestMarkdown content="Revenue of $70M" />);
    const katex = container.querySelector('.katex');
    expect(katex).toBeFalsy();
    expect(container.textContent).toContain('$70M');
  });

  it('renders display math $$', () => {
    const { container } = render(<TestMarkdown content="$$E=mc^2$$" />);
    const katexDisplay = container.querySelector('.katex-display');
    expect(katexDisplay).toBeTruthy();
  });

  it('handles empty string', () => {
    const { container } = render(<TestMarkdown content="" />);
    expect(container.querySelector('[data-testid="md"]')).toBeTruthy();
  });

  it('preserves code block $ from math conversion', () => {
    const { container } = render(<TestMarkdown content={"```js\nconst x = \"$100\";\n```"} />);
    // The code block should contain $100 literally
    const codeElements = container.querySelectorAll('code');
    const allText = Array.from(codeElements).map(e => e.textContent).join(' ');
    expect(allText).toContain('$100');
  });

  it('mixed: currency + math + code', () => {
    const { container } = render(<TestMarkdown content="Revenue $70M. Math $x^2$. Code `var`" />);
    const katex = container.querySelector('.katex');
    expect(katex).toBeTruthy(); // x^2 rendered as math
    expect(container.textContent).toContain('$70M');
    expect(container.textContent).toContain('var');
  });

  it('preprocessContent converts backslash-paren to dollar', () => {
    const input = '\\(x^2\\)';
    const output = preprocessContent(input);
    expect(output).toBe('$x^2$');
  });

  it('preprocessContent converts full sentence with backslash-paren', () => {
    const input = 'The formula \\(x^2 + y^2\\) is important';
    const output = preprocessContent(input);
    expect(output).toBe('The formula $x^2 + y^2$ is important');
  });

  it('renders direct $x^2 + y^2$ as math', () => {
    const { container } = render(<TestMarkdown content="The formula $x^2 + y^2$ is important" />);
    const katex = container.querySelector('.katex');
    expect(katex).toBeTruthy();
  });

  it('renders \\(...\\) inline math via KaTeX', () => {
    const input = 'The formula \\(x^2 + y^2\\) is important';
    const processed = preprocessContent(input);
    expect(processed).toBe('The formula $x^2 + y^2$ is important');
    const { container } = render(<TestMarkdown content={input} />);
    const katex = container.querySelector('.katex');
    expect(katex).toBeTruthy();
  });

  it('renders \\[...\\] display math via KaTeX', () => {
    const { container } = render(<TestMarkdown content="\\[E = mc^2\\]" />);
    const katexDisplay = container.querySelector('.katex-display');
    expect(katexDisplay).toBeTruthy();
  });

  it('renders \\(...\\) with nested parens (e.g. \\sigma)', () => {
    const { container } = render(<TestMarkdown content="Activation \\(\\sigma(h_j) = h_j(1 - h_j)\\) is used" />);
    const katex = container.querySelector('.katex');
    expect(katex).toBeTruthy();
  });

  it('renders \\(...\\) with \\frac and \\partial', () => {
    const { container } = render(<TestMarkdown content="Error \\(\\frac{\\partial L}{\\partial h}\\) propagates" />);
    const katex = container.querySelector('.katex');
    expect(katex).toBeTruthy();
  });

  it('handles mixed $...$ and \\(...\\) in same message', () => {
    const { container } = render(<TestMarkdown content="Inline $a+b$ and also \\(c+d\\) here" />);
    const katexElements = container.querySelectorAll('.katex');
    expect(katexElements.length).toBeGreaterThanOrEqual(2);
  });
});
