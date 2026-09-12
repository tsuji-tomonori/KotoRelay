import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
export function safeLink(url: string): string | undefined {
  if (url.startsWith('#') || url.startsWith('/')) return url.startsWith('//') ? undefined : url;
  try {
    const parsed = new URL(url);
    return ['https:', 'http:'].includes(parsed.protocol) ? url : undefined;
  } catch {
    return undefined;
  }
}
export default function Markdown({ body }: { body: string }) {
  return (
    <div className="markdown">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        skipHtml
        urlTransform={safeLink}
        components={{
          img: ({ alt }) => <span className="muted">[外部画像: {alt ?? '画像'}]</span>,
          a: ({ href, children }) => (
            <a href={safeLink(href ?? '')} target="_blank" rel="noopener noreferrer">
              {children}
            </a>
          ),
        }}
      >
        {body}
      </ReactMarkdown>
    </div>
  );
}
