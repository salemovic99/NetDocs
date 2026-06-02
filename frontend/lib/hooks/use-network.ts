"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { api, type QueryParams } from "@/lib/api/client";
import type { IspLink, Page, Wireless } from "@/lib/api/types";

export function useIspLinks(params: QueryParams) {
  return useQuery({
    queryKey: ["isp-links", "list", params],
    queryFn: () => api.get<Page<IspLink>>("isp-links", params),
  });
}

export function useIspLinkMutations() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: ["isp-links"] });
  return {
    create: useMutation({
      mutationFn: (body: unknown) => api.post<IspLink>("isp-links", body),
      onSuccess: () => {
        invalidate();
        toast.success("ISP link created");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    update: useMutation({
      mutationFn: ({ id, body }: { id: string; body: unknown }) =>
        api.patch<IspLink>(`isp-links/${id}`, body),
      onSuccess: () => {
        invalidate();
        toast.success("ISP link updated");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    remove: useMutation({
      mutationFn: (id: string) => api.del<void>(`isp-links/${id}`),
      onSuccess: () => {
        invalidate();
        toast.success("ISP link deleted");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
  };
}

export function useWirelessNetworks(params: QueryParams) {
  return useQuery({
    queryKey: ["wireless", "list", params],
    queryFn: () => api.get<Page<Wireless>>("wireless-networks", params),
  });
}

export function useWirelessMutations() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: ["wireless"] });
  return {
    create: useMutation({
      mutationFn: (body: unknown) => api.post<Wireless>("wireless-networks", body),
      onSuccess: () => {
        invalidate();
        toast.success("Wireless network created");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    update: useMutation({
      mutationFn: ({ id, body }: { id: string; body: unknown }) =>
        api.patch<Wireless>(`wireless-networks/${id}`, body),
      onSuccess: () => {
        invalidate();
        toast.success("Wireless network updated");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    remove: useMutation({
      mutationFn: (id: string) => api.del<void>(`wireless-networks/${id}`),
      onSuccess: () => {
        invalidate();
        toast.success("Wireless network deleted");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
  };
}
