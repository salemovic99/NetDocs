import type { Metadata } from "next";
import Link from "next/link";
import { Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/shared/page-header";
import { ProblemsByCategory } from "./_components/problems-by-category";

export const metadata: Metadata = { title: "Problems — NetDocs" };

export default function ProblemsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Problems"
        description="Documented problems, root causes and resolutions."
        actions={
          <Button asChild>
            <Link href="/problems/new">
              <Plus /> New problem
            </Link>
          </Button>
        }
      />
      <ProblemsByCategory />
    </div>
  );
}
