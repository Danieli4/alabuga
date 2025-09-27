// В этом модуле собраны утилиты для работы с сессией пользователя на сервере.
// Мы храним JWT и базовую информацию о пользователе в httpOnly-cookie,
// чтобы управлять правами доступа без дублирования логики на каждом экране.

import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

import { apiFetch } from '../api';

interface SessionPayload {
  token: string;
  role: 'pilot' | 'hr';
  fullName: string;
}

const SESSION_COOKIE = 'alabuga_session';

function parseSession(raw: string | undefined): SessionPayload | null {
  // Cookie может отсутствовать либо быть повреждённой, поэтому парсинг
  // оборачиваем в try/catch и возвращаем null, если что-то пошло не так.
  if (!raw) return null;
  try {
    return JSON.parse(raw) as SessionPayload;
  } catch (error) {
    console.error('Failed to parse session cookie:', error);
    return null;
  }
}

export async function getSession(): Promise<SessionPayload | null> {
  // Читаем cookie и, если токен действительно есть, дополнительно проверяем его
  // на сервере вызовом `/auth/me`. Так мы гарантируем, что вернём только
  // актуальные сессии, а устаревшие токены удалим.
  const store = cookies();
  const session = parseSession(store.get(SESSION_COOKIE)?.value);
  if (!session) {
    return null;
  }

  try {
    await apiFetch('/auth/me', { authToken: session.token });
    return session;
  } catch (error) {
    console.warn('Session validation failed:', error);
    store.delete(SESSION_COOKIE);
    return null;
  }
}

export async function requireSession(): Promise<SessionPayload> {
  // В случае отсутствия сессии сразу отправляем пользователя на страницу входа.
  const session = await getSession();
  if (!session) {
    redirect('/login');
  }
  return session;
}

export async function requireRole(role: SessionPayload['role']): Promise<SessionPayload> {
  // Дополнительная проверка права доступа: если роль не совпадает, выполняем
  // безопасный редирект на подходящую страницу (пилоты возвращаются на дашборд,
  // а HR — в админку).
  const session = await requireSession();
  if (session.role !== role) {
    if (role === 'hr') {
      redirect('/');
    }
    redirect('/admin');
  }
  return session;
}

export function createSession(session: SessionPayload) {
  // Сохраняем данные в httpOnly-cookie, чтобы клиентский JavaScript не имел к ним доступа.
  const store = cookies();
  store.set(SESSION_COOKIE, JSON.stringify(session), {
    httpOnly: true,
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production',
    path: '/',
    maxAge: 60 * 60 * 12,
  });
}

export function destroySession() {
  // Удаление cookie при выходе пользователя.
  cookies().delete(SESSION_COOKIE);
}
