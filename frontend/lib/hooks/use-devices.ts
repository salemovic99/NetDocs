"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { api, type QueryParams } from "@/lib/api/client";
import type { Device, Page, Vlan } from "@/lib/api/types";

export const deviceKeys = {
  all: ["devices"] as const,
  list: (params: QueryParams) => ["devices", "list", params] as const,
  detail: (id: string) => ["devices", "detail", id] as const,
  vlans: (id: string) => ["devices", id, "vlans"] as const,
};

export function useDevices(params: QueryParams) {
  return useQuery({
    queryKey: deviceKeys.list(params),
    queryFn: () => api.get<Page<Device>>("devices", params),
  });
}

export function useDevice(id: string) {
  return useQuery({
    queryKey: deviceKeys.detail(id),
    queryFn: () => api.getWithEtag<Device>(`devices/${id}`),
    enabled: Boolean(id),
  });
}

export function useCreateDevice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: unknown) => api.post<Device>("devices", body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: deviceKeys.all });
      toast.success("Device created");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}

export function useUpdateDevice(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ body, etag }: { body: unknown; etag?: string | null }) =>
      api.patch<Device>(`devices/${id}`, body, etag),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: deviceKeys.all });
      toast.success("Device updated");
    },
    onError: (e: { message: string; status?: number }) =>
      toast.error(
        e.status === 409
          ? "This device changed elsewhere — reload and retry"
          : e.message,
      ),
  });
}

export function useDeleteDevice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.del<void>(`devices/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: deviceKeys.all });
      toast.success("Device removed");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}

// --- VLANs (per device) ---
export function useVlans(deviceId: string) {
  return useQuery({
    queryKey: deviceKeys.vlans(deviceId),
    queryFn: () => api.get<Vlan[]>(`devices/${deviceId}/vlans`),
    enabled: Boolean(deviceId),
  });
}

export function useVlanMutations(deviceId: string) {
  const qc = useQueryClient();
  const invalidate = () =>
    qc.invalidateQueries({ queryKey: deviceKeys.vlans(deviceId) });
  return {
    create: useMutation({
      mutationFn: (body: unknown) =>
        api.post<Vlan>(`devices/${deviceId}/vlans`, body),
      onSuccess: () => {
        invalidate();
        toast.success("VLAN added");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    update: useMutation({
      mutationFn: ({ id, body }: { id: string; body: unknown }) =>
        api.patch<Vlan>(`vlans/${id}`, body),
      onSuccess: () => {
        invalidate();
        toast.success("VLAN updated");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    remove: useMutation({
      mutationFn: (id: string) => api.del<void>(`vlans/${id}`),
      onSuccess: () => {
        invalidate();
        toast.success("VLAN removed");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
  };
}
