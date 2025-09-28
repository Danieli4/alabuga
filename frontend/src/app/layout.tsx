import type { Metadata } from 'next';
import StyledComponentsRegistry from '../lib/styled-registry';
import '../styles/globals.css';
import { getSession } from '../lib/auth/session';

export const metadata: Metadata = {
  title: 'Автостопом по Алабуге',
  description: 'Галактогид по миссиям и рангам Алабуги в духе «Автостопом по Галактике»'
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  // Пробуем получить сессию (если пользователь не авторизован, вернётся null).
  const session = await getSession();

  // Сохраняем подсказки, кто сейчас вошёл и включил ли HR режим «просмотра глазами пилота».
  const isHr = session?.role === 'hr';
  const viewingAsPilot = Boolean(session?.viewAsPilot);

  // Формируем пункты меню в зависимости от текущего режима.
  let links: Array<{ href: string; label: string }> = [];

  if (!session) {
    links = [{ href: '/login', label: 'Войти' }];
  } else if (isHr && !viewingAsPilot) {
    links = [
      { href: '/admin', label: 'HR панель' },
      { href: '/leaderboard', label: 'Лидерборд' },
      { href: '/admin/view-as', label: 'Просмотр от лица пилота' },
    ];
  } else {
    links = [
      { href: '/', label: 'Дашборд' },
      { href: '/onboarding', label: 'Онбординг' },
      { href: '/missions', label: 'Миссии' },
      { href: '/journal', label: 'Журнал' },
      { href: '/store', label: 'Магазин' },
      { href: '/leaderboard', label: 'Лидерборд' },
    ];
    if (isHr) {
      // Дополнительный пункт для HR: быстрый выход из режима просмотра.
      links.push({ href: '/admin/exit-view', label: 'Вернуться к HR' });
    }
  }

  return (
    <html lang="ru">
      <body style={{ backgroundAttachment: 'fixed' }}>
        <StyledComponentsRegistry>
          <header
            style={{
              padding: '1.5rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              background:
                'linear-gradient(135deg, rgba(108,92,231,0.25), rgba(0,184,148,0.15))',
              borderBottom: '1px solid rgba(162, 155, 254, 0.2)',
              boxShadow: '0 10px 30px rgba(0,0,0,0.25)'
            }}
          >
            <div>
              <h1 style={{ margin: 0, letterSpacing: '0.08em', textTransform: 'uppercase' }}>Автостопом по Алабуге</h1>
              <p style={{ margin: 0, color: 'var(--text-muted)' }}>
                Всегда держите полотенце под рукой и следуйте подсказкам бортового гидронавигатора
              </p>
            </div>
            <nav style={{ display: 'flex', gap: '1rem', alignItems: 'center', fontWeight: 500 }}>
              {links.map((link) => (
                <a key={link.href} href={link.href}>
                  {link.label}
                </a>
              ))}
              {viewingAsPilot && (
                <span style={{
                  color: '#ffeaa7',
                  fontSize: '0.85rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.08em'
                }}>
                  режим просмотра пилота
                </span>
              )}
              {session && (
                <>
                  <span style={{ color: 'var(--text-muted)', marginLeft: '1rem' }}>
                    {session.fullName} · {session.role === 'hr' ? 'HR' : 'Пилот'}
                  </span>
                  <a href="/logout" style={{ fontWeight: 600 }}>
                    Выйти
                  </a>
                </>
              )}
            </nav>
          </header>
          <main>{children}</main>
        </StyledComponentsRegistry>
      </body>
    </html>
  );
}
