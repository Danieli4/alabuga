import { NextResponse } from 'next/server';
import { disablePilotView, requireRole } from '../../../lib/auth/session';

export async function GET(request: Request) {
  // Возвращаем HR к своему интерфейсу.
  // Cookie `alabuga_view_as` хранит флаг режима просмотра, удаляем его и редиректим в админку.
  await requireRole('hr');
  disablePilotView();

  const proto = request.headers.get('x-forwarded-proto') ?? 'https'; const host = request.headers.get('x-forwarded-host') ?? request.headers.get('host') ?? 'localhost'; const 
  target = `${proto}://${host}/admin`;

  return NextResponse.redirect(target);;
}
