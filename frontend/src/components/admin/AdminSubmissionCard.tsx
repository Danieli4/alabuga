'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

import { apiFetch, clientApiUrl } from '../../lib/api';

type Submission = {
  mission_id: number;
  status: string;
  comment: string | null;
  proof_url: string | null;
  resume_link: string | null;
  passport_url: string | null;
  photo_url: string | null;
  resume_url: string | null;
  awarded_xp: number;
  awarded_mana: number;
  updated_at: string;
  id: number;
};

interface Props {
  submission: Submission;
  token: string;
}

export function AdminSubmissionCard({ submission, token }: Props) {
  const router = useRouter();
  const [loading, setLoading] = useState<'approve' | 'reject' | null>(null);
  const [error, setError] = useState<string | null>(null);

  const downloadDocument = async (path: string | null, fallbackName: string) => {
    if (!path) {
      return;
    }

    try {
      setError(null);
      const response = await fetch(`${clientApiUrl}${path}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const contentType = response.headers.get('content-type') ?? '';
        if (contentType.includes('application/json')) {
          try {
            const data = await response.json();
            const detail = data?.detail ?? data?.message ?? data?.error;
            throw new Error(detail ? String(detail) : `Не удалось скачать файл (${response.status}).`);
          } catch (err) {
            if (err instanceof Error) {
              throw err;
            }
            throw new Error(`Не удалось скачать файл (${response.status}).`);
          }
        }

        const text = await response.text();
        throw new Error(text || `Не удалось скачать файл (${response.status}).`);
      }

      const blob = await response.blob();
      const disposition = response.headers.get('content-disposition') ?? '';

      let filename = fallbackName;
      const utf8Match = disposition.match(/filename\*=UTF-8''([^;]+)/i);
      if (utf8Match && utf8Match[1]) {
        try {
          filename = decodeURIComponent(utf8Match[1]);
        } catch {
          filename = utf8Match[1];
        }
      } else {
        const asciiMatch = disposition.match(/filename="?([^";]+)"?/i);
        if (asciiMatch && asciiMatch[1]) {
          filename = asciiMatch[1];
        }
      }

      const objectUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = objectUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(objectUrl);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось скачать файл');
    }
  };

  const handleAction = async (action: 'approve' | 'reject') => {
    setLoading(action);
    setError(null);
    try {
      await apiFetch(`/api/admin/submissions/${submission.id}/${action}`, {
        method: 'POST',
        authToken: token
      });
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось выполнить действие');
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="card" style={{ marginBottom: 0 }}>
      <h4>Миссия #{submission.mission_id}</h4>
      <p>Статус: {submission.status}</p>
      {submission.comment && <p>Комментарий пилота: {submission.comment}</p>}
      {submission.proof_url && (
        <p>
          Доказательство:{' '}
          <a href={submission.proof_url} target="_blank" rel="noreferrer">
            открыть
          </a>
        </p>
      )}
      <div style={{ marginTop: '0.5rem' }}>
        <strong>Документы кандидата:</strong>
        <ul style={{ listStyle: 'none', padding: 0, margin: '0.5rem 0 0' }}>
          <li>
            Паспорт:{' '}
            {submission.passport_url ? (
              <a
                href={submission.passport_url}
                onClick={(event) => {
                  event.preventDefault();
                  void downloadDocument(submission.passport_url, 'passport');
                }}
              >
                скачать
              </a>
            ) : (
              'нет файла'
            )}
          </li>
          <li>
            Фото:{' '}
            {submission.photo_url ? (
              <a
                href={submission.photo_url}
                onClick={(event) => {
                  event.preventDefault();
                  void downloadDocument(submission.photo_url, 'photo');
                }}
              >
                скачать
              </a>
            ) : (
              'нет файла'
            )}
          </li>
          <li>
            Резюме (файл):{' '}
            {submission.resume_url ? (
              <a
                href={submission.resume_url}
                onClick={(event) => {
                  event.preventDefault();
                  void downloadDocument(submission.resume_url, 'resume');
                }}
              >
                скачать
              </a>
            ) : (
              'нет файла'
            )}
          </li>
          <li>
            Резюме (ссылка): {submission.resume_link ? <a href={submission.resume_link} target="_blank" rel="noreferrer">открыть</a> : 'не указана'}
          </li>
        </ul>
      </div>
      <small style={{ color: 'var(--text-muted)' }}>
        Обновлено: {new Date(submission.updated_at).toLocaleString('ru-RU')}
      </small>
      <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.75rem' }}>
        <button
          className="primary"
          onClick={() => handleAction('approve')}
          disabled={loading === 'approve'}
        >
          {loading === 'approve' ? 'Одобряем...' : 'Одобрить'}
        </button>
        <button
          className="secondary"
          onClick={() => handleAction('reject')}
          disabled={loading === 'reject'}
          style={{ cursor: loading === 'reject' ? 'not-allowed' : 'pointer' }}
        >
          {loading === 'reject' ? 'Отклоняем...' : 'Отклонить'}
        </button>
      </div>
      {error && <p style={{ color: 'var(--error)', marginTop: '0.5rem' }}>{error}</p>}
    </div>
  );
}
