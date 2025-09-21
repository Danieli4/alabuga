import { apiFetch } from '../../lib/api';
import { getDemoToken } from '../../lib/demo-auth';
import { StoreItems } from '../../components/StoreItems';

interface StoreItem {
  id: number;
  name: string;
  description: string;
  cost_mana: number;
  stock: number;
}

async function fetchStore() {
  const token = await getDemoToken();
  const items = await apiFetch<StoreItem[]>('/api/store/items', { authToken: token });
  return { items, token };
}

export default async function StorePage() {
  const { items, token } = await fetchStore();

  return (
    <section>
      <h2>Магазин артефактов</h2>
      <p style={{ color: 'var(--text-muted)' }}>
        Обменивайте ману на уникальные впечатления и мерч. Доступно только для активных членов экипажа.
      </p>
      <StoreItems items={items} token={token} />
    </section>
  );
}
