'use client';

import styled from 'styled-components';

type Rank = {
  id: number | null;
  title?: string;
};

type Competency = {
  competency: {
    id: number;
    name: string;
  };
  level: number;
};

type Artifact = {
  id: number;
  name: string;
  rarity: string;
};

export interface ProfileProps {
  fullName: string;
  xp: number;
  mana: number;
  rank?: Rank;
  competencies: Competency[];
  artifacts: Artifact[];
  nextRankTitle?: string;
  xpProgress: number;
  xpTarget: number;
}

const Card = styled.div`
  background: rgba(17, 22, 51, 0.85);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(108, 92, 231, 0.4);
`;

const ProgressBar = styled.div<{ value: number }>`
  position: relative;
  height: 12px;
  border-radius: 999px;
  background: rgba(162, 155, 254, 0.2);
  overflow: hidden;
  margin-top: 0.5rem;

  &::after {
    content: '';
    position: absolute;
    inset: 0;
    width: ${({ value }) => Math.min(100, value)}%;
    background: linear-gradient(90deg, #6c5ce7, #00b894);
  }
`;

export function ProgressOverview({
  fullName,
  xp,
  mana,
  rank,
  competencies,
  artifacts,
  nextRankTitle,
  xpProgress,
  xpTarget
}: ProfileProps) {
  const xpPercent = xpTarget > 0 ? Math.min(100, (xpProgress / xpTarget) * 100) : 100;

  return (
    <Card>
      <h2 style={{ marginTop: 0 }}>{fullName}</h2>
      <p style={{ color: 'var(--text-muted)' }}>Текущий ранг: {rank?.title ?? 'не назначен'}</p>
      <div style={{ marginTop: '1rem' }}>
        <strong>Опыт:</strong>
        <ProgressBar value={xpPercent} />
        {nextRankTitle ? (
          <small style={{ color: 'var(--text-muted)' }}>
            Осталось {Math.max(xpTarget - xpProgress, 0)} XP до ранга «{nextRankTitle}»
          </small>
        ) : (
          <small style={{ color: 'var(--text-muted)' }}>Вы достигли максимального ранга в демо-версии</small>
        )}
      </div>
      <div style={{ marginTop: '1rem' }}>
        <strong>Мана:</strong>
        <p style={{ margin: '0.5rem 0' }}>{mana} ⚡</p>
      </div>
      <div style={{ marginTop: '1.5rem' }}>
        <strong>Компетенции</strong>
        <ul style={{ listStyle: 'none', padding: 0, margin: '0.5rem 0 0' }}>
          {competencies.map((item) => (
            <li key={item.competency.id} style={{ marginBottom: '0.25rem' }}>
              <span className="badge">{item.competency.name}</span> — уровень {item.level}
            </li>
          ))}
        </ul>
      </div>
      <div style={{ marginTop: '1.5rem' }}>
        <strong>Артефакты</strong>
        <div className="grid" style={{ marginTop: '0.75rem' }}>
          {artifacts.length === 0 && <p>Ещё нет трофеев — выполните миссии!</p>}
          {artifacts.map((artifact) => (
            <div key={artifact.id} className="card">
              <span className="badge">{artifact.rarity}</span>
              <h4 style={{ marginBottom: '0.5rem' }}>{artifact.name}</h4>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}
