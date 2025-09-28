import { apiFetch } from '../../lib/api';
import { requireSession } from '../../lib/auth/session';

interface CompetencyEntry {
  competency: {
    id: number;
    name: string;
    category: string;
  };
  level: number;
}

interface LeaderboardRow {
  user_id: number;
  full_name: string;
  rank_title: string | null;
  xp: number;
  mana: number;
  completed_missions: number;
  competencies: CompetencyEntry[];
}

async function fetchLeaderboard(token: string) {
  return apiFetch<LeaderboardRow[]>('/api/leaderboard', { authToken: token });
}

function CompetencyChips({ competencies }: { competencies: CompetencyEntry[] }) {
  if (!competencies.length) {
    return <span style={{ color: 'var(--text-muted)' }}>Нет данных</span>;
  }

  return (
    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
      {competencies.map((entry) => (
        <span
          key={entry.competency.id}
          style={{
            fontSize: '0.85rem',
            padding: '0.35rem 0.75rem',
            borderRadius: '999px',
            background: 'rgba(108, 92, 231, 0.18)',
            border: '1px solid rgba(108,92,231,0.35)'
          }}
        >
          {entry.competency.name} · {entry.level}
        </span>
      ))}
    </div>
  );
}

export default async function LeaderboardPage() {
  const session = await requireSession();
  const rows = await fetchLeaderboard(session.token);

  return (
    <section>
      <h2>Лидерборд пилотов</h2>
      <p style={{ color: 'var(--text-muted)', maxWidth: '720px' }}>
        Здесь собраны все пилоты программы, отсортированные по опыту. HR может использовать таблицу как быстрый срез
        прогресса и компетенций, а кандидаты — видеть своё место в космофлоте.
      </p>

      <div className="card" style={{ marginTop: '1.5rem', overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '720px' }}>
          <thead>
            <tr style={{ textAlign: 'left', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              <th style={{ padding: '0.75rem 1rem' }}>#</th>
              <th style={{ padding: '0.75rem 1rem' }}>Пилот</th>
              <th style={{ padding: '0.75rem 1rem' }}>Ранг</th>
              <th style={{ padding: '0.75rem 1rem' }}>Опыт</th>
              <th style={{ padding: '0.75rem 1rem' }}>Мана</th>
              <th style={{ padding: '0.75rem 1rem' }}>Завершено миссий</th>
              <th style={{ padding: '0.75rem 1rem' }}>Компетенции</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={row.user_id} style={{ borderTop: '1px solid rgba(162, 155, 254, 0.15)' }}>
                <td style={{ padding: '0.75rem 1rem', width: '48px' }}>{index + 1}</td>
                <td style={{ padding: '0.75rem 1rem' }}>
                  <strong>{row.full_name}</strong>
                </td>
                <td style={{ padding: '0.75rem 1rem' }}>{row.rank_title ?? '—'}</td>
                <td style={{ padding: '0.75rem 1rem' }}>{row.xp}</td>
                <td style={{ padding: '0.75rem 1rem' }}>{row.mana}</td>
                <td style={{ padding: '0.75rem 1rem' }}>{row.completed_missions}</td>
                <td style={{ padding: '0.75rem 1rem' }}>
                  <CompetencyChips competencies={row.competencies} />
                </td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td colSpan={7} style={{ padding: '1rem 1rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                  Пока нет данных — завершите первую миссию, чтобы попасть в лидерборд.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
