"use client";
import { formResolver } from "@/lib/schemas";

import * as React from "react";
import { useForm } from "react-hook-form";
import { Pencil, Plus, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Form } from "@/components/ui/form";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { EmptyState } from "@/components/shared/empty-state";
import {
  SelectFormField,
  TextFormField,
  TextareaFormField,
} from "@/components/shared/form-fields";
import { usePermissions } from "@/lib/auth/session-context";
import { useIspLinkMutations, useIspLinks } from "@/lib/hooks/use-network";
import { useSites } from "@/lib/hooks/use-sites";
import { PERMISSIONS } from "@/lib/permissions";
import {
  clean,
  CONNECTION_TYPES,
  ISP_STATUSES,
  ispLinkSchema,
  type IspLinkInput,
} from "@/lib/schemas";
import type { IspLink } from "@/lib/api/types";

export function IspLinksList() {
  const { can } = usePermissions();
  const manage = can(PERMISSIONS.INVENTORY_MANAGE);
  const { data, isLoading } = useIspLinks({ page_size: 100 });
  const { create, update, remove } = useIspLinkMutations();
  const sites = useSites({ page_size: 100 });
  const [open, setOpen] = React.useState(false);
  const [editing, setEditing] = React.useState<IspLink | null>(null);

  const siteName = (id: string) =>
    sites.data?.items.find((s) => s.id === id)?.name ?? "—";

  return (
    <Card>
      <CardContent className="space-y-4 pt-6">
        {manage ? (
          <div className="flex justify-end">
            <Button
              onClick={() => {
                setEditing(null);
                setOpen(true);
              }}
            >
              <Plus /> New link
            </Button>
          </div>
        ) : null}

        {isLoading ? (
          <Skeleton className="h-40 w-full" />
        ) : !data?.items.length ? (
          <EmptyState title="No ISP links" description="Add a WAN circuit." />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Provider</TableHead>
                <TableHead>Site</TableHead>
                <TableHead>Circuit</TableHead>
                <TableHead>Public IP</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Status</TableHead>
                {manage ? <TableHead className="w-20" /> : null}
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.items.map((l) => (
                <TableRow key={l.id}>
                  <TableCell className="text-on-surface">
                    {l.provider_name ?? "—"}
                  </TableCell>
                  <TableCell className="text-on-surface-variant">
                    {siteName(l.site_id)}
                  </TableCell>
                  <TableCell className="text-mono text-on-surface-variant">
                    {l.circuit_id ?? "—"}
                  </TableCell>
                  <TableCell className="text-mono text-on-surface-variant">
                    {l.public_ip ?? "—"}
                  </TableCell>
                  <TableCell>{l.connection_type ?? "—"}</TableCell>
                  <TableCell>
                    {l.status ? <Badge variant="outline">{l.status}</Badge> : "—"}
                  </TableCell>
                  {manage ? (
                    <TableCell className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={() => {
                          setEditing(l);
                          setOpen(true);
                        }}
                      >
                        <Pencil />
                      </Button>
                      <ConfirmDialog
                        trigger={
                          <Button variant="ghost" size="icon-sm">
                            <Trash2 className="text-error" />
                          </Button>
                        }
                        title="Delete this ISP link?"
                        confirmLabel="Delete"
                        onConfirm={() => remove.mutate(l.id)}
                      />
                    </TableCell>
                  ) : null}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>

      {manage ? (
        <IspLinkDialog
          key={editing?.id ?? "new"}
          open={open}
          onOpenChange={setOpen}
          link={editing}
          siteOptions={(sites.data?.items ?? []).map((s) => ({
            value: s.id,
            label: s.name,
          }))}
          onSubmit={async (values) => {
            const payload = clean(values);
            if (editing) {
              await update.mutateAsync({ id: editing.id, body: payload });
            } else {
              await create.mutateAsync(payload);
            }
            setOpen(false);
          }}
        />
      ) : null}
    </Card>
  );
}

function IspLinkDialog({
  open,
  onOpenChange,
  link,
  siteOptions,
  onSubmit,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  link: IspLink | null;
  siteOptions: { value: string; label: string }[];
  onSubmit: (values: IspLinkInput) => Promise<void>;
}) {
  const form = useForm<IspLinkInput>({
    resolver: formResolver(ispLinkSchema),
    defaultValues: {
      site_id: link?.site_id ?? "",
      provider_name: link?.provider_name ?? "",
      circuit_id: link?.circuit_id ?? "",
      public_ip: link?.public_ip ?? "",
      bandwidth_mbps: link?.bandwidth_mbps ?? undefined,
      connection_type: (link?.connection_type as IspLinkInput["connection_type"]) ?? "",
      status: (link?.status as IspLinkInput["status"]) ?? "",
      notes: link?.notes ?? "",
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>{link ? "Edit ISP link" : "New ISP link"}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="grid grid-cols-2 gap-4"
          >
            <div className="col-span-2">
              <SelectFormField
                control={form.control}
                name="site_id"
                label="Site *"
                allowNone={false}
                options={siteOptions}
              />
            </div>
            <TextFormField control={form.control} name="provider_name" label="Provider" />
            <TextFormField control={form.control} name="circuit_id" label="Circuit ID" />
            <TextFormField control={form.control} name="public_ip" label="Public IP" />
            <TextFormField
              control={form.control}
              name="bandwidth_mbps"
              label="Bandwidth (Mbps)"
              type="number"
            />
            <SelectFormField
              control={form.control}
              name="connection_type"
              label="Type"
              options={CONNECTION_TYPES.map((t) => ({ value: t, label: t }))}
            />
            <SelectFormField
              control={form.control}
              name="status"
              label="Status"
              options={ISP_STATUSES.map((s) => ({ value: s, label: s }))}
            />
            <div className="col-span-2">
              <TextareaFormField control={form.control} name="notes" label="Notes" rows={2} />
            </div>
            <DialogFooter className="col-span-2">
              <Button type="submit" disabled={form.formState.isSubmitting}>
                {link ? "Save" : "Create"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
