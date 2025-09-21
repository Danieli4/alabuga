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
      <body>
        <StyledComponentsRegistry>
          <header style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between' }}>
            <div>
              <h1 style={{ margin: 0 }}>Mission Control</h1>
              <p style={{ margin: 0, color: 'var(--text-muted)' }}>
                Путь пилота от искателя до члена экипажа
              </p>
            </div>
            <nav style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <a href="/">Дашборд</a>
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
