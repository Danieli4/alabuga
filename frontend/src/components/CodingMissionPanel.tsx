'use client';

import { useEffect, useMemo, useState } from 'react';
import { apiFetch } from '../lib/api';

interface CodingChallengeState {
  id: number;
  order: number;
  title: string;
  prompt: string;
  starter_code: string | null;
  is_passed: boolean;
  is_unlocked: boolean;
  last_submitted_code: string | null;
  last_stdout: string | null;
  last_stderr: string | null;
  last_exit_code: number | null;
  updated_at: string | null;
}

interface CodingMissionState {
  mission_id: number;
  total_challenges: number;
  completed_challenges: number;
  current_challenge_id: number | null;
  is_mission_completed: boolean;
  challenges: CodingChallengeState[];
}

interface CodingMissionPanelProps {
  missionId: number;
  token?: string;
  initialState: CodingMissionState | null;
  initialCompleted?: boolean;
}

interface RunResult {
  stdout: string;
  stderr: string;
  exit_code: number;
  is_passed: boolean;
  mission_completed: boolean;
  expected_output?: string | null;
}

export function CodingMissionPanel({ missionId, token, initialState, initialCompleted = false }: CodingMissionPanelProps) {
  const [state, setState] = useState<CodingMissionState | null>(initialState);
  const [missionCompleted, setMissionCompleted] = useState(initialState?.is_mission_completed || initialCompleted);
  const [activeChallengeId, setActiveChallengeId] = useState<number | null>(
    initialState?.current_challenge_id ?? initialState?.challenges?.[0]?.id ?? null
  );
  const [editorCode, setEditorCode] = useState<string>(() => {
    const active = initialState?.challenges.find((challenge) => challenge.id === activeChallengeId);
    if (!active) {
      return '';
    }
    return active.last_submitted_code ?? active.starter_code ?? '';
  });
  const [status, setStatus] = useState<string | null>(null);
  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [loading, setLoading] = useState(false);

  const activeChallenge = useMemo(() => {
    if (!state || !state.challenges.length) {
      return null;
    }
    const targetId = state.current_challenge_id ?? activeChallengeId;
    if (targetId == null) {
      return null;
    }
    return state.challenges.find((challenge) => challenge.id === targetId) ?? null;
  }, [state, activeChallengeId]);

  useEffect(() => {
    if (!state || !state.challenges.length) {
      return;
    }
    const nextActiveId = state.current_challenge_id ?? state.challenges[state.challenges.length - 1].id;
    if (nextActiveId !== activeChallengeId) {
      setActiveChallengeId(nextActiveId);
      const nextChallenge = state.challenges.find((challenge) => challenge.id === nextActiveId);
      const nextCode = nextChallenge?.last_submitted_code ?? nextChallenge?.starter_code ?? '';
      setEditorCode(nextCode);
      setRunResult(null);
      setStatus(null);
    }
    setMissionCompleted(state.is_mission_completed);
  }, [state, activeChallengeId]);

  useEffect(() => {
    if (!activeChallenge) {
      return;
    }
    if (editorCode) {
      return;
    }
    const baseCode = activeChallenge.last_submitted_code ?? activeChallenge.starter_code ?? '';
    setEditorCode(baseCode);
  }, [activeChallenge]);

  if (!state) {
    return (
      <div className="card" style={{ marginTop: '2rem' }}>
        <p>
          Не удалось загрузить задания для миссии. Попробуйте обновить страницу или обратитесь к HR, чтобы
          проверить настройки миссии.
        </p>
      </div>
    );
  }

  const handleRefresh = async () => {
    if (!token) {
      return;
    }
    const updated = await apiFetch<CodingMissionState>(`/api/missions/${missionId}/coding/challenges`, {
      authToken: token
    });
    setState(updated);
  };

  const handleRun = async () => {
    if (!token) {
      setStatus('Не удалось получить токен авторизации. Перезайдите в систему.');
      return;
    }
    if (!activeChallenge) {
      setStatus('Все задания выполнены — можно переходить к другим миссиям.');
      return;
    }
    if (!editorCode.trim()) {
      setStatus('Добавьте решение в редакторе, прежде чем запускать проверку.');
      return;
    }

    try {
      setLoading(true);
      setStatus(null);
      const result = await apiFetch<RunResult>(
        `/api/missions/${missionId}/coding/challenges/${activeChallenge.id}/run`,
        {
          method: 'POST',
          body: JSON.stringify({ code: editorCode }),
          authToken: token
        }
      );
      setRunResult(result);
      setMissionCompleted(result.mission_completed);
      setStatus(
        result.is_passed
          ? 'Отлично! Задание пройдено. Можно переходить к следующему шагу.'
          : 'Проверка не пройдена. Сверьтесь с выводом программы и подсказками.'
      );
      await handleRefresh();
    } catch (error) {
      if (error instanceof Error) {
        setStatus(error.message);
      } else {
        setStatus('Неожиданная ошибка при выполнении проверки. Попробуйте повторить позже.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {state.challenges.map((challenge) => {
        const isActive = activeChallenge?.id === challenge.id && !missionCompleted;
        return (
          <div key={challenge.id} className="card" style={{ border: challenge.is_passed ? '1px solid rgba(85,239,196,0.4)' : undefined }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ marginBottom: '0.25rem' }}>
                {challenge.order}. {challenge.title}
              </h3>
              {challenge.is_passed && <span style={{ color: '#55efc4' }}>✓ Готово</span>}
            </div>
            <p style={{ color: 'var(--text-muted)' }}>{challenge.prompt}</p>
            {!challenge.is_unlocked && !challenge.is_passed && (
              <p style={{ marginTop: '0.75rem', color: 'var(--text-muted)' }}>
                🔒 Задание откроется после успешного решения предыдущих пунктов.
              </p>
            )}
            {challenge.is_passed && challenge.last_stdout && (
              <div style={{ marginTop: '0.75rem' }}>
                <small style={{ color: 'var(--text-muted)' }}>Последний вывод программы:</small>
                <pre style={{ background: 'rgba(99, 110, 114, 0.2)', padding: '0.75rem', borderRadius: '12px', overflowX: 'auto' }}>
                  {challenge.last_stdout}
                </pre>
              </div>
            )}
            {isActive && (
              <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <label>
                  <span style={{ display: 'block', marginBottom: '0.5rem' }}>Редактор кода</span>
                  <textarea
                    value={editorCode}
                    onChange={(event) => setEditorCode(event.target.value)}
                    rows={12}
                    style={{ width: '100%', borderRadius: '12px', padding: '0.75rem', fontFamily: 'monospace' }}
                    disabled={loading || missionCompleted}
                  />
                </label>
                <button
                  type="button"
                  className="primary"
                  onClick={handleRun}
                  disabled={loading || missionCompleted}
                >
                  {missionCompleted ? 'Миссия завершена' : loading ? 'Выполняем код...' : 'Проверить'}
                </button>
                {status && (
                  <p
                    style={{
                      marginTop: '-0.25rem',
                      color: status.startsWith('Отлично') ? 'var(--accent-light)' : status.includes('Проверка') ? 'var(--error)' : 'var(--text-muted)'
                    }}
                  >
                    {status}
                  </p>
                )}
                {runResult && (
                  <div>
                    <details open>
                      <summary style={{ cursor: 'pointer', color: 'var(--accent)' }}>Результат последнего запуска</summary>
                      <div style={{ marginTop: '0.5rem' }}>
                        <strong>stdout:</strong>
                        <pre style={{ background: 'rgba(108, 92, 231, 0.15)', padding: '0.75rem', borderRadius: '12px', overflowX: 'auto' }}>
                          {runResult.stdout || '<пусто>'}
                        </pre>
                        <strong>stderr:</strong>
                        <pre style={{ background: 'rgba(225, 112, 85, 0.15)', padding: '0.75rem', borderRadius: '12px', overflowX: 'auto' }}>
                          {runResult.stderr || '<пусто>'}
                        </pre>
                        <p style={{ marginTop: '0.5rem', color: 'var(--text-muted)' }}>
                          Код завершился с статусом {runResult.exit_code}.
                        </p>
                        {runResult.expected_output && (
                          <div style={{ marginTop: '0.5rem' }}>
                            <strong>Ожидаемый вывод:</strong>
                            <pre style={{ background: 'rgba(99, 110, 114, 0.2)', padding: '0.75rem', borderRadius: '12px', overflowX: 'auto' }}>
                              {runResult.expected_output}
                            </pre>
                          </div>
                        )}
                      </div>
                    </details>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
      {missionCompleted && (
        <div className="card" style={{ border: '1px solid rgba(85,239,196,0.35)', background: 'rgba(85,239,196,0.12)' }}>
          <h3>Все задания выполнены!</h3>
          <p style={{ marginTop: '0.5rem', color: 'var(--text-muted)' }}>
            Система уже зачислила опыт и ману за миссию. Можно вернуться к списку миссий и выбрать следующее испытание.
          </p>
        </div>
      )}
    </div>
  );
}

