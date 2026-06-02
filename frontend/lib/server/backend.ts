/**
 * Server-only backend access constants + helpers (BFF).
 * The browser never sees these — it only ever calls same-origin Next routes.
 */
import "server-only";

export const API_INTERNAL_URL =
  process.env.API_INTERNAL_URL ?? "http://localhost:8000";

export const API_BASE = `${API_INTERNAL_URL}/api/v1`;

export const ACCESS_COOKIE = "netdocs_access";
export const REFRESH_COOKIE = "netdocs_refresh";

const isProd = process.env.NODE_ENV === "production";

export function sessionCookieOptions(maxAgeSeconds: number) {
  return {
    httpOnly: true,
    secure: isProd,
    sameSite: "lax" as const,
    path: "/",
    maxAge: maxAgeSeconds,
  };
}

// Cookie lifetime: keep both tokens for the refresh window; the access token
// itself expires server-side (JWT exp) and the proxy refreshes it on 401.
export const COOKIE_MAX_AGE = 60 * 60 * 24 * 14; // 14 days
