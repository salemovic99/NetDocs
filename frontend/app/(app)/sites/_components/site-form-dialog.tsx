"use client";
import { formResolver } from "@/lib/schemas";

import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Form } from "@/components/ui/form";
import {
  TextFormField,
  TextareaFormField,
} from "@/components/shared/form-fields";
import { useSiteMutations } from "@/lib/hooks/use-sites";
import { clean, siteSchema, type SiteInput } from "@/lib/schemas";
import type { Site } from "@/lib/api/types";

export function SiteFormDialog({
  open,
  onOpenChange,
  site,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  site?: Site | null;
  onSaved?: () => void;
}) {
  const { create, update } = useSiteMutations();
  const form = useForm<SiteInput>({
    resolver: formResolver(siteSchema),
    defaultValues: {
      name: site?.name ?? "",
      city: site?.city ?? "",
      country: site?.country ?? "",
      timezone: site?.timezone ?? "",
      google_map_location: site?.google_map_location ?? "",
      notes: site?.notes ?? "",
    },
  });

  async function onSubmit(values: SiteInput) {
    const payload = clean(values);
    if (site) {
      await update.mutateAsync({ id: site.id, body: payload });
    } else {
      await create.mutateAsync(payload);
    }
    onOpenChange(false);
    onSaved?.();
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>{site ? "Edit site" : "New site"}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="grid grid-cols-2 gap-4"
          >
            <div className="col-span-2">
              <TextFormField control={form.control} name="name" label="Name *" />
            </div>
            <TextFormField control={form.control} name="city" label="City" />
            <TextFormField control={form.control} name="country" label="Country" />
            <TextFormField control={form.control} name="timezone" label="Timezone" />
            <TextFormField
              control={form.control}
              name="google_map_location"
              label="Google Maps URL"
            />
            <div className="col-span-2">
              <TextareaFormField control={form.control} name="notes" label="Notes" rows={2} />
            </div>
            <DialogFooter className="col-span-2">
              <Button type="submit" disabled={form.formState.isSubmitting}>
                {site ? "Save" : "Create"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
