import { AdminBranchManager } from '../../components/admin/AdminBranchManager';
import { AdminMissionManager } from '../../components/admin/AdminMissionManager';
import { AdminRankManager } from '../../components/admin/AdminRankManager';
import { AdminArtifactManager } from '../../components/admin/AdminArtifactManager';
import { AdminSubmissionCard } from '../../components/admin/AdminSubmissionCard';
import { apiFetch } from '../../lib/api';
import { getDemoToken } from '../../lib/demo-auth';

interface Submission {
  id: number;
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
  image_url?: string | null;
}

interface SubmissionStats {
  pending: number;
  approved: number;
  rejected: number;
}

interface BranchCompletionStat {
  branch_id: number;
  branch_title: string;
  completion_rate: number;
}

interface AdminStats {
  total_users: number;
  active_pilots: number;
  average_completed_missions: number;
  submission_stats: SubmissionStats;
  branch_completion: BranchCompletionStat[];
}

export default async function AdminPage() {
  const token = await getDemoToken('hr');

  const [submissions, missions, branches, ranks, competencies, artifacts, stats] = await Promise.all([
    apiFetch<Submission[]>('/api/admin/submissions', { authToken: token }),
    apiFetch<MissionSummary[]>('/api/admin/missions', { authToken: token }),
    apiFetch<BranchSummary[]>('/api/admin/branches', { authToken: token }),
    apiFetch<RankSummary[]>('/api/admin/ranks', { authToken: token }),
    apiFetch<CompetencySummary[]>('/api/admin/competencies', { authToken: token }),
    apiFetch<ArtifactSummary[]>('/api/admin/artifacts', { authToken: token }),
    apiFetch<AdminStats>('/api/admin/stats', { authToken: token })
  ]);

  return (
    <section>
      <h2>HR-панель</h2>
      <p style={{ color: 'var(--text-muted)' }}>
        Управляйте миссиями, ветками и рангами, а также следите за очередью модерации отчётов.
      </p>

      <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        <div className="card" style={{ gridColumn: '1 / -1', display: 'grid', gap: '1rem' }}>
          <h3>Сводка</h3>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
            <div className="card" style={{ marginBottom: 0 }}>
              <span className="badge">Пилоты</span>
              <p style={{ fontSize: '2rem', margin: '1rem 0 0' }}>{stats.total_users}</p>
              <small style={{ color: 'var(--text-muted)' }}>Всего зарегистрировано</small>
            </div>
            <div className="card" style={{ marginBottom: 0 }}>
              <span className="badge">Активность</span>
              <p style={{ fontSize: '2rem', margin: '1rem 0 0' }}>{stats.active_pilots}</p>
              <small style={{ color: 'var(--text-muted)' }}>Закрыли хотя бы одну миссию</small>
            </div>
            <div className="card" style={{ marginBottom: 0 }}>
              <span className="badge">Средний прогресс</span>
              <p style={{ fontSize: '2rem', margin: '1rem 0 0' }}>{stats.average_completed_missions.toFixed(1)}</p>
              <small style={{ color: 'var(--text-muted)' }}>Миссий на пилота</small>
            </div>
          </div>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
            <div className="card" style={{ marginBottom: 0 }}>
              <strong>Очередь модерации</strong>
              <p style={{ marginTop: '0.5rem' }}>На проверке: {stats.submission_stats.pending}</p>
              <small style={{ color: 'var(--text-muted)' }}>
                Одобрено: {stats.submission_stats.approved} · Отклонено: {stats.submission_stats.rejected}
              </small>
            </div>
            <div className="card" style={{ marginBottom: 0 }}>
              <strong>Завершённость веток</strong>
              <ul style={{ listStyle: 'none', margin: '0.75rem 0 0', padding: 0 }}>
                {stats.branch_completion.map((branchStat) => (
                  <li key={branchStat.branch_id} style={{ marginBottom: '0.25rem' }}>
                    {branchStat.branch_title}: {(branchStat.completion_rate * 100).toFixed(0)}%
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        <div className="card" style={{ gridColumn: '1 / -1' }}>
          <h3>Очередь модерации</h3>
          <p style={{ color: 'var(--text-muted)' }}>
            Список последующих отправок миссий. Для полноты UX можно добавить действия approve/reject прямо отсюда.
          </p>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem' }}>
            {submissions.map((submission) => (
              <AdminSubmissionCard key={submission.id} submission={submission} token={token} />
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
        <AdminArtifactManager token={token} artifacts={artifacts} />
      </div>
    </section>
  );
}
