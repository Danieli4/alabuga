import { apiFetch } from '../../lib/api';
import { getDemoToken } from '../../lib/demo-auth';
import { OnboardingCarousel, OnboardingSlide } from '../../components/OnboardingCarousel';

interface OnboardingState {
  last_completed_order: number;
  is_completed: boolean;
}

interface OnboardingResponse {
  slides: OnboardingSlide[];
  state: OnboardingState;
  next_order: number | null;
}

async function fetchOnboarding() {
  const token = await getDemoToken();
  const data = await apiFetch<OnboardingResponse>('/api/onboarding/', { authToken: token });
  return { token, data };
}

export default async function OnboardingPage() {
  const { token, data } = await fetchOnboarding();

  return (
    <section className="grid" style={{ gridTemplateColumns: '2fr 1fr', alignItems: 'start', gap: '2rem' }}>
      <div>
        <OnboardingCarousel
          token={token}
          slides={data.slides}
          initialCompletedOrder={data.state.last_completed_order}
          nextOrder={data.next_order}
        />
      </div>
      <aside className="card" style={{ position: 'sticky', top: '1.5rem' }}>
        <h3>Бортовой навигатор</h3>
        <p style={{ color: 'var(--text-muted)', lineHeight: 1.6 }}>
          Онбординг знакомит вас с космической культурой «Алабуги» и объясняет, как миссии превращают карьерные шаги в
          единый маршрут. Каждый шаг открывает новые подсказки и призы в магазине.
        </p>
        <ul style={{ listStyle: 'none', margin: '1rem 0 0', padding: 0, color: 'var(--text-muted)' }}>
          <li>• Читайте лор и переходите к миссиям напрямую.</li>
          <li>• Следите за прогрессом — статус сохраняется автоматически.</li>
          <li>• Доступ к веткам миссий открывается по мере выполнения шагов.</li>
        </ul>
      </aside>
    </section>
  );
}

