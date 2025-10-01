import { apiFetch } from '../../lib/api';
import { requireSession } from '../../lib/auth/session';
import { ArtifactManager } from '../../components/ArtifactManager';
import { ProgressOverview } from '../../components/ProgressOverview';

interface ProfileResponse {
  full_name: string;
  email: string;
  xp: number;
  mana: number;
  preferred_branch: string | null;
  motivation: string | null;
  competencies: Array<{
    competency: { id: number; name: string };
    level: number;
  }>;
  artifacts: Array<{
    id: number;
    artifact: {
      id: number;
      name: string;
      description: string;
      rarity: string;
      image_url: string | null;
      is_profile_modifier: boolean;
      background_effect: string | null;
      profile_effect: string | null;
      modifier_description: string | null;
    };
  }>;
  profile_photo_uploaded: boolean;
}

interface AppliedArtifact {
  id: number;
  name: string;
  description: string;
  rarity: string;
  image_url: string | null;
  is_profile_modifier: boolean;
  background_effect: string | null;
  profile_effect: string | null;
  modifier_description: string | null;
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

async function fetchProfileData(token: string) {
  const [profile, appliedArtifacts, progress] = await Promise.all([
    apiFetch<ProfileResponse>('/api/me', { authToken: token }),
    apiFetch<AppliedArtifact[]>('/api/me/applied-artifacts', { authToken: token }),
    apiFetch<ProgressResponse>('/api/progress', { authToken: token })
  ]);

  return { profile, appliedArtifacts, progress };
}

export default async function ProfilePage() {
  const session = await requireSession();
  const { profile, appliedArtifacts, progress } = await fetchProfileData(session.token);

  // Фильтруем артефакты-модификаторы
  const modifierArtifacts = profile.artifacts.filter(
    (ua) => ua.artifact.is_profile_modifier
  );

  const appliedIds = new Set(appliedArtifacts.map((a) => a.id));
  const availableArtifacts = modifierArtifacts
    .filter((ua) => !appliedIds.has(ua.artifact.id))
    .map((ua) => ua.artifact);

  // Получаем эффекты от применённых артефактов
  const backgroundEffects = appliedArtifacts
    .filter(a => a.background_effect)
    .map(a => a.background_effect)
    .join(', ');

  // Преобразуем артефакты для ProgressOverview
  const artifactsForOverview = profile.artifacts.map(ua => ({
    id: ua.artifact.id,
    name: ua.artifact.name,
    rarity: ua.artifact.rarity
  }));

  return (
    <section className="grid" style={{ gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
      <div style={{ 
        background: backgroundEffects || undefined,
        borderRadius: '16px',
        padding: backgroundEffects ? '1rem' : '0'
      }}>
        <ProgressOverview
          fullName={profile.full_name}
          mana={profile.mana}
          competencies={profile.competencies}
          artifacts={artifactsForOverview}
          token={session.token}
          profilePhotoUploaded={profile.profile_photo_uploaded}
          progress={progress}
        />
      </div>

      <aside>
        <ArtifactManager
          appliedArtifacts={appliedArtifacts}
          availableArtifacts={availableArtifacts}
          token={session.token}
        />
      </aside>
    </section>
  );
}
