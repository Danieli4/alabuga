'use client';

import styled from 'styled-components';

type JournalEntry = {
  id: number;
  title: string;
  description: string;
  event_type: string;
  xp_delta: number;
  mana_delta: number;
  created_at: string;
};

const Timeline = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const Item = styled.li`
  position: relative;
  padding-left: 1.5rem;
  margin-bottom: 1.25rem;

  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0.4rem;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 8px rgba(108, 92, 231, 0.5);
  }
`;

export function JournalTimeline({ entries }: { entries: JournalEntry[] }) {
  if (entries.length === 0) {
    return <p>Журнал пуст — выполните миссии, чтобы увидеть прогресс.</p>;
  }

  return (
    <Timeline>
      {entries.map((entry) => (
        <Item key={entry.id}>
          <h4 style={{ margin: 0 }}>{entry.title}</h4>
          <small style={{ color: 'var(--text-muted)' }}>{new Date(entry.created_at).toLocaleString('ru-RU')}</small>
          <p style={{ marginTop: '0.5rem' }}>{entry.description}</p>
          <div style={{ color: 'var(--text-muted)' }}>
            {entry.xp_delta !== 0 && <span style={{ marginRight: '1rem' }}>{entry.xp_delta} XP</span>}
            {entry.mana_delta !== 0 && <span>{entry.mana_delta} ⚡</span>}
          </div>
        </Item>
      ))}
    </Timeline>
  );
}
