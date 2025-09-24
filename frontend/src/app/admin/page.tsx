import { AdminBranchManager } from '../../components/admin/AdminBranchManager';
import { AdminMissionManager } from '../../components/admin/AdminMissionManager';
import { AdminRankManager } from '../../components/admin/AdminRankManager';
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

interface MissionSummary {
  id: number;
  title: string;
  description: string;
  xp_reward: number;
  mana_reward: number;
  difficulty: string;
  is_active: boolean;
}

interface BranchSummary {
  id: number;
  title: string;
  description: string;
  category: string;
  missions: Array<{ mission_id: number; mission_title: string; order: number }>;
}

interface RankSummary {
  id: number;
  title: string;
  description: string;
  required_xp: number;
}

interface CompetencySummary {
  id: number;
  name: string;
  description: string;
  category: string;
}

interface ArtifactSummary {
  id: number;
  name: string;
  description: string;
  rarity: string;
}

export default async function AdminPage() {
  const token = await getDemoToken('hr');

  const [submissions, missions, branches, ranks, competencies, artifacts] = await Promise.all([
    apiFetch<Submission[]>('/api/admin/submissions', { authToken: token }),
    apiFetch<MissionSummary[]>('/api/admin/missions', { authToken: token }),
    apiFetch<BranchSummary[]>('/api/admin/branches', { authToken: token }),
    apiFetch<RankSummary[]>('/api/admin/ranks', { authToken: token }),
    apiFetch<CompetencySummary[]>('/api/admin/competencies', { authToken: token }),
    apiFetch<ArtifactSummary[]>('/api/admin/artifacts', { authToken: token })
  ]);

  return (
    <section>
      <h2>HR-панель</h2>
      <p style={{ color: 'var(--text-muted)' }}>
        Управляйте миссиями, ветками и рангами, а также следите за очередью модерации отчётов.
      </p>

      <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        <div className="card" style={{ gridColumn: '1 / -1' }}>
          <h3>Очередь модерации</h3>
          <p style={{ color: 'var(--text-muted)' }}>
            Список последующих отправок миссий. Для полноты UX можно добавить действия approve/reject прямо отсюда.
          </p>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem' }}>
            {submissions.map((submission) => (
              <div key={`${submission.mission_id}-${submission.updated_at}`} className="card">
                <h4>Миссия #{submission.mission_id}</h4>
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
        </div>

        <AdminBranchManager token={token} branches={branches} />
        <AdminMissionManager
          token={token}
          missions={missions}
          branches={branches}
          ranks={ranks}
          competencies={competencies}
          artifacts={artifacts}
        />
        <AdminRankManager token={token} ranks={ranks} missions={missions} competencies={competencies} />
      </div>
    </section>
  );
}
