"use client";
import { formResolver } from "@/lib/schemas";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { FileText, Link2, Stethoscope, Tags } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { MultiSelect } from "@/components/shared/multi-select";
import { useCategories, useTags } from "@/lib/hooks/use-lookups";
import { useDevices } from "@/lib/hooks/use-devices";
import {
  useCreateProblem,
  useProblems,
  useUpdateProblem,
} from "@/lib/hooks/use-problems";
import {
  clean,
  PROBLEM_STATUSES,
  problemSchema,
  SEVERITIES,
  type ProblemInput,
} from "@/lib/schemas";
import type { Problem } from "@/lib/api/types";

const NONE = "__none__";

export function ProblemForm({
  problem,
  etag,
}: {
  problem?: Problem;
  etag?: string | null;
}) {
  const router = useRouter();
  const isEdit = Boolean(problem);
  const create = useCreateProblem();
  const update = useUpdateProblem(problem?.id ?? "");

  const tags = useTags();
  const categories = useCategories();
  const devices = useDevices({ page_size: 100 });
  const relatable = useProblems({ page_size: 100 });

  const form = useForm<ProblemInput>({
    resolver: formResolver(problemSchema),
    defaultValues: {
      title: problem?.title ?? "",
      symptoms: problem?.symptoms ?? "",
      root_cause: problem?.root_cause ?? "",
      resolution: problem?.resolution ?? "",
      severity: problem?.severity ?? "medium",
      status: problem?.status ?? "open",
      category_id: problem?.category?.id ?? "",
      tag_ids: problem?.tags.map((t) => t.id) ?? [],
      device_ids: problem?.devices.map((d) => d.id) ?? [],
      related_problem_ids: problem?.related_problems.map((p) => p.id) ?? [],
    },
  });

  async function onSubmit(values: ProblemInput) {
    const payload = clean(values);
    if (isEdit && problem) {
      await update.mutateAsync({ body: payload, etag });
      router.push(`/problems/${problem.id}`);
    } else {
      const created = await create.mutateAsync(payload);
      router.push(`/problems/${created.id}`);
    }
    router.refresh();
  }

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="grid gap-6 lg:grid-cols-3"
      >
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <CardHeader className="flex-row items-center gap-3 border-b border-border/60">
              <FileText className="size-5 text-primary" />
              <div className="space-y-0.5">
                <CardTitle className="text-h3">Overview</CardTitle>
                <p className="text-body-sm text-on-surface-variant">
                  A short, searchable summary of the problem.
                </p>
              </div>
            </CardHeader>
            <CardContent className="pt-4">
              <FormField
                control={form.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Title</FormLabel>
                    <FormControl>
                      <Input placeholder="Short summary of the problem" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex-row items-center gap-3 border-b border-border/60">
              <Stethoscope className="size-5 text-primary" />
              <div className="space-y-0.5">
                <CardTitle className="text-h3">Diagnosis</CardTitle>
                <p className="text-body-sm text-on-surface-variant">
                  What was observed, why it happened, and how it was fixed.
                </p>
              </div>
            </CardHeader>
            <CardContent className="space-y-4 pt-4">
              {(
                [
                  ["symptoms", "Symptoms"],
                  ["root_cause", "Root cause"],
                  ["resolution", "Resolution (Markdown)"],
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
                        <Textarea
                          rows={name === "resolution" ? 6 : 3}
                          {...field}
                          value={field.value ?? ""}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              ))}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader className="flex-row items-center gap-3 border-b border-border/60">
              <Tags className="size-5 text-primary" />
              <CardTitle className="text-h3">Classification</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 pt-4">
              <FormField
                control={form.control}
                name="severity"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Severity</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      value={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {SEVERITIES.map((s) => (
                          <SelectItem key={s} value={s} className="capitalize">
                            {s}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="status"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Status</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      value={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {PROBLEM_STATUSES.map((s) => (
                          <SelectItem key={s} value={s}>
                            {s.replace("_", " ")}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="category_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Category</FormLabel>
                    <Select
                      onValueChange={(v) =>
                        field.onChange(v === NONE ? "" : v)
                      }
                      value={field.value || NONE}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="None" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value={NONE}>None</SelectItem>
                        {(categories.data?.items ?? []).map((c) => (
                          <SelectItem key={c.id} value={c.id}>
                            {c.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex-row items-center gap-3 border-b border-border/60">
              <Link2 className="size-5 text-primary" />
              <CardTitle className="text-h3">Links</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 pt-4">
              <FormField
                control={form.control}
                name="tag_ids"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tags</FormLabel>
                    <MultiSelect
                      placeholder="Add tags"
                      value={field.value}
                      onChange={field.onChange}
                      options={(tags.data?.items ?? []).map((t) => ({
                        value: t.id,
                        label: t.name,
                      }))}
                    />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="device_ids"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Affected devices</FormLabel>
                    <MultiSelect
                      placeholder="Link devices"
                      value={field.value}
                      onChange={field.onChange}
                      options={(devices.data?.items ?? []).map((d) => ({
                        value: d.id,
                        label: d.hostname,
                      }))}
                    />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="related_problem_ids"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Related problems</FormLabel>
                    <MultiSelect
                      placeholder="Link problems"
                      value={field.value}
                      onChange={field.onChange}
                      options={(relatable.data?.items ?? [])
                        .filter((p) => p.id !== problem?.id)
                        .map((p) => ({ value: p.id, label: p.title }))}
                    />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          <div className="sticky bottom-4 flex gap-2 rounded-lg border border-border bg-card/80 p-3 shadow-sm backdrop-blur">
            <Button
              type="submit"
              className="flex-1"
              disabled={form.formState.isSubmitting}
            >
              {isEdit ? "Save changes" : "Create problem"}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => router.back()}
            >
              Cancel
            </Button>
          </div>
        </div>
      </form>
    </Form>
  );
}
