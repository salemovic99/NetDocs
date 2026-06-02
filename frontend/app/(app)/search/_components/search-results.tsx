"use client";

import * as React from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Search, Server, TriangleAlert } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { ProblemStatusBadge, SeverityBadge } from "@/components/shared/badges";
import { usePermissions } from "@/lib/auth/session-context";
import { useProblems } from "@/lib/hooks/use-problems";
import { useDevices } from "@/lib/hooks/use-devices";
import { useUrlFilters } from "@/lib/hooks/use-url-filters";
import { PERMISSIONS } from "@/lib/permissions";

export function SearchResults() {
  const params = useSearchParams();
  const { setMany } = useUrlFilters();
  const { can } = usePermissions();
  const q = params.get("q") ?? "";
  const [term, setTerm] = React.useState(q);

  React.useEffect(() => {
    const t = setTimeout(() => {
      if (term !== q) setMany({ q: term });
    }, 350);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [term]);

  const canProblems = can(PERMISSIONS.PROBLEMS_READ);
  const canInventory = can(PERMISSIONS.INVENTORY_READ);

  const problems = useProblems({ q: q || undefined, page_size: 10 });
  const devices = useDevices({ q: q || undefined, page_size: 10 });

  return (
    <div className="space-y-6">
      <div className="relative max-w-xl">
        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-on-surface-variant/60" />
        <Input
          autoFocus
          value={term}
          onChange={(e) => setTerm(e.target.value)}
          placeholder="Search problems and devices…"
          className="pl-9"
        />
      </div>

      {!q ? (
        <EmptyState
          title="Start typing to search"
          description="Results update as you type."
          icon={<Search className="size-5" />}
        />
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          {canProblems ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-h4">
                  <TriangleAlert className="size-4" /> Problems
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-1.5">
                {problems.isLoading ? (
                  <Skeleton className="h-24 w-full" />
                ) : !problems.data?.items.length ? (
                  <p className="text-body-sm text-on-surface-variant">
                    No matching problems.
                  </p>
                ) : (
                  problems.data.items.map((p) => (
                    <Link
                      key={p.id}
                      href={`/problems/${p.id}`}
                      className="flex items-center justify-between gap-2 rounded-md px-2 py-2 hover:bg-surface-container-high"
                    >
                      <span className="truncate text-body-lg text-on-surface">
                        {p.title}
                      </span>
                      <span className="flex shrink-0 items-center gap-1.5">
                        <SeverityBadge severity={p.severity} />
                        <ProblemStatusBadge status={p.status} />
                      </span>
                    </Link>
                  ))
                )}
              </CardContent>
            </Card>
          ) : null}

          {canInventory ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-h4">
                  <Server className="size-4" /> Devices
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-1.5">
                {devices.isLoading ? (
                  <Skeleton className="h-24 w-full" />
                ) : !devices.data?.items.length ? (
                  <p className="text-body-sm text-on-surface-variant">
                    No matching devices.
                  </p>
                ) : (
                  devices.data.items.map((d) => (
                    <Link
                      key={d.id}
                      href={`/inventory/${d.id}`}
                      className="flex items-center justify-between gap-2 rounded-md px-2 py-2 hover:bg-surface-container-high"
                    >
                      <span className="truncate text-on-surface">
                        {d.hostname}
                      </span>
                      <span className="text-mono text-body-sm text-on-surface-variant">
                        {d.management_ip ?? ""}
                      </span>
                    </Link>
                  ))
                )}
              </CardContent>
            </Card>
          ) : null}
        </div>
      )}
    </div>
  );
}
