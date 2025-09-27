import { redirect } from 'next/navigation';
import { apiFetch } from '../../lib/api';
import { createSession, getSession } from '../../lib/auth/session';

import styles from './styles.module.css';

// Server Action: выполняет проверку логина, создаёт сессию и перенаправляет пользователя.
async function authenticate(formData: FormData) {
  'use server';

  const email = String(formData.get('email') ?? '').trim();
  const password = String(formData.get('password') ?? '').trim();

  if (!email || !password) {
    redirect('/login?error=' + encodeURIComponent('Введите email и пароль.'));
  }

  try {
    // 1. Запрашиваем у backend JWT.
    const { access_token: token } = await apiFetch<{ access_token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    // 2. Валидируем токен и получаем роль/имя для приветствия.
    const profile = await apiFetch<{ full_name: string; role: 'pilot' | 'hr' }>(
      '/auth/me',
      { authToken: token }
    );

    // 3. Сохраняем токен в httpOnly-cookie, чтобы браузер запомнил сессию.
    createSession({ token, role: profile.role, fullName: profile.full_name });

    // 4. Перенаправляем пользователя на подходящий раздел.
    redirect(profile.role === 'hr' ? '/admin' : '/');
  } catch (error) {
    console.error('Login failed:', error);
    let message = 'Неверный email или пароль. Попробуйте ещё раз.';
    if (error instanceof Error && error.message.includes('Подтвердите e-mail')) {
      message = 'Почта не подтверждена. Запросите письмо с кодом и завершите подтверждение.';
    }
    redirect('/login?error=' + encodeURIComponent(message));
  }
}

export default async function LoginPage({
  searchParams
}: {
  searchParams: { error?: string; info?: string };
}) {
  // Если пользователь уже вошёл, сразу перенаправляем его на рабочую страницу.
  const existing = await getSession();
  if (existing) {
    redirect(existing.role === 'hr' ? '/admin' : '/');
  }

  const message = searchParams.error;
  const info = searchParams.info;

  return (
    <section className={styles.container}>
      <form className={styles.form} action={authenticate}>
        <h1>Вход в Mission Control</h1>
        {/* Подсказка для демо-режима, чтобы не искать логин/пароль в README. */}
        <p className={styles.hint}>
          Используйте демо-учётные записи: <strong>candidate@alabuga.space / orbita123</strong> или
          <strong> hr@alabuga.space / orbita123</strong>.
        </p>

        {info && <p className={styles.info}>{info}</p>}
        {message && <p className={styles.error}>{message}</p>}

        <label className={styles.field}>
          Email
          <input className={styles.input} type="email" name="email" required placeholder="user@alabuga.space" />
        </label>
        <label className={styles.field}>
          Пароль
          <input className={styles.input} type="password" name="password" required placeholder="Введите пароль" />
        </label>
        <button className={styles.submit} type="submit">Войти</button>
        <p className={styles.footer}>
          Впервые на платформе? <a href="/register">Зарегистрируйтесь и начните путь пилота.</a>
        </p>
      </form>
    </section>
  );
}
