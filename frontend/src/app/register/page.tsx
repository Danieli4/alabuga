import { redirect } from 'next/navigation';
import { apiFetch } from '../../lib/api';
import { createSession, getSession } from '../../lib/auth/session';

import styles from './styles.module.css';

// Server Action: оформляет регистрацию и в зависимости от настроек либо сразу
// авторизует пользователя, либо перенаправляет его на страницу входа
// с подсказкой подтвердить почту.
async function registerAction(formData: FormData) {
  'use server';

  // 1. Извлекаем значения из формы. Метод `FormData.get` возвращает `FormDataEntryValue` | null,
  //    поэтому приводим к строке и удаляем пробелы по краям.
  const fullName = String(formData.get('fullName') ?? '').trim();
  const email = String(formData.get('email') ?? '').trim();
  const password = String(formData.get('password') ?? '').trim();
  // Необязательные поля переводим в undefined, чтобы backend не записывал пустые строки.
  const preferredBranch = String(formData.get('preferredBranch') ?? '').trim() || undefined;
  const motivation = String(formData.get('motivation') ?? '').trim() || undefined;

  if (!fullName || !email || !password) {
    redirect('/register?error=' + encodeURIComponent('Заполните имя, email и пароль.'));
  }

  try {
    // 2. Собираем payload в формате, который ожидает FastAPI.
    const payload = { full_name: fullName, email, password, preferred_branch: preferredBranch, motivation };
    const response = await apiFetch<any>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    if (response && 'access_token' in response) {
      // 3a. Если подтверждение почты отключено — получаем JWT, создаём сессию и отправляем пилота на онбординг.
      createSession({ token: response.access_token, role: 'pilot', fullName });
      redirect('/onboarding');
    }

    // 3b. При включённом подтверждении backend возвращает текст подсказки и debug-код.
    const detail = response?.detail ?? 'Проверьте почту для подтверждения.';
    const debug = response?.debug_token ? ` Код: ${response.debug_token}` : '';
    redirect('/login?info=' + encodeURIComponent(`${detail}${debug}`));
  } catch (error) {
    console.error('Registration failed:', error);
    // 4. Любые сетевые/серверные ошибки показываем пользователю через query string.
    const message = error instanceof Error ? error.message : 'Не удалось завершить регистрацию.';
    redirect('/register?error=' + encodeURIComponent(message));
  }
}

export default async function RegisterPage({ searchParams }: { searchParams: { error?: string } }) {
  const existing = await getSession();
  if (existing) {
    redirect(existing.role === 'hr' ? '/admin' : '/');
  }

  const errorMessage = searchParams.error;

  return (
    <section className={styles.container}>
      <form className={styles.form} action={registerAction}>
        <h1>Регистрация пилота</h1>
        <p className={styles.hint}>
          После регистрации вы попадёте на онбординг и сможете выполнять миссии.
          Если включено подтверждение почты, мы отправим код на указанную почту.
        </p>

        {errorMessage && <p className={styles.error}>{errorMessage}</p>}

        <label className={styles.field}>
          Полное имя
          <input className={styles.input} name="fullName" required placeholder="Как к вам обращаться" />
        </label>
        <label className={styles.field}>
          Email
          <input className={styles.input} type="email" name="email" required placeholder="user@alabuga.space" />
        </label>
        <label className={styles.field}>
          Пароль
          <input className={styles.input} type="password" name="password" required placeholder="Придумайте пароль" />
        </label>
        <label className={styles.field}>
          Интересующая ветка (необязательно)
          <select className={styles.input} name="preferredBranch" defaultValue="">
            <option value="">Выберите ветку</option>
            <option value="Получение оффера">Получение оффера</option>
            <option value="Рекрутинг">Рекрутинг</option>
            <option value="Квесты">Квесты</option>
            <option value="Симулятор">Симулятор</option>
            <option value="Лекторий">Лекторий</option>
          </select>
        </label>
        <label className={styles.field}>
          Что хотите добиться?
          <textarea className={styles.textarea} name="motivation" rows={3} placeholder="Например: хочу собрать портфолио и познакомиться с командой" />
        </label>
        <button className={styles.submit} type="submit">Создать аккаунт</button>
        <p className={styles.footer}>
          Уже есть аккаунт? <a href="/login">Войдите</a>.
        </p>
      </form>
    </section>
  );
}
