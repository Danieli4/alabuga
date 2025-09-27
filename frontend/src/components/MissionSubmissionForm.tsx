'use client';

import { useState } from 'react';
import { apiFetch } from '../lib/api';

interface MissionSubmissionFormProps {
  missionId: number;
  token?: string;
  locked?: boolean;
}

export function MissionSubmissionForm({ missionId, token, locked = false }: MissionSubmissionFormProps) {
  const [comment, setComment] = useState('');
  const [proofUrl, setProofUrl] = useState('');
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!token) {
      setStatus('Не удалось получить токен демо-пользователя.');
      return;
    }

    if (locked) {
      setStatus('Миссия пока недоступна — выполните предыдущие условия.');
      return;
    }

    try {
      setLoading(true);
      setStatus(null);
      await apiFetch(`/api/missions/${missionId}/submit`, {
        method: 'POST',
        body: JSON.stringify({ comment, proof_url: proofUrl }),
        authToken: token
      });
      setStatus('Отчёт отправлен! HR проверит миссию в панели модерации.');
      setComment('');
      setProofUrl('');
    } catch (error) {
      if (error instanceof Error) {
        setStatus(error.message);
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit} style={{ marginTop: '2rem' }}>
      <h3>Отправить отчёт</h3>
      <label style={{ display: 'block', marginBottom: '0.5rem' }}>
        Комментарий
        <textarea
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          rows={4}
          style={{ width: '100%', marginTop: '0.5rem', borderRadius: '12px', padding: '0.75rem' }}
          placeholder="Опишите, что сделали."
          disabled={locked}
        />
      </label>
      <label style={{ display: 'block', marginBottom: '0.5rem' }}>
        Ссылка на доказательство
        <input
          type="url"
          value={proofUrl}
          onChange={(event) => setProofUrl(event.target.value)}
          style={{ width: '100%', marginTop: '0.5rem', borderRadius: '12px', padding: '0.75rem' }}
          placeholder="https://..."
          disabled={locked}
        />
      </label>
      <button className="primary" type="submit" disabled={loading || locked}>
        {locked ? 'Недоступно' : loading ? 'Отправляем...' : 'Отправить HR'}
      </button>
      {status && <p style={{ marginTop: '1rem', color: 'var(--accent-light)' }}>{status}</p>}
    </form>
  );
}
