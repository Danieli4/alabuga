import { apiFetch } from '../../../lib/api';
import { getDemoToken } from '../../../lib/demo-auth';
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
}

async function fetchMission(id: number) {
  const token = await getDemoToken();
  const mission = await apiFetch<MissionDetail>(`/api/missions/${id}`, { authToken: token });
  return { mission, token };
}

interface MissionPageProps {
  params: { id: string };
}

export default async function MissionPage({ params }: MissionPageProps) {
  const missionId = Number(params.id);
  const { mission, token } = await fetchMission(missionId);

  return (
    <section>
      <h2>{mission.title}</h2>
      <span className="badge">{mission.difficulty}</span>
      <p style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>{mission.description}</p>
      <p style={{ marginTop: '1rem' }}>
        Награда: {mission.xp_reward} XP · {mission.mana_reward} ⚡
      </p>
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
      <MissionSubmissionForm missionId={mission.id} token={token} />
    </section>
  );
}
