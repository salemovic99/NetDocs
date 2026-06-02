/**
 * Browser API client. Always calls the same-origin BFF proxy (/api/proxy/*),
 * which attaches the Bearer token from the httpOnly cookie and auto-refreshes.
 */

const PROXY_BASE = "/api/proxy";

export class ApiError extends Error {
  status: number;
  code: string;
  constructor(message: string, status: number, code: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

export type QueryParams = Record<
  string,
  string | number | boolean | null | undefined
>;

function buildUrl(path: string, params?: QueryParams): string {
  const url = `${PROXY_BASE}/${path.replace(/^\//, "")}`;
  if (!params) return url;
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  }
  const qs = search.toString();
  return qs ? `${url}?${qs}` : url;
}

async function parse<T>(res: Response): Promise<T> {
  if (res.status === 204) return undefined as T;
  const text = await res.text();
  const data = text ? JSON.parse(text) : undefined;
  if (!res.ok) {
    if (res.status === 401) {
      // Session gone — bounce to login.
      if (typeof window !== "undefined") window.location.href = "/login";
    }
    throw new ApiError(
      data?.detail ?? res.statusText,
      res.status,
      data?.code ?? "error",
    );
  }
  return data as T;
}

export interface ResultWithEtag<T> {
  data: T;
  etag: string | null;
}

export const api = {
  async get<T>(path: string, params?: QueryParams): Promise<T> {
    const res = await fetch(buildUrl(path, params), { cache: "no-store" });
    return parse<T>(res);
  },

  /** GET that also returns the ETag (for optimistic concurrency on edit). */
  async getWithEtag<T>(path: string, params?: QueryParams): Promise<ResultWithEtag<T>> {
    const res = await fetch(buildUrl(path, params), { cache: "no-store" });
    const data = await parse<T>(res);
    return { data, etag: res.headers.get("etag") };
  },

  async post<T>(path: string, body?: unknown): Promise<T> {
    const res = await fetch(buildUrl(path), {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    return parse<T>(res);
  },

  async patch<T>(path: string, body: unknown, etag?: string | null): Promise<T> {
    const headers: Record<string, string> = { "content-type": "application/json" };
    if (etag) headers["If-Unmatched"] = etag;
    const res = await fetch(buildUrl(path), {
      method: "PATCH",
      headers,
      body: JSON.stringify(body),
    });
    return parse<T>(res);
  },

  async put<T>(path: string, body: unknown): Promise<T> {
    const res = await fetch(buildUrl(path), {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    });
    return parse<T>(res);
  },

  async del<T>(path: string): Promise<T> {
    const res = await fetch(buildUrl(path), { method: "DELETE" });
    return parse<T>(res);
  },

  async upload<T>(path: string, file: File): Promise<T> {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(buildUrl(path), { method: "POST", body: form });
    return parse<T>(res);
  },
};
