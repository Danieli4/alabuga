import type { Metadata } from 'next';
import StyledComponentsRegistry from '../lib/styled-registry';
import '../styles/globals.css';

export const metadata: Metadata = {
  title: 'Alabuga Mission Control',
  description: 'Космический модуль геймификации для пилотов Алабуги'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
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
              <a href="/">Дашборд</a>
              <a href="/onboarding">Онбординг</a>
              <a href="/missions">Миссии</a>
              <a href="/journal">Журнал</a>
              <a href="/store">Магазин</a>
              <a href="/admin">HR Панель</a>
            </nav>
          </header>
          <main>{children}</main>
        </StyledComponentsRegistry>
      </body>
    </html>
  );
}
