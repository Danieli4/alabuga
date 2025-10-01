'use client';

import { ChangeEvent, FormEvent, useEffect, useMemo, useRef, useState } from 'react';
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
  const [currentImageUrl, setCurrentImageUrl] = useState<string | null>(null);
  const [removeImage, setRemoveImage] = useState(false);
  const objectUrlRef = useRef<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const itemById = useMemo(() => new Map(items.map((item) => [item.id, item])), [items]);

  const updatePreview = (url: string | null, isObjectUrl = false) => {
    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current);
      objectUrlRef.current = null;
    }
    if (isObjectUrl && url) {
      objectUrlRef.current = url;
    }
    setImagePreview(url);
  };

  useEffect(() => {
    return () => {
      if (objectUrlRef.current) {
        URL.revokeObjectURL(objectUrlRef.current);
        objectUrlRef.current = null;
      }
    };
  }, []);

  const resetForm = () => {
    setForm({ ...emptyForm });
    setSelectedId('new');
    setImageFile(null);
    setCurrentImageUrl(null);
    setRemoveImage(false);
    updatePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSelect = (id: number | 'new') => {
    setStatus(null);
    setError(null);
    setSelectedId(id);
    if (id === 'new') {
      setForm({ ...emptyForm });
      setImageFile(null);
      setCurrentImageUrl(null);
      setRemoveImage(false);
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
        setCurrentImageUrl(item.image_url ?? null);
        setImageFile(null);
        setRemoveImage(false);
        updatePreview(item.image_url ?? null);
      }
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleImageChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    setStatus(null);
    setError(null);

    if (file) {
      setImageFile(file);
      setRemoveImage(false);
      const previewUrl = URL.createObjectURL(file);
      updatePreview(previewUrl, true);
    } else {
      setImageFile(null);
      updatePreview(removeImage ? null : currentImageUrl, false);
    }
  };

  const handleClearSelectedFile = () => {
    setImageFile(null);
    updatePreview(removeImage ? null : currentImageUrl, false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleToggleRemoveImage = () => {
    setRemoveImage((prev) => {
      const next = !prev;
      updatePreview(next ? null : currentImageUrl, false);
      return next;
    });
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSaving(true);
    setStatus(null);
    setError(null);

    try {
      const trimmedName = form.name.trim();
      const trimmedDescription = form.description.trim();

      if (!trimmedName || !trimmedDescription) {
        throw new Error('Название и описание не должны быть пустыми.');
      }

      const formData = new FormData();
      formData.append('name', trimmedName);
      formData.append('description', trimmedDescription);
      formData.append('cost_mana', String(form.cost_mana));
      formData.append('stock', String(form.stock));

      if (imageFile) {
        formData.append('image', imageFile);
      }

      if (removeImage && selectedId !== 'new') {
        formData.append('remove_image', 'true');
      }

      if (selectedId === 'new') {
        await apiFetch<StoreItem>('/api/admin/store/items', {
          method: 'POST',
          body: formData,
          authToken: token,
        });
        setStatus('Товар добавлен. Мы обновили список, можно проверить карточку ниже.');
        resetForm();
      } else {
        const saved = await apiFetch<StoreItem>(`/api/admin/store/items/${selectedId}`, {
          method: 'PATCH',
          body: formData,
          authToken: token,
        });
        setStatus('Изменения сохранены. Страница магазина обновится автоматически.');
        setForm({
          name: saved.name,
          description: saved.description,
          cost_mana: saved.cost_mana,
          stock: saved.stock,
        });
        setCurrentImageUrl(saved.image_url ?? null);
        setImageFile(null);
        setRemoveImage(false);
        updatePreview(saved.image_url ?? null, false);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
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
            Изображение товара
          </label>
          {imagePreview && (
            <img
              src={imagePreview}
              alt={form.name || 'Превью товара'}
              style={{
                width: '100%',
                maxHeight: '200px',
                borderRadius: '10px',
                marginBottom: '0.75rem',
                objectFit: 'cover',
              }}
            />
          )}
          <input
            id="store-image"
            ref={fileInputRef}
            type="file"
            accept="image/png,image/jpeg,image/webp"
            onChange={handleImageChange}
            disabled={saving}
          />
          <small style={{ color: 'var(--text-muted)' }}>
            Загрузите файл JPG, PNG или WEBP. Он сохранится в директории uploads на сервере.
          </small>
          {(imageFile || imagePreview) && (
            <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              {imageFile && (
                <button type="button" className="secondary" onClick={handleClearSelectedFile} disabled={saving}>
                  Очистить выбранный файл
                </button>
              )}
              {selectedId !== 'new' && currentImageUrl && !imageFile && (
                <button type="button" className="secondary" onClick={handleToggleRemoveImage} disabled={saving}>
                  {removeImage ? 'Отменить удаление' : 'Удалить текущее изображение'}
                </button>
              )}
            </div>
          )}
          {removeImage && (
            <small style={{ color: 'var(--error)' }}>
              Изображение будет удалено после сохранения изменений.
            </small>
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
