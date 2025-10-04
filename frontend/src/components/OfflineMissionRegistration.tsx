'use client';

import { useState } from 'react';

import { apiFetch } from '../lib/api';

type SubmissionStatus = 'pending' | 'approved' | 'rejected';

interface ExistingSubmission {
  id: number;
  comment: string | null;
  status: SubmissionStatus;
}

interface OfflineMissionRegistrationProps {
  missionId: number;
  token?: string;
  locked?: boolean;
  registrationOpen: boolean;
  registeredCount: number;
  capacity?: number | null;
  submission?: ExistingSubmission | null;
  eventLocation?: string | null;
  eventAddress?: string | null;
  eventStartsAt?: string | null;
  eventEndsAt?: string | null;
  registrationDeadline?: string | null;
  registrationUrl?: string | null;
  registrationNotes?: string | null;
  contactPerson?: string | null;
  contactPhone?: string | null;
}

function formatDateTime(value?: string | null) {
  if (!value) return null;
  const date = new Date(value);
  const formattedDate = date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
  });
  const formattedTime = date.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  });
  return `${formattedDate} · ${formattedTime}`;
}

export function OfflineMissionRegistration({
  missionId,
  token,
  locked = false,
  registrationOpen,
  registeredCount,
  capacity,
  submission,
  eventLocation,
  eventAddress,
  eventStartsAt,
  eventEndsAt,
  registrationDeadline,
  registrationUrl,
  registrationNotes,
  contactPerson,
  contactPhone,
}: OfflineMissionRegistrationProps) {
  const [currentSubmission, setCurrentSubmission] = useState<ExistingSubmission | null>(submission ?? null);
  const [comment, setComment] = useState(() => {
    if (submission?.status === 'rejected') {
      return '';
    }
    return submission?.comment ?? '';
  });
  const initialStatus = (() => {
    if (submission?.status === 'approved') {
      return 'Регистрация подтверждена HR. Встретимся офлайн!';
    }
    if (submission?.status === 'pending') {
      return 'Заявка отправлена и ожидает подтверждения HR.';
    }
    if (submission?.status === 'rejected') {
      return 'Предыдущая заявка была отклонена. Проверьте комментарий и отправьте снова.';
    }
    if (!registrationOpen) {
      return 'Регистрация закрыта: лимит мест или срок записи истёк.';
    }
    return null;
  })();
  const [status, setStatus] = useState<string | null>(initialStatus);
  const [loading, setLoading] = useState(false);

  const submissionStatus = currentSubmission?.status;
  const isApproved = submissionStatus === 'approved';
  const isPending = submissionStatus === 'pending';
  const isRejected = submissionStatus === 'rejected';
  const reviewerComment = isRejected && currentSubmission?.comment ? currentSubmission.comment : null;
  const canSubmit = !locked && (registrationOpen || Boolean(currentSubmission));

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      setStatus('Не удалось авторизовать отправку. Перезагрузите страницу.');
      return;
    }

    if (!canSubmit) {
      setStatus('Регистрация закрыта.');
      return;
    }

    try {
      setLoading(true);
      setStatus(null);
      const formData = new FormData();
      formData.append('comment', comment.trim());
      const updated = await apiFetch<ExistingSubmission & { status: SubmissionStatus; comment: string | null }>(
        `/api/missions/${missionId}/submit`,
        {
          method: 'POST',
          body: formData,
          authToken: token,
        },
      );
      setCurrentSubmission(updated);
      setComment(updated.comment ?? '');
      if (updated.status === 'approved') {
        setStatus('Регистрация подтверждена HR.');
      } else {
        setStatus('Заявка отправлена! HR свяжется с вами при необходимости.');
      }
    } catch (error) {
      if (error instanceof Error) {
        setStatus(error.message);
      } else {
        setStatus('Не удалось отправить заявку. Попробуйте позже.');
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit} style={{ marginTop: '2rem' }}>
      <h3>Запись на офлайн-мероприятие</h3>
      <p style={{ color: 'var(--text-muted)' }}>
        {eventLocation ?? 'Офлайн событие'}
        {eventAddress ? ` · ${eventAddress}` : ''}
      </p>
      {isRejected && (
        <div
          style={{
            marginTop: '0.75rem',
            padding: '0.75rem',
            borderRadius: '12px',
            border: '1px solid rgba(255, 118, 117, 0.45)',
            background: 'rgba(255, 118, 117, 0.08)',
            color: 'var(--error)',
          }}
        >
          <strong>Предыдущая заявка отклонена.</strong>
          {reviewerComment && (
            <p style={{ marginTop: '0.5rem', whiteSpace: 'pre-wrap' }}>
              Комментарий HR: {reviewerComment}
            </p>
          )}
          {!reviewerComment && (
            <p style={{ marginTop: '0.5rem' }}>
              Обновите информацию и отправьте заявку повторно.
            </p>
          )}
        </div>
      )}
      <div style={{ display: 'grid', gap: '0.5rem', margin: '1rem 0' }}>
        {eventStartsAt && (
          <div>
            <strong>Начало:</strong> {formatDateTime(eventStartsAt)}
          </div>
        )}
        {eventEndsAt && (
          <div>
            <strong>Завершение:</strong> {formatDateTime(eventEndsAt)}
          </div>
        )}
        <div>
          <strong>Участников:</strong> {registeredCount}
          {capacity ? ` из ${capacity}` : ''}
        </div>
        {registrationDeadline && (
          <div>
            <strong>Запись до:</strong> {formatDateTime(registrationDeadline)}
          </div>
        )}
        {registrationUrl && (
          <div>
            <a href={registrationUrl} target="_blank" rel="noreferrer" className="secondary">
              Открыть страницу мероприятия
            </a>
          </div>
        )}
        {contactPerson && (
          <div>
            <strong>Контакт HR:</strong> {contactPerson}
            {contactPhone ? ` · ${contactPhone}` : ''}
          </div>
        )}
        {registrationNotes && (
          <div style={{ color: 'var(--accent-light)' }}>{registrationNotes}</div>
        )}
      </div>

      <label style={{ display: 'block', marginBottom: '0.75rem' }}>
        Комментарий (опционально)
        <textarea
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          rows={4}
          style={{ width: '100%', marginTop: '0.5rem', borderRadius: '12px', padding: '0.75rem' }}
          placeholder="Например: приеду с запасным удостоверением"
          disabled={!canSubmit || isApproved}
        />
      </label>

      <button className="primary" type="submit" disabled={!canSubmit || loading || isApproved}>
        {isApproved ? 'Регистрация подтверждена' : isPending ? 'Заявка отправлена' : registrationOpen ? 'Записаться' : 'Регистрация закрыта'}
      </button>

      {status && (
        <p
          style={{
            marginTop: '1rem',
            color: status.includes('подтверждена') ? 'var(--accent-light)' : status.includes('отправлена') ? 'var(--accent-light)' : 'var(--error)',
          }}
        >
          {status}
        </p>
      )}
    </form>
  );
}
