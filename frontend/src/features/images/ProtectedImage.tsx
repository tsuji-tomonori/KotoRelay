import { useEffect, useState } from 'react';
import { getImage } from '../../lib/api';
export function ProtectedImage({
  token,
  id,
  version,
  alt = '文書の添付画像',
}: {
  token: string;
  id: string;
  version?: string;
  alt?: string;
}) {
  const [url, setUrl] = useState('');
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    let active = true;
    setUrl('');
    setFailed(false);
    let objectUrl = '';
    getImage(token, id, version)
      .then((value) => {
        objectUrl = value;
        if (active) setUrl(value);
        else URL.revokeObjectURL(value);
      })
      .catch(() => {
        if (active) setFailed(true);
      });
    return () => {
      active = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [token, id, version]);
  return failed ? (
    <p>画像を表示できません。</p>
  ) : url ? (
    <img src={url} alt={alt} />
  ) : (
    <span>画像を読み込み中…</span>
  );
}
