import { apiFetch } from '../../../lib/api';
import { requireSession } from '../../../lib/auth/session';
import { MissionSubmissionForm } from '../../../components/MissionSubmissionForm';
import { CodingMissionPanel } from '../../../components/CodingMissionPanel';
import { OfflineMissionRegistration } from '../../../components/OfflineMissionRegistration';

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
  event_location?: string | null;
  event_address?: string | null;
  event_starts_at?: string | null;
  event_ends_at?: string | null;
  registration_deadline?: string | null;
  registration_url?: string | null;
  registration_notes?: string | null;
  capacity?: number | null;
  contact_person?: string | null;
  contact_phone?: string | null;
  submission_status?: 'pending' | 'approved' | 'rejected' | null;
  registered_participants: number;
  registration_open: boolean;
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

  return (
    <section>
      <h2>{mission.title}</h2>
      <span className="badge">{mission.difficulty}</span>
      <p style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>{mission.description}</p>
      {mission.format === 'offline' && (
        <div className="card" style={{ marginTop: '1rem', background: 'rgba(162, 155, 254, 0.08)' }}>
          <h3 style={{ marginBottom: '0.5rem' }}>Офлайн событие</h3>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, color: 'var(--text-muted)' }}>
            {mission.event_location && <li>📍 {mission.event_location}</li>}
            {mission.event_address && <li>🧭 {mission.event_address}</li>}
            {mission.event_starts_at && (
              <li>
                🗓 Старт: {new Date(mission.event_starts_at).toLocaleString('ru-RU', { day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit' })}
              </li>
            )}
            {mission.event_ends_at && (
              <li>
                🕘 Завершение: {new Date(mission.event_ends_at).toLocaleString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
              </li>
            )}
            <li>
              👥 Зарегистрировано: {mission.registered_participants}
              {mission.capacity ? ` из ${mission.capacity}` : ''}
            </li>
            {mission.registration_deadline && (
              <li>
                ⏳ Запись до: {new Date(mission.registration_deadline).toLocaleString('ru-RU', { day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit' })}
              </li>
            )}
            {mission.registration_notes && <li>ℹ️ {mission.registration_notes}</li>}
            {mission.registration_open ? (
              <li style={{ color: 'var(--accent-light)' }}>Регистрация открыта</li>
            ) : (
              <li style={{ color: 'var(--error)' }}>Регистрация закрыта</li>
            )}
          </ul>
        </div>
      )}
      <p style={{ marginTop: '1rem' }}>
        Награда: {mission.xp_reward} XP · {mission.mana_reward} ⚡
      </p>
      {mission.has_coding_challenges && (
        <p style={{ marginTop: '0.5rem', color: 'var(--accent-light)' }}>
          Прогресс тренажёра: {mission.completed_coding_challenges}/{mission.coding_challenge_count} заданий
        </p>
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
      ) : mission.format === 'offline' ? (
        <OfflineMissionRegistration
          missionId={mission.id}
          token={session.token}
          locked={!mission.is_available && !mission.is_completed}
          registrationOpen={mission.registration_open}
          registeredCount={mission.registered_participants}
          capacity={mission.capacity}
          submission={submission ? { id: submission.id, comment: submission.comment, status: submission.status } : null}
          eventLocation={mission.event_location}
          eventAddress={mission.event_address}
          eventStartsAt={mission.event_starts_at}
          eventEndsAt={mission.event_ends_at}
          registrationDeadline={mission.registration_deadline}
          registrationUrl={mission.registration_url}
          registrationNotes={mission.registration_notes}
          contactPerson={mission.contact_person}
          contactPhone={mission.contact_phone}
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
