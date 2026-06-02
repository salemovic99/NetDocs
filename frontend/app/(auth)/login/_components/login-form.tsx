"use client";
import { formResolver } from "@/lib/schemas";

import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useLogin } from "@/lib/hooks/use-auth";
import { loginSchema, type LoginInput } from "@/lib/schemas";

export function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const login = useLogin();

  const form = useForm<LoginInput>({
    resolver: formResolver(loginSchema),
    defaultValues: { identifier: "", password: "" },
  });

  async function onSubmit(values: LoginInput) {
    try {
      const result = await login.mutateAsync(values);
      router.refresh();
      if (result.must_change_password) {
        router.push("/change-password");
      } else {
        router.push(params.get("next") ?? "/");
      }
    } catch (e) {
      form.setError("password", {
        message: e instanceof Error ? e.message : "Invalid credentials",
      });
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="identifier"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email or username</FormLabel>
              <FormControl>
                <Input
                  autoComplete="username"
                  placeholder="admin"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  autoComplete="current-password"
                  placeholder="••••••••••••"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button
          type="submit"
          className="w-full"
          disabled={form.formState.isSubmitting}
        >
          {form.formState.isSubmitting ? (
            <Loader2 className="animate-spin" />
          ) : null}
          Sign in
        </Button>
      </form>
    </Form>
  );
}
