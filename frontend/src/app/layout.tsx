import type { Metadata } from 'next';
import Link from 'next/link';
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
              padding: '1.2rem 1.5rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              background: 'linear-gradient(135deg, rgba(0, 93, 172, 0.3), rgba(0, 174, 239, 0.2))',
              borderBottom: '1px solid rgba(106, 207, 246, 0.2)',
              boxShadow: '0 10px 30px rgba(0,0,0,0.25)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              {/* Логотип - замени путь на актуальный */}
              <img 
                src="/artifacts/logo-white-ru.png" 
                alt="Alabuga logo" 
                style={{ 
                  width: '160px', 
                  height: '35px',
                  objectFit: 'contain',
                  borderRadius: '0px'
                }} 
              />
              
              {/* Вертикальный разделитель */}
              <div 
                style={{
                  width: '1px',
                  height: '35px',
                  backgroundColor: 'rgba(255, 255, 255, 0.3)'
                }}
              />
              
              {/* Заголовок */}
              <h1 
                style={{ 
                  margin: 0, 
                  letterSpacing: '0.05em',
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  textTransform: 'none',
                  lineHeight: '1.2'
                }}
              >
                Автостопом<br />по Алабуге
              </h1>
            </div>
            
            <nav style={{ 
              display: 'flex', 
              gap: '1rem', 
              alignItems: 'center', 
              fontWeight: 500,
              fontSize: '0.9rem'
            }}>
              {links.map((link) => (
                <Link key={link.href} href={link.href}>
                  {link.label}
                </Link>
              ))}
              {viewingAsPilot && (
                <span style={{
                  color: '#ffeaa7',
                  fontSize: '0.8rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.08em'
                }}>
                  режим просмотра пилота
                </span>
              )}
              {session && (
                <>
                  <Link href="/profile" style={{ 
                    marginLeft: '1rem',
                    color: 'var(--text-muted)',
                    fontSize: '0.85rem'
                  }}>
                    {session.fullName}
                  </Link>
                  <Link href="/logout" style={{ fontWeight: 600, fontSize: '0.9rem' }}>
                    Выйти
                  </Link>
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
