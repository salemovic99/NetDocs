"use client";

import * as React from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

/**
 * URL-synced filter/pagination state for list pages.
 * Reads from the query string and writes back via the router (shallow push).
 */
export function useUrlFilters() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const get = React.useCallback(
    (key: string) => searchParams.get(key) ?? "",
    [searchParams],
  );

  const setMany = React.useCallback(
    (updates: Record<string, string | number | undefined | null>) => {
      const params = new URLSearchParams(searchParams.toString());
      for (const [key, value] of Object.entries(updates)) {
        if (value === undefined || value === null || value === "") {
          params.delete(key);
        } else {
          params.set(key, String(value));
        }
      }
      // Any filter change resets pagination.
      if (!("page" in updates)) params.delete("page");
      router.push(`${pathname}?${params.toString()}`, { scroll: false });
    },
    [pathname, router, searchParams],
  );

  const page = Number(searchParams.get("page") ?? "1") || 1;

  return { get, setMany, page, searchParams };
}
