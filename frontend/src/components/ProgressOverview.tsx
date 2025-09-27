'use client';

import styled from 'styled-components';

// Компетенции и артефакты из профиля пользователя.
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

// Мы получаем агрегированный прогресс от backend и пробрасываем его в компонент целиком.
export interface ProfileProps {
  fullName: string;
  mana: number;
  competencies: Competency[];
  artifacts: Artifact[];
  progress: {
    current_rank: { title: string } | null;
    next_rank: { title: string } | null;
    xp: {
      baseline: number;
      current: number;
      target: number;
      remaining: number;
      progress_percent: number;
    };
    mission_requirements: Array<{ mission_id: number; mission_title: string; is_completed: boolean }>;
    competency_requirements: Array<{
      competency_id: number;
      competency_name: string;
      required_level: number;
      current_level: number;
      is_met: boolean;
    }>;
    completed_missions: number;
    total_missions: number;
    met_competencies: number;
    total_competencies: number;
  };
}

const Card = styled.div`
  background: rgba(17, 22, 51, 0.85);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(108, 92, 231, 0.4);
  display: grid;
  gap: 1.5rem;
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

const RequirementRow = styled.div<{ $completed?: boolean }>`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  border: 1px solid ${({ $completed }) => ($completed ? 'rgba(0, 184, 148, 0.35)' : 'rgba(162, 155, 254, 0.25)')};
  background: ${({ $completed }) => ($completed ? 'rgba(0, 184, 148, 0.18)' : 'rgba(162, 155, 254, 0.12)')};
`;

const RequirementTitle = styled.span`
  font-weight: 500;
`;

const ChecklistGrid = styled.div`
  display: grid;
  gap: 0.75rem;
`;

const SectionTitle = styled.h3`
  margin: 0;
  font-size: 1.1rem;
`;

const InlineBadge = styled.span<{ $kind?: 'success' | 'warning' }>`
  border-radius: 999px;
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  background: ${({ $kind }) => ($kind === 'success' ? 'rgba(0, 184, 148, 0.25)' : 'rgba(255, 118, 117, 0.18)')};
  color: ${({ $kind }) => ($kind === 'success' ? '#55efc4' : '#ff7675')};
`;

export function ProgressOverview({ fullName, mana, competencies, artifacts, progress }: ProfileProps) {
  const xpPercent = Math.round(progress.xp.progress_percent * 100);
  const hasNextRank = Boolean(progress.next_rank);

  return (
    <Card>
      <header>
        <h2 style={{ margin: 0 }}>{fullName}</h2>
        <p style={{ color: 'var(--text-muted)', marginTop: '0.25rem' }}>
          Текущий ранг: {progress.current_rank?.title ?? 'не назначен'} · Цель:{' '}
          {hasNextRank ? `«${progress.next_rank?.title}»` : 'достигнут максимум в демо'}
        </p>
      </header>

      <section>
        <SectionTitle>Опыт до следующего ранга</SectionTitle>
        <p style={{ margin: '0.25rem 0', color: 'var(--text-muted)' }}>
          {progress.xp.current} XP из {progress.xp.target} · осталось {progress.xp.remaining} XP
        </p>
        <ProgressBar value={xpPercent} />
      </section>

      <section className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))' }}>
        <div>
          <SectionTitle>Ключевые миссии</SectionTitle>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            {progress.completed_missions}/{progress.total_missions} выполнено.
          </p>
          <ChecklistGrid>
            {progress.mission_requirements.length === 0 && (
              <RequirementRow $completed>
                <RequirementTitle>Все миссии для ранга уже зачтены.</RequirementTitle>
              </RequirementRow>
            )}
            {progress.mission_requirements.map((mission) => (
              <RequirementRow key={mission.mission_id} $completed={mission.is_completed}>
                <RequirementTitle>{mission.mission_title}</RequirementTitle>
                <InlineBadge $kind={mission.is_completed ? 'success' : 'warning'}>
                  {mission.is_completed ? 'готово' : 'ожидает'}
                </InlineBadge>
              </RequirementRow>
            ))}
          </ChecklistGrid>
        </div>
        <div>
          <SectionTitle>Компетенции ранга</SectionTitle>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            {progress.met_competencies}/{progress.total_competencies} требований закрыто.
          </p>
          <ChecklistGrid>
            {progress.competency_requirements.length === 0 && (
              <RequirementRow $completed>
                <RequirementTitle>Дополнительные требования к компетенциям отсутствуют.</RequirementTitle>
              </RequirementRow>
            )}
            {progress.competency_requirements.map((competency) => {
              const percentage = competency.required_level
                ? Math.min(100, (competency.current_level / competency.required_level) * 100)
                : 100;
              const delta = Math.max(0, competency.required_level - competency.current_level);

              return (
                <RequirementRow key={competency.competency_id} $completed={competency.is_met}>
                  <div style={{ flex: 1 }}>
                    <RequirementTitle>{competency.competency_name}</RequirementTitle>
                    <small style={{ color: 'var(--text-muted)' }}>
                      Уровень {competency.current_level} / {competency.required_level}
                    </small>
                    <ProgressBar value={percentage} />
                  </div>
                  <InlineBadge $kind={competency.is_met ? 'success' : 'warning'}>
                    {competency.is_met ? 'готово' : `нужно +${delta}`}
                  </InlineBadge>
                </RequirementRow>
              );
            })}
          </ChecklistGrid>
        </div>
      </section>

      <section className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))' }}>
        <div className="card" style={{ margin: 0 }}>
          <SectionTitle>Мана экипажа</SectionTitle>
          <p style={{ marginTop: '0.5rem', fontSize: '1.75rem', fontWeight: 600 }}>{mana} ⚡</p>
          <small style={{ color: 'var(--text-muted)' }}>Тратьте в магазине на мерч и бонусы.</small>
        </div>
        <div className="card" style={{ margin: 0 }}>
          <SectionTitle>Текущие компетенции</SectionTitle>
          <ul style={{ listStyle: 'none', padding: 0, margin: '0.75rem 0 0', display: 'grid', gap: '0.5rem' }}>
            {competencies.map((item) => (
              <li key={item.competency.id} style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span className="badge">{item.competency.name}</span>
                <span>уровень {item.level}</span>
              </li>
            ))}
            {competencies.length === 0 && <li style={{ color: 'var(--text-muted)' }}>Компетенции ещё не открыты.</li>}
          </ul>
        </div>
      </section>

      <section>
        <SectionTitle>Артефакты</SectionTitle>
        <div className="grid" style={{ marginTop: '0.75rem' }}>
          {artifacts.length === 0 && <p>Выполните миссии, чтобы собрать коллекцию трофеев.</p>}
          {artifacts.map((artifact) => (
            <div key={artifact.id} className="card" style={{ margin: 0 }}>
              <span className="badge">{artifact.rarity}</span>
              <h4 style={{ marginBottom: '0.5rem' }}>{artifact.name}</h4>
            </div>
          ))}
        </div>
      </section>
    </Card>
  );
}
