import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { ACCESS_COOKIE, API_BASE, REFRESH_COOKIE } from "@/lib/server/backend";

export async function POST() {
  const cookieStore = await cookies();
  const refresh = cookieStore.get(REFRESH_COOKIE)?.value;

  if (refresh) {
    // Best-effort backend revocation; ignore failures.
    await fetch(`${API_BASE}/auth/logout`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    }).catch(() => undefined);
  }

  cookieStore.delete(ACCESS_COOKIE);
  cookieStore.delete(REFRESH_COOKIE);
  return NextResponse.json({ ok: true });
}
