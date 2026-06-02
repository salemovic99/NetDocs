import type { Metadata } from "next";

import { PageHeader } from "@/components/shared/page-header";
import { DevicesList } from "./_components/devices-list";

export const metadata: Metadata = { title: "Inventory — NetDocs" };

export default function InventoryPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Inventory"
        description="Network devices across all sites."
      />
      <DevicesList />
    </div>
  );
}
