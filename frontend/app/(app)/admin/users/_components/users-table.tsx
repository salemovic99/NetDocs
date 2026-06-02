"use client";

import * as React from "react";
import { KeyRound, MoreHorizontal, Plus, ShieldCheck, Unlock } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { MultiSelect } from "@/components/shared/multi-select";
import { useRoles, useUserMutations, useUsers } from "@/lib/hooks/use-admin";
import type { User } from "@/lib/api/types";
import { UserForm } from "./user-form";

export function UsersTable() {
  const { data, isLoading } = useUsers({ page_size: 100 });
  const [createOpen, setCreateOpen] = React.useState(false);
  const [rolesFor, setRolesFor] = React.useState<User | null>(null);

  return (
    <Card>
      <CardContent className="space-y-4 pt-6">
        <div className="flex justify-end">
          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <Button onClick={() => setCreateOpen(true)}>
              <Plus /> New user
            </Button>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle>New user</DialogTitle>
              </DialogHeader>
              <UserForm onDone={() => setCreateOpen(false)} />
            </DialogContent>
          </Dialog>
        </div>

        {isLoading ? (
          <Skeleton className="h-40 w-full" />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Roles</TableHead>
                <TableHead className="w-24">Active</TableHead>
                <TableHead className="w-12" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {data?.items.map((u) => (
                <TableRow key={u.id}>
                  <TableCell>
                    <div className="flex flex-col">
                      <span className="text-on-surface">
                        {u.full_name || u.username}
                      </span>
                      <span className="text-body-sm text-on-surface-variant">
                        {u.email}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="space-x-1">
                    {u.roles.length ? (
                      u.roles.map((r) => (
                        <Badge key={r.id} variant="default">
                          {r.name}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-on-surface-variant">—</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge variant={u.is_active ? "success" : "destructive"}>
                      {u.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <UserActions
                      user={u}
                      onManageRoles={() => setRolesFor(u)}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>

      <ManageRolesDialog
        key={rolesFor?.id ?? "none"}
        user={rolesFor}
        onClose={() => setRolesFor(null)}
      />
    </Card>
  );
}

function UserActions({
  user,
  onManageRoles,
}: {
  user: User;
  onManageRoles: () => void;
}) {
  const { unlock, resetPassword } = useUserMutations();
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={onManageRoles}>
          <ShieldCheck /> Manage roles
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => unlock.mutate(user.id)}>
          <Unlock /> Unlock account
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={async () => {
            const res = await resetPassword.mutateAsync(user.id);
            toast.success("Temporary password generated", {
              description: res.temporary_password,
              duration: 30000,
            });
          }}
        >
          <KeyRound /> Reset password
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function ManageRolesDialog({
  user,
  onClose,
}: {
  user: User | null;
  onClose: () => void;
}) {
  const roles = useRoles();
  const { setRoles } = useUserMutations();
  // Initialised from props; the parent remounts this via `key` per user.
  const [selected, setSelected] = React.useState<string[]>(
    () => user?.roles.map((r) => r.name) ?? [],
  );

  return (
    <Dialog open={Boolean(user)} onOpenChange={(o) => !o && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Manage roles</DialogTitle>
          <DialogDescription>
            {user?.full_name || user?.username}
          </DialogDescription>
        </DialogHeader>
        <MultiSelect
          placeholder="Assign roles"
          value={selected}
          onChange={setSelected}
          options={(roles.data?.items ?? []).map((r) => ({
            value: r.name,
            label: r.name,
          }))}
        />
        <DialogFooter>
          <Button
            onClick={async () => {
              if (!user) return;
              await setRoles.mutateAsync({ id: user.id, role_names: selected });
              onClose();
            }}
          >
            Save roles
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
