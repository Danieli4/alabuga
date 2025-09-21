import { apiFetch } from '../../lib/api';
import { getDemoToken } from '../../lib/demo-auth';
import { MissionList, MissionSummary } from '../../components/MissionList';

async function fetchMissions() {
  const token = await getDemoToken();
  const missions = await apiFetch<MissionSummary[]>('/api/missions/', { authToken: token });
  return missions;
}

export default async function MissionsPage() {
  const missions = await fetchMissions();

  return (
    <section>
      <h2>Активные миссии</h2>
      <p style={{ color: 'var(--text-muted)' }}>
        Список обновляется в реальном времени и зависит от вашего ранга и прогресса. HR может добавлять новые
        задания в админ-панели.
      </p>
      <MissionList missions={missions} />
    </section>
  );
}
