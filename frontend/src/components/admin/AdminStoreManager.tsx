'use client';

import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from 'react';
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
}

const emptyForm: FormState = {
  name: '',
  description: '',
  cost_mana: 0,
  stock: 0,
};

export function AdminStoreManager({ token, items }: Props) {
  const router = useRouter();
  const [selectedId, setSelectedId] = useState<number | 'new'>('new');
  const [form, setForm] = useState<FormState>(emptyForm);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const itemById = useMemo(() => new Map(items.map((item) => [item.id, item])), [items]);
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const resolveImageSrc = (source: string | null | undefined) => {
    if (!source) {
      return null;
    }
    if (source.startsWith('http://') || source.startsWith('https://')) {
      return source;
    }
    if (source.startsWith('/uploads/')) {
      return `${apiBaseUrl}${source}`;
    }
    return source;
  };

  const updatePreview = (next: string | null) => {
    setImagePreview((previous) => {
      if (previous && previous.startsWith('blob:') && previous !== next) {
        URL.revokeObjectURL(previous);
      }
      return next;
    });
  };

  useEffect(() => {
    return () => {
      if (imagePreview && imagePreview.startsWith('blob:')) {
        URL.revokeObjectURL(imagePreview);
      }
    };
  }, [imagePreview]);

  const resetForm = () => {
    setForm({ ...emptyForm });
    setSelectedId('new');
    setImageFile(null);
    updatePreview(null);
  };

  const handleSelect = (id: number | 'new') => {
    setStatus(null);
    setError(null);
    setSelectedId(id);
    setImageFile(null);
    if (id === 'new') {
      setForm({ ...emptyForm });
      updatePreview(null);
    } else {
      const item = itemById.get(id);
      if (item) {
        // Подставляем актуальные значения товара в форму.
        setForm({
          name: item.name,
          description: item.description,
          cost_mana: item.cost_mana,
          stock: item.stock,
        });
        updatePreview(resolveImageSrc(item.image_url));
      }
    }
  };

  const handleImageChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      setImageFile(null);
      if (selectedId !== 'new') {
        const current = itemById.get(selectedId);
        updatePreview(resolveImageSrc(current?.image_url));
      } else {
        updatePreview(null);
      }
      return;
    }

    setImageFile(file);
    const previewUrl = URL.createObjectURL(file);
    updatePreview(previewUrl);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSaving(true);
    setStatus(null);
    setError(null);

    try {
      const name = form.name.trim();
      const description = form.description.trim();

      if (!name || !description) {
        throw new Error('Название и описание не должны быть пустыми.');
      }

      if (selectedId === 'new') {
        if (!imageFile) {
          throw new Error('Добавьте изображение товара через загрузку файла.');
        }

        const formData = new FormData();
        formData.append('name', name);
        formData.append('description', description);
        formData.append('cost_mana', String(form.cost_mana));
        formData.append('stock', String(form.stock));
        formData.append('image', imageFile);

        await apiFetch('/api/admin/store/items', {
          method: 'POST',
          body: formData,
          authToken: token,
        });
        setStatus('Товар добавлен. Мы обновили список, можно проверить карточку ниже.');
        resetForm();
      } else {
        const payload = {
          name,
          description,
          cost_mana: form.cost_mana,
          stock: form.stock,
        };

        await apiFetch(`/api/admin/store/items/${selectedId}`, {
          method: 'PATCH',
          body: JSON.stringify(payload),
          authToken: token,
        });
        if (imageFile) {
          const imageData = new FormData();
          imageData.append('image', imageFile);
          await apiFetch(`/api/admin/store/items/${selectedId}/image`, {
            method: 'POST',
            body: imageData,
            authToken: token,
          });
          setImageFile(null);
        }
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

  useEffect(() => {
    if (selectedId === 'new' || imageFile) {
      return;
    }
    const current = items.find((item) => item.id === selectedId);
    if (current) {
      updatePreview(resolveImageSrc(current.image_url));
    }
  }, [items, selectedId, imageFile]);

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
            Изображение товара
          </label>
          <input
            id="store-image"
            type="file"
            accept="image/png,image/jpeg,image/webp"
            onChange={handleImageChange}
          />
          <small style={{ color: 'var(--text-muted)' }}>
            Загрузите файл PNG, JPG или WEBP. После сохранения он станет доступен на витрине.
          </small>
          {imagePreview ? (
            <img
              src={imagePreview}
              alt="Предпросмотр изображения товара"
              style={{
                width: '100%',
                maxWidth: '240px',
                marginTop: '1rem',
                borderRadius: '10px',
                objectFit: 'cover',
              }}
            />
          ) : (
            <p style={{ color: 'var(--text-muted)', marginTop: '0.75rem' }}>
              Предпросмотр появится после загрузки файла.
            </p>
          )}
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
