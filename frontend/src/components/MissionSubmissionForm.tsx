'use client';

import { useRef, useState } from 'react';
import { apiFetch } from '../lib/api';

type ExistingSubmission = {
  id: number;
  comment: string | null;
  proof_url: string | null;
  resume_link: string | null;
  passport_url: string | null;
  photo_url: string | null;
  resume_url: string | null;
  status: 'pending' | 'approved' | 'rejected';
};

interface MissionSubmissionFormProps {
  missionId: number;
  token?: string;
  locked?: boolean;
  submission?: ExistingSubmission | null;
  completed?: boolean;
  requiresDocuments?: boolean;
}

export function MissionSubmissionForm({ missionId, token, locked = false, submission, completed = false, requiresDocuments = false }: MissionSubmissionFormProps) {
  const [currentSubmission, setCurrentSubmission] = useState<ExistingSubmission | null>(submission ?? null);
  const [comment, setComment] = useState(() => {
    if (submission?.status === 'rejected') {
      return '';
    }
    return submission?.comment ?? '';
  });
  const [proofUrl, setProofUrl] = useState(submission?.proof_url ?? '');
  const [resumeLink, setResumeLink] = useState(submission?.resume_link ?? '');
  const initialStatus = submission?.status === 'approved' || completed
    ? 'Миссия уже зачтена. Вы можете просматривать прикреплённые документы.'
    : submission?.status === 'rejected'
      ? 'Предыдущая отправка отклонена. Проверьте комментарий HR и отправьте отчёт заново.'
      : null;
  const [status, setStatus] = useState<string | null>(initialStatus);
  const [loading, setLoading] = useState(false);

  const passportInputRef = useRef<HTMLInputElement>(null);
  const photoInputRef = useRef<HTMLInputElement>(null);
  const resumeInputRef = useRef<HTMLInputElement>(null);

  const isApproved = completed || currentSubmission?.status === 'approved';
  const isRejected = !completed && currentSubmission?.status === 'rejected';
  const reviewerComment = isRejected && currentSubmission?.comment ? currentSubmission.comment : null;

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      setStatus('Не удалось получить токен демо-пользователя.');
      return;
    }

    if (locked) {
      setStatus('Миссия пока недоступна — выполните предыдущие условия.');
      return;
    }

    if (isApproved) {
      setStatus('Миссия уже зачтена. Дополнительная отправка не требуется.');
      return;
    }

    const passportFile = passportInputRef.current?.files?.[0];
    const photoFile = photoInputRef.current?.files?.[0];
    const resumeFile = resumeInputRef.current?.files?.[0];
    const resumeTrimmed = resumeLink.trim();

    if (requiresDocuments) {
      if (!currentSubmission?.passport_url && !passportFile) {
        setStatus('Добавьте скан паспорта кандидата.');
        return;
      }
      if (!currentSubmission?.photo_url && !photoFile) {
        setStatus('Приложите фотографию кандидата.');
        return;
      }
      const hasResumeAttachment = Boolean(currentSubmission?.resume_url || currentSubmission?.resume_link);
      if (!hasResumeAttachment && !resumeFile && !resumeTrimmed) {
        setStatus('Укажите ссылку на резюме или загрузите файл.');
        return;
      }
    }

    const formData = new FormData();
    formData.append('comment', comment.trim());
    formData.append('proof_url', proofUrl.trim());
    formData.append('resume_link', resumeTrimmed);

    if (passportFile) {
      formData.append('passport', passportFile);
    }

    if (photoFile) {
      formData.append('photo', photoFile);
    }

    if (resumeFile) {
      formData.append('resume_file', resumeFile);
    }

    try {
      setLoading(true);
      setStatus(null);
      const updated = await apiFetch<ExistingSubmission>(`/api/missions/${missionId}/submit`, {
        method: 'POST',
        body: formData,
        authToken: token
      });

      setCurrentSubmission(updated);
      setComment(updated.comment ?? '');
      setProofUrl(updated.proof_url ?? '');
      setResumeLink(updated.resume_link ?? '');

      if (passportInputRef.current) passportInputRef.current.value = '';
      if (photoInputRef.current) photoInputRef.current.value = '';
      if (resumeInputRef.current) resumeInputRef.current.value = '';

      const nextStatus = updated.status === 'approved'
        ? 'Миссия уже зачтена. Вы можете просматривать прикреплённые документы.'
        : 'Отчёт и документы отправлены! HR проверит миссию в панели модерации.';
      setStatus(nextStatus);
    } catch (error) {
      if (error instanceof Error) {
        setStatus(error.message);
      } else {
        setStatus('Не удалось отправить данные. Попробуйте позже.');
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit} style={{ marginTop: '2rem' }} encType="multipart/form-data">
      <h3>Отправить отчёт</h3>
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
          <strong>Предыдущая отправка отклонена.</strong>
          {reviewerComment && (
            <p style={{ marginTop: '0.5rem', whiteSpace: 'pre-wrap' }}>
              Комментарий HR: {reviewerComment}
            </p>
          )}
          {!reviewerComment && (
            <p style={{ marginTop: '0.5rem' }}>
              Проверьте материалы и приложите обновлённый отчёт.
            </p>
          )}
        </div>
      )}
      {requiresDocuments && (
        <p style={{ marginTop: '0.25rem', color: 'var(--text-muted)' }}>
          Для этой миссии необходимо приложить паспорт, фотографию и резюме. Файлы попадут напрямую в панель HR.
        </p>
      )}
      <label style={{ display: 'block', marginBottom: '0.75rem' }}>
        Комментарий
        <textarea
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          rows={4}
          style={{ width: '100%', marginTop: '0.5rem', borderRadius: '12px', padding: '0.75rem' }}
          placeholder="Опишите, что сделали."
          disabled={locked || isApproved}
        />
      </label>
      <label style={{ display: 'block', marginBottom: '0.75rem' }}>
        Ссылка на доказательство (опционально)
        <input
          type="url"
          value={proofUrl}
          onChange={(event) => setProofUrl(event.target.value)}
          style={{ width: '100%', marginTop: '0.5rem', borderRadius: '12px', padding: '0.75rem' }}
          placeholder="https://..."
          disabled={locked || isApproved}
        />
      </label>

      <fieldset style={{ border: '1px solid rgba(162, 155, 254, 0.35)', borderRadius: '16px', padding: '1rem', marginBottom: '1rem' }}>
        <legend style={{ padding: '0 0.5rem' }}>Документы</legend>
        <label style={{ display: 'block', marginBottom: '0.75rem' }}>
          Паспорт (PDF или изображение)
          <input
            ref={passportInputRef}
            type="file"
            name="passport"
            accept="application/pdf,image/*"
            style={{ marginTop: '0.5rem' }}
            disabled={locked || isApproved}
            required={requiresDocuments && !currentSubmission?.passport_url}
          />
        </label>
        <label style={{ display: 'block', marginBottom: '0.75rem' }}>
          Фотография кандидата
          <input
            ref={photoInputRef}
            type="file"
            name="photo"
            accept="image/*"
            style={{ marginTop: '0.5rem' }}
            disabled={locked || isApproved}
            required={requiresDocuments && !currentSubmission?.photo_url}
          />
        </label>
        <label style={{ display: 'block', marginBottom: '0.75rem' }}>
          Резюме (можно приложить файл и/или ссылку)
          <input
            ref={resumeInputRef}
            type="file"
            name="resume_file"
            accept="application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            style={{ marginTop: '0.5rem' }}
            disabled={locked || isApproved}
            required={requiresDocuments && !currentSubmission?.resume_url && !currentSubmission?.resume_link}
          />
          <input
            type="url"
            value={resumeLink}
            onChange={(event) => setResumeLink(event.target.value)}
            style={{ width: '100%', marginTop: '0.5rem', borderRadius: '12px', padding: '0.75rem' }}
            placeholder="https://disk.yandex.ru/..."
            disabled={locked || isApproved}
            required={requiresDocuments && !currentSubmission?.resume_url && !currentSubmission?.resume_link}
          />
        </label>

        {currentSubmission && (
          <div style={{ marginTop: '0.75rem', color: 'var(--text-muted)' }}>
            <strong>Загружено ранее:</strong>
            <ul style={{ listStyle: 'none', margin: '0.5rem 0 0', padding: 0 }}>
              <li>
                Паспорт: {currentSubmission.passport_url ? <a href={currentSubmission.passport_url} target="_blank" rel="noreferrer">скачать</a> : 'файл не прикреплён'}
              </li>
              <li>
                Фото: {currentSubmission.photo_url ? <a href={currentSubmission.photo_url} target="_blank" rel="noreferrer">скачать</a> : 'файл не прикреплён'}
              </li>
              <li>
                Резюме (файл): {currentSubmission.resume_url ? <a href={currentSubmission.resume_url} target="_blank" rel="noreferrer">скачать</a> : 'файл не прикреплён'}
              </li>
              <li>
                Резюме (ссылка): {currentSubmission.resume_link ? <a href={currentSubmission.resume_link} target="_blank" rel="noreferrer">открыть</a> : 'ссылка не указана'}
              </li>
            </ul>
          </div>
        )}
      </fieldset>

      <button className="primary" type="submit" disabled={loading || locked || isApproved}>
        {locked ? 'Недоступно' : isApproved ? 'Миссия выполнена' : loading ? 'Отправляем...' : 'Отправить HR'}
      </button>
      {status && (
        <p
          style={{
            marginTop: '1rem',
            color: status.includes('зачтена') ? 'var(--accent-light)' : status.startsWith('Отчёт') ? 'var(--accent-light)' : 'var(--error)'
          }}
        >
          {status}
        </p>
      )}
    </form>
  );
}
