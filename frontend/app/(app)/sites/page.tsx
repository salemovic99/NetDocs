import type { Metadata } from "next";

import { PageHeader } from "@/components/shared/page-header";
import { SitesList } from "./_components/sites-list";

export const metadata: Metadata = { title: "Sites — NetDocs" };

export default function SitesPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Sites"
        description="Branch locations anchoring devices, racks, ISP links and wireless."
      />
      <SitesList />
    </div>
  );
}
