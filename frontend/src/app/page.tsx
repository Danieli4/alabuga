import { apiFetch } from '../lib/api';
import { getDemoToken } from '../lib/demo-auth';
import { ProgressOverview } from '../components/ProgressOverview';

interface ProfileResponse {
  full_name: string;
  xp: number;
  mana: number;
  current_rank_id: number | null;
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

interface RankResponse {
  id: number;
  title: string;
  description: string;
  required_xp: number;
}

async function fetchProfile() {
  const token = await getDemoToken();
  const profile = await apiFetch<ProfileResponse>('/api/me', { authToken: token });
  const ranks = await apiFetch<RankResponse[]>('/api/ranks', { authToken: token });
  const orderedRanks = [...ranks].sort((a, b) => a.required_xp - b.required_xp);
  const currentIndex = Math.max(
    orderedRanks.findIndex((rank) => rank.id === profile.current_rank_id),
    0
  );
  const currentRank = orderedRanks[currentIndex] ?? null;
  const nextRank = orderedRanks[currentIndex + 1] ?? null;
  const baselineXp = currentRank ? currentRank.required_xp : 0;
  const progress = Math.max(profile.xp - baselineXp, 0);
  const target = nextRank ? nextRank.required_xp - baselineXp : 0;

  return { token, profile, currentRank, nextRank, progress, target };
}

export default async function DashboardPage() {
  const { token, profile, currentRank, nextRank, progress, target } = await fetchProfile();

  return (
    <section className="grid" style={{ gridTemplateColumns: '2fr 1fr' }}>
      <div>
        <ProgressOverview
          fullName={profile.full_name}
          xp={profile.xp}
          mana={profile.mana}
          rank={currentRank}
          competencies={profile.competencies}
          artifacts={profile.artifacts}
          nextRankTitle={nextRank?.title}
          xpProgress={progress}
          xpTarget={target}
        />
      </div>
      <aside className="card">
        <h3>Ближайшая цель</h3>
        <p style={{ color: 'var(--text-muted)' }}>
          Выполните миссии ветки «Получение оффера», чтобы закрепиться в экипаже и открыть доступ к
          сложным задачам.
        </p>
        <p style={{ marginTop: '1rem' }}>Доступ к HR-панели: {token ? 'есть (демо-режим)' : 'нет'}</p>
        <a className="primary" style={{ marginTop: '1rem', display: 'inline-block' }} href="/missions">
          Посмотреть миссии
        </a>
      </aside>
    </section>
  );
}
