import type { Metadata } from "next";

import { PageHeader } from "@/components/shared/page-header";
import { WirelessList } from "./_components/wireless-list";

export const metadata: Metadata = { title: "Wireless — NetDocs" };

export default function WirelessPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Wireless networks"
        description="SSIDs per site and their VLAN segmentation."
      />
      <WirelessList />
    </div>
  );
}
