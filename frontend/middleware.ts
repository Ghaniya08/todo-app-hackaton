import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Check for token cookie (JWT token set by backend)
  const tokenCookie = request.cookies.get('token');
  const hasSession = !!tokenCookie;

  const { pathname } = request.nextUrl;

  // Allow home page without authentication
  if (pathname === '/') {
    return NextResponse.next();
  }

  // Define protected and auth-only routes
  const isAuthPage = pathname.startsWith('/signin') || pathname.startsWith('/signup');
  const isProtectedPage = pathname.startsWith('/dashboard');

  // Redirect authenticated users away from auth pages
  if (hasSession && isAuthPage) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // Redirect unauthenticated users to signin
  if (!hasSession && isProtectedPage) {
    return NextResponse.redirect(new URL('/signin', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
