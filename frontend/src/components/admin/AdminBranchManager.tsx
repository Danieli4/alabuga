'use client';

import { FormEvent, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';

import { apiFetch } from '../../lib/api';

type Branch = {
  id: number;
  title: string;
  description: string;
  category: string;
};

interface Props {
  token: string;
  branches: Branch[];
}

const DEFAULT_CATEGORY_OPTIONS = ['quest', 'recruiting', 'lecture', 'simulator'];

export function AdminBranchManager({ token, branches }: Props) {
  const router = useRouter();
  const [selectedId, setSelectedId] = useState<number | 'new'>('new');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('quest');
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const categoryOptions = useMemo(() => {
    const existing = new Set(DEFAULT_CATEGORY_OPTIONS);
    branches.forEach((branch) => existing.add(branch.category));
    return Array.from(existing.values());
  }, [branches]);

  const resetForm = () => {
    setTitle('');
    setDescription('');
    setCategory(categoryOptions[0] ?? 'quest');
  };

  const handleSelect = (value: string) => {
    if (value === 'new') {
      setSelectedId('new');
      resetForm();
      return;
    }

    const id = Number(value);
    const branch = branches.find((item) => item.id === id);
    if (!branch) {
      setSelectedId('new');
      resetForm();
      return;
    }

    setSelectedId(id);
    setTitle(branch.title);
    setDescription(branch.description);
    setCategory(branch.category);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStatus(null);
    setError(null);

    const payload = { title, description, category };

    try {
      if (selectedId === 'new') {
        await apiFetch('/api/admin/branches', {
          method: 'POST',
          body: JSON.stringify(payload),
          authToken: token
        });
        setStatus('Ветка создана');
      } else {
        await apiFetch(`/api/admin/branches/${selectedId}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
          authToken: token
        });
        setStatus('Ветка обновлена');
      }
      router.refresh();
      if (selectedId === 'new') {
        resetForm();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось сохранить ветку');
    }
  };

  return (
    <div className="card">
      <h3>Управление ветками</h3>
      <p style={{ color: 'var(--text-muted)' }}>
        Создавайте или обновляйте ветки, чтобы миссии были организованы по сюжетам и категориям.
      </p>
      <form onSubmit={handleSubmit} className="admin-form">
        <label>
          Выбранная ветка
          <select value={selectedId === 'new' ? 'new' : String(selectedId)} onChange={(event) => handleSelect(event.target.value)}>
            <option value="new">Новая ветка</option>
            {branches.map((branch) => (
              <option key={branch.id} value={branch.id}>
                {branch.title}
              </option>
            ))}
          </select>
        </label>

        <label>
          Название
          <input value={title} onChange={(event) => setTitle(event.target.value)} required />
        </label>

        <label>
          Описание
          <textarea value={description} onChange={(event) => setDescription(event.target.value)} required rows={3} />
        </label>

        <label>
          Категория
          <select value={category} onChange={(event) => setCategory(event.target.value)}>
            {categoryOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>

        <button type="submit" className="primary">Сохранить</button>

        {status && <p style={{ color: 'var(--success)', marginTop: '0.5rem' }}>{status}</p>}
        {error && <p style={{ color: 'var(--error)', marginTop: '0.5rem' }}>{error}</p>}
      </form>
    </div>
  );
}
