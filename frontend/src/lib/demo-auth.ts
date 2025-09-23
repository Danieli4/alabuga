import { apiFetch } from './api';

type DemoRole = 'pilot' | 'hr';

const tokenCache: Partial<Record<DemoRole, string>> = {};

function resolveCredentials(role: DemoRole) {
  if (role === 'hr') {
    const email = process.env.NEXT_PUBLIC_DEMO_HR_EMAIL ?? 'hr@alabuga.space';
    const password =
      process.env.NEXT_PUBLIC_DEMO_HR_PASSWORD ?? process.env.NEXT_PUBLIC_DEMO_PASSWORD ?? 'orbita123';
    return { email, password };
  }

  return {
    email: process.env.NEXT_PUBLIC_DEMO_EMAIL ?? 'candidate@alabuga.space',
    password: process.env.NEXT_PUBLIC_DEMO_PASSWORD ?? 'orbita123'
  };
}

export async function getDemoToken(role: DemoRole = 'pilot') {
  const cachedToken = tokenCache[role];
  if (cachedToken) {
    return cachedToken;
  }

  const credentials = resolveCredentials(role);

  const data = await apiFetch<{ access_token: string }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials)
  });

  tokenCache[role] = data.access_token;
  return data.access_token;
}
