import { NextResponse } from 'next/server';
import { disablePilotView, requireRole } from '../../../lib/auth/session';

export async function GET(request: Request) {
  // Возвращаем HR к своему интерфейсу.
  // Cookie `alabuga_view_as` хранит флаг режима просмотра, удаляем его и редиректим в админку.
  await requireRole('hr');
  disablePilotView();
  return NextResponse.redirect(new URL('/admin', request.url));
}
