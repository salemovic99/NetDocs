"use client";

import { Skeleton } from "@/components/ui/skeleton";
import { useProblem } from "@/lib/hooks/use-problems";
import { ProblemForm } from "../../../_components/problem-form";

export function ProblemEdit({ id }: { id: string }) {
  const { data, isLoading } = useProblem(id);

  if (isLoading || !data) {
    return (
      <div className="grid gap-6 lg:grid-cols-3">
        <Skeleton className="h-80 lg:col-span-2" />
        <Skeleton className="h-80" />
      </div>
    );
  }

  return <ProblemForm problem={data.data} etag={data.etag} />;
}
