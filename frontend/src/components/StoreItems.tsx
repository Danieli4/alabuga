'use client';

import { useState } from 'react';
import styled from 'styled-components';
import { apiFetch } from '../lib/api';

type StoreItem = {
  id: number;
  name: string;
  description: string;
  cost_mana: number;
  stock: number;
};

const Card = styled.div`
  background: rgba(17, 22, 51, 0.85);
  border-radius: 14px;
  padding: 1.25rem;
  border: 1px solid rgba(108, 92, 231, 0.25);
`;

export function StoreItems({ items, token }: { items: StoreItem[]; token?: string }) {
  const [loadingId, setLoadingId] = useState<number | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  async function handlePurchase(id: number) {
    try {
      setLoadingId(id);
      setMessage(null);
      await apiFetch(`/api/store/orders`, {
        method: 'POST',
        body: JSON.stringify({ item_id: id }),
        authToken: token
      });
      setMessage('Заказ оформлен — проверьте журнал событий.');
    } catch (error) {
      if (error instanceof Error) {
        setMessage(error.message);
      }
    } finally {
      setLoadingId(null);
    }
  }

  return (
    <div>
      {message && <p style={{ color: 'var(--accent-light)' }}>{message}</p>}
      <div className="grid">
        {items.map((item) => (
          <Card key={item.id}>
            <h3 style={{ marginBottom: '0.5rem' }}>{item.name}</h3>
            <p style={{ color: 'var(--text-muted)' }}>{item.description}</p>
            <p style={{ marginTop: '1rem' }}>{item.cost_mana} ⚡ · остаток {item.stock}</p>
            <button
              className="primary"
              style={{ marginTop: '1rem' }}
              onClick={() => handlePurchase(item.id)}
              disabled={item.stock === 0 || !token || loadingId === item.id}
            >
              {loadingId === item.id ? 'Оформляем...' : 'Получить приз'}
            </button>
          </Card>
        ))}
      </div>
    </div>
  );
}
