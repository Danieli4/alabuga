import { apiFetch } from '../../lib/api';
import { getDemoToken } from '../../lib/demo-auth';
import { JournalTimeline } from '../../components/JournalTimeline';

interface JournalEntry {
  id: number;
  title: string;
  description: string;
  event_type: string;
  xp_delta: number;
  mana_delta: number;
  created_at: string;
}

interface LeaderboardEntry {
  user_id: number;
  full_name: string;
  xp_delta: number;
  mana_delta: number;
}

interface LeaderboardResponse {
  period: string;
  entries: LeaderboardEntry[];
}

async function fetchJournal() {
  const token = await getDemoToken();
  const [entries, week, month, year] = await Promise.all([
    apiFetch<JournalEntry[]>('/api/journal/', { authToken: token }),
    apiFetch<LeaderboardResponse>('/api/journal/leaderboard?period=week', { authToken: token }),
    apiFetch<LeaderboardResponse>('/api/journal/leaderboard?period=month', { authToken: token }),
    apiFetch<LeaderboardResponse>('/api/journal/leaderboard?period=year', { authToken: token })
  ]);
  return { entries, leaderboards: [week, month, year] };
}

export default async function JournalPage() {
  const { entries, leaderboards } = await fetchJournal();

  return (
    <section className="grid" style={{ gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
      <div>
        <h2>Бортовой журнал</h2>
        <p style={{ color: 'var(--text-muted)' }}>
          Здесь фиксируется каждый шаг: отправка миссий, повышение ранга, получение артефактов и покупки в магазине.
        </p>
        <JournalTimeline entries={entries} />
      </div>
      <aside className="card" style={{ position: 'sticky', top: '1.5rem' }}>
        <h3>ТОП экипажа</h3>
        {leaderboards.map((board) => (
          <div key={board.period} style={{ marginBottom: '1rem' }}>
            <strong style={{ textTransform: 'capitalize' }}>
              {board.period === 'week' ? 'Неделя' : board.period === 'month' ? 'Месяц' : 'Год'}
            </strong>
            <ul style={{ listStyle: 'none', padding: 0, margin: '0.5rem 0 0' }}>
              {board.entries.length === 0 && <li style={{ color: 'var(--text-muted)' }}>Пока нет лидеров.</li>}
              {board.entries.map((entry, index) => (
                <li key={entry.user_id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                  <span>
                    #{index + 1} {entry.full_name}
                  </span>
                  <span>{entry.xp_delta} XP · {entry.mana_delta} ⚡</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </aside>
    </section>
  );
}
