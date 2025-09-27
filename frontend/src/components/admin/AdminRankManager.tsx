'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';

import { apiFetch } from '../../lib/api';

type RankBase = {
  id: number;
  title: string;
  description: string;
  required_xp: number;
};

type MissionOption = {
  id: number;
  title: string;
};

type CompetencyOption = {
  id: number;
  name: string;
  description: string;
  category: string;
};

interface RankDetail extends RankBase {
  mission_requirements: Array<{ mission_id: number; mission_title: string }>;
  competency_requirements: Array<{ competency_id: number; competency_name: string; required_level: number }>;
}

interface Props {
  token: string;
  ranks: RankBase[];
  missions: MissionOption[];
  competencies: CompetencyOption[];
}

type CompetencyRequirementInput = { competency_id: number | ''; required_level: number };

type RankFormState = {
  title: string;
  description: string;
  required_xp: number;
  mission_ids: number[];
  competency_requirements: CompetencyRequirementInput[];
};

const initialRankForm: RankFormState = {
  title: '',
  description: '',
  required_xp: 0,
  mission_ids: [],
  competency_requirements: []
};

export function AdminRankManager({ token, ranks, missions, competencies }: Props) {
  const router = useRouter();
  const [selectedId, setSelectedId] = useState<number | 'new'>('new');
  const [form, setForm] = useState<RankFormState>(initialRankForm);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const resetForm = () => {
    setForm(initialRankForm);
  };

  const loadRank = async (rankId: number) => {
    try {
      setLoading(true);
      const rank = await apiFetch<RankDetail>(`/api/admin/ranks/${rankId}`, { authToken: token });
      setForm({
        title: rank.title,
        description: rank.description,
        required_xp: rank.required_xp,
        mission_ids: rank.mission_requirements.map((item) => item.mission_id),
        competency_requirements: rank.competency_requirements.map((item) => ({
          competency_id: item.competency_id,
          required_level: item.required_level
        }))
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось загрузить ранг');
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
    setSelectedId(id);
    void loadRank(id);
  };

  const updateField = <K extends keyof RankFormState>(field: K, value: RankFormState[K]) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleMissionSelect = (event: FormEvent<HTMLSelectElement>) => {
    const options = Array.from(event.currentTarget.selectedOptions);
    updateField(
      'mission_ids',
      options.map((option) => Number(option.value))
    );
  };

  const addCompetencyRequirement = () => {
    updateField('competency_requirements', [...form.competency_requirements, { competency_id: '', required_level: 1 }]);
  };

  const updateCompetencyRequirement = (index: number, value: CompetencyRequirementInput) => {
    const next = [...form.competency_requirements];
    next[index] = value;
    updateField('competency_requirements', next);
  };

  const removeCompetencyRequirement = (index: number) => {
    const next = [...form.competency_requirements];
    next.splice(index, 1);
    updateField('competency_requirements', next);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStatus(null);
    setError(null);
    setLoading(true);

    const payload = {
      title: form.title,
      description: form.description,
      required_xp: Number(form.required_xp),
      mission_ids: form.mission_ids,
      competency_requirements: form.competency_requirements
        .filter((item) => item.competency_id !== '')
        .map((item) => ({
          competency_id: Number(item.competency_id),
          required_level: Number(item.required_level)
        }))
    };

    try {
      if (selectedId === 'new') {
        await apiFetch('/api/admin/ranks', {
          method: 'POST',
          body: JSON.stringify(payload),
          authToken: token
        });
        setStatus('Ранг создан');
        resetForm();
      } else {
        await apiFetch(`/api/admin/ranks/${selectedId}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
          authToken: token
        });
        setStatus('Ранг обновлён');
      }
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось сохранить ранг');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h3>Ранги и условия повышения</h3>
      <p style={{ color: 'var(--text-muted)' }}>
        Управляйте требованиями к рангу: задавайте минимальный опыт, ключевые миссии и уровни компетенций.
      </p>
      <form onSubmit={handleSubmit} className="admin-form">
        <label>
          Выбранный ранг
          <select value={selectedId === 'new' ? 'new' : String(selectedId)} onChange={(event) => handleSelect(event.target.value)}>
            <option value="new">Новый ранг</option>
            {ranks.map((rank) => (
              <option key={rank.id} value={rank.id}>
                {rank.title}
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
          <textarea value={form.description} onChange={(event) => updateField('description', event.target.value)} required rows={3} />
        </label>

        <label>
          Требуемый опыт
          <input type="number" min={0} value={form.required_xp} onChange={(event) => updateField('required_xp', Number(event.target.value))} required />
        </label>

        <label>
          Ключевые миссии
          <select multiple value={form.mission_ids.map(String)} onChange={handleMissionSelect} size={Math.min(6, missions.length)}>
            {missions.map((mission) => (
              <option key={mission.id} value={mission.id}>
                {mission.title}
              </option>
            ))}
          </select>
        </label>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Требования к компетенциям</span>
            <button type="button" onClick={addCompetencyRequirement} className="secondary">
              Добавить требование
            </button>
          </div>
          {form.competency_requirements.length === 0 && (
            <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
              Пока нет требований. Добавьте компетенции, которые нужно прокачать до определённого уровня.
            </p>
          )}
          {form.competency_requirements.map((item, index) => (
            <div key={index} style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', marginTop: '0.5rem' }}>
              <select
                value={item.competency_id === '' ? '' : String(item.competency_id)}
                onChange={(event) =>
                  updateCompetencyRequirement(index, {
                    competency_id: event.target.value === '' ? '' : Number(event.target.value),
                    required_level: item.required_level
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
                min={0}
                value={item.required_level}
                onChange={(event) =>
                  updateCompetencyRequirement(index, {
                    competency_id: item.competency_id,
                    required_level: Number(event.target.value)
                  })
                }
                style={{ width: '80px' }}
              />
              <button type="button" className="secondary" onClick={() => removeCompetencyRequirement(index)}>
                Удалить
              </button>
            </div>
          ))}
        </div>

        <button type="submit" className="primary" disabled={loading}>
          {selectedId === 'new' ? 'Создать ранг' : 'Сохранить изменения'}
        </button>

        {status && <p style={{ color: 'var(--success)', marginTop: '0.5rem' }}>{status}</p>}
        {error && <p style={{ color: 'var(--error)', marginTop: '0.5rem' }}>{error}</p>}
      </form>
    </div>
  );
}
