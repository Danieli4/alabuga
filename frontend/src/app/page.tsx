import { redirect } from 'next/navigation';
import { requireSession } from '../lib/auth/session';

export default async function HomePage() {
  // Редиректим на профиль
  await requireSession();
  redirect('/profile');
}
