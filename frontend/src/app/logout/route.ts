import { NextResponse } from 'next/server';

export function GET(request: Request) {
  // Очищаем cookie и мгновенно перенаправляем пользователя на страницу входа.
  // Здесь не используем `destroySession`, потому что `NextResponse` позволяет
  // выставить заголовки прямо в объекте ответа.
  const target = new URL('/login', request.url);
  const response = NextResponse.redirect(target);
  response.cookies.delete('alabuga_session');
  response.cookies.delete('alabuga_view_as');
  return response;
}
