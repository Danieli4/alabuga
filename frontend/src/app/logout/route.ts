import { NextResponse } from 'next/server';

export function GET(request: Request) {
  // Очищаем cookie и мгновенно перенаправляем пользователя на страницу входа.
  // Здесь не используем `destroySession`, потому что `NextResponse` позволяет
  // выставить заголовки прямо в объекте ответа.
  const proto = request.headers.get('x-forwarded-proto') ?? 'https';
  const host = request.headers.get('x-forwarded-host') ?? request.headers.get('host') ?? 'localhost';
  const target = `${proto}://${host}/login`;

  const response = NextResponse.redirect(target);
  response.cookies.delete('alabuga_session');
  response.cookies.delete('alabuga_view_as');
  return response;
}
