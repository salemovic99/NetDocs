"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { EmptyState } from "@/components/shared/empty-state";
import { ProblemStatusBadge, SeverityBadge } from "@/components/shared/badges";
import { useProblems } from "@/lib/hooks/use-problems";

export function RecentProblems() {
  const { data, isLoading } = useProblems({
    page_size: 8,
    sort: "-created_at",
  });

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle>Recent problems</CardTitle>
        <Button variant="ghost" size="sm" asChild>
          <Link href="/problems">
            View all <ArrowRight />
          </Link>
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-9 w-full" />
            ))}
          </div>
        ) : !data?.items.length ? (
          <EmptyState
            title="No problems yet"
            description="Documented problems will appear here."
          />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead className="w-32">Severity</TableHead>
                <TableHead className="w-36">Status</TableHead>
                <TableHead className="w-40">Category</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.items.map((p) => (
                <TableRow key={p.id} className="cursor-pointer">
                  <TableCell>
                    <Link
                      href={`/problems/${p.id}`}
                      className="text-on-surface hover:text-primary"
                    >
                      {p.title}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <SeverityBadge severity={p.severity} />
                  </TableCell>
                  <TableCell>
                    <ProblemStatusBadge status={p.status} />
                  </TableCell>
                  <TableCell className="text-on-surface-variant">
                    {p.category?.name ?? "—"}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
