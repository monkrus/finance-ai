import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Since we rely on HttpOnly cookies or Zustand localStorage, 
  // we check for a generic session cookie if set by backend, or we fallback to client-side checks.
  // For a strict middleware check, let's assume the backend sets a cookie named 'access_token' or 'refresh_token' 
  // or we simply check for 'auth-storage' in cookies if we manually synced it.
  // For now, we will do a soft check if any cookie exists that hints at auth.
  const hasAuthCookie = request.cookies.has('access_token') || request.cookies.has('refresh_token') || request.cookies.has('finpilot_session');
  
  const pathname = request.nextUrl.pathname;
  
  const isAuthPage = 
    pathname.startsWith('/login') || 
    pathname.startsWith('/register') ||
    pathname.startsWith('/forgot-password') ||
    pathname.startsWith('/reset-password') ||
    pathname.startsWith('/verify');

  const isDashboardRoute = 
    pathname === '/dashboard' ||
    pathname.startsWith('/portfolio') ||
    pathname.startsWith('/market') ||
    pathname.startsWith('/analysis') ||
    pathname.startsWith('/documents') ||
    pathname.startsWith('/news') ||
    pathname.startsWith('/wealth') ||
    pathname.startsWith('/notifications') ||
    pathname.startsWith('/integrations') ||
    pathname.startsWith('/settings') ||
    pathname.startsWith('/ai');

  // Redirect authenticated users away from auth pages
  if (isAuthPage && hasAuthCookie) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // Soft redirect unauthenticated users to login
  if (isDashboardRoute && !hasAuthCookie) {
    // Note: The client-side ProtectedRoute will catch cases where the cookie exists but the token is invalid.
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)',
  ],
};
