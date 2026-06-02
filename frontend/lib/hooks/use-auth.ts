"use client";

import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { api } from "@/lib/api/client";

async function postAuth(path: string, body?: unknown) {
  const res = await fetch(`/api/auth/${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data?.detail ?? "Request failed");
  return data;
}

export function useLogin() {
  return useMutation({
    mutationFn: (body: { identifier: string; password: string }) =>
      postAuth("login", body) as Promise<{
        ok: boolean;
        must_change_password: boolean;
      }>,
  });
}

export function useLogout() {
  const router = useRouter();
  return useMutation({
    mutationFn: () => postAuth("logout"),
    onSuccess: () => {
      router.push("/login");
      router.refresh();
    },
  });
}

export function useChangePassword() {
  return useMutation({
    mutationFn: (body: { current_password: string; new_password: string }) =>
      api.post<void>("auth/change-password", body),
    onSuccess: () => toast.success("Password changed"),
    onError: (e: Error) => toast.error(e.message),
  });
}
