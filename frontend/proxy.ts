import { NextResponse, type NextRequest } from "next/server";

// Next.js 16: route guard lives in `proxy.ts` (formerly middleware.ts), Node runtime.
const ACCESS_COOKIE = "netdocs_access";

const PUBLIC_PATHS = ["/login"];

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasSession = Boolean(request.cookies.get(ACCESS_COOKIE)?.value);
  const isPublic = PUBLIC_PATHS.some((p) => pathname.startsWith(p));

  // Unauthenticated user hitting a protected page -> login (preserve return path).
  if (!hasSession && !isPublic) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    if (pathname !== "/") url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }

  // Authenticated user hitting /login -> dashboard.
  if (hasSession && isPublic) {
    const url = request.nextUrl.clone();
    url.pathname = "/";
    url.search = "";
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  // Guard everything except Next internals, the BFF API routes, and static assets.
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
