import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import {
  ACCESS_COOKIE,
  API_BASE,
  COOKIE_MAX_AGE,
  REFRESH_COOKIE,
  sessionCookieOptions,
} from "@/lib/server/backend";

export async function POST(request: Request) {
  const body = await request.json().catch(() => null);
  if (!body?.identifier || !body?.password) {
    return NextResponse.json(
      { detail: "identifier and password are required", code: "bad_request" },
      { status: 400 },
    );
  }

  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      identifier: body.identifier,
      password: body.password,
    }),
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    return NextResponse.json(data, { status: res.status });
  }

  const cookieStore = await cookies();
  cookieStore.set(
    ACCESS_COOKIE,
    data.access_token,
    sessionCookieOptions(COOKIE_MAX_AGE),
  );
  cookieStore.set(
    REFRESH_COOKIE,
    data.refresh_token,
    sessionCookieOptions(COOKIE_MAX_AGE),
  );

  return NextResponse.json({
    ok: true,
    must_change_password: Boolean(data.must_change_password),
  });
}
