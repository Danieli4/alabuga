import { apiFetch } from '../../../lib/api';
import { requireSession } from '../../../lib/auth/session';
import { MissionSubmissionForm } from '../../../components/MissionSubmissionForm';

interface MissionDetail {
  id: number;
  title: string;
  description: string;
  xp_reward: number;
  mana_reward: number;
  difficulty: string;
  minimum_rank_id: number | null;
  artifact_id: number | null;
  prerequisites: number[];
  competency_rewards: Array<{
    competency_id: number;
    competency_name: string;
    level_delta: number;
  }>;
  is_available: boolean;
  locked_reasons: string[];
  is_completed: boolean;
  requires_documents: boolean;
}

async function fetchMission(id: number, token: string) {
  const [mission, submission] = await Promise.all([
    apiFetch<MissionDetail>(`/api/missions/${id}`, { authToken: token }),
    apiFetch<MissionSubmission | null>(`/api/missions/${id}/submission`, { authToken: token })
  ]);
  return { mission, submission };
}

interface MissionSubmission {
  id: number;
  comment: string | null;
  proof_url: string | null;
  resume_link: string | null;
  passport_url: string | null;
  photo_url: string | null;
  resume_url: string | null;
  status: 'pending' | 'approved' | 'rejected';
}

interface MissionPageProps {
  params: { id: string };
}

export default async function MissionPage({ params }: MissionPageProps) {
  const missionId = Number(params.id);
  // Даже при прямом переходе на URL миссия доступна только авторизованным пользователям.
  const session = await requireSession();
  const { mission, submission } = await fetchMission(missionId, session.token);

  return (
    <section>
      <h2>{mission.title}</h2>
      <span className="badge">{mission.difficulty}</span>
      <p style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>{mission.description}</p>
      <p style={{ marginTop: '1rem' }}>
        Награда: {mission.xp_reward} XP · {mission.mana_reward} ⚡
      </p>
      {mission.is_completed && (
        <div
          className="card"
          style={{
            marginTop: '1rem',
            border: '1px solid rgba(85, 239, 196, 0.35)',
            background: 'rgba(85, 239, 196, 0.12)'
          }}
        >
          <strong>Миссия завершена</strong>
          <p style={{ marginTop: '0.5rem', color: 'var(--text-muted)' }}>
            HR уже подтвердил выполнение. Вы можете просмотреть прикреплённые документы ниже.
          </p>
        </div>
      )}
      {!mission.is_available && !mission.is_completed && mission.locked_reasons.length > 0 && (
        <div className="card" style={{ border: '1px solid rgba(255, 118, 117, 0.5)', background: 'rgba(255,118,117,0.1)' }}>
          <strong>Миссия заблокирована</strong>
          <ul style={{ marginTop: '0.5rem' }}>
            {mission.locked_reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        </div>
      )}
      <div className="card">
        <h3>Компетенции</h3>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {mission.competency_rewards.map((reward) => (
            <li key={reward.competency_id}>
              {reward.competency_name} +{reward.level_delta}
            </li>
          ))}
          {mission.competency_rewards.length === 0 && <li>Нет прокачки компетенций.</li>}
        </ul>
      </div>
      <MissionSubmissionForm
        missionId={mission.id}
        token={session.token}
        locked={!mission.is_available && !mission.is_completed}
        completed={mission.is_completed}
        requiresDocuments={mission.requires_documents}
        submission={submission ?? undefined}
      />
    </section>
  );
}
