"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { api, type QueryParams } from "@/lib/api/client";
import type { Page, Site, SiteDetail } from "@/lib/api/types";

export const siteKeys = {
  all: ["sites"] as const,
  list: (params: QueryParams) => ["sites", "list", params] as const,
  detail: (id: string) => ["sites", "detail", id] as const,
};

export function useSites(params: QueryParams) {
  return useQuery({
    queryKey: siteKeys.list(params),
    queryFn: () => api.get<Page<Site>>("sites", params),
  });
}

export function useSite(id: string) {
  return useQuery({
    queryKey: siteKeys.detail(id),
    queryFn: () => api.get<SiteDetail>(`sites/${id}`),
    enabled: Boolean(id),
  });
}

export function useSiteMutations() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: siteKeys.all });
  return {
    create: useMutation({
      mutationFn: (body: unknown) => api.post<Site>("sites", body),
      onSuccess: () => {
        invalidate();
        toast.success("Site created");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    update: useMutation({
      mutationFn: ({ id, body }: { id: string; body: unknown }) =>
        api.patch<Site>(`sites/${id}`, body),
      onSuccess: () => {
        invalidate();
        toast.success("Site updated");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    remove: useMutation({
      mutationFn: (id: string) => api.del<void>(`sites/${id}`),
      onSuccess: () => {
        invalidate();
        toast.success("Site deleted");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
  };
}

export function useRoomMutations(siteId: string) {
  const qc = useQueryClient();
  const invalidate = () =>
    qc.invalidateQueries({ queryKey: siteKeys.detail(siteId) });
  return {
    create: useMutation({
      mutationFn: (body: unknown) => api.post(`sites/${siteId}/rooms`, body),
      onSuccess: () => {
        invalidate();
        toast.success("Room added");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    update: useMutation({
      mutationFn: ({ id, body }: { id: string; body: unknown }) =>
        api.patch(`rooms/${id}`, body),
      onSuccess: () => {
        invalidate();
        toast.success("Room updated");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    remove: useMutation({
      mutationFn: (id: string) => api.del(`rooms/${id}`),
      onSuccess: () => {
        invalidate();
        toast.success("Room removed");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
  };
}
