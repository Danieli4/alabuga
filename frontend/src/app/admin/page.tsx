import { apiFetch } from '../../lib/api';
import { getDemoToken } from '../../lib/demo-auth';

interface Submission {
  mission_id: number;
  status: string;
  comment: string | null;
  proof_url: string | null;
  awarded_xp: number;
  awarded_mana: number;
  updated_at: string;
}

async function fetchModerationQueue() {
  const token = await getDemoToken();
  const submissions = await apiFetch<Submission[]>('/api/admin/submissions', { authToken: token });
  return submissions;
}

export default async function AdminPage() {
  const submissions = await fetchModerationQueue();

  return (
    <section>
      <h2>HR-панель: очередь модерации</h2>
      <p style={{ color: 'var(--text-muted)' }}>
        Демонстрационная выборка отправленных миссий. В реальном приложении добавим карточки с деталями пилота и
        кнопки approve/reject непосредственно из UI.
      </p>
      <div className="grid">
        {submissions.map((submission) => (
          <div key={submission.mission_id} className="card">
            <h3>Миссия #{submission.mission_id}</h3>
            <p>Статус: {submission.status}</p>
            {submission.comment && <p>Комментарий пилота: {submission.comment}</p>}
            {submission.proof_url && (
              <p>
                Доказательство:{' '}
                <a href={submission.proof_url} target="_blank" rel="noreferrer">
                  открыть
                </a>
              </p>
            )}
            <small style={{ color: 'var(--text-muted)' }}>
              Обновлено: {new Date(submission.updated_at).toLocaleString('ru-RU')}
            </small>
          </div>
        ))}
        {submissions.length === 0 && <p>Очередь пуста — все миссии проверены.</p>}
      </div>
    </section>
  );
}
