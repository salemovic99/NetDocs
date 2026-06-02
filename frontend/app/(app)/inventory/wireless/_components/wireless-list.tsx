"use client";
import { formResolver } from "@/lib/schemas";

import * as React from "react";
import { Controller, useForm } from "react-hook-form";
import { Pencil, Plus, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Form, FormItem, FormLabel } from "@/components/ui/form";
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
import { SelectFormField, TextFormField } from "@/components/shared/form-fields";
import { usePermissions } from "@/lib/auth/session-context";
import { useWirelessMutations, useWirelessNetworks } from "@/lib/hooks/use-network";
import { useSites } from "@/lib/hooks/use-sites";
import { PERMISSIONS } from "@/lib/permissions";
import {
  clean,
  SECURITY_TYPES,
  wirelessSchema,
  type WirelessInput,
} from "@/lib/schemas";
import type { Wireless } from "@/lib/api/types";

export function WirelessList() {
  const { can } = usePermissions();
  const manage = can(PERMISSIONS.INVENTORY_MANAGE);
  const { data, isLoading } = useWirelessNetworks({ page_size: 100 });
  const { create, update, remove } = useWirelessMutations();
  const sites = useSites({ page_size: 100 });
  const [open, setOpen] = React.useState(false);
  const [editing, setEditing] = React.useState<Wireless | null>(null);

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
              <Plus /> New SSID
            </Button>
          </div>
        ) : null}

        {isLoading ? (
          <Skeleton className="h-40 w-full" />
        ) : !data?.items.length ? (
          <EmptyState title="No wireless networks" description="Add an SSID." />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>SSID</TableHead>
                <TableHead>Site</TableHead>
                <TableHead>VLAN</TableHead>
                <TableHead>Security</TableHead>
                <TableHead>Hidden</TableHead>
                {manage ? <TableHead className="w-20" /> : null}
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.items.map((w) => (
                <TableRow key={w.id}>
                  <TableCell className="text-on-surface">{w.ssid}</TableCell>
                  <TableCell className="text-on-surface-variant">
                    {siteName(w.site_id)}
                  </TableCell>
                  <TableCell className="text-mono text-on-surface-variant">
                    {w.vlan_tag ?? "—"}
                  </TableCell>
                  <TableCell>
                    {w.security_type ? (
                      <Badge variant="outline">{w.security_type}</Badge>
                    ) : (
                      "—"
                    )}
                  </TableCell>
                  <TableCell className="text-on-surface-variant">
                    {w.hidden ? "Yes" : "No"}
                  </TableCell>
                  {manage ? (
                    <TableCell className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={() => {
                          setEditing(w);
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
                        title={`Delete SSID "${w.ssid}"?`}
                        confirmLabel="Delete"
                        onConfirm={() => remove.mutate(w.id)}
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
        <WirelessDialog
          key={editing?.id ?? "new"}
          open={open}
          onOpenChange={setOpen}
          net={editing}
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

function WirelessDialog({
  open,
  onOpenChange,
  net,
  siteOptions,
  onSubmit,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  net: Wireless | null;
  siteOptions: { value: string; label: string }[];
  onSubmit: (values: WirelessInput) => Promise<void>;
}) {
  const form = useForm<WirelessInput>({
    resolver: formResolver(wirelessSchema),
    defaultValues: {
      site_id: net?.site_id ?? "",
      ssid: net?.ssid ?? "",
      vlan_tag: net?.vlan_tag ?? undefined,
      security_type: (net?.security_type as WirelessInput["security_type"]) ?? "",
      hidden: net?.hidden ?? false,
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>{net ? "Edit SSID" : "New SSID"}</DialogTitle>
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
            <TextFormField control={form.control} name="ssid" label="SSID *" />
            <TextFormField
              control={form.control}
              name="vlan_tag"
              label="VLAN tag"
              type="number"
            />
            <SelectFormField
              control={form.control}
              name="security_type"
              label="Security"
              options={SECURITY_TYPES.map((s) => ({ value: s, label: s }))}
            />
            <Controller
              control={form.control}
              name="hidden"
              render={({ field }) => (
                <FormItem className="flex-row items-center gap-2 pt-7">
                  <Checkbox
                    checked={field.value}
                    onCheckedChange={field.onChange}
                  />
                  <FormLabel className="!mt-0">Hidden SSID</FormLabel>
                </FormItem>
              )}
            />
            <DialogFooter className="col-span-2">
              <Button type="submit" disabled={form.formState.isSubmitting}>
                {net ? "Save" : "Create"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
