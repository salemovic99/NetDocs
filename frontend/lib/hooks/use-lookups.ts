"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { api } from "@/lib/api/client";
import type { Category, DeviceType, Page, Rack, Tag, Vendor } from "@/lib/api/types";

const PAGE = { page_size: 100, sort: "name" };

/** Generic lookup list hook factory. */
function listHook<T>(resource: string, key: string) {
  return () =>
    useQuery({
      queryKey: [key, "list"],
      queryFn: () => api.get<Page<T>>(resource, PAGE),
    });
}

export const useTags = listHook<Tag>("tags", "tags");
export const useCategories = listHook<Category>("problem-categories", "categories");
export const useDeviceTypes = listHook<DeviceType>("device-types", "device-types");
export const useVendors = listHook<Vendor>("vendors", "vendors");
export const useRacks = listHook<Rack>("racks", "racks");

/** Generic create/delete for a managed lookup, invalidating its list. */
export function useLookupMutations(resource: string, key: string) {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: [key] });
  return {
    create: useMutation({
      mutationFn: (body: unknown) => api.post(resource, body),
      onSuccess: () => {
        invalidate();
        toast.success("Created");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    update: useMutation({
      mutationFn: ({ id, body }: { id: string; body: unknown }) =>
        api.patch(`${resource}/${id}`, body),
      onSuccess: () => {
        invalidate();
        toast.success("Updated");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
    remove: useMutation({
      mutationFn: (id: string) => api.del(`${resource}/${id}`),
      onSuccess: () => {
        invalidate();
        toast.success("Deleted");
      },
      onError: (e: Error) => toast.error(e.message),
    }),
  };
}
