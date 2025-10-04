const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const SERVER_API_URL = process.env.NEXT_INTERNAL_API_URL || CLIENT_API_URL;

export const clientApiUrl = CLIENT_API_URL;
export const serverApiUrl = SERVER_API_URL;

export interface RequestOptions extends RequestInit {
  authToken?: string;
}

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData;

  if (!isFormData && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (options.authToken) {
    headers.set('Authorization', `Bearer ${options.authToken}`);
  }

  const baseUrl = typeof window === 'undefined' ? SERVER_API_URL : CLIENT_API_URL;
  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers,
    cache: 'no-store'
  });

  if (!response.ok) {
    const contentType = response.headers.get('content-type') ?? '';
    if (contentType.includes('application/json')) {
      try {
        const data = await response.json();
        const detail = data?.detail ?? data?.message ?? data?.error;
        if (detail) {
          throw new Error(String(detail));
        }
        throw new Error(`Запрос завершился ошибкой (${response.status}).`);
      } catch (parseError) {
        if (parseError instanceof Error) {
          throw parseError;
        }
        throw new Error(`Запрос завершился ошибкой (${response.status}).`);
      }
    }

    const text = await response.text();
    throw new Error(text || `Запрос завершился ошибкой (${response.status}).`);
  }
  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return response.json() as Promise<T>;
  }

  const raw = await response.text();
  return raw as unknown as T;
}
