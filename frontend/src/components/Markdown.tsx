import { createElement } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkParse from 'remark-parse';
import { unified } from 'unified';
import type { Root, RootContent } from 'mdast';
export function safeLink(url: string): string | undefined {
  if (url.startsWith('#') || url.startsWith('/')) return url.startsWith('//') ? undefined : url;
  try {
    const parsed = new URL(url);
    return ['https:', 'http:'].includes(parsed.protocol) ? url : undefined;
  } catch {
    return undefined;
  }
}
function nodeText(node: RootContent): string {
  return 'value' in node
    ? node.value
    : 'children' in node
      ? node.children.map(nodeText).join('')
      : '';
}
export function headings(body: string, prefix = 'document') {
  const root = unified().use(remarkParse).parse(body) as Root;
  return root.children
    .filter((n) => n.type === 'heading')
    .map((n) => ({
      id: `${prefix}-${n.position!.start.offset}`,
      text: nodeText(n),
      depth: n.depth,
    }));
}
export default function Markdown({ body, prefix = 'document' }: { body: string; prefix?: string }) {
  const headingComponents = Object.fromEntries(
    [1, 2, 3, 4, 5, 6].map((level) => [
      `h${level}`,
      ({
        children,
        node,
      }: {
        children?: React.ReactNode;
        node?: { position?: { start: { offset?: number } } };
      }) =>
        createElement(
          `h${Math.min(6, level + 1)}`,
          { id: `${prefix}-${node?.position?.start.offset}`, tabIndex: -1 },
          children,
        ),
    ]),
  );
  return (
    <div className="markdown">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        skipHtml
        urlTransform={safeLink}
        components={{
          ...headingComponents,
          img: ({ alt }) => <span className="muted">[外部画像: {alt ?? '画像'}]</span>,
          a: ({ href, children }) => {
            const safe = safeLink(href ?? '');
            const external = !!safe && /^https?:/.test(safe);
            return (
              <a
                href={safe}
                target={external ? '_blank' : undefined}
                rel={external ? 'noopener noreferrer' : undefined}
              >
                {children}
                {external && <span className="sr-only">（別タブで開きます）</span>}
              </a>
            );
          },
        }}
      >
        {body}
      </ReactMarkdown>
    </div>
  );
}
