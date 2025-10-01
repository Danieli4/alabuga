'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';

import { apiFetch } from '../lib/api';

interface MissionRegistrationPanelProps {
  missionId: number;
  token: string;
  isRegistered: boolean;
  isRegistrationOpen: boolean;
  registeredCount: number;
  spotsLeft: number | null;
  registrationDeadline: string | null;
  startsAt: string | null;
}

export function MissionRegistrationPanel({
  missionId,
  token,
  isRegistered,
  isRegistrationOpen,
  registeredCount,
  spotsLeft,
  registrationDeadline,
  startsAt
}: MissionRegistrationPanelProps) {
  const router = useRouter();
  const [registered, setRegistered] = useState(isRegistered);
  const [pending, setPending] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [count, setCount] = useState(registeredCount);
  const [spots, setSpots] = useState<number | null>(spotsLeft);

  const dateFormatter = new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit'
  });

  const startText = startsAt ? dateFormatter.format(new Date(startsAt)) : null;
  const deadlineText = registrationDeadline ? dateFormatter.format(new Date(registrationDeadline)) : null;

  const handleRegister = async () => {
    if (registered || pending || !isRegistrationOpen) {
      return;
    }
    setPending(true);
    setStatus(null);
    try {
      await apiFetch(`/api/missions/${missionId}/register`, {
        method: 'POST',
        authToken: token
      });
      setRegistered(true);
      setStatus('Вы успешно записались! Напомним о встрече ближе к дате.');
      setCount((prev) => prev + 1);
      setSpots((prev) => (prev === null ? prev : Math.max(prev - 1, 0)));
      router.refresh();
    } catch (error) {
      if (error instanceof Error) {
        setStatus(error.message);
      } else {
        setStatus('Не удалось записаться. Попробуйте повторить позже.');
      }
    } finally {
      setPending(false);
    }
  };

  return (
    <div className="card" style={{ marginTop: '2rem' }}>
      <h3>Регистрация</h3>
      <p style={{ marginTop: '0.5rem', color: 'var(--text-muted)' }}>
        Участников: {count}
        {spots !== null ? ` · свободно: ${spots}` : ''}
      </p>
      {startText && (
        <p style={{ marginTop: '0.25rem', color: 'var(--accent-light)' }}>Старт мероприятия: {startText}</p>
      )}
      {deadlineText && (
        <p style={{ marginTop: '0.25rem', color: 'var(--accent-light)' }}>Регистрация до {deadlineText}</p>
      )}
      {registered ? (
        <p style={{ marginTop: '0.75rem', color: 'var(--success)' }}>
          Вы уже зарегистрированы. Ждём на площадке!
        </p>
      ) : isRegistrationOpen ? (
        <button type="button" className="primary" onClick={handleRegister} disabled={pending} style={{ marginTop: '1rem' }}>
          {pending ? 'Отправка...' : 'Записаться'}
        </button>
      ) : (
        <p style={{ marginTop: '0.75rem', color: 'var(--text-muted)' }}>Регистрация закрыта.</p>
      )}
      {status && <p style={{ marginTop: '0.75rem', color: registered ? 'var(--success)' : 'var(--error)' }}>{status}</p>}
    </div>
  );
}
