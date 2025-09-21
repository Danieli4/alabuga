import { apiFetch } from './api';

let cachedToken: string | null = null;

export async function getDemoToken() {
  if (cachedToken) {
    return cachedToken;
  }

  const email = process.env.NEXT_PUBLIC_DEMO_EMAIL ?? 'candidate@alabuga.space';
  const password = process.env.NEXT_PUBLIC_DEMO_PASSWORD ?? 'orbita123';

  const data = await apiFetch<{ access_token: string }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password })
  });

  cachedToken = data.access_token;
  return cachedToken;
}
