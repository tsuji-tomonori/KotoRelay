import { createContext, useContext, useEffect, useId } from 'react';
export const Workspace = createContext<{
  dirty: (key: string, value: boolean) => void;
  navigate: (action: () => void) => void;
} | null>(null);
export function useUnsaved(value: boolean) {
  const workspace = useContext(Workspace);
  const key = useId();
  const dirty = workspace?.dirty;
  useEffect(() => {
    dirty?.(key, value);
    return () => dirty?.(key, false);
  }, [dirty, key, value]);
  useEffect(() => {
    const prevent = (event: BeforeUnloadEvent) => {
      if (value) event.preventDefault();
    };
    window.addEventListener('beforeunload', prevent);
    return () => window.removeEventListener('beforeunload', prevent);
  }, [value]);
  return { navigate: workspace?.navigate, markSaved: () => dirty?.(key, false) };
}
