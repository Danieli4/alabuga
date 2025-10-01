import { apiFetch } from '../../../lib/api';
import { requireSession } from '../../../lib/auth/session';
import { MissionSubmissionForm } from '../../../components/MissionSubmissionForm';
import { CodingMissionPanel } from '../../../components/CodingMissionPanel';
import { MissionRegistrationPanel } from '../../../components/MissionRegistrationPanel';

interface MissionDetail {
  id: number;
  title: string;
  description: string;
  xp_reward: number;
  mana_reward: number;
  difficulty: string;
  format: 'online' | 'offline';
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
  has_coding_challenges: boolean;
  coding_challenge_count: number;
  completed_coding_challenges: number;
  registration_deadline: string | null;
  starts_at: string | null;
  ends_at: string | null;
  location_title: string | null;
  location_address: string | null;
  location_url: string | null;
  capacity: number | null;
  registered_count: number;
  spots_left: number | null;
  is_registration_open: boolean;
  is_registered: boolean;
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

interface CodingChallengeState {
  id: number;
  order: number;
  title: string;
  prompt: string;
  starter_code: string | null;
  is_passed: boolean;
  is_unlocked: boolean;
  last_submitted_code: string | null;
  last_stdout: string | null;
  last_stderr: string | null;
  last_exit_code: number | null;
  updated_at: string | null;
}

interface CodingMissionState {
  mission_id: number;
  total_challenges: number;
  completed_challenges: number;
  current_challenge_id: number | null;
  is_mission_completed: boolean;
  challenges: CodingChallengeState[];
}

export default async function MissionPage({ params }: MissionPageProps) {
  const missionId = Number(params.id);
  // Даже при прямом переходе на URL миссия доступна только авторизованным пользователям.
  const session = await requireSession();
  const { mission, submission } = await fetchMission(missionId, session.token);
  const codingState = mission.has_coding_challenges
    ? await apiFetch<CodingMissionState>(`/api/missions/${missionId}/coding/challenges`, {
        authToken: session.token
      })
    : null;

  const isOffline = mission.format === 'offline';
  const dateFormatter = new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit'
  });
  const timeFormatter = new Intl.DateTimeFormat('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
  });
  const startText = mission.starts_at ? dateFormatter.format(new Date(mission.starts_at)) : null;
  const endDate = mission.ends_at ? new Date(mission.ends_at) : null;
  const endText = endDate ? timeFormatter.format(endDate) : null;
  const deadlineText = mission.registration_deadline ? dateFormatter.format(new Date(mission.registration_deadline)) : null;

  return (
    <section>
      <h2>{mission.title}</h2>
      <span className="badge">{mission.difficulty}</span>
      <p style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>{mission.description}</p>
      <p style={{ marginTop: '1rem' }}>
        Награда: {mission.xp_reward} XP · {mission.mana_reward} ⚡
      </p>
      {mission.has_coding_challenges && (
        <p style={{ marginTop: '0.5rem', color: 'var(--accent-light)' }}>
          Прогресс тренажёра: {mission.completed_coding_challenges}/{mission.coding_challenge_count} заданий
        </p>
      )}
      {isOffline && (
        <div className="card" style={{ marginTop: '1rem' }}>
          <h3>Офлайн-мероприятие</h3>
          {startText && (
            <p style={{ marginTop: '0.5rem' }}>
              🗓 {startText}
              {endText ? ` · до ${endText}` : ''}
            </p>
          )}
          {mission.location_title && (
            <p style={{ marginTop: '0.25rem' }}>
              📍 {mission.location_title}
              {mission.location_address ? ` — ${mission.location_address}` : ''}
            </p>
          )}
          {mission.location_url && (
            <p style={{ marginTop: '0.25rem' }}>
              <a className="secondary" href={mission.location_url} target="_blank" rel="noreferrer">
                Открыть карту
              </a>
            </p>
          )}
          {mission.capacity !== null && (
            <p style={{ marginTop: '0.25rem' }}>
              👥 Мест осталось: {mission.spots_left ?? 0} из {mission.capacity}
            </p>
          )}
          {deadlineText && (
            <p style={{ marginTop: '0.25rem', color: 'var(--accent-light)' }}>
              Регистрация до {deadlineText}
            </p>
          )}
          {mission.is_registered && (
            <p style={{ marginTop: '0.25rem', color: 'var(--success)' }}>Вы уже зарегистрированы на мероприятие.</p>
          )}
        </div>
      )}
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
            {mission.has_coding_challenges
              ? 'Система проверила код автоматически и уже начислила награды.'
              : 'HR уже подтвердил выполнение. Вы можете просмотреть прикреплённые документы ниже.'}
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
      {mission.has_coding_challenges ? (
        <CodingMissionPanel
          missionId={mission.id}
          token={session.token}
          initialState={codingState}
          initialCompleted={mission.is_completed}
        />
      ) : isOffline ? (
        <MissionRegistrationPanel
          missionId={mission.id}
          token={session.token}
          isRegistered={mission.is_registered}
          isRegistrationOpen={mission.is_registration_open}
          registeredCount={mission.registered_count}
          spotsLeft={mission.spots_left}
          registrationDeadline={mission.registration_deadline}
          startsAt={mission.starts_at}
        />
      ) : (
        <MissionSubmissionForm
          missionId={mission.id}
          token={session.token}
          locked={!mission.is_available && !mission.is_completed}
          completed={mission.is_completed}
          requiresDocuments={mission.requires_documents}
          submission={submission ?? undefined}
        />
      )}
    </section>
  );
}
