import type { Metadata } from "next";

import { PageHeader } from "@/components/shared/page-header";
import { RolesMatrix } from "./_components/roles-matrix";

export const metadata: Metadata = { title: "Roles — NetDocs" };

export default function RolesPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Roles & permissions"
        description="Grant or revoke capabilities per role. Changes apply immediately."
      />
      <RolesMatrix />
    </div>
  );
}
