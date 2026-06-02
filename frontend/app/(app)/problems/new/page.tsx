import type { Metadata } from "next";

import { PageHeader } from "@/components/shared/page-header";
import { ProblemForm } from "../_components/problem-form";

export const metadata: Metadata = { title: "New problem — NetDocs" };

export default function NewProblemPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="New problem"
        description="Capture a problem, its root cause and resolution."
      />
      <ProblemForm />
    </div>
  );
}
