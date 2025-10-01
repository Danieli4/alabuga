'use client';

import styled from 'styled-components';

export interface MissionSummary {
  id: number;
  title: string;
  description: string;
  xp_reward: number;
  mana_reward: number;
  difficulty: string;
  is_active: boolean;
  is_available: boolean;
  locked_reasons: string[];
  is_completed: boolean;
  requires_documents: boolean;
  has_coding_challenges: boolean;
  coding_challenge_count: number;
  completed_coding_challenges: number;
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

  return (
    <div className="grid">
      {missions.map((mission) => {
        const completed = mission.is_completed;
        const locked = !mission.is_available && !completed;
        const primaryClass = completed ? 'secondary' : locked ? 'secondary' : 'primary';
        const linkDisabled = locked;
        const actionLabel = completed
          ? 'Миссия выполнена'
          : mission.is_available
          ? mission.has_coding_challenges
            ? 'Решать задачи'
            : 'Открыть брифинг'
          : 'Заблокировано';

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
            <p style={{ marginTop: '1rem' }}>{mission.xp_reward} XP · {mission.mana_reward} ⚡</p>
            {locked && mission.locked_reasons.length > 0 && (
              <p style={{ color: 'var(--error)', fontSize: '0.85rem' }}>{mission.locked_reasons[0]}</p>
            )}
            <a
              className={primaryClass}
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
