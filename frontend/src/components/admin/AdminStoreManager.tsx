'use client';

import { ChangeEvent, FormEvent, useState } from 'react';
import styled from 'styled-components';

import { apiFetch } from '../../lib/api';

interface StoreItem {
  id: number;
  name: string;
  description: string;
  cost_mana: number;
  stock: number;
  image_url?: string | null;
}

interface Feedback {
  kind: 'success' | 'error';
  text: string;
}

const SectionCard = styled.div`
  background: rgba(17, 22, 51, 0.8);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(108, 92, 231, 0.25);
  display: grid;
  gap: 1.5rem;
`;

const ItemsGrid = styled.div`
  display: grid;
  gap: 1.25rem;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
`;

const ItemCard = styled.div`
  background: rgba(10, 15, 40, 0.75);
  border-radius: 14px;
  padding: 1.25rem;
  border: 1px solid rgba(108, 92, 231, 0.25);
  display: grid;
  gap: 1rem;
`;

const ItemImage = styled.img`
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid rgba(108, 92, 231, 0.35);
  background: rgba(108, 92, 231, 0.08);
`;

const ImagePlaceholder = styled.div`
  width: 100%;
  aspect-ratio: 4 / 3;
  border-radius: 12px;
  border: 1px dashed rgba(108, 92, 231, 0.35);
  display: grid;
  place-items: center;
  color: var(--text-muted);
  background: rgba(108, 92, 231, 0.05);
`;

const FieldGroup = styled.div`
  display: grid;
  gap: 0.5rem;
`;

const InlineFields = styled.div`
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
`;

const Label = styled.label`
  display: grid;
  gap: 0.35rem;
  font-size: 0.875rem;
  color: var(--text-muted);
`;

const TextInput = styled.input`
  border-radius: 8px;
  border: 1px solid rgba(108, 92, 231, 0.35);
  background: rgba(9, 13, 34, 0.8);
  padding: 0.5rem 0.75rem;
  color: var(--text-primary);
`;

const TextArea = styled.textarea`
  border-radius: 8px;
  border: 1px solid rgba(108, 92, 231, 0.35);
  background: rgba(9, 13, 34, 0.8);
  padding: 0.5rem 0.75rem;
  color: var(--text-primary);
  min-height: 96px;
  resize: vertical;
`;

const FileInput = styled.input`
  border-radius: 8px;
  border: 1px dashed rgba(108, 92, 231, 0.35);
  padding: 0.5rem;
  background: rgba(9, 13, 34, 0.6);
`;

const Actions = styled.div`
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
`;

const Message = styled.p<{ kind: 'success' | 'error' }>`
  margin: 0;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  background: ${({ kind }) =>
    kind === 'success' ? 'rgba(46, 213, 115, 0.12)' : 'rgba(230, 57, 70, 0.12)'};
  color: ${({ kind }) => (kind === 'success' ? 'var(--accent-light)' : 'var(--error)')};
  border: 1px solid
    ${({ kind }) => (kind === 'success' ? 'rgba(46, 213, 115, 0.35)' : 'rgba(230, 57, 70, 0.35)')};
`;

interface AdminStoreManagerProps {
  items: StoreItem[];
  token: string;
}

export function AdminStoreManager({ items, token }: AdminStoreManagerProps) {
  const [storeItems, setStoreItems] = useState<StoreItem[]>(items);
  const [message, setMessage] = useState<Feedback | null>(null);
  const [creating, setCreating] = useState(false);
  const [updatingId, setUpdatingId] = useState<number | null>(null);
  const [uploadingImageId, setUploadingImageId] = useState<number | null>(null);
  const [newImageFile, setNewImageFile] = useState<File | null>(null);

  const resolveErrorMessage = (error: unknown) => {
    if (error instanceof Error) {
      return error.message || 'Произошла ошибка. Попробуйте ещё раз.';
    }
    return 'Произошла ошибка. Попробуйте ещё раз.';
  };

  const handleCreate = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);

    const name = String(formData.get('name') ?? '').trim();
    const description = String(formData.get('description') ?? '').trim();
    const costMana = Number(formData.get('cost_mana') ?? 0);
    const stock = Number(formData.get('stock') ?? 0);

    if (!name || !description) {
      setMessage({ kind: 'error', text: 'Заполните название и описание товара.' });
      return;
    }
    if (!newImageFile) {
      setMessage({ kind: 'error', text: 'Добавьте изображение перед созданием товара.' });
      return;
    }

    const payload = new FormData();
    payload.append('name', name);
    payload.append('description', description);
    payload.append('cost_mana', String(costMana));
    payload.append('stock', String(stock));
    payload.append('image', newImageFile);

    try {
      setCreating(true);
      setMessage(null);
      const created = await apiFetch<StoreItem>('/api/admin/store/items', {
        method: 'POST',
        body: payload,
        authToken: token
      });
      setStoreItems((prev) => [...prev, created]);
      setMessage({ kind: 'success', text: 'Товар создан. Он сразу появился в витрине.' });
      setNewImageFile(null);
      form.reset();
    } catch (error) {
      setMessage({ kind: 'error', text: resolveErrorMessage(error) });
    } finally {
      setCreating(false);
    }
  };

  const handleUpdate = (item: StoreItem) => async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);

    const payload: Record<string, unknown> = {};
    const name = String(formData.get('name') ?? '').trim();
    const description = String(formData.get('description') ?? '').trim();
    const costMana = formData.get('cost_mana');
    const stock = formData.get('stock');

    if (name && name !== item.name) {
      payload.name = name;
    }
    if (description && description !== item.description) {
      payload.description = description;
    }
    if (costMana !== null && costMana !== '') {
      const parsed = Number(costMana);
      if (!Number.isNaN(parsed) && parsed !== item.cost_mana) {
        payload.cost_mana = parsed;
      }
    }
    if (stock !== null && stock !== '') {
      const parsed = Number(stock);
      if (!Number.isNaN(parsed) && parsed !== item.stock) {
        payload.stock = parsed;
      }
    }

    if (Object.keys(payload).length === 0) {
      setMessage({ kind: 'error', text: 'Измените поля перед сохранением.' });
      return;
    }

    try {
      setUpdatingId(item.id);
      setMessage(null);
      const updated = await apiFetch<StoreItem>(`/api/admin/store/items/${item.id}`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
        authToken: token
      });
      setStoreItems((prev) => prev.map((candidate) => (candidate.id === item.id ? updated : candidate)));
      setMessage({ kind: 'success', text: `Товар «${updated.name}» обновлён.` });
    } catch (error) {
      setMessage({ kind: 'error', text: resolveErrorMessage(error) });
    } finally {
      setUpdatingId(null);
    }
  };

  const handleImageUpload = (itemId: number) => async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    const payload = new FormData();
    payload.append('image', file);

    try {
      setUploadingImageId(itemId);
      setMessage(null);
      const updated = await apiFetch<StoreItem>(`/api/admin/store/items/${itemId}/image`, {
        method: 'POST',
        body: payload,
        authToken: token
      });
      setStoreItems((prev) => prev.map((candidate) => (candidate.id === itemId ? updated : candidate)));
      setMessage({ kind: 'success', text: `Изображение для «${updated.name}» обновлено.` });
    } catch (error) {
      setMessage({ kind: 'error', text: resolveErrorMessage(error) });
    } finally {
      setUploadingImageId(null);
      event.target.value = '';
    }
  };

  const handleRemoveImage = async (item: StoreItem) => {
    if (!item.image_url) {
      return;
    }
    try {
      setUpdatingId(item.id);
      setMessage(null);
      const updated = await apiFetch<StoreItem>(`/api/admin/store/items/${item.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ image_url: null }),
        authToken: token
      });
      setStoreItems((prev) => prev.map((candidate) => (candidate.id === item.id ? updated : candidate)));
      setMessage({ kind: 'success', text: `Изображение для «${updated.name}» удалено.` });
    } catch (error) {
      setMessage({ kind: 'error', text: resolveErrorMessage(error) });
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <SectionCard>
      <div>
        <h3>Магазин экипажа</h3>
        <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
          Управляйте витриной: добавляйте новые призы, обновляйте описания и следите за складом. Изображения
          загружаются как файлы и сразу становятся доступны пилотам.
        </p>
      </div>

      {message && <Message kind={message.kind}>{message.text}</Message>}

      <section>
        <h4 style={{ marginBottom: '0.75rem' }}>Добавить новый товар</h4>
        <form onSubmit={handleCreate} className="grid" style={{ gap: '0.75rem' }}>
          <FieldGroup>
            <Label>
              Название
              <TextInput name="name" placeholder="Например, экскурсия по цехам" required />
            </Label>
            <Label>
              Описание
              <TextArea name="description" placeholder="Коротко расскажите, что получает пилот" required />
            </Label>
            <InlineFields>
              <Label>
                Стоимость ⚡
                <TextInput type="number" min={0} name="cost_mana" defaultValue={100} required />
              </Label>
              <Label>
                Остаток на складе
                <TextInput type="number" min={0} name="stock" defaultValue={1} required />
              </Label>
            </InlineFields>
            <Label>
              Изображение товара
              <FileInput
                type="file"
                accept="image/png,image/jpeg,image/webp"
                onChange={(event) => setNewImageFile(event.target.files?.[0] ?? null)}
                required
              />
            </Label>
          </FieldGroup>
          <button className="primary" type="submit" disabled={creating}>
            {creating ? 'Сохраняем…' : 'Создать товар'}
          </button>
        </form>
      </section>

      <section>
        <h4 style={{ marginBottom: '0.75rem' }}>Существующие позиции</h4>
        {storeItems.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>Пока нет товаров — добавьте первый приз.</p>
        ) : (
          <ItemsGrid>
            {storeItems.map((item) => (
              <ItemCard key={item.id}>
                {item.image_url ? (
                  <ItemImage src={item.image_url} alt={`Изображение товара «${item.name}»`} loading="lazy" />
                ) : (
                  <ImagePlaceholder>Изображение не загружено</ImagePlaceholder>
                )}

                <form onSubmit={handleUpdate(item)} className="grid" style={{ gap: '0.75rem' }}>
                  <FieldGroup>
                    <Label>
                      Название
                      <TextInput name="name" defaultValue={item.name} required />
                    </Label>
                    <Label>
                      Описание
                      <TextArea name="description" defaultValue={item.description} required />
                    </Label>
                    <InlineFields>
                      <Label>
                        Стоимость ⚡
                        <TextInput type="number" name="cost_mana" defaultValue={item.cost_mana} min={0} required />
                      </Label>
                      <Label>
                        Остаток
                        <TextInput type="number" name="stock" defaultValue={item.stock} min={0} required />
                      </Label>
                    </InlineFields>
                  </FieldGroup>
                  <button className="secondary" type="submit" disabled={updatingId === item.id}>
                    {updatingId === item.id ? 'Сохраняем…' : 'Сохранить изменения'}
                  </button>
                </form>

                <FieldGroup>
                  <Label>
                    Обновить изображение
                    <FileInput
                      type="file"
                      accept="image/png,image/jpeg,image/webp"
                      onChange={handleImageUpload(item.id)}
                    />
                  </Label>
                  <Actions>
                    <button
                      type="button"
                      className="secondary"
                      onClick={() => handleRemoveImage(item)}
                      disabled={!item.image_url || updatingId === item.id}
                    >
                      Удалить изображение
                    </button>
                    {uploadingImageId === item.id && <span style={{ color: 'var(--text-muted)' }}>Загружаем…</span>}
                  </Actions>
                </FieldGroup>
              </ItemCard>
            ))}
          </ItemsGrid>
        )}
      </section>
    </SectionCard>
  );
}
