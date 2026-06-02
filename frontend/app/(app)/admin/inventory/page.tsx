import type { Metadata } from "next";

import { PageHeader } from "@/components/shared/page-header";
import { LookupsManager } from "./_components/lookups-manager";

export const metadata: Metadata = { title: "Lookups — NetDocs" };

export default function AdminInventoryPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Managed lookups"
        description="Device types, vendors, racks, tags and problem categories."
      />
      <LookupsManager />
    </div>
  );
}
