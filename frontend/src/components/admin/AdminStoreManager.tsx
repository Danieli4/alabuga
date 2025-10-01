'use client';

import { FormEvent, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';

import { apiFetch } from '../../lib/api';

export type StoreItem = {
  id: number;
  name: string;
  description: string;
  cost_mana: number;
  stock: number;
  image_url: string | null;
};

interface Props {
  token: string;
  items: StoreItem[];
}

interface FormState {
  name: string;
  description: string;
  cost_mana: number;
  stock: number;
  image_url: string;
}

const emptyForm: FormState = {
  name: '',
  description: '',
  cost_mana: 0,
  stock: 0,
  image_url: '',
};

export function AdminStoreManager({ token, items }: Props) {
  const router = useRouter();
  const [selectedId, setSelectedId] = useState<number | 'new'>('new');
  const [form, setForm] = useState<FormState>(emptyForm);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const itemById = useMemo(() => new Map(items.map((item) => [item.id, item])), [items]);

  const resetForm = () => {
    setForm({ ...emptyForm });
    setSelectedId('new');
  };

  const handleSelect = (id: number | 'new') => {
    setStatus(null);
    setError(null);
    setSelectedId(id);
    if (id === 'new') {
      setForm({ ...emptyForm });
    } else {
      const item = itemById.get(id);
      if (item) {
        // Подставляем актуальные значения товара в форму.
        setForm({
          name: item.name,
          description: item.description,
          cost_mana: item.cost_mana,
          stock: item.stock,
          image_url: item.image_url ?? '',
        });
      }
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSaving(true);
    setStatus(null);
    setError(null);

    try {
      const payload = {
        name: form.name.trim(),
        description: form.description.trim(),
        cost_mana: form.cost_mana,
        stock: form.stock,
        image_url: form.image_url.trim() === '' ? null : form.image_url.trim(),
      };

      if (!payload.name || !payload.description) {
        throw new Error('Название и описание не должны быть пустыми.');
      }

      if (selectedId === 'new') {
        await apiFetch('/api/admin/store/items', {
          method: 'POST',
          body: JSON.stringify(payload),
          authToken: token,
        });
        setStatus('Товар добавлен. Мы обновили список, можно проверить карточку ниже.');
        resetForm();
      } else {
        await apiFetch(`/api/admin/store/items/${selectedId}`, {
          method: 'PATCH',
          body: JSON.stringify(payload),
          authToken: token,
        });
        setStatus('Изменения сохранены. Страница магазина обновится автоматически.');
      }

      router.refresh();
    } catch (submitError) {
      const message = submitError instanceof Error ? submitError.message : 'Не удалось сохранить товар.';
      setError(message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="card" style={{ gridColumn: '1 / -1' }}>
      <h3>Магазин</h3>
      <p style={{ color: 'var(--text-muted)' }}>
        Управляйте призами: загружайте изображения, задавайте стоимость в мане и поддерживайте актуальный остаток.
      </p>

      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <div style={{ minWidth: '260px' }}>
          <label className="label" htmlFor="store-item-select">
            Выберите товар
          </label>
          <select
            id="store-item-select"
            value={selectedId === 'new' ? 'new' : selectedId}
            onChange={(event) => {
              const value = event.target.value === 'new' ? 'new' : Number(event.target.value);
              handleSelect(value);
            }}
          >
            <option value="new">Добавить новый</option>
            {items.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </div>
        <button type="button" className="secondary" onClick={resetForm} disabled={saving}>
          Очистить форму
        </button>
      </div>

      <form onSubmit={handleSubmit} style={{ marginTop: '1.5rem', display: 'grid', gap: '1rem' }}>
        <div>
          <label className="label" htmlFor="store-name">
            Название
          </label>
          <input
            id="store-name"
            value={form.name}
            onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
            placeholder="Например, экскурсия по кампусу"
          />
        </div>

        <div>
          <label className="label" htmlFor="store-description">
            Описание
          </label>
          <textarea
            id="store-description"
            value={form.description}
            onChange={(event) => setForm((prev) => ({ ...prev, description: event.target.value }))}
            rows={4}
            placeholder="Коротко расскажите, что получит пилот"
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '1rem' }}>
          <div>
            <label className="label" htmlFor="store-cost">
              Стоимость (⚡)
            </label>
            <input
              id="store-cost"
              type="number"
              min={0}
              value={form.cost_mana}
              onChange={(event) => setForm((prev) => ({ ...prev, cost_mana: Number(event.target.value) }))}
            />
          </div>
          <div>
            <label className="label" htmlFor="store-stock">
              Остаток
            </label>
            <input
              id="store-stock"
              type="number"
              min={0}
              value={form.stock}
              onChange={(event) => setForm((prev) => ({ ...prev, stock: Number(event.target.value) }))}
            />
          </div>
        </div>

        <div>
          <label className="label" htmlFor="store-image">
            Ссылка на изображение
          </label>
          <input
            id="store-image"
            value={form.image_url}
            onChange={(event) => setForm((prev) => ({ ...prev, image_url: event.target.value }))}
            placeholder="Например, /store/excursion-alabuga.svg"
          />
          <small style={{ color: 'var(--text-muted)' }}>
            Изображение можно сохранить в public/store и указать относительный путь.
          </small>
        </div>

        <button className="primary" type="submit" disabled={saving}>
          {saving ? 'Сохраняем...' : selectedId === 'new' ? 'Добавить товар' : 'Сохранить изменения'}
        </button>
      </form>

      {status && (
        <p style={{ color: 'var(--accent-light)', marginTop: '1rem' }}>
          {status}
        </p>
      )}
      {error && (
        <p style={{ color: 'var(--error)', marginTop: '1rem' }}>
          {error}
        </p>
      )}
    </div>
  );
}
