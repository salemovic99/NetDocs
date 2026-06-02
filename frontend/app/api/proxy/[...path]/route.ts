import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import {
  ACCESS_COOKIE,
  API_BASE,
  COOKIE_MAX_AGE,
  REFRESH_COOKIE,
  sessionCookieOptions,
} from "@/lib/server/backend";

export const dynamic = "force-dynamic";

// Headers worth forwarding from the browser to the backend.
const FORWARD_REQUEST_HEADERS = [
  "content-type",
  "accept",
  "if-unmatched",
  "if-match",
];
// Headers worth returning from the backend to the browser.
const FORWARD_RESPONSE_HEADERS = [
  "content-type",
  "content-disposition",
  "etag",
  "x-request-id",
  "retry-after",
];

type Ctx = { params: Promise<{ path: string[] }> };

async function refreshTokens(refresh: string): Promise<string | null> {
  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ refresh_token: refresh }),
  });
  if (!res.ok) return null;
  const data = await res.json().catch(() => null);
  if (!data?.access_token) return null;

  const cookieStore = await cookies();
  cookieStore.set(
    ACCESS_COOKIE,
    data.access_token,
    sessionCookieOptions(COOKIE_MAX_AGE),
  );
  if (data.refresh_token) {
    cookieStore.set(
      REFRESH_COOKIE,
      data.refresh_token,
      sessionCookieOptions(COOKIE_MAX_AGE),
    );
  }
  return data.access_token as string;
}

async function handle(request: Request, ctx: Ctx): Promise<Response> {
  const { path } = await ctx.params;
  const cookieStore = await cookies();
  const access = cookieStore.get(ACCESS_COOKIE)?.value;
  const refresh = cookieStore.get(REFRESH_COOKIE)?.value;

  if (!access) {
    return NextResponse.json(
      { detail: "Not authenticated", code: "unauthenticated" },
      { status: 401 },
    );
  }

  const url = new URL(request.url);
  const target = `${API_BASE}/${path.join("/")}${url.search}`;

  const hasBody = !["GET", "HEAD"].includes(request.method);
  const rawBody = hasBody ? await request.arrayBuffer() : undefined;

  const buildHeaders = (token: string) => {
    const headers = new Headers();
    for (const h of FORWARD_REQUEST_HEADERS) {
      const v = request.headers.get(h);
      if (v) headers.set(h, v);
    }
    headers.set("authorization", `Bearer ${token}`);
    return headers;
  };

  const doFetch = (token: string) =>
    fetch(target, {
      method: request.method,
      headers: buildHeaders(token),
      body: rawBody && rawBody.byteLength ? rawBody : undefined,
      redirect: "manual",
    });

  let backendRes = await doFetch(access);

  // Access token expired -> rotate via refresh and retry once.
  if (backendRes.status === 401 && refresh) {
    const newAccess = await refreshTokens(refresh);
    if (newAccess) {
      backendRes = await doFetch(newAccess);
    } else {
      cookieStore.delete(ACCESS_COOKIE);
      cookieStore.delete(REFRESH_COOKIE);
      return NextResponse.json(
        { detail: "Session expired", code: "session_expired" },
        { status: 401 },
      );
    }
  }

  const responseHeaders = new Headers();
  for (const h of FORWARD_RESPONSE_HEADERS) {
    const v = backendRes.headers.get(h);
    if (v) responseHeaders.set(h, v);
  }

  return new NextResponse(backendRes.body, {
    status: backendRes.status,
    headers: responseHeaders,
  });
}

export const GET = handle;
export const POST = handle;
export const PUT = handle;
export const PATCH = handle;
export const DELETE = handle;
