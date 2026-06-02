import type { Metadata } from "next";

import { PageHeader } from "@/components/shared/page-header";
import { UsersTable } from "./_components/users-table";

export const metadata: Metadata = { title: "Users — NetDocs" };

export default function UsersPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Users"
        description="Manage accounts and role assignments."
      />
      <UsersTable />
    </div>
  );
}
