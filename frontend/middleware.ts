import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// [Task]: AUTH-FIX-002
// [From]: Cross-origin cookie issue - backend on different domain than frontend
// When backend is on a different domain (e.g., HuggingFace Space), cookies are set
// for that domain and not accessible to Next.js middleware on localhost.
// Solution: Disable middleware auth checks, let client-side auth context handle it.

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow home page without authentication
  if (pathname === '/') {
    return NextResponse.next();
  }

  // For cross-origin backend setup, we cannot check cookies in middleware
  // because cookies are set on the backend domain, not localhost.
  // Client-side auth context will handle authentication checks.

  // Allow all routes - auth context will handle redirects
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
