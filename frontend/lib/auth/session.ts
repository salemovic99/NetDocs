import "server-only";

import { cookies } from "next/headers";

import { ACCESS_COOKIE, API_BASE } from "@/lib/server/backend";

export interface SessionUser {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  must_change_password: boolean;
  roles: string[];
}

export interface Session {
  user: SessionUser;
  permissions: string[];
}

/**
 * Server-side: resolve the current user + effective permissions from the
 * access cookie. Returns null when unauthenticated (caller redirects to /login).
 */
export async function getSession(): Promise<Session | null> {
  const access = (await cookies()).get(ACCESS_COOKIE)?.value;
  if (!access) return null;

  const headers = { authorization: `Bearer ${access}` };
  const [meRes, permRes] = await Promise.all([
    fetch(`${API_BASE}/auth/me`, { headers, cache: "no-store" }),
    fetch(`${API_BASE}/auth/me/permissions`, { headers, cache: "no-store" }),
  ]);

  if (!meRes.ok) return null;

  const user = (await meRes.json()) as SessionUser;
  const permissions = permRes.ok
    ? ((await permRes.json()).permissions as string[])
    : [];

  return { user, permissions };
}
