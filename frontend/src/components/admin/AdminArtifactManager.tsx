'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';

import { apiFetch } from '../../lib/api';

type Artifact = {
  id: number;
  name: string;
  description: string;
  rarity: string;
  image_url?: string | null;
  is_profile_modifier?: boolean;
  background_effect?: string | null;
  profile_effect?: string | null;
  modifier_description?: string | null;
};

const RARITY_OPTIONS = [
  { value: 'common', label: 'Обычный' },
  { value: 'rare', label: 'Редкий' },
  { value: 'epic', label: 'Эпический' },
  { value: 'legendary', label: 'Легендарный' }
];

interface Props {
  token: string;
  artifacts: Artifact[];
}

export function AdminArtifactManager({ token, artifacts }: Props) {
  const router = useRouter();
  const [selectedId, setSelectedId] = useState<number | 'new'>('new');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [rarity, setRarity] = useState('rare');
  const [imageUrl, setImageUrl] = useState('');
  const [isProfileModifier, setIsProfileModifier] = useState(false);
  const [backgroundEffect, setBackgroundEffect] = useState('');
  const [profileEffect, setProfileEffect] = useState('');
  const [modifierDescription, setModifierDescription] = useState('');
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const resetForm = () => {
    setName('');
    setDescription('');
    setRarity('rare');
    setImageUrl('');
    setIsProfileModifier(false);
    setBackgroundEffect('');
    setProfileEffect('');
    setModifierDescription('');
  };

  const handleSelect = (value: string) => {
    if (value === 'new') {
      setSelectedId('new');
      resetForm();
      setStatus(null);
      setError(null);
      return;
    }

    const id = Number(value);
    const artifact = artifacts.find((item) => item.id === id);
    if (!artifact) {
      return;
    }

    setSelectedId(id);
    setName(artifact.name);
    setDescription(artifact.description);
    setRarity(artifact.rarity);
    setImageUrl(artifact.image_url ?? '');
    setIsProfileModifier(artifact.is_profile_modifier ?? false);
    setBackgroundEffect(artifact.background_effect ?? '');
    setProfileEffect(artifact.profile_effect ?? '');
    setModifierDescription(artifact.modifier_description ?? '');
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setStatus(null);
    setError(null);

    const payload = {
      name,
      description,
      rarity,
      image_url: imageUrl || null,
      is_profile_modifier: isProfileModifier,
      background_effect: backgroundEffect || null,
      profile_effect: profileEffect || null,
      modifier_description: modifierDescription || null
    };

    try {
      if (selectedId === 'new') {
        await apiFetch('/api/admin/artifacts', {
          method: 'POST',
          body: JSON.stringify(payload),
          authToken: token
        });
        setStatus('Артефакт создан');
        resetForm();
      } else {
        await apiFetch(`/api/admin/artifacts/${selectedId}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
          authToken: token
        });
        setStatus('Артефакт обновлён');
      }
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось сохранить артефакт');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (selectedId === 'new') {
      return;
    }
    setLoading(true);
    setStatus(null);
    setError(null);
    try {
      await apiFetch(`/api/admin/artifacts/${selectedId}`, {
        method: 'DELETE',
        authToken: token
      });
      setStatus('Артефакт удалён');
      setSelectedId('new');
      resetForm();
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось удалить артефакт');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h3>Артефакты</h3>
      <p style={{ color: 'var(--text-muted)' }}>
        Подготовьте коллекционные награды за миссии: укажите название, редкость и изображение. Артефакты можно привязывать
        в карточке миссии.
      </p>
      <form onSubmit={handleSubmit} className="admin-form">
        <label>
          Выбранный артефакт
          <select value={selectedId === 'new' ? 'new' : String(selectedId)} onChange={(event) => handleSelect(event.target.value)}>
            <option value="new">Новый артефакт</option>
            {artifacts.map((artifact) => (
              <option key={artifact.id} value={artifact.id}>
                {artifact.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Название
          <input value={name} onChange={(event) => setName(event.target.value)} required />
        </label>

        <label>
          Описание
          <textarea value={description} onChange={(event) => setDescription(event.target.value)} rows={3} required />
        </label>

        <label>
          Редкость
          <select value={rarity} onChange={(event) => setRarity(event.target.value)}>
            {RARITY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label>
          Изображение (URL)
          <input value={imageUrl} onChange={(event) => setImageUrl(event.target.value)} placeholder="https://..." />
        </label>

        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
          <input 
            type="checkbox" 
            checked={isProfileModifier} 
            onChange={(event) => setIsProfileModifier(event.target.checked)}
            style={{ width: 'auto' }}
          />
          <span>Модификатор профиля</span>
        </label>

        {isProfileModifier && (
          <>
            <label>
              Эффект фона (CSS)
              <input 
                value={backgroundEffect} 
                onChange={(event) => setBackgroundEffect(event.target.value)} 
                placeholder="url(/artifacts/image.jpg), linear-gradient(...)"
              />
              <small style={{ color: 'var(--text-muted)', marginTop: '0.25rem', display: 'block' }}>
                Примеры: url(/artifacts/image.jpg), linear-gradient(135deg, #667eea 0%, #764ba2 100%)
              </small>
            </label>

            <label>
              Дополнительный эффект (CSS)
              <input 
                value={profileEffect} 
                onChange={(event) => setProfileEffect(event.target.value)} 
                placeholder="box-shadow: 0 0 20px rgba(108, 92, 231, 0.5)"
              />
              <small style={{ color: 'var(--text-muted)', marginTop: '0.25rem', display: 'block' }}>
                Дополнительные CSS-эффекты для профиля (опционально)
              </small>
            </label>

            <label>
              Описание модификатора
              <textarea 
                value={modifierDescription} 
                onChange={(event) => setModifierDescription(event.target.value)} 
                rows={2}
                placeholder="Добавляет космический фон на профиль"
              />
            </label>
          </>
        )}

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <button type="submit" className="primary" disabled={loading}>
            {selectedId === 'new' ? 'Создать артефакт' : 'Сохранить изменения'}
          </button>
          {selectedId !== 'new' && (
            <button type="button" className="secondary" onClick={handleDelete} disabled={loading} style={{ cursor: loading ? 'not-allowed' : 'pointer' }}>
              Удалить
            </button>
          )}
        </div>

        {status && <p style={{ color: 'var(--success)', marginTop: '0.5rem' }}>{status}</p>}
        {error && <p style={{ color: 'var(--error)', marginTop: '0.5rem' }}>{error}</p>}
      </form>
    </div>
  );
}
