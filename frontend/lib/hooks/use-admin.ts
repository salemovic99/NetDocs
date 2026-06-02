"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { api, type QueryParams } from "@/lib/api/client";
import type { AuditLog, Page, Permission, Role, User } from "@/lib/api/types";

// --- Users ---
export function useUsers(params: QueryParams) {
  return useQuery({
    queryKey: ["users", "list", params],
    queryFn: () => api.get<Page<User>>("users", params),
  });
}

export function useUserMutations() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: ["users"] });
  return {
    create: useMutation({
      mutationFn: (body: unknown) => api.post<User>("users", body),
      onSuccess: () => {
        invalidate();
        toast.success("User created");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    update: useMutation({
      mutationFn: ({ id, body }: { id: string; body: unknown }) =>
        api.patch<User>(`users/${id}`, body),
      onSuccess: () => {
        invalidate();
        toast.success("User updated");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    setRoles: useMutation({
      mutationFn: ({ id, role_names }: { id: string; role_names: string[] }) =>
        api.put<User>(`users/${id}/roles`, { role_names }),
      onSuccess: () => {
        invalidate();
        toast.success("Roles updated");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    unlock: useMutation({
      mutationFn: (id: string) => api.post<User>(`users/${id}/unlock`),
      onSuccess: () => {
        invalidate();
        toast.success("User unlocked");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    resetPassword: useMutation({
      mutationFn: (id: string) =>
        api.post<{ user_id: string; temporary_password: string }>(
          `users/${id}/reset-password`,
        ),
      onError: (e: Error) => toast.error(e.message),
    }),
  };
}

// --- Roles & permissions ---
export function useRoles(params: QueryParams = { page_size: 100 }) {
  return useQuery({
    queryKey: ["roles", "list", params],
    queryFn: () => api.get<Page<Role>>("roles", params),
  });
}

export function usePermissions() {
  return useQuery({
    queryKey: ["permissions", "list"],
    queryFn: () => api.get<Page<Permission>>("permissions", { page_size: 100 }),
  });
}

export function useRoleMutations() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: ["roles"] });
  return {
    create: useMutation({
      mutationFn: (body: unknown) => api.post<Role>("roles", body),
      onSuccess: () => {
        invalidate();
        toast.success("Role created");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    update: useMutation({
      mutationFn: ({ id, body }: { id: string; body: unknown }) =>
        api.patch<Role>(`roles/${id}`, body),
      onSuccess: () => {
        invalidate();
        toast.success("Role updated");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    remove: useMutation({
      mutationFn: (id: string) => api.del<void>(`roles/${id}`),
      onSuccess: () => {
        invalidate();
        toast.success("Role deleted");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    setPermissions: useMutation({
      mutationFn: ({ id, codes }: { id: string; codes: string[] }) =>
        api.put<Role>(`roles/${id}/permissions`, { permission_codes: codes }),
      onSuccess: () => {
        invalidate();
        toast.success("Permissions updated");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
  };
}

// --- Audit log ---
export function useAuditLog(params: QueryParams) {
  return useQuery({
    queryKey: ["audit-log", "list", params],
    queryFn: () => api.get<Page<AuditLog>>("audit-log", params),
  });
}
