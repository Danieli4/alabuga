'use client';

import { FormEvent, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';

import { apiFetch } from '../../lib/api';

const DIFFICULTIES = [
  { value: 'easy', label: 'Лёгкая' },
  { value: 'medium', label: 'Средняя' },
  { value: 'hard', label: 'Сложная' }
] as const;

type Difficulty = (typeof DIFFICULTIES)[number]['value'];

type MissionBase = {
  id: number;
  title: string;
  description: string;
  xp_reward: number;
  mana_reward: number;
  difficulty: Difficulty;
  is_active: boolean;
};

interface MissionDetail extends MissionBase {
  minimum_rank_id: number | null;
  artifact_id: number | null;
  prerequisites: number[];
  competency_rewards: Array<{ competency_id: number; competency_name: string; level_delta: number }>;
}

type Branch = {
  id: number;
  title: string;
  description: string;
  category: string;
  missions: Array<{ mission_id: number; mission_title: string; order: number }>;
};

type Rank = {
  id: number;
  title: string;
  description: string;
  required_xp: number;
};

type Competency = {
  id: number;
  name: string;
  description: string;
  category: string;
};

type Artifact = {
  id: number;
  name: string;
  description: string;
  rarity: string;
};

interface Props {
  token: string;
  missions: MissionBase[];
  branches: Branch[];
  ranks: Rank[];
  competencies: Competency[];
  artifacts: Artifact[];
}

type RewardInput = { competency_id: number | ''; level_delta: number };

type FormState = {
  title: string;
  description: string;
  xp_reward: number;
  mana_reward: number;
  difficulty: Difficulty;
  minimum_rank_id: number | '';
  artifact_id: number | '';
  branch_id: number | '';
  branch_order: number;
  prerequisite_ids: number[];
  competency_rewards: RewardInput[];
  is_active: boolean;
};

const initialFormState: FormState = {
  title: '',
  description: '',
  xp_reward: 0,
  mana_reward: 0,
  difficulty: 'medium',
  minimum_rank_id: '',
  artifact_id: '',
  branch_id: '',
  branch_order: 1,
  prerequisite_ids: [],
  competency_rewards: [],
  is_active: true
};

export function AdminMissionManager({ token, missions, branches, ranks, competencies, artifacts }: Props) {
  const router = useRouter();
  const [selectedId, setSelectedId] = useState<number | 'new'>('new');
  const [form, setForm] = useState<FormState>(initialFormState);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Позволяет мгновенно подставлять базовые поля при переключении миссии,
  // пока загрузка детальной карточки не завершилась.
  const missionById = useMemo(() => new Map(missions.map((mission) => [mission.id, mission])), [missions]);

  const resetForm = () => {
    setForm(initialFormState);
  };

  const loadMission = async (missionId: number) => {
    try {
      setLoading(true);
      const mission = await apiFetch<MissionDetail>(`/api/admin/missions/${missionId}`, { authToken: token });
      setForm({
        title: mission.title,
        description: mission.description,
        xp_reward: mission.xp_reward,
        mana_reward: mission.mana_reward,
        difficulty: mission.difficulty,
        minimum_rank_id: mission.minimum_rank_id ?? '',
        artifact_id: mission.artifact_id ?? '',
        branch_id: (() => {
          const branchLink = branches
            .flatMap((branch) => branch.missions.map((item) => ({ branch, item })))
            .find(({ item }) => item.mission_id === mission.id);
          return branchLink?.branch.id ?? '';
        })(),
        branch_order: (() => {
          const branchLink = branches
            .flatMap((branch) => branch.missions.map((item) => ({ branch, item })))
            .find(({ item }) => item.mission_id === mission.id);
          return branchLink?.item.order ?? 1;
        })(),
        prerequisite_ids: mission.prerequisites,
        competency_rewards: mission.competency_rewards.map((reward) => ({
          competency_id: reward.competency_id,
          level_delta: reward.level_delta
        })),
        is_active: mission.is_active
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось загрузить миссию');
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (value: string) => {
    setStatus(null);
    setError(null);
    if (value === 'new') {
      setSelectedId('new');
      resetForm();
      return;
    }

    const id = Number(value);

    const baseMission = missionById.get(id);
    if (baseMission) {
      setForm((prev) => ({
        ...prev,
        title: baseMission.title,
        description: baseMission.description,
        xp_reward: baseMission.xp_reward,
        mana_reward: baseMission.mana_reward,
        difficulty: baseMission.difficulty,
        is_active: baseMission.is_active
      }));
    }

    setSelectedId(id);
    void loadMission(id);
  };

  const updateField = <K extends keyof FormState>(field: K, value: FormState[K]) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handlePrerequisitesChange = (event: FormEvent<HTMLSelectElement>) => {
    const options = Array.from(event.currentTarget.selectedOptions);
    updateField(
      'prerequisite_ids',
      options.map((option) => Number(option.value))
    );
  };

  const addReward = () => {
    updateField('competency_rewards', [...form.competency_rewards, { competency_id: '', level_delta: 1 }]);
  };

  const updateReward = (index: number, value: RewardInput) => {
    const next = [...form.competency_rewards];
    next[index] = value;
    updateField('competency_rewards', next);
  };

  const removeReward = (index: number) => {
    const next = [...form.competency_rewards];
    next.splice(index, 1);
    updateField('competency_rewards', next);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStatus(null);
    setError(null);
    setLoading(true);

    const payloadBase = {
      title: form.title,
      description: form.description,
      xp_reward: Number(form.xp_reward),
      mana_reward: Number(form.mana_reward),
      difficulty: form.difficulty,
      minimum_rank_id: form.minimum_rank_id === '' ? null : Number(form.minimum_rank_id),
      artifact_id: form.artifact_id === '' ? null : Number(form.artifact_id),
      prerequisite_ids: form.prerequisite_ids,
      competency_rewards: form.competency_rewards
        .filter((reward) => reward.competency_id !== '')
        .map((reward) => ({
          competency_id: Number(reward.competency_id),
          level_delta: Number(reward.level_delta)
        })),
      branch_id: form.branch_id === '' ? null : Number(form.branch_id),
      branch_order: Number(form.branch_order) || 1,
      is_active: form.is_active
    };

    try {
      if (selectedId === 'new') {
        const { is_active, ...createPayload } = payloadBase;
        await apiFetch('/api/admin/missions', {
          method: 'POST',
          body: JSON.stringify(createPayload),
          authToken: token
        });
        setStatus('Миссия создана');
        resetForm();
        setSelectedId('new');
      } else {
        await apiFetch(`/api/admin/missions/${selectedId}`, {
          method: 'PUT',
          body: JSON.stringify(payloadBase),
          authToken: token
        });
        setStatus('Миссия обновлена');
      }
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось сохранить миссию');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h3>Миссии</h3>
      <p style={{ color: 'var(--text-muted)' }}>
        Создавайте и обновляйте миссии: настраивайте награды, зависимости, ветки и компетенции. Все изменения мгновенно
        отражаются в списках пилотов.
      </p>
      <form onSubmit={handleSubmit} className="admin-form">
        <label>
          Выбранная миссия
          <select value={selectedId === 'new' ? 'new' : String(selectedId)} onChange={(event) => handleSelect(event.target.value)}>
            <option value="new">Новая миссия</option>
            {missions.map((mission) => (
              <option key={mission.id} value={mission.id}>
                {mission.title}
              </option>
            ))}
          </select>
        </label>

        <label>
          Название
          <input value={form.title} onChange={(event) => updateField('title', event.target.value)} required />
        </label>

        <label>
          Описание
          <textarea value={form.description} onChange={(event) => updateField('description', event.target.value)} required rows={4} />
        </label>

        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
          <label>
            Награда (XP)
            <input type="number" min={0} value={form.xp_reward} onChange={(event) => updateField('xp_reward', Number(event.target.value))} required />
          </label>
          <label>
            Награда (мана)
            <input type="number" min={0} value={form.mana_reward} onChange={(event) => updateField('mana_reward', Number(event.target.value))} required />
          </label>
          <label>
            Сложность
            <select value={form.difficulty} onChange={(event) => updateField('difficulty', event.target.value as Difficulty)}>
              {DIFFICULTIES.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Доступен с ранга
            <select value={form.minimum_rank_id === '' ? '' : String(form.minimum_rank_id)} onChange={(event) => updateField('minimum_rank_id', event.target.value === '' ? '' : Number(event.target.value))}>
              <option value="">Любой ранг</option>
              {ranks.map((rank) => (
                <option key={rank.id} value={rank.id}>
                  {rank.title}
                </option>
              ))}
            </select>
          </label>
          <label>
            Артефакт
            <select value={form.artifact_id === '' ? '' : String(form.artifact_id)} onChange={(event) => updateField('artifact_id', event.target.value === '' ? '' : Number(event.target.value))}>
              <option value="">Без артефакта</option>
              {artifacts.map((artifact) => (
                <option key={artifact.id} value={artifact.id}>
                  {artifact.name}
                </option>
              ))}
            </select>
          </label>
          <label className="checkbox">
            <input type="checkbox" checked={form.is_active} onChange={(event) => updateField('is_active', event.target.checked)} /> Миссия активна
          </label>
        </div>

        <label>
          Ветка
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <select value={form.branch_id === '' ? '' : String(form.branch_id)} onChange={(event) => updateField('branch_id', event.target.value === '' ? '' : Number(event.target.value))}>
              <option value="">Без ветки</option>
              {branches.map((branch) => (
                <option key={branch.id} value={branch.id}>
                  {branch.title}
                </option>
              ))}
            </select>
            <label style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              Порядок
              <input type="number" min={1} value={form.branch_order} onChange={(event) => updateField('branch_order', Number(event.target.value) || 1)} style={{ width: '80px' }} />
            </label>
          </div>
        </label>

        <label>
          Предварительные миссии
          <select multiple value={form.prerequisite_ids.map(String)} onChange={handlePrerequisitesChange} size={Math.min(6, missions.length)}>
            {missions
              .filter((mission) => selectedId === 'new' || mission.id !== selectedId)
              .map((mission) => (
                <option key={mission.id} value={mission.id}>
                  {mission.title}
                </option>
              ))}
          </select>
        </label>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Прокачка компетенций</span>
            <button type="button" onClick={addReward} className="secondary">
              Добавить компетенцию
            </button>
          </div>
          {form.competency_rewards.length === 0 && (
            <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>Для миссии пока не назначены компетенции.</p>
          )}
          {form.competency_rewards.map((reward, index) => (
            <div key={index} style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', marginTop: '0.5rem' }}>
              <select
                value={reward.competency_id === '' ? '' : String(reward.competency_id)}
                onChange={(event) =>
                  updateReward(index, {
                    competency_id: event.target.value === '' ? '' : Number(event.target.value),
                    level_delta: reward.level_delta
                  })
                }
              >
                <option value="">Выберите компетенцию</option>
                {competencies.map((competency) => (
                  <option key={competency.id} value={competency.id}>
                    {competency.name}
                  </option>
                ))}
              </select>
              <input
                type="number"
                min={1}
                value={reward.level_delta}
                onChange={(event) =>
                  updateReward(index, {
                    competency_id: reward.competency_id,
                    level_delta: Number(event.target.value)
                  })
                }
                style={{ width: '80px' }}
              />
              <button type="button" className="secondary" onClick={() => removeReward(index)}>
                Удалить
              </button>
            </div>
          ))}
        </div>

        <button type="submit" className="primary" disabled={loading}>
          {selectedId === 'new' ? 'Создать миссию' : 'Сохранить изменения'}
        </button>

        {status && <p style={{ color: 'var(--success)', marginTop: '0.5rem' }}>{status}</p>}
        {error && <p style={{ color: 'var(--error)', marginTop: '0.5rem' }}>{error}</p>}
      </form>
    </div>
  );
}
