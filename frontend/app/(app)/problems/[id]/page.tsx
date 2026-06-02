import type { Metadata } from "next";

import { ProblemDetail } from "./_components/problem-detail";

export const metadata: Metadata = { title: "Problem — NetDocs" };

export default async function ProblemDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <ProblemDetail id={id} />;
}
