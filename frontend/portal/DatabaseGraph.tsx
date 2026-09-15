import { useEffect, useMemo, useRef, useState } from 'react';
import type { Table, Relationship } from './DatabaseExplorer';
type View = { x: number; y: number; scale: number };
export function Graph({
  tables,
  visible,
  column,
  relation,
  nameMode,
  onColumn,
  onRelation,
  relationships,
  selected,
  onSelect,
}: {
  tables: Table[];
  visible: Table[];
  column: string;
  relation: string;
  nameMode: string;
  onColumn: (table: string, column: string) => void;
  onRelation: (relation: Relationship) => void;
  relationships: Relationship[];
  selected: string;
  onSelect: (name: string) => void;
}) {
  const viewport = useRef<HTMLDivElement>(null);
  const [view, setView] = useState<View>({ x: 20, y: 20, scale: 1 });
  const points = useRef(new Map<number, { x: number; y: number }>());
  const cameraTarget = useRef('');
  const drag = useRef<{ name: string; x: number; y: number; moved: boolean } | null>(null);
  const [offsets, setOffsets] = useState<Record<string, { x: number; y: number }>>({});
  const [size, setSize] = useState({ width: 600, height: 700 });
  const positions = useMemo(() => {
    const groups = [...new Set(tables.map((t) => t.group))];
    const next = groups.map(() => 40);
    return new Map(
      tables.map((t) => {
        const g = groups.indexOf(t.group);
        const p = { x: 40 + g * 470, y: next[g], height: 58 + t.columns.length * 38 };
        next[g] += p.height + 90;
        return [t.name, { ...p, ...offsets[t.name] }];
      }),
    );
  }, [tables, offsets]);
  const width = Math.max(...[...positions.values()].map((p) => p.x + 420));
  const height = Math.max(...[...positions.values()].map((p) => p.y + p.height + 40));
  const bounds = visible.map((t) => positions.get(t.name)!);
  const left = Math.min(...bounds.map((p) => p.x)) - 30;
  const top = Math.min(...bounds.map((p) => p.y)) - 30;
  const right = Math.max(...bounds.map((p) => p.x + 360)) + 30;
  const bottom = Math.max(...bounds.map((p) => p.y + p.height)) + 30;
  function fit() {
    const box = viewport.current;
    if (!box) return;
    const scale = Math.min(
      (box.clientWidth - 32) / (right - left),
      (box.clientHeight - 32) / (bottom - top),
      1,
    );
    setView({
      x: (box.clientWidth - (right - left) * scale) / 2 - left * scale,
      y: (box.clientHeight - (bottom - top) * scale) / 2 - top * scale,
      scale,
    });
  }
  useEffect(() => {
    const box = viewport.current;
    if (!box) return;
    const observer = new ResizeObserver(() =>
      setSize({ width: box.clientWidth, height: box.clientHeight }),
    );
    observer.observe(box);
    return () => observer.disconnect();
  }, []);
  useEffect(() => {
    const key = `${selected}:${size.width}:${size.height}`;
    if (cameraTarget.current === key) return;
    cameraTarget.current = key;
    const p = positions.get(selected);
    if (p)
      setView({
        scale: 0.85,
        x: size.width / 2 - (p.x + 180) * 0.85,
        y: Math.max(30, (size.height - p.height * 0.85) / 2) - p.y * 0.85,
      });
    // 配置を動かす間はカメラを追従させず、テーブルの選択時だけ中央へ移動する。
  }, [selected, size, positions]);
  function zoom(factor: number, x?: number, y?: number) {
    const cx = x ?? (viewport.current?.clientWidth ?? 0) / 2;
    const cy = y ?? (viewport.current?.clientHeight ?? 0) / 2;
    setView((v) => {
      const scale = Math.max(0.15, Math.min(3, v.scale * factor));
      return {
        x: cx - ((cx - v.x) * scale) / v.scale,
        y: cy - ((cy - v.y) * scale) / v.scale,
        scale,
      };
    });
  }
  useEffect(() => {
    const box = viewport.current;
    if (!box) return;
    const wheel = (event: WheelEvent) => {
      event.preventDefault();
      const rect = box.getBoundingClientRect();
      zoom(Math.exp(-event.deltaY * 0.002), event.clientX - rect.left, event.clientY - rect.top);
    };
    box.addEventListener('wheel', wheel, { passive: false });
    return () => box.removeEventListener('wheel', wheel);
  }, []);
  function center() {
    const p = positions.get(selected);
    const box = viewport.current;
    if (p && box)
      setView({
        scale: 1,
        x: box.clientWidth / 2 - p.x - 180,
        y: Math.max(30, (box.clientHeight - p.height) / 2) - p.y,
      });
  }
  return (
    <section className="db-graph-panel" aria-label="テーブル関係図">
      <div className="db-toolbar">
        <button onClick={() => zoom(1.25)} aria-label="ER図を拡大">
          ＋
        </button>
        <button onClick={() => zoom(0.8)} aria-label="ER図を縮小">
          −
        </button>
        <output aria-label="ER図の倍率">{Math.round(view.scale * 100)}%</output>
        <button onClick={fit}>全体表示</button>
        <button onClick={center}>選択テーブルへ</button>
        <button onClick={() => setOffsets({})}>配置を初期化</button>
      </div>
      <p id="db-graph-help">
        背景をドラッグで移動、ホイール／ピンチで拡大縮小。表題をドラッグで配置。カラム・線を選択して詳細へ。矢印キー・＋・−・Homeにも対応。
      </p>
      <div
        ref={viewport}
        className="db-viewport"
        tabIndex={0}
        role="region"
        aria-label="操作できるER図"
        aria-describedby="db-graph-help"
        onKeyDown={(e) => {
          if (e.target !== e.currentTarget) return;
          if (
            ['+', '=', '-', 'Home', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(
              e.key,
            )
          )
            e.preventDefault();
          if (['+', '='].includes(e.key)) zoom(1.25);
          if (e.key === '-') zoom(0.8);
          if (e.key === 'Home') fit();
          const delta: Record<string, [number, number]> = {
            ArrowLeft: [50, 0],
            ArrowRight: [-50, 0],
            ArrowUp: [0, 50],
            ArrowDown: [0, -50],
          };
          if (delta[e.key])
            setView((v) => ({ ...v, x: v.x + delta[e.key][0], y: v.y + delta[e.key][1] }));
        }}
        onPointerDown={(e) => {
          if ((e.target as Element).closest('button, [role=button]') || e.button > 0) return;
          points.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
          e.currentTarget.setPointerCapture(e.pointerId);
        }}
        onPointerMove={(e) => {
          const old = points.current.get(e.pointerId);
          if (!old) return;
          const before = [...points.current.values()];
          points.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
          const after = [...points.current.values()];
          if (before.length === 2) {
            const distance = (p: typeof before) => Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y);
            const rect = e.currentTarget.getBoundingClientRect();
            const bx = (before[0].x + before[1].x) / 2 - rect.left;
            const by = (before[0].y + before[1].y) / 2 - rect.top;
            const ax = (after[0].x + after[1].x) / 2 - rect.left;
            const ay = (after[0].y + after[1].y) / 2 - rect.top;
            setView((v) => {
              const scale = Math.max(
                0.15,
                Math.min(3, (v.scale * distance(after)) / Math.max(1, distance(before))),
              );
              return {
                scale,
                x: ax - ((bx - v.x) * scale) / v.scale,
                y: ay - ((by - v.y) * scale) / v.scale,
              };
            });
          } else setView((v) => ({ ...v, x: v.x + e.clientX - old.x, y: v.y + e.clientY - old.y }));
        }}
        onPointerUp={(e) => points.current.delete(e.pointerId)}
        onPointerCancel={(e) => points.current.delete(e.pointerId)}
        onLostPointerCapture={(e) => points.current.delete(e.pointerId)}
      >
        <div
          className="db-world"
          style={{
            width,
            height,
            transform: `translate(${view.x}px, ${view.y}px) scale(${view.scale})`,
          }}
        >
          <svg width={width} height={height} className="db-edges" aria-label="外部キー関係">
            <defs>
              <marker
                id="db-arrow"
                viewBox="0 0 10 10"
                refX="9"
                refY="5"
                markerWidth="7"
                markerHeight="7"
                orient="auto-start-reverse"
              >
                <path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke" />
              </marker>
            </defs>
            {relationships
              .filter(
                (r) =>
                  visible.some((t) => t.name === r.from) && visible.some((t) => t.name === r.to),
              )
              .map((r, ri) => {
                const from = positions.get(r.from)!,
                  to = positions.get(r.to)!;
                const fromTable = tables.find((t) => t.name === r.from)!,
                  toTable = tables.find((t) => t.name === r.to)!;
                const active = relation
                  ? relation === r.id
                  : column
                    ? (r.from === selected && r.columns.includes(column)) ||
                      (r.to === selected && r.targetColumns.includes(column))
                    : r.from === selected || r.to === selected;
                const outgoing = to.x > from.x;
                return (
                  <g
                    key={r.id}
                    role="button"
                    tabIndex={0}
                    aria-label={
                      '関係 ' +
                      r.from +
                      ' (' +
                      r.columns.join(', ') +
                      ') → ' +
                      r.to +
                      ' (' +
                      r.targetColumns.join(', ') +
                      ')'
                    }
                    aria-pressed={relation === r.id}
                    className={active ? 'selected' : ''}
                    onClick={() => onRelation(r)}
                    onKeyDown={(e) => {
                      if (['Enter', ' '].includes(e.key)) {
                        e.preventDefault();
                        onRelation(r);
                      }
                    }}
                  >
                    <title>
                      {fromTable.logicalName} → {toTable.logicalName}: {r.definition}
                    </title>
                    {r.columns.map((c, i) => {
                      const sx = from.x + (outgoing ? 360 : 0),
                        tx = to.x + (outgoing ? 0 : 360);
                      const sy =
                        from.y +
                        58 +
                        fromTable.columns.findIndex((col) => col.name === c) * 38 +
                        19;
                      const ty =
                        to.y +
                        58 +
                        toTable.columns.findIndex((col) => col.name === r.targetColumns[i]) * 38 +
                        19;
                      const same = from.x === to.x;
                      const bend = same
                        ? from.x - 35 - (ri % 5) * 12
                        : (sx + tx) / 2 + (ri % 5) * 8;
                      const end = same ? to.x : tx;
                      const path = `M ${sx} ${sy} C ${bend} ${sy}, ${bend} ${ty}, ${end} ${ty}`;
                      return (
                        <g key={c}>
                          <path className="db-edge-hit" d={path} />
                          <path className="db-edge" d={path} markerEnd="url(#db-arrow)" />
                        </g>
                      );
                    })}
                  </g>
                );
              })}
          </svg>
          {visible.map((t) => (
            <section
              key={t.name}
              className={'db-node' + (selected === t.name ? ' is-selected' : '')}
              style={{ left: positions.get(t.name)!.x, top: positions.get(t.name)!.y }}
            >
              <button
                className="db-node-title"
                aria-label={'テーブル ' + t.name}
                aria-pressed={selected === t.name}
                title={t.logicalName + ' / ' + t.name + ' — ' + t.description}
                onPointerDown={(e) => {
                  if (e.button > 0) return;
                  e.stopPropagation();
                  drag.current = { name: t.name, x: e.clientX, y: e.clientY, moved: false };
                  e.currentTarget.setPointerCapture(e.pointerId);
                }}
                onPointerMove={(e) => {
                  const d = drag.current;
                  if (!d || d.name !== t.name || !e.currentTarget.hasPointerCapture(e.pointerId))
                    return;
                  const dx = e.clientX - d.x,
                    dy = e.clientY - d.y;
                  if (!d.moved && Math.hypot(dx, dy) < 4) return;
                  d.moved = true;
                  const p = positions.get(t.name)!;
                  setOffsets((old) => ({
                    ...old,
                    [t.name]: {
                      x: Math.max(10, p.x + dx / view.scale),
                      y: Math.max(10, p.y + dy / view.scale),
                    },
                  }));
                  d.x = e.clientX;
                  d.y = e.clientY;
                }}
                onPointerCancel={() => {
                  drag.current = null;
                }}
                onClick={() => {
                  if (!drag.current?.moved) onSelect(t.name);
                  drag.current = null;
                }}
                onDoubleClick={center}
              >
                <strong>{nameMode === 'physical' ? t.name : t.logicalName}</strong>
                <small>{nameMode === 'both' ? t.name : t.columns.length + ' カラム'}</small>
              </button>
              {t.columns.map((c) => (
                <button
                  key={c.name}
                  className={
                    'db-node-column' +
                    (selected === t.name && column === c.name ? ' is-selected' : '')
                  }
                  aria-label={'カラム ' + t.name + '.' + c.name}
                  aria-pressed={selected === t.name && column === c.name}
                  onClick={() => onColumn(t.name, c.name)}
                  title={
                    c.logicalName +
                    ' / ' +
                    c.name +
                    ' — ' +
                    c.description +
                    ' / NULL ' +
                    (c.nullable ? '可' : '不可')
                  }
                >
                  <span className="db-key-mark">
                    {c.primaryKey
                      ? 'PK'
                      : relationships.some((r) => r.from === t.name && r.columns.includes(c.name))
                        ? 'FK'
                        : ''}
                  </span>
                  <span className="db-field-name">
                    <strong>{nameMode === 'physical' ? c.name : c.logicalName}</strong>
                    {nameMode === 'both' && <small>{c.name}</small>}
                  </span>
                  <span className="db-field-type">
                    {c.type}
                    <small>{c.nullable ? 'NULL' : 'NOT NULL'}</small>
                  </span>
                </button>
              ))}
            </section>
          ))}
        </div>
      </div>
      <div className="db-minimap" aria-label="ER図のミニマップ">
        <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="全体の配置と表示範囲">
          <rect width={width} height={height} fill="#edf2f7" />
          {visible.map((t) => {
            const p = positions.get(t.name)!;
            return (
              <rect
                key={t.name}
                x={p.x}
                y={p.y}
                width="360"
                height={p.height}
                fill={t.name === selected ? '#397ad2' : '#aabacd'}
              />
            );
          })}
          <rect
            x={-view.x / view.scale}
            y={-view.y / view.scale}
            width={size.width / view.scale}
            height={size.height / view.scale}
            fill="#397ad211"
            stroke="#173e76"
            strokeWidth="12"
          />
        </svg>
        <button onClick={fit}>全体を表示</button>
      </div>
    </section>
  );
}
