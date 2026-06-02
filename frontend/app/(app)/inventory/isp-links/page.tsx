import type { Metadata } from "next";

import { PageHeader } from "@/components/shared/page-header";
import { IspLinksList } from "./_components/isp-links-list";

export const metadata: Metadata = { title: "ISP & WAN — NetDocs" };

export default function IspLinksPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="ISP & WAN links"
        description="Internet and WAN circuits per site (primary + backup)."
      />
      <IspLinksList />
    </div>
  );
}
