import { vi } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import type { Api, Document, Identity, Placement } from '../src/lib/api';
export const identity: Identity = {
  user: { id: 'u1', display_name: '架空の執筆者', operator: true },
  departments: [{ id: 'd1', name: '開発部' }],
  memberships: [
    {
      id: 'm1',
      user_id: 'u1',
      department_id: 'd1',
      leader: true,
      can_author: true,
      can_review: true,
      active: true,
    },
  ],
  mode: 'local',
};
export const doc: Document = {
  id: 'doc1',
  title: '開発ガイド',
  department_id: 'd1',
  latest_version_id: 'v1',
  revision: 2,
  next_version: 2,
  status: 'active',
  visibility: 'department',
  shared_departments: '[]',
  updated_at: '2026-09-12T00:00:00Z',
};
export const version = {
  id: 'v1',
  document_id: 'doc1',
  number: 1,
  title: doc.title,
  manifest_hash: 'a'.repeat(64),
  created_by: 'u2',
  created_at: doc.updated_at,
  manifest: '{"images":[]}',
};
export const submission = {
  id: 's1',
  document_id: 'doc1',
  version_id: 'v1',
  status: 'pending',
  manifest_hash: version.manifest_hash,
  reason: '',
  created_at: doc.updated_at,
  decided_at: null,
};
export const placement: Placement = {
  id: 'p1',
  asset_id: 'a1',
  ocr_run_id: 'o1',
  offset: 0,
  heading: '画像',
};
export const region = {
  region_id: 'r1',
  source: 'detected',
  text: '画像の文字',
  x: 0,
  y: 0,
  width: 1,
  height: 1,
  confidence: 1,
  order: 0,
};
export const answer = {
  id: 'a1',
  conversation_id: 'c1',
  question: '開発フロー',
  answer: '承認します',
  status: 'answered',
  citations: [
    { document_id: 'doc1', version_id: 'v1', chunk_id: 'k1', title: doc.title, heading: '手順' },
  ],
  model: 'local-extractive-v1',
  created_at: doc.updated_at,
};
export function mockApi(
  handler: (path: string, method?: string, data?: unknown) => unknown = () => [],
) {
  const calls = vi.fn(handler);
  const api: Api = async <T>(path: string, method?: string, data?: unknown) => {
    const value = await calls(path, method, data);
    return (
      path.startsWith('/documents?') && path.includes('page=true') && Array.isArray(value)
        ? { items: value, has_next: value.length === 30 }
        : value
    ) as T;
  };
  return { api, calls };
}
export function fill(label: string, value: string) {
  fireEvent.change(screen.getByLabelText(label), { target: { value } });
}
export const error = () => vi.fn();
