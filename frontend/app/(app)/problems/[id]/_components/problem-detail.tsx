"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Archive, Pencil, Server } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { ProblemStatusBadge, SeverityBadge } from "@/components/shared/badges";
import { usePermissions } from "@/lib/auth/session-context";
import { useArchiveProblem, useProblem } from "@/lib/hooks/use-problems";
import { PERMISSIONS } from "@/lib/permissions";
import { AttachmentsPanel } from "./attachments-panel";

function Section({ title, body }: { title: string; body: string | null }) {
  return (
    <div className="space-y-1.5">
      <h3 className="text-label-caps text-on-surface-variant">{title}</h3>
      <p className="whitespace-pre-wrap text-body-lg text-on-surface">
        {body?.trim() ? body : "—"}
      </p>
    </div>
  );
}

export function ProblemDetail({ id }: { id: string }) {
  const router = useRouter();
  const { can } = usePermissions();
  const { data, isLoading } = useProblem(id);
  const archive = useArchiveProblem();

  if (isLoading || !data) {
    return (
      <div className="grid gap-6 lg:grid-cols-3">
        <Skeleton className="h-96 lg:col-span-2" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  const problem = data.data;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-border pb-4">
        <div className="space-y-2">
          <h1 className="text-h1 text-on-surface">{problem.title}</h1>
          <div className="flex items-center gap-2">
            <SeverityBadge severity={problem.severity} />
            <ProblemStatusBadge status={problem.status} />
            {problem.category ? (
              <Badge variant="outline">{problem.category.name}</Badge>
            ) : null}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {can(PERMISSIONS.PROBLEMS_WRITE) ? (
            <Button variant="outline" asChild>
              <Link href={`/problems/${problem.id}/edit`}>
                <Pencil /> Edit
              </Link>
            </Button>
          ) : null}
          {can(PERMISSIONS.PROBLEMS_DELETE) ? (
            <ConfirmDialog
              trigger={
                <Button variant="outline">
                  <Archive /> Archive
                </Button>
              }
              title="Archive this problem?"
              description="It will be hidden from default views. This can be undone in the database."
              confirmLabel="Archive"
              onConfirm={async () => {
                await archive.mutateAsync(problem.id);
                router.push("/problems");
                router.refresh();
              }}
            />
          ) : null}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <CardContent className="space-y-5 pt-6">
              <Section title="Symptoms" body={problem.symptoms} />
              <Separator />
              <Section title="Root cause" body={problem.root_cause} />
              <Separator />
              <Section title="Resolution" body={problem.resolution} />
            </CardContent>
          </Card>

          <AttachmentsPanel problemId={problem.id} />
        </div>

        <div className="space-y-6">
          {problem.tags.length ? (
            <Card>
              <CardHeader>
                <CardTitle className="text-h4">Tags</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-wrap gap-1.5">
                {problem.tags.map((t) => (
                  <Badge key={t.id} variant="default">
                    {t.name}
                  </Badge>
                ))}
              </CardContent>
            </Card>
          ) : null}

          <Card>
            <CardHeader>
              <CardTitle className="text-h4">Affected devices</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1.5">
              {problem.devices.length ? (
                problem.devices.map((d) => (
                  <Link
                    key={d.id}
                    href={`/inventory/${d.id}`}
                    className="flex items-center gap-2 rounded-md px-2 py-1.5 text-body-lg text-on-surface hover:bg-surface-container-high"
                  >
                    <Server className="size-4 text-on-surface-variant" />
                    {d.hostname}
                  </Link>
                ))
              ) : (
                <p className="text-body-sm text-on-surface-variant">
                  No linked devices.
                </p>
              )}
            </CardContent>
          </Card>

          {problem.related_problems.length ? (
            <Card>
              <CardHeader>
                <CardTitle className="text-h4">Related problems</CardTitle>
              </CardHeader>
              <CardContent className="space-y-1.5">
                {problem.related_problems.map((p) => (
                  <Link
                    key={p.id}
                    href={`/problems/${p.id}`}
                    className="block rounded-md px-2 py-1.5 text-body-lg text-on-surface hover:bg-surface-container-high"
                  >
                    {p.title}
                  </Link>
                ))}
              </CardContent>
            </Card>
          ) : null}
        </div>
      </div>
    </div>
  );
}
