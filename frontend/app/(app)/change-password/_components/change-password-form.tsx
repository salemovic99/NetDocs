"use client";
import { formResolver } from "@/lib/schemas";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useChangePassword } from "@/lib/hooks/use-auth";
import { changePasswordSchema, type ChangePasswordInput } from "@/lib/schemas";

export function ChangePasswordForm() {
  const router = useRouter();
  const changePassword = useChangePassword();
  const form = useForm<ChangePasswordInput>({
    resolver: formResolver(changePasswordSchema),
    defaultValues: {
      current_password: "",
      new_password: "",
      confirm_password: "",
    },
  });

  async function onSubmit(values: ChangePasswordInput) {
    await changePassword.mutateAsync({
      current_password: values.current_password,
      new_password: values.new_password,
    });
    router.push("/");
    router.refresh();
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            {(
              [
                ["current_password", "Current password"],
                ["new_password", "New password"],
                ["confirm_password", "Confirm new password"],
              ] as const
            ).map(([name, label]) => (
              <FormField
                key={name}
                control={form.control}
                name={name}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{label}</FormLabel>
                    <FormControl>
                      <Input type="password" autoComplete="off" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            ))}
            <Button
              type="submit"
              className="w-full"
              disabled={form.formState.isSubmitting}
            >
              Update password
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
