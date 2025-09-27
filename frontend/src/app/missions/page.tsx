import { apiFetch } from '../../lib/api';
import { getDemoToken } from '../../lib/demo-auth';
import { MissionList, MissionSummary } from '../../components/MissionList';

interface BranchMission {
  mission_id: number;
  mission_title: string;
  order: number;
  is_completed: boolean;
  is_available: boolean;
}

interface BranchOverview {
  id: number;
  title: string;
  description: string;
  category: string;
  missions: BranchMission[];
  total_missions: number;
  completed_missions: number;
}

async function fetchMissions() {
  const token = await getDemoToken();
  const [missions, branches] = await Promise.all([
    apiFetch<MissionSummary[]>('/api/missions/', { authToken: token }),
    apiFetch<BranchOverview[]>('/api/missions/branches', { authToken: token })
  ]);
  return { missions, branches };
}

export default async function MissionsPage() {
  const { missions, branches } = await fetchMissions();

  return (
    <section>
      <h2>Активные миссии</h2>
      <p style={{ color: 'var(--text-muted)' }}>
        Список обновляется в реальном времени и зависит от вашего ранга и прогресса. HR может добавлять новые
        задания в админ-панели.
      </p>
      <div className="grid" style={{ marginBottom: '2rem' }}>
        {branches.map((branch) => {
          const progress = branch.total_missions
            ? Math.round((branch.completed_missions / branch.total_missions) * 100)
            : 0;
          const nextMission = branch.missions.find((mission) => !mission.is_completed);
          return (
            <div key={branch.id} className="card">
              <h3 style={{ marginBottom: '0.5rem' }}>{branch.title}</h3>
              <p style={{ color: 'var(--text-muted)', minHeight: '3rem' }}>{branch.description}</p>
              <div style={{ marginTop: '1rem' }}>
                <small>Прогресс ветки: {progress}%</small>
                <div
                  style={{
                    marginTop: '0.5rem',
                    height: '8px',
                    borderRadius: '999px',
                    background: 'rgba(162, 155, 254, 0.2)',
                    overflow: 'hidden'
                  }}
                >
                  <div
                    style={{
                      width: `${progress}%`,
                      height: '100%',
                      background: 'linear-gradient(90deg, var(--accent), #00b894)'
                    }}
                  />
                </div>
              </div>
              {nextMission && (
                <p style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>
                  Следующая миссия: «{nextMission.mission_title}»
                </p>
              )}
            </div>
          );
        })}
      </div>
      <MissionList missions={missions} />
    </section>
  );
}
