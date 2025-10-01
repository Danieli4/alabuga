import { apiFetch } from '../../lib/api';
import { requireSession } from '../../lib/auth/session';
import { StoreItems } from '../../components/StoreItems';

interface StoreItem {
  id: number;
  name: string;
  description: string;
  cost_mana: number;
  stock: number;
  image_url?: string | null;
}

async function fetchStore(token: string) {
  const items = await apiFetch<StoreItem[]>('/api/store/items', { authToken: token });
  return { items };
}

export default async function StorePage() {
  // Витрина открыта только для членов экипажа: гостям необходимо авторизоваться.
  const session = await requireSession();
  const { items } = await fetchStore(session.token);

  return (
    <section>
      <h2>Магазин артефактов</h2>
      <p style={{ color: 'var(--text-muted)' }}>
        Обменивайте ману на уникальные впечатления и мерч. Доступно только для активных членов экипажа.
      </p>
      <StoreItems items={items} token={session.token} />
    </section>
  );
}
