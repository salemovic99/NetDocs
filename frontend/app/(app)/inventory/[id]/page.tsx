import type { Metadata } from "next";

import { DeviceDetail } from "./_components/device-detail";

export const metadata: Metadata = { title: "Device — NetDocs" };

export default async function DeviceDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <DeviceDetail id={id} />;
}
