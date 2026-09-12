export interface Document {
  id: string;
  title: string;
  department_id: string;
  latest_version_id: string | null;
  revision: number;
  next_version: number;
  status: string;
  visibility: string;
  shared_departments: string;
  updated_at: string;
}
export interface Membership {
  id: string;
  user_id: string;
  department_id: string;
  leader: boolean;
  can_author: boolean;
  can_review: boolean;
  active: boolean;
}
export interface Identity {
  user: { id: string; display_name: string; operator: boolean };
  departments: { id: string; name: string }[];
  memberships: Membership[];
  mode: string;
}
export interface Placement {
  id: string;
  asset_id: string;
  ocr_run_id: string;
  offset: number;
  heading: string;
}
export interface Draft {
  document: Document;
  body: string;
  revision: number;
  placements: Placement[];
}
export interface Region {
  text: string;
  x: number;
  y: number;
  width: number;
  height: number;
  confidence: number;
  order: number;
}
export interface Ocr {
  regions: Region[];
  status: string;
  engine: string;
}
export interface Version {
  id: string;
  document_id: string;
  number: number;
  title: string;
  manifest_hash: string;
  created_by: string;
  created_at: string;
  manifest: string;
}
export interface Submission {
  id: string;
  document_id: string;
  version_id: string;
  status: string;
  manifest_hash: string;
  reason: string;
  created_at: string;
  decided_at: string | null;
}
export interface Review {
  submission: Submission;
  title: string;
  can_review: boolean;
}
export interface ReadDocument {
  document: Document;
  version: Version;
  body: string;
  index_ready: boolean;
}
export interface Citation {
  document_id: string;
  version_id: string;
  chunk_id: string;
  title: string;
  heading: string;
}
export interface Answer {
  id: string;
  conversation_id: string;
  question: string;
  answer: string;
  status: string;
  citations: Citation[];
  model: string;
  created_at: string;
}
export interface Job {
  id: string;
  document_id: string;
  kind: string;
  status: string;
  attempts: number;
  error_code: string;
}
export interface Metrics {
  questions: number;
  views: number;
  unique_viewers: number;
  outcomes: Record<string, number>;
  generated_at: string;
  timezone: string;
  documents: { id: string; title: string; views: number; contributions: number }[];
}
export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
  ) {
    super(message);
  }
}
export type Api = <T>(path: string, method?: string, data?: unknown, key?: string) => Promise<T>;
export function createApi(token: string): Api {
  return async <T>(path: string, method = 'GET', data?: unknown, key?: string): Promise<T> => {
    const headers: Record<string, string> = { Authorization: `Bearer ${token}` };
    if (data !== undefined && !(data instanceof FormData))
      headers['Content-Type'] = 'application/json';
    if (key) headers['Idempotency-Key'] = key;
    const response = await fetch(`/api${path}`, {
      method,
      headers,
      body: data instanceof FormData ? data : data === undefined ? undefined : JSON.stringify(data),
      cache: 'no-store',
    });
    if (!response.ok) {
      const error = (await response.json()) as { code: string; message: string };
      throw new ApiError(response.status, error.code, error.message);
    }
    return (await response.json()) as T;
  };
}
export async function getImage(token: string, id: string, version?: string): Promise<string> {
  const response = await fetch(`/api/images/${id}${version ? `?version_id=${version}` : ''}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: 'no-store',
  });
  if (!response.ok) throw new Error('画像を取得できません。');
  return URL.createObjectURL(await response.blob());
}
export const personaNames: Record<string, string> = {
  author: '執筆者',
  reviewer: '承認者',
  reader: '閲覧者',
  leader: '部署リーダー',
  operator: '運用者',
  other: '他部署の閲覧者',
};
export function formatDate(value: string): string {
  return new Intl.DateTimeFormat('ja-JP', {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: 'Asia/Tokyo',
  }).format(new Date(value));
}
export function statusLabel(status: string): string {
  return (
    (
      {
        active: '公開可能',
        withdrawn: '公開停止',
        deleted: '削除済み',
        pending: '審査待ち',
        approved: '承認済み',
        rejected: '却下',
        done: '反映済み',
        failed: '失敗',
        obsolete: '失効',
        retained: '保持期間中',
        answered: '回答済み',
        held: '回答保留',
        hidden: '非表示',
      } as Record<string, string>
    )[status] ?? status
  );
}
