"use client";

import * as React from "react";
import Link from "next/link";
import { Pencil } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { AttachmentList } from "@/components/shared/attachment-list";
import { DeviceStatusBadge, SeverityBadge } from "@/components/shared/badges";
import { EmptyState } from "@/components/shared/empty-state";
import { PageHeader } from "@/components/shared/page-header";
import { usePermissions } from "@/lib/auth/session-context";
import { useDevice } from "@/lib/hooks/use-devices";
import { useProblems } from "@/lib/hooks/use-problems";
import {
  useDeleteAttachment,
  useDeviceAttachments,
  useUploadAttachment,
} from "@/lib/hooks/use-attachments";
import { PERMISSIONS } from "@/lib/permissions";
import { DeviceForm } from "../../_components/device-form";
import { VlanTable } from "./vlan-table";

function Field({ label, value }: { label: string; value?: string | null }) {
  return (
    <div className="space-y-0.5">
      <p className="text-label-caps text-on-surface-variant">{label}</p>
      <p className="text-body-lg text-on-surface">{value || "—"}</p>
    </div>
  );
}

export function DeviceDetail({ id }: { id: string }) {
  const { can } = usePermissions();
  const { data, isLoading } = useDevice(id);
  const [editOpen, setEditOpen] = React.useState(false);

  const attachments = useDeviceAttachments(id);
  const upload = useUploadAttachment("devices", id);
  const removeAttachment = useDeleteAttachment();
  const problems = useProblems({ device: id, page_size: 50 });

  if (isLoading || !data) {
    return (
      <div className="grid gap-6 lg:grid-cols-3">
        <Skeleton className="h-96 lg:col-span-2" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  const device = data.data;

  return (
    <div className="space-y-6">
      <PageHeader
        title={device.hostname}
        actions={
          can(PERMISSIONS.INVENTORY_MANAGE) ? (
            <Dialog open={editOpen} onOpenChange={setEditOpen}>
              <Button variant="outline" onClick={() => setEditOpen(true)}>
                <Pencil /> Edit
              </Button>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Edit device</DialogTitle>
                </DialogHeader>
                <DeviceForm
                  device={device}
                  etag={data.etag}
                  onDone={() => setEditOpen(false)}
                />
              </DialogContent>
            </Dialog>
          ) : null
        }
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-h4">
                Device details <DeviceStatusBadge status={device.status} />
              </CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-4 sm:grid-cols-3">
              <Field label="Type" value={device.device_type?.name} />
              <Field label="Vendor" value={device.vendor?.name} />
              <Field label="Site" value={device.site?.name} />
              <Field label="Model" value={device.model} />
              <Field label="Mgmt IP" value={device.management_ip} />
              <Field label="MAC" value={device.mac_address} />
              <Field label="Firmware" value={device.firmware_version} />
              <Field label="OS" value={device.os_version} />
              <Field label="Serial" value={device.serial_number} />
              <Field label="Asset tag" value={device.asset_tag} />
              <Field label="Rack" value={device.rack?.name} />
              <Field
                label="U-position"
                value={device.rack_position?.toString()}
              />
            </CardContent>
          </Card>

          <VlanTable deviceId={device.id} />

          <AttachmentList
            items={attachments.data}
            isLoading={attachments.isLoading}
            canUpload={can(PERMISSIONS.ATTACHMENTS_UPLOAD)}
            canDownload={can(PERMISSIONS.ATTACHMENTS_DOWNLOAD)}
            uploading={upload.isPending}
            onUpload={(f) => upload.mutate(f)}
            onDelete={(aid) => removeAttachment.mutate(aid)}
          />
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-h4">Related problems</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1.5">
            {problems.data?.items.length ? (
              problems.data.items.map((p) => (
                <Link
                  key={p.id}
                  href={`/problems/${p.id}`}
                  className="flex items-center justify-between gap-2 rounded-md px-2 py-1.5 hover:bg-surface-container-high"
                >
                  <span className="truncate text-body-lg text-on-surface">
                    {p.title}
                  </span>
                  <SeverityBadge severity={p.severity} />
                </Link>
              ))
            ) : (
              <EmptyState
                title="No related problems"
                description="Problems linked to this device appear here."
              />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
