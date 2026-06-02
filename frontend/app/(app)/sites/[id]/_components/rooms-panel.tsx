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
import { Form } from "@/components/ui/form";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { TextFormField } from "@/components/shared/form-fields";
import { usePermissions } from "@/lib/auth/session-context";
import { useRoomMutations } from "@/lib/hooks/use-sites";
import { PERMISSIONS } from "@/lib/permissions";
import { clean, roomSchema, type RoomInput } from "@/lib/schemas";
import type { Room } from "@/lib/api/types";

export function RoomsPanel({
  siteId,
  rooms,
}: {
  siteId: string;
  rooms: Room[];
}) {
  const { can } = usePermissions();
  const manage = can(PERMISSIONS.INVENTORY_MANAGE);
  const { create, update, remove } = useRoomMutations(siteId);
  const [open, setOpen] = React.useState(false);
  const [editing, setEditing] = React.useState<Room | null>(null);

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle className="text-h4">Rooms</CardTitle>
        {manage ? (
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setEditing(null);
              setOpen(true);
            }}
          >
            <Plus /> Add room
          </Button>
        ) : null}
      </CardHeader>
      <CardContent className="space-y-2">
        {!rooms.length ? (
          <p className="text-body-sm text-on-surface-variant">No rooms.</p>
        ) : (
          rooms.map((r) => (
            <div
              key={r.id}
              className="flex items-center justify-between gap-2 rounded-md border border-border bg-surface-container-low px-3 py-2"
            >
              <div>
                <p className="text-body-lg text-on-surface">{r.name ?? "—"}</p>
                <p className="text-body-sm text-on-surface-variant">
                  {[r.floor, r.purpose].filter(Boolean).join(" · ") || "—"}
                </p>
              </div>
              {manage ? (
                <div className="flex gap-1">
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={() => {
                      setEditing(r);
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
                    title="Remove room?"
                    confirmLabel="Remove"
                    onConfirm={() => remove.mutate(r.id)}
                  />
                </div>
              ) : null}
            </div>
          ))
        )}
      </CardContent>

      {manage ? (
        <RoomDialog
          key={editing?.id ?? "new"}
          open={open}
          onOpenChange={setOpen}
          room={editing}
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

function RoomDialog({
  open,
  onOpenChange,
  room,
  onSubmit,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  room: Room | null;
  onSubmit: (values: RoomInput) => Promise<void>;
}) {
  const form = useForm<RoomInput>({
    resolver: formResolver(roomSchema),
    defaultValues: {
      name: room?.name ?? "",
      floor: room?.floor ?? "",
      purpose: room?.purpose ?? "",
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{room ? "Edit room" : "Add room"}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="grid grid-cols-2 gap-4"
          >
            <div className="col-span-2">
              <TextFormField control={form.control} name="name" label="Name" />
            </div>
            <TextFormField control={form.control} name="floor" label="Floor" />
            <TextFormField
              control={form.control}
              name="purpose"
              label="Purpose"
              placeholder="Server Room, MDF, IDF…"
            />
            <DialogFooter className="col-span-2">
              <Button type="submit" disabled={form.formState.isSubmitting}>
                {room ? "Save" : "Add"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
