import type { Metadata } from "next";

import { PageHeader } from "@/components/shared/page-header";
import { ProblemEdit } from "./_components/problem-edit";

export const metadata: Metadata = { title: "Edit problem — NetDocs" };

export default async function EditProblemPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <div className="space-y-6">
      <PageHeader title="Edit problem" />
      <ProblemEdit id={id} />
    </div>
  );
}
