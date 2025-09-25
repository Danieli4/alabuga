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
      {missions.map((mission) => (
        <Card key={mission.id}>
          <span className="badge">{mission.difficulty}</span>
          <h3 style={{ marginBottom: '0.5rem' }}>{mission.title}</h3>
          <p style={{ color: 'var(--text-muted)', minHeight: '3rem' }}>{mission.description}</p>
        <p style={{ marginTop: '1rem' }}>{mission.xp_reward} XP · {mission.mana_reward} ⚡</p>
        {!mission.is_available && mission.locked_reasons.length > 0 && (
          <p style={{ color: 'var(--error)', fontSize: '0.85rem' }}>{mission.locked_reasons[0]}</p>
        )}
        <a
          className={mission.is_available ? 'primary' : 'secondary'}
          style={{
            display: 'inline-block',
            marginTop: '1rem',
            pointerEvents: mission.is_available ? 'auto' : 'none',
            opacity: mission.is_available ? 1 : 0.5
          }}
          href={mission.is_available ? `/missions/${mission.id}` : '#'}
        >
          {mission.is_available ? 'Открыть брифинг' : 'Заблокировано'}
        </a>
      </Card>
    ))}
  </div>
  );
}
