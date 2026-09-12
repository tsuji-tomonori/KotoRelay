import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Markdown from '../src/components/Markdown';
describe('Markdown表示', () => {
  it('見出し・表・コード・箇条書きを表示する', () => {
    render(
      <Markdown
        body={
          '# 手順\n\n- 確認\n\n| 項目 | 値 |\n|---|---|\n| 状態 | 承認 |\n\n```ts\nconst x = 1;\n```'
        }
      />,
    );
    expect(screen.getByRole('heading', { name: '手順' })).toBeVisible();
    expect(screen.getByRole('table')).toHaveTextContent('承認');
    expect(screen.getByRole('list')).toHaveTextContent('確認');
    expect(screen.getByText('const x = 1;')).toBeVisible();
  });
  it('スクリプトを実行せず外部画像を読み込まない', () => {
    const { container } = render(
      <Markdown
        body={
          '<script>alert(1)</script>\n\n![外部](https://example.com/tracker.png)\n\n[危険](javascript:alert(1))'
        }
      />,
    );
    expect(container.querySelector('script')).toBeNull();
    expect(container.querySelector('img')).toBeNull();
    expect(screen.getByText('[外部画像: 外部]')).toBeVisible();
    expect(container.querySelector('a')).not.toHaveAttribute('href');
  });
  it('安全な外部リンクへrelを付ける', () => {
    render(<Markdown body={'[公式](https://example.com)'} />);
    expect(screen.getByRole('link')).toHaveAttribute('rel', 'noopener noreferrer');
  });
});
