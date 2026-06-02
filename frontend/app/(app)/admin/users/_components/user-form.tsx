"use client";

import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { MultiSelect } from "@/components/shared/multi-select";
import { TextFormField } from "@/components/shared/form-fields";
import { useRoles, useUserMutations } from "@/lib/hooks/use-admin";
import { clean, formResolver, userSchema, type UserInput } from "@/lib/schemas";

export function UserForm({ onDone }: { onDone: () => void }) {
  const roles = useRoles();
  const { create } = useUserMutations();

  const form = useForm<UserInput>({
    resolver: formResolver(userSchema),
    defaultValues: {
      email: "",
      username: "",
      full_name: "",
      password: "",
      role_names: [],
      must_change_password: true,
    },
  });

  async function onSubmit(values: UserInput) {
    await create.mutateAsync(clean(values));
    onDone();
  }

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="grid grid-cols-2 gap-4"
      >
        <TextFormField control={form.control} name="email" label="Email *" />
        <TextFormField control={form.control} name="username" label="Username *" />
        <div className="col-span-2">
          <TextFormField control={form.control} name="full_name" label="Full name" />
        </div>
        <div className="col-span-2">
          <TextFormField
            control={form.control}
            name="password"
            label="Temporary password *"
            type="password"
          />
        </div>
        <div className="col-span-2">
          <FormField
            control={form.control}
            name="role_names"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Roles</FormLabel>
                <MultiSelect
                  placeholder="Assign roles"
                  value={field.value}
                  onChange={field.onChange}
                  options={(roles.data?.items ?? []).map((r) => ({
                    value: r.name,
                    label: r.name,
                  }))}
                />
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
        <FormField
          control={form.control}
          name="must_change_password"
          render={({ field }) => (
            <FormItem className="col-span-2 flex-row items-center gap-2">
              <FormControl>
                <Checkbox
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
              </FormControl>
              <FormLabel className="!mt-0">
                Require password change on first login
              </FormLabel>
            </FormItem>
          )}
        />
        <div className="col-span-2 flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onDone}>
            Cancel
          </Button>
          <Button type="submit" disabled={form.formState.isSubmitting}>
            Create user
          </Button>
        </div>
      </form>
    </Form>
  );
}
