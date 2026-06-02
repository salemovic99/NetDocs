"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { api } from "@/lib/api/client";
import type { Attachment } from "@/lib/api/types";

export function useProblemAttachments(problemId: string) {
  return useQuery({
    queryKey: ["attachments", "problem", problemId],
    queryFn: () => api.get<Attachment[]>(`problems/${problemId}/attachments`),
    enabled: Boolean(problemId),
  });
}

export function useDeviceAttachments(deviceId: string) {
  return useQuery({
    queryKey: ["attachments", "device", deviceId],
    queryFn: () => api.get<Attachment[]>(`devices/${deviceId}/attachments`),
    enabled: Boolean(deviceId),
  });
}

export function useUploadAttachment(scope: "problems" | "devices", id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (file: File) =>
      api.upload<Attachment>(`${scope}/${id}/attachments`, file),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["attachments"] });
      toast.success("File uploaded");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}

export function useDeleteAttachment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.del<void>(`attachments/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["attachments"] });
      toast.success("Attachment deleted");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}

/** Download URL goes straight through the BFF proxy (auth-gated). */
export function attachmentDownloadUrl(id: string): string {
  return `/api/proxy/attachments/${id}`;
}
