import { toast } from 'react-toastify';
import type { SentraError } from './httpClient';

export const notifyError = (err: unknown): void => {
  const e = err as SentraError;
  const msg = `[${e.code}] ${e.message}`;
  const suggestion = e.suggestion ? ` – ${e.suggestion}` : '';
  const id = e.requestId ? ` (#${e.requestId.slice(0, 8)})` : '';

  toast.error(`${msg}${suggestion}${id}`);
};

export const notifySuccess = (msg: string): void => {
  toast.success(msg);
};

export const notifyInfo = (msg: string): void => {
  toast.info(msg);
};
