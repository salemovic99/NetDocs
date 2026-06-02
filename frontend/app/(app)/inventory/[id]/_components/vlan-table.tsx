"use client";
import { formResolver } from "@/lib/schemas";

import * as React from "react";
import { useForm } from "react-hook-form";
import { Pencil, Plus, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { usePermissions } from "@/lib/auth/session-context";
import { useVlanMutations, useVlans } from "@/lib/hooks/use-devices";
import { PERMISSIONS } from "@/lib/permissions";
import { clean, vlanSchema, type VlanInput } from "@/lib/schemas";
import type { Vlan } from "@/lib/api/types";

export function VlanTable({ deviceId }: { deviceId: string }) {
  const { can } = usePermissions();
  const { data, isLoading } = useVlans(deviceId);
  const { create, update, remove } = useVlanMutations(deviceId);
  const [editing, setEditing] = React.useState<Vlan | null>(null);
  const [open, setOpen] = React.useState(false);
  const manage = can(PERMISSIONS.INVENTORY_MANAGE);

  const openCreate = () => {
    setEditing(null);
    setOpen(true);
  };
  const openEdit = (vlan: Vlan) => {
    setEditing(vlan);
    setOpen(true);
  };

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle className="text-h4">VLANs</CardTitle>
        {manage ? (
          <Button variant="outline" size="sm" onClick={openCreate}>
            <Plus /> Add VLAN
          </Button>
        ) : null}
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p className="text-body-sm text-on-surface-variant">Loading…</p>
        ) : !data?.length ? (
          <p className="text-body-sm text-on-surface-variant">
            No VLANs documented on this switch.
          </p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-20">Tag</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Subnet</TableHead>
                <TableHead>Gateway</TableHead>
                {manage ? <TableHead className="w-20" /> : null}
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((v) => (
                <TableRow key={v.id}>
                  <TableCell className="text-mono">{v.vlan_id}</TableCell>
                  <TableCell>{v.name ?? "—"}</TableCell>
                  <TableCell className="text-mono text-on-surface-variant">
                    {v.subnet ?? "—"}
                  </TableCell>
                  <TableCell className="text-mono text-on-surface-variant">
                    {v.gateway ?? "—"}
                  </TableCell>
                  {manage ? (
                    <TableCell className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={() => openEdit(v)}
                      >
                        <Pencil />
                      </Button>
                      <ConfirmDialog
                        trigger={
                          <Button variant="ghost" size="icon-sm">
                            <Trash2 className="text-error" />
                          </Button>
                        }
                        title={`Remove VLAN ${v.vlan_id}?`}
                        confirmLabel="Remove"
                        onConfirm={() => remove.mutate(v.id)}
                      />
                    </TableCell>
                  ) : null}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>

      <VlanDialog
        key={editing?.id ?? "new"}
        open={open}
        onOpenChange={setOpen}
        vlan={editing}
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
    </Card>
  );
}

function VlanDialog({
  open,
  onOpenChange,
  vlan,
  onSubmit,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  vlan: Vlan | null;
  onSubmit: (values: VlanInput) => Promise<void>;
}) {
  const form = useForm<VlanInput>({
    resolver: formResolver(vlanSchema),
    defaultValues: {
      vlan_id: vlan?.vlan_id ?? (undefined as unknown as number),
      name: vlan?.name ?? "",
      description: vlan?.description ?? "",
      subnet: vlan?.subnet ?? "",
      gateway: vlan?.gateway ?? "",
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{vlan ? "Edit VLAN" : "Add VLAN"}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="grid grid-cols-2 gap-4"
          >
            {(
              [
                ["vlan_id", "Tag (1–4094)", "number"],
                ["name", "Name", "text"],
                ["subnet", "Subnet (CIDR)", "text"],
                ["gateway", "Gateway", "text"],
              ] as const
            ).map(([name, label, type]) => (
              <FormField
                key={name}
                control={form.control}
                name={name}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{label}</FormLabel>
                    <FormControl>
                      <Input
                        type={type}
                        {...field}
                        value={field.value ?? ""}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            ))}
            <DialogFooter className="col-span-2">
              <Button type="submit" disabled={form.formState.isSubmitting}>
                {vlan ? "Save" : "Add"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
