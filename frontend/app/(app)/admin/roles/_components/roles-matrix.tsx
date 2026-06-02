"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { Plus } from "lucide-react";

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
import {
  TextFormField,
  TextareaFormField,
} from "@/components/shared/form-fields";
import {
  usePermissions,
  useRoleMutations,
  useRoles,
} from "@/lib/hooks/use-admin";
import { clean, formResolver, roleSchema, type RoleInput } from "@/lib/schemas";
import type { Role } from "@/lib/api/types";

export function RolesMatrix() {
  const roles = useRoles();
  const permissions = usePermissions();
  const { setPermissions } = useRoleMutations();
  const [createOpen, setCreateOpen] = React.useState(false);

  if (roles.isLoading || permissions.isLoading) {
    return <Skeleton className="h-96 w-full" />;
  }

  const roleList = roles.data?.items ?? [];
  const permList = permissions.data?.items ?? [];

  const toggle = (role: Role, code: string, checked: boolean) => {
    const current = new Set(role.permissions.map((p) => p.code));
    if (checked) current.add(code);
    else current.delete(code);
    setPermissions.mutate({ id: role.id, codes: [...current] });
  };

  return (
    <Card>
      <CardContent className="space-y-4 pt-6">
        <div className="flex justify-end">
          <Button onClick={() => setCreateOpen(true)}>
            <Plus /> New role
          </Button>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="min-w-56">Capability</TableHead>
              {roleList.map((r) => (
                <TableHead key={r.id} className="text-center">
                  {r.name}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {permList.map((perm) => (
              <TableRow key={perm.id}>
                <TableCell>
                  <span className="text-mono text-on-surface">{perm.code}</span>
                  {perm.description ? (
                    <p className="text-body-sm text-on-surface-variant">
                      {perm.description}
                    </p>
                  ) : null}
                </TableCell>
                {roleList.map((r) => {
                  const checked = r.permissions.some(
                    (p) => p.code === perm.code,
                  );
                  return (
                    <TableCell key={r.id} className="text-center">
                      <div className="flex justify-center">
                        <Checkbox
                          checked={checked}
                          onCheckedChange={(v) =>
                            toggle(r, perm.code, Boolean(v))
                          }
                        />
                      </div>
                    </TableCell>
                  );
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>

      <NewRoleDialog open={createOpen} onOpenChange={setCreateOpen} />
    </Card>
  );
}

function NewRoleDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
}) {
  const { create } = useRoleMutations();
  const form = useForm<RoleInput>({
    resolver: formResolver(roleSchema),
    defaultValues: { name: "", description: "" },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New role</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(async (values) => {
              await create.mutateAsync(clean(values));
              onOpenChange(false);
            })}
            className="space-y-4"
          >
            <TextFormField control={form.control} name="name" label="Name *" />
            <TextareaFormField
              control={form.control}
              name="description"
              label="Description"
              rows={2}
            />
            <DialogFooter>
              <Button type="submit" disabled={form.formState.isSubmitting}>
                Create role
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
