"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { toast } from "sonner";

import { api, type QueryParams } from "@/lib/api/client";
import type { Page, Problem } from "@/lib/api/types";

export const problemKeys = {
  all: ["problems"] as const,
  list: (params: QueryParams) => ["problems", "list", params] as const,
  detail: (id: string) => ["problems", "detail", id] as const,
};

export function useProblems(params: QueryParams) {
  return useQuery({
    queryKey: problemKeys.list(params),
    queryFn: () => api.get<Page<Problem>>("problems", params),
  });
}

export function useProblem(id: string) {
  return useQuery({
    queryKey: problemKeys.detail(id),
    queryFn: () => api.getWithEtag<Problem>(`problems/${id}`),
    enabled: Boolean(id),
  });
}

export function useCreateProblem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: unknown) => api.post<Problem>("problems", body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: problemKeys.all });
      toast.success("Problem created");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}

export function useUpdateProblem(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ body, etag }: { body: unknown; etag?: string | null }) =>
      api.patch<Problem>(`problems/${id}`, body, etag),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: problemKeys.all });
      toast.success("Problem updated");
    },
    onError: (e: { message: string; status?: number }) => {
      if ((e as { status?: number }).status === 409) {
        toast.error("This problem changed elsewhere — reload and retry");
      } else {
        toast.error(e.message);
      }
    },
  });
}

export function useArchiveProblem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.del<void>(`problems/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: problemKeys.all });
      toast.success("Problem archived");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}
