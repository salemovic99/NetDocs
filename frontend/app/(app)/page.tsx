import type { Metadata } from "next";

import { PageHeader } from "@/components/shared/page-header";
import { StatCards } from "./_components/stat-cards";
import { RecentProblems } from "./_components/recent-problems";

export const metadata: Metadata = { title: "Dashboard — NetDocs" };

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        description="Operational overview of documented problems and infrastructure."
      />
      <StatCards />
      <RecentProblems />
    </div>
  );
}
