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

async function fetchJournal() {
  const token = await getDemoToken();
  const entries = await apiFetch<JournalEntry[]>('/api/journal/', { authToken: token });
  return entries;
}

export default async function JournalPage() {
  const entries = await fetchJournal();

  return (
    <section>
      <h2>Бортовой журнал</h2>
      <p style={{ color: 'var(--text-muted)' }}>
        Здесь фиксируется каждый шаг: отправка миссий, повышение ранга, получение артефактов и покупки в магазине.
      </p>
      <JournalTimeline entries={entries} />
    </section>
  );
}
