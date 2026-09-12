import { useCallback, useEffect, useRef, useState } from 'react';
import { type Api, type Ocr, type Placement, type Region } from '../../lib/api';
import { useUnsaved } from '../../components/layout/Workspace';
import { ProtectedImage } from './ProtectedImage';

export function Images({
  api,
  token,
  documentId,
  versionId,
  edit,
  placements,
  onChange,
  offset,
  onError,
  onPending,
}: {
  api: Api;
  token: string;
  documentId: string;
  versionId?: string;
  edit: boolean;
  placements: Placement[];
  onChange: (p: Placement[]) => void;
  offset: number;
  onError: (message: string) => void;
  onPending?: (pending: boolean) => void;
}) {
  const latest = useRef({ placements, onChange, offset });
  latest.current = { placements, onChange, offset };
  const [busy, setBusy] = useState(false);
  const [pending, setPending] = useState<Record<string, boolean>>({});
  const report = useCallback(
    (id: string, value: boolean) =>
      setPending((current) => (current[id] === value ? current : { ...current, [id]: value })),
    [],
  );
  const waiting = busy || placements.some((p) => pending[p.id] !== false);
  useEffect(() => {
    onPending?.(waiting && edit);
  }, [waiting, edit, onPending]);
  useUnsaved(busy);
  async function upload(file: File) {
    setBusy(true);
    try {
      const form = new FormData();
      form.append('file', file);
      const result = await api<{ asset: { id: string }; ocr_run: { id: string }; ocr: Ocr }>(
        `/images/documents/${documentId}`,
        'POST',
        form,
      );
      latest.current.onChange([
        ...latest.current.placements,
        {
          id: crypto.randomUUID(),
          asset_id: result.asset.id,
          ocr_run_id: result.ocr_run.id,
          offset: latest.current.offset,
          heading: '',
          alt_text: '',
          caption: '',
        },
      ]);
    } catch (e) {
      onError(String(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="panel images-panel">
      <div className="section-heading">
        <h2>
          画像とOCR <span className="count">{placements.length}枚</span>
        </h2>
      </div>
      {edit && (
        <>
          <p id="image-limits" className="muted">
            PNG / JPEG · 1枚3 MiB以下 · 20メガピクセル・各辺8000px以下 ·
            文書10枚まで。本文のカーソル位置へ挿入します。
          </p>
          <label className="file-field">
            画像を添付
            <input
              aria-label="画像を添付"
              aria-describedby="image-limits"
              type="file"
              accept="image/png,image/jpeg"
              disabled={busy || placements.length >= 10}
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) void upload(file);
                e.target.value = '';
              }}
            />
          </label>
          {busy && <p role="status">画像を取り込み、文字を読み取っています…</p>}
        </>
      )}
      {placements.length === 0 ? (
        <p className="muted">添付画像はありません。</p>
      ) : (
        placements.map((p, i) => (
          <ImageEditor
            key={p.id}
            api={api}
            token={token}
            p={p}
            number={i + 1}
            versionId={versionId}
            edit={edit}
            onChange={(next) => onChange(placements.map((v) => (v.id === p.id ? next : v)))}
            onRemove={() => onChange(placements.filter((v) => v.id !== p.id))}
            onError={onError}
            report={report}
          />
        ))
      )}
    </section>
  );
}
export function ImageEditor({
  api,
  token,
  p,
  number,
  versionId,
  edit,
  onChange,
  onRemove,
  onError,
  report,
}: {
  api: Api;
  token: string;
  p: Placement;
  number: number;
  versionId?: string;
  edit: boolean;
  onChange: (p: Placement) => void;
  onRemove: () => void;
  onError: (message: string) => void;
  report: (id: string, pending: boolean) => void;
}) {
  const current = useRef({ p, onChange });
  current.current = { p, onChange };
  const [ocr, setOcr] = useState<Ocr | null>(null);
  const [regions, setRegions] = useState<Region[]>([]);
  const [selected, setSelected] = useState('');
  const [dirty, setDirty] = useState(false);
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);
  const [retry, setRetry] = useState(0);
  const [notice, setNotice] = useState('');
  const [adding, setAdding] = useState(false);
  const [bounds, setBounds] = useState({ x: '0', y: '0', width: '0.2', height: '0.1' });
  const refs = useRef<Record<string, HTMLTextAreaElement | null>>({});
  useUnsaved(dirty || busy || adding);
  useEffect(() => {
    let active = true;
    setOcr(null);
    setFailed(false);
    api<Ocr>(`/images/ocr/${p.ocr_run_id}${versionId ? `?version_id=${versionId}` : ''}`)
      .then((value) => {
        if (active) {
          setOcr(value);
          setRegions(value.regions);
          setDirty(false);
        }
      })
      .catch((e) => {
        if (active) {
          setFailed(true);
          onError(String(e));
        }
      });
    return () => {
      active = false;
    };
  }, [api, p.ocr_run_id, versionId, onError, retry]);
  useEffect(() => {
    report(p.id, dirty || busy || adding || !ocr?.confirmed);
  }, [report, p.id, dirty, busy, adding, ocr?.confirmed]);
  function change(id: string, field: keyof Region, value: string | number) {
    setRegions(
      regions.map((r) =>
        r.region_id === id ? { ...r, [field]: value, source: 'human', confidence: null } : r,
      ),
    );
    setDirty(true);
  }
  async function confirm() {
    setBusy(true);
    try {
      const result = await api<{ ocr_run: { id: string } }>(`/images/${p.asset_id}/ocr`, 'POST', {
        regions: regions.map((r, i) => ({ ...r, order: i })),
        confirmed: true,
      });
      setDirty(false);
      current.current.onChange({ ...current.current.p, ocr_run_id: result.ocr_run.id });
      setNotice('OCRを確認しました。文書を保存してください。');
    } catch (e) {
      onError(String(e));
    } finally {
      setBusy(false);
    }
  }
  const valid = (r: { x: number; y: number; width: number; height: number }) =>
    r.x >= 0 &&
    r.y >= 0 &&
    r.width > 0 &&
    r.height > 0 &&
    r.x + r.width <= 1.000001 &&
    r.y + r.height <= 1.000001;
  const newBounds = {
    x: Number(bounds.x),
    y: Number(bounds.y),
    width: Number(bounds.width),
    height: Number(bounds.height),
  };
  return (
    <section className="image-section" aria-label={`図${number}の編集`}>
      <h3>
        図{number} ·{' '}
        {ocr
          ? ocr.status === 'failed'
            ? '読取失敗'
            : ocr.confirmed && !dirty
              ? '確認済み'
              : '確認が必要'
          : '読込中'}
      </h3>
      {notice && (
        <p role="status" className="success">
          {notice}
        </p>
      )}
      {edit && (
        <div className="image-metadata">
          <label>
            図{number}の代替テキスト
            <input
              value={p.alt_text ?? ''}
              maxLength={1000}
              onChange={(e) => onChange({ ...p, alt_text: e.target.value })}
            />
          </label>
          <small>図が伝える意味や結論を説明してください。</small>
          <label>
            図{number}の説明文
            <input
              value={p.caption ?? ''}
              maxLength={2000}
              onChange={(e) => onChange({ ...p, caption: e.target.value })}
            />
          </label>
          <label>
            図{number}の挿入位置（文字数）
            <input
              type="number"
              min={0}
              max={100000}
              value={p.offset}
              onChange={(e) => onChange({ ...p, offset: Number(e.target.value) })}
            />
          </label>
          <p className="muted">
            絵文字も1文字として数えます。本文の変更に合わせて位置を調整し、プレビューで確認できます。
          </p>
        </div>
      )}
      <div className="image-review">
        <div className="image-frame">
          <ProtectedImage
            token={token}
            id={p.asset_id}
            version={versionId}
            alt={p.alt_text || `図${number}のOCR確認画像`}
          />
          <div className="ocr-overlay">
            {regions.map((r, i) => (
              <button
                type="button"
                tabIndex={-1}
                key={r.region_id}
                className={selected === r.region_id ? 'selected' : ''}
                aria-label={`領域${i + 1}を選択`}
                style={{
                  left: `${r.x * 100}%`,
                  top: `${r.y * 100}%`,
                  width: `${r.width * 100}%`,
                  height: `${r.height * 100}%`,
                }}
                onClick={() => {
                  setSelected(r.region_id!);
                  refs.current[r.region_id!]?.focus();
                }}
              >
                {i + 1}
              </button>
            ))}
          </div>
        </div>
        <div className="region-list">
          {failed && (
            <div className="alert">
              OCRを読み込めませんでした。<button onClick={() => setRetry(retry + 1)}>再試行</button>
            </div>
          )}
          {regions.map((r, i) => (
            <section
              key={r.region_id}
              className={`ocr-region ${selected === r.region_id ? 'selected' : ''}`}
            >
              <h4>領域{i + 1}</h4>
              {edit ? (
                <>
                  <label>
                    図{number}・領域{i + 1}の文字
                    <textarea
                      ref={(node) => {
                        refs.current[r.region_id!] = node;
                      }}
                      value={r.text}
                      maxLength={5000}
                      onFocus={() => setSelected(r.region_id!)}
                      onChange={(e) => change(r.region_id!, 'text', e.target.value)}
                    />
                  </label>
                  <details>
                    <summary>文字領域の位置・サイズ</summary>
                    <div className="coordinates">
                      {(['x', 'y', 'width', 'height'] as const).map((field, j) => (
                        <label key={field}>
                          {['左位置', '上位置', '幅', '高さ'][j]}
                          <input
                            aria-label={`図${number}・領域${i + 1}の${['左位置', '上位置', '幅', '高さ'][j]}`}
                            type="number"
                            min="0"
                            max="1"
                            step="0.01"
                            value={r[field]}
                            onChange={(e) => change(r.region_id!, field, Number(e.target.value))}
                          />
                        </label>
                      ))}
                    </div>
                  </details>
                  <button
                    type="button"
                    onClick={() => {
                      setRegions(regions.filter((v) => v.region_id !== r.region_id));
                      setDirty(true);
                    }}
                  >
                    領域{i + 1}を削除
                  </button>
                </>
              ) : (
                <p>{r.text}</p>
              )}
              <small>
                {r.source === 'human'
                  ? '人による訂正・確信度は未測定'
                  : r.confidence === null
                    ? '確信度は未測定'
                    : `自動読取の確信度 ${Math.round(r.confidence * 100)}%`}
              </small>
            </section>
          ))}
          {edit && (
            <>
              <button className="secondary" onClick={() => setAdding(!adding)}>
                文字領域を追加
              </button>
              {adding && (
                <div className="panel">
                  <p>追加する領域の位置と大きさを指定してください（0〜1）。</p>
                  <div className="coordinates">
                    {(['x', 'y', 'width', 'height'] as const).map((field, i) => (
                      <label key={field}>
                        新しい領域の{['左位置', '上位置', '幅', '高さ'][i]}
                        <input
                          type="number"
                          min="0"
                          max="1"
                          step="0.01"
                          value={bounds[field]}
                          onChange={(e) => setBounds({ ...bounds, [field]: e.target.value })}
                        />
                      </label>
                    ))}
                  </div>
                  <button
                    disabled={!valid(newBounds)}
                    onClick={() => {
                      const id = crypto.randomUUID();
                      setRegions([
                        ...regions,
                        {
                          ...newBounds,
                          region_id: id,
                          text: '',
                          source: 'human',
                          confidence: null,
                          order: regions.length,
                        },
                      ]);
                      setSelected(id);
                      setDirty(true);
                      setAdding(false);
                    }}
                  >
                    この範囲で追加
                  </button>
                </div>
              )}
              <p className="muted">改行を増やしても、他の領域の文字や座標は変わりません。</p>
              {regions.some((r) => !valid(r)) && (
                <p role="alert">領域は画像内に収まる位置と大きさを指定してください。</p>
              )}
              <div className="actions">
                <button
                  className="secondary"
                  disabled={busy || !ocr || adding || regions.some((r) => !valid(r))}
                  onClick={() => void confirm()}
                >
                  OCRを確認して確定
                </button>
                <button disabled={busy} onClick={onRemove}>
                  配置を削除
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
