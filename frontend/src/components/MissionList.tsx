'use client';

import styled from 'styled-components';

export interface MissionSummary {
  id: number;
  title: string;
  description: string;
  xp_reward: number;
  mana_reward: number;
  difficulty: string;
  format: 'online' | 'offline';
  is_active: boolean;
  is_available: boolean;
  locked_reasons: string[];
  is_completed: boolean;
  requires_documents: boolean;
  has_coding_challenges: boolean;
  coding_challenge_count: number;
  completed_coding_challenges: number;
  registration_deadline: string | null;
  starts_at: string | null;
  ends_at: string | null;
  location_title: string | null;
  location_address: string | null;
  location_url: string | null;
  capacity: number | null;
  registered_count: number;
  spots_left: number | null;
  is_registration_open: boolean;
  is_registered: boolean;
}

const Card = styled.div`
  background: rgba(17, 22, 51, 0.85);
  border-radius: 14px;
  padding: 1.25rem;
  border: 1px solid rgba(108, 92, 231, 0.25);
`;

export function MissionList({ missions }: { missions: MissionSummary[] }) {
  if (missions.length === 0) {
    return <p>Нет активных миссий — скоро появятся новые испытания.</p>;
  }

  const dateFormatter = new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit'
  });

  const timeFormatter = new Intl.DateTimeFormat('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
  });

  const formatDateTime = (value: string | null) => {
    if (!value) return null;
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return null;
    return dateFormatter.format(date);
  };

  return (
    <div className="grid">
      {missions.map((mission) => {
        const completed = mission.is_completed;
        const locked = !mission.is_available && !completed;
        const isOffline = mission.format === 'offline';
        let linkDisabled = locked;
        let actionClass = completed ? 'secondary' : locked ? 'secondary' : 'primary';
        let actionLabel = completed
          ? 'Миссия выполнена'
          : mission.is_available
          ? mission.has_coding_challenges
            ? 'Решать задачи'
            : 'Открыть брифинг'
          : 'Заблокировано';

        if (isOffline) {
          if (mission.is_registered) {
            actionLabel = 'Подробнее';
            actionClass = 'secondary';
          } else if (mission.is_registration_open && mission.is_available) {
            actionLabel = 'Записаться';
          } else {
            actionLabel = 'Подробнее';
            actionClass = 'secondary';
          }
          linkDisabled = locked;
        }

        const startText = formatDateTime(mission.starts_at);
        const endDate = mission.ends_at ? new Date(mission.ends_at) : null;
        const endText = endDate ? timeFormatter.format(endDate) : null;
        const deadlineText = formatDateTime(mission.registration_deadline);

        return (
          <Card key={mission.id} style={completed ? { opacity: 0.85 } : undefined}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="badge">{mission.difficulty}</span>
              {completed && <span style={{ color: '#55efc4', fontSize: '0.85rem' }}>✓ завершено</span>}
            </div>
            {mission.requires_documents && !completed && (
              <p style={{ marginTop: '0.25rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                🗂 Требуется загрузка документов
              </p>
            )}
            <h3 style={{ marginBottom: '0.5rem' }}>{mission.title}</h3>
            <p style={{ color: 'var(--text-muted)', minHeight: '3rem' }}>{mission.description}</p>
            {mission.has_coding_challenges && (
              <p style={{ marginTop: '0.5rem', color: 'var(--accent-light)' }}>
                💻 Прогресс: {mission.completed_coding_challenges}/{mission.coding_challenge_count} заданий
              </p>
            )}
            {isOffline && (
              <div style={{ marginTop: '0.75rem', fontSize: '0.9rem', lineHeight: 1.5 }}>
                <strong>Офлайн-мероприятие</strong>
                {startText && (
                  <p style={{ marginTop: '0.25rem' }}>
                    🗓 {startText}
                    {endText ? ` · до ${endText}` : ''}
                  </p>
                )}
                {mission.location_title && (
                  <p style={{ marginTop: '0.25rem' }}>
                    📍 {mission.location_title}
                    {mission.location_address ? ` — ${mission.location_address}` : ''}
                  </p>
                )}
                {mission.capacity !== null && (
                  <p style={{ marginTop: '0.25rem' }}>
                    👥 Свободных мест: {mission.spots_left ?? 0} из {mission.capacity}
                  </p>
                )}
                {mission.is_registered ? (
                  <p style={{ marginTop: '0.25rem', color: 'var(--success)' }}>Вы уже записаны на мероприятие.</p>
                ) : mission.is_registration_open ? (
                  deadlineText && (
                    <p style={{ marginTop: '0.25rem', color: 'var(--accent-light)' }}>
                      Регистрация открыта до {deadlineText}
                    </p>
                  )
                ) : (
                  <p style={{ marginTop: '0.25rem', color: 'var(--text-muted)' }}>Регистрация закрыта.</p>
                )}
              </div>
            )}
            <p style={{ marginTop: '1rem' }}>{mission.xp_reward} XP · {mission.mana_reward} ⚡</p>
            {locked && mission.locked_reasons.length > 0 && (
              <p style={{ color: 'var(--error)', fontSize: '0.85rem' }}>{mission.locked_reasons[0]}</p>
            )}
            <a
              className={actionClass}
              style={{
                display: 'inline-block',
                marginTop: '1rem',
                pointerEvents: linkDisabled ? 'none' : 'auto',
                opacity: linkDisabled ? 0.5 : 1
              }}
              href={linkDisabled ? '#' : `/missions/${mission.id}`}
            >
              {actionLabel}
            </a>
          </Card>
        );
      })}
  </div>
  );
}
