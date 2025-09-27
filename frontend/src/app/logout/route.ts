import { NextResponse } from 'next/server';

export function GET(request: Request) {
  // Очищаем cookie и мгновенно перенаправляем пользователя на страницу входа.
  const target = new URL('/login', request.url);
  const response = NextResponse.redirect(target);
  response.cookies.delete('alabuga_session');
  return response;
}
