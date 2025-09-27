import type { Metadata } from 'next';
import StyledComponentsRegistry from '../lib/styled-registry';
import '../styles/globals.css';
import { getSession } from '../lib/auth/session';

export const metadata: Metadata = {
  title: 'Alabuga Mission Control',
  description: 'Космический модуль геймификации для пилотов Алабуги'
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  // Пробуем получить сессию (если пользователь не авторизован, вернётся null).
  const session = await getSession();

  // Формируем список пунктов меню в зависимости от роли пользователя.
  const links = session
    ? [
        { href: '/', label: 'Дашборд' },
        { href: '/onboarding', label: 'Онбординг' },
        { href: '/missions', label: 'Миссии' },
        { href: '/journal', label: 'Журнал' },
        { href: '/store', label: 'Магазин' },
        ...(session.role === 'hr' ? [{ href: '/admin', label: 'HR панель' }] : []),
      ]
    : [{ href: '/login', label: 'Войти' }];

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
              <h1 style={{ margin: 0, letterSpacing: '0.08em', textTransform: 'uppercase' }}>Mission Control</h1>
              <p style={{ margin: 0, color: 'var(--text-muted)' }}>
                Путь пилота от искателя до командира космической эскадры
              </p>
            </div>
            <nav style={{ display: 'flex', gap: '1rem', alignItems: 'center', fontWeight: 500 }}>
              {links.map((link) => (
                <a key={link.href} href={link.href}>
                  {link.label}
                </a>
              ))}
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
