import Markdown, { headings } from '../../components/Markdown';
import { type Placement } from '../../lib/api';
import { ProtectedImage } from '../images/ProtectedImage';

// offsetはUnicodeコードポイント数。Python lenと同じ単位で、UTF-16の途中を分割しない。
export function documentParts(body: string, placements: Placement[]) {
  const chars = Array.from(body);
  let offset = 0;
  const parts: { text: string; placement?: Placement; prefix: string }[] = [...placements]
    .sort((a, b) => a.offset - b.offset)
    .map((p, index) => {
      const end = Math.min(chars.length, Math.max(offset, p.offset));
      const text = chars.slice(offset, end).join('');
      offset = end;
      return { text, placement: p, prefix: `document-part-${index}` };
    });
  parts.push({ text: chars.slice(offset).join(''), prefix: 'document-end' });
  return parts;
}
export function relocatePlacements(
  before: string,
  after: string,
  placements: Placement[],
): Placement[] {
  const a = Array.from(before),
    b = Array.from(after);
  let start = 0,
    end = 0;
  while (start < a.length && start < b.length && a[start] === b[start]) start++;
  while (
    end < a.length - start &&
    end < b.length - start &&
    a[a.length - 1 - end] === b[b.length - 1 - end]
  )
    end++;
  return placements.map((p) => ({
    ...p,
    offset:
      p.offset <= start
        ? p.offset
        : p.offset >= a.length - end
          ? p.offset + b.length - a.length
          : b.length - end,
  }));
}
export function PlacedDocument({
  body,
  placements,
  token,
  version,
  toc = false,
}: {
  body: string;
  placements: Placement[];
  token: string;
  version?: string;
  toc?: boolean;
}) {
  const parts = documentParts(body, placements);
  const outline = parts.flatMap((p) => headings(p.text, p.prefix));
  return (
    <div className="placed-document">
      {toc && outline.length > 0 && (
        <nav className="document-toc" aria-label="文書の目次">
          <h2>目次</h2>
          <ul>
            {outline.map((h) => (
              <li key={h.id}>
                <a href={'#' + h.id}>{h.text}</a>
              </li>
            ))}
          </ul>
        </nav>
      )}
      {parts.map((part, index) => (
        <div key={part.prefix} className="document-part">
          <Markdown body={part.text} prefix={part.prefix} />
          {part.placement && (
            <figure data-placement={part.placement.id}>
              <ProtectedImage
                token={token}
                id={part.placement.asset_id}
                version={version}
                alt={part.placement.alt_text || part.placement.heading || `図${index + 1}`}
              />
              <figcaption>
                図{index + 1} {part.placement.caption || part.placement.heading}
              </figcaption>
            </figure>
          )}
        </div>
      ))}
    </div>
  );
}
