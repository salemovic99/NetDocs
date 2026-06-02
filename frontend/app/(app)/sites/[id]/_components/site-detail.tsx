"use client";

import * as React from "react";
import Link from "next/link";
import { ExternalLink, MapPin, Pencil } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/components/shared/page-header";
import { usePermissions } from "@/lib/auth/session-context";
import { useSite } from "@/lib/hooks/use-sites";
import { PERMISSIONS } from "@/lib/permissions";
import { SiteFormDialog } from "../../_components/site-form-dialog";
import { RoomsPanel } from "./rooms-panel";

function AggregateCard({
  title,
  count,
  children,
}: {
  title: string;
  count: number;
  children: React.ReactNode;
}) {
  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle className="text-h4">{title}</CardTitle>
        <Badge variant="default">{count}</Badge>
      </CardHeader>
      <CardContent className="space-y-1.5">{children}</CardContent>
    </Card>
  );
}

export function SiteDetail({ id }: { id: string }) {
  const { can } = usePermissions();
  const { data: site, isLoading } = useSite(id);
  const [editOpen, setEditOpen] = React.useState(false);

  if (isLoading || !site) {
    return (
      <div className="grid gap-6 lg:grid-cols-3">
        <Skeleton className="h-80 lg:col-span-2" />
        <Skeleton className="h-80" />
      </div>
    );
  }

  const manage = can(PERMISSIONS.INVENTORY_MANAGE);

  return (
    <div className="space-y-6">
      <PageHeader
        title={site.name}
        description={[site.city, site.country].filter(Boolean).join(", ")}
        actions={
          <div className="flex gap-2">
            {site.google_map_location ? (
              <Button variant="outline" asChild>
                <a
                  href={site.google_map_location}
                  target="_blank"
                  rel="noreferrer"
                >
                  <MapPin /> Map <ExternalLink className="size-3" />
                </a>
              </Button>
            ) : null}
            {manage ? (
              <Button variant="outline" onClick={() => setEditOpen(true)}>
                <Pencil /> Edit
              </Button>
            ) : null}
          </div>
        }
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="grid gap-4 sm:grid-cols-2">
            <AggregateCard title="Devices" count={site.devices.length}>
              {site.devices.length ? (
                site.devices.slice(0, 8).map((d) => (
                  <Link
                    key={d.id}
                    href={`/inventory/${d.id}`}
                    className="block truncate rounded-md px-2 py-1 text-body-lg text-on-surface hover:bg-surface-container-high"
                  >
                    {d.hostname}
                  </Link>
                ))
              ) : (
                <p className="text-body-sm text-on-surface-variant">None</p>
              )}
            </AggregateCard>

            <AggregateCard title="Racks" count={site.racks.length}>
              {site.racks.length ? (
                site.racks.map((r) => (
                  <p key={r.id} className="px-2 py-1 text-body-lg text-on-surface">
                    {r.name}
                  </p>
                ))
              ) : (
                <p className="text-body-sm text-on-surface-variant">None</p>
              )}
            </AggregateCard>

            <AggregateCard title="ISP links" count={site.isp_links.length}>
              {site.isp_links.length ? (
                site.isp_links.map((l) => (
                  <p
                    key={l.id}
                    className="px-2 py-1 text-body-lg text-on-surface"
                  >
                    {l.provider_name ?? "—"}{" "}
                    <span className="text-body-sm text-on-surface-variant">
                      {l.connection_type}
                    </span>
                  </p>
                ))
              ) : (
                <p className="text-body-sm text-on-surface-variant">None</p>
              )}
            </AggregateCard>

            <AggregateCard
              title="Wireless"
              count={site.wireless_networks.length}
            >
              {site.wireless_networks.length ? (
                site.wireless_networks.map((w) => (
                  <p
                    key={w.id}
                    className="px-2 py-1 text-body-lg text-on-surface"
                  >
                    {w.ssid}{" "}
                    {w.vlan_tag ? (
                      <span className="text-mono text-on-surface-variant">
                        VLAN {w.vlan_tag}
                      </span>
                    ) : null}
                  </p>
                ))
              ) : (
                <p className="text-body-sm text-on-surface-variant">None</p>
              )}
            </AggregateCard>
          </div>

          {site.notes ? (
            <Card>
              <CardHeader>
                <CardTitle className="text-h4">Notes</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="whitespace-pre-wrap text-body-lg text-on-surface">
                  {site.notes}
                </p>
              </CardContent>
            </Card>
          ) : null}
        </div>

        <RoomsPanel siteId={site.id} rooms={site.rooms} />
      </div>

      {manage ? (
        <SiteFormDialog
          open={editOpen}
          onOpenChange={setEditOpen}
          site={site}
        />
      ) : null}
    </div>
  );
}
