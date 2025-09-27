import { NextResponse } from 'next/server';
import { enablePilotView, requireRole } from '../../../lib/auth/session';

export async function GET(request: Request) {
  // Доступно только HR: включаем режим просмотра и отправляем на дашборд кандидата.
  // Благодаря этому HR увидит интерфейс пилота без необходимости заводить отдельную учётку.
  await requireRole('hr');
  enablePilotView();
  return NextResponse.redirect(new URL('/', request.url));
}
