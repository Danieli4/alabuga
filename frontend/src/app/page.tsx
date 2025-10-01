import { apiFetch } from '../lib/api';
import { requireSession } from '../lib/auth/session';
import { ProgressOverview } from '../components/ProgressOverview';

interface ProfileResponse {
  full_name: string;
  xp: number;
  mana: number;
  competencies: Array<{
    competency: { id: number; name: string };
    level: number;
  }>;
  artifacts: Array<{
    id: number;
    name: string;
    rarity: string;
  }>;
}

interface ProgressResponse {
  current_rank: { id: number; title: string; description: string; required_xp: number } | null;
  next_rank: { id: number; title: string; description: string; required_xp: number } | null;
  xp: {
    baseline: number;
    current: number;
    target: number;
    remaining: number;
    progress_percent: number;
  };
  mission_requirements: Array<{ mission_id: number; mission_title: string; is_completed: boolean }>;
  competency_requirements: Array<{
    competency_id: number;
    competency_name: string;
    required_level: number;
    current_level: number;
    is_met: boolean;
  }>;
  completed_missions: number;
  total_missions: number;
  met_competencies: number;
  total_competencies: number;
}

async function fetchProfile(token: string) {
  const [profile, progress] = await Promise.all([
    apiFetch<ProfileResponse>('/api/me', { authToken: token }),
    apiFetch<ProgressResponse>('/api/progress', { authToken: token })
  ]);

  return { profile, progress };
}

export default async function DashboardPage() {
  // Стартовая страница доступна только авторизованным пользователям (пилотам).
  // Если сессия отсутствует, `requireSession` автоматически выполнит редирект на `/login`.
  const session = await requireSession();
  const { profile, progress } = await fetchProfile(session.token);

  return (
    <section className="grid" style={{ gridTemplateColumns: '2fr 1fr' }}>
      <div>
        <ProgressOverview
          fullName={profile.full_name}
          mana={profile.mana}
          competencies={profile.competencies}
          artifacts={profile.artifacts}
          progress={progress}
        />
      </div>
      <aside className="card">
        <h3>Ближайшая цель</h3>
        <p style={{ color: 'var(--text-muted)', lineHeight: 1.5 }}>
          Следующий рубеж: {progress.next_rank ? `ранг «${progress.next_rank.title}»` : 'вы на максимальном ранге демо-версии'}.
          Закройте ключевые миссии и подтяните компетенции, чтобы взять оффер.
        </p>
        <p style={{ marginTop: '1rem' }}>
          Осталось {progress.xp.remaining} XP · {progress.completed_missions}/{progress.total_missions} миссий ·{' '}
          {progress.met_competencies}/{progress.total_competencies} компетенций.
        </p>
        <p style={{ marginTop: '1rem' }}>
          Доступ к HR-панели: {session.role === 'hr' ? 'есть' : 'нет'}
        </p>
        <a className="primary" style={{ marginTop: '1rem', display: 'inline-block' }} href="/missions">
          Посмотреть миссии
        </a>
      </aside>
    </section>
  );
}
