'use client';

import { useState } from 'react';

import { apiFetch } from '../lib/api';

export interface OnboardingSlide {
  id: number;
  order: number;
  title: string;
  body: string;
  media_url?: string | null;
  cta_text?: string | null;
  cta_link?: string | null;
}

interface OnboardingCarouselProps {
  token?: string;
  slides: OnboardingSlide[];
  initialCompletedOrder: number;
  nextOrder: number | null;
}

export function OnboardingCarousel({ token, slides, initialCompletedOrder, nextOrder }: OnboardingCarouselProps) {
  const startIndex = nextOrder ? Math.max(slides.findIndex((slide) => slide.order === nextOrder), 0) : slides.length - 1;
  const [currentIndex, setCurrentIndex] = useState(Math.max(startIndex, 0));
  const [completedOrder, setCompletedOrder] = useState(initialCompletedOrder);
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const currentSlide = slides[currentIndex];
  const allCompleted = completedOrder >= (slides.at(-1)?.order ?? 0);

  async function handleComplete() {
    if (!token || !currentSlide) {
      setStatus('Не удалось определить пользователя. Попробуйте обновить страницу.');
      return;
    }

    try {
      setLoading(true);
      await apiFetch('/api/onboarding/complete', {
        method: 'POST',
        body: JSON.stringify({ order: currentSlide.order }),
        authToken: token
      });
      setCompletedOrder(currentSlide.order);
      setStatus('Шаг отмечен как выполненный!');
      if (currentIndex < slides.length - 1) {
        setCurrentIndex(currentIndex + 1);
      }
    } catch (error) {
      if (error instanceof Error) {
        setStatus(error.message);
      }
    } finally {
      setLoading(false);
    }
  }

  if (!currentSlide) {
    return <p>Онбординг недоступен. Свяжитесь с HR.</p>;
  }

  return (
    <div className="card" style={{ display: 'grid', gap: '1.5rem', background: 'rgba(17, 22, 51, 0.9)' }}>
      <header>
        <span className="badge">Шаг {currentIndex + 1} из {slides.length}</span>
        <h2 style={{ margin: '0.75rem 0' }}>{currentSlide.title}</h2>
        <p style={{ color: 'var(--text-muted)', lineHeight: 1.6 }}>{currentSlide.body}</p>
      </header>

      {currentSlide.media_url && (
        <div
          style={{
            borderRadius: '16px',
            overflow: 'hidden',
            border: '1px solid rgba(162, 155, 254, 0.25)'
          }}
        >
          <img src={currentSlide.media_url} alt={currentSlide.title} style={{ width: '100%', height: 'auto' }} />
        </div>
      )}

      <footer style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {currentSlide.cta_text && currentSlide.cta_link && (
          <a className="primary" href={currentSlide.cta_link}>
            {currentSlide.cta_text}
          </a>
        )}

        {!allCompleted && (
          <button className="primary" onClick={handleComplete} disabled={loading}>
            {loading ? 'Сохраняем...' : 'Отметить как выполнено'}
          </button>
        )}

        {status && <small style={{ color: 'var(--accent-light)' }}>{status}</small>}

        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem' }}>
          <button
            className="secondary"
            onClick={() => setCurrentIndex(Math.max(currentIndex - 1, 0))}
            disabled={currentIndex === 0}
            style={{ cursor: currentIndex === 0 ? 'not-allowed' : 'pointer' }}
          >
            Назад
          </button>
          <button
            className="secondary"
            onClick={() => setCurrentIndex(Math.min(currentIndex + 1, slides.length - 1))}
            disabled={currentIndex === slides.length - 1}
            style={{ cursor: currentIndex === slides.length - 1 ? 'not-allowed' : 'pointer' }}
          >
            Далее
          </button>
        </div>
        {allCompleted && <p style={{ color: 'var(--success)', marginTop: '0.5rem' }}>Вы прошли весь онбординг!</p>}
      </footer>
    </div>
  );
}

