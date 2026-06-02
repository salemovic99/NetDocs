import type { Metadata } from "next";

import { SiteDetail } from "./_components/site-detail";

export const metadata: Metadata = { title: "Site — NetDocs" };

export default async function SiteDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <SiteDetail id={id} />;
}
