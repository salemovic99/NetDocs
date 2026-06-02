"use client";

/* eslint-disable @typescript-eslint/no-explicit-any */

import {
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

const NONE = "__none__";

export function TextFormField({
  control,
  name,
  label,
  type,
  placeholder,
}: {
  control: any;
  name: string;
  label: string;
  type?: string;
  placeholder?: string;
}) {
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <Input
              type={type}
              placeholder={placeholder}
              {...field}
              value={field.value ?? ""}
            />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

export function TextareaFormField({
  control,
  name,
  label,
  rows = 3,
}: {
  control: any;
  name: string;
  label: string;
  rows?: number;
}) {
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <Textarea rows={rows} {...field} value={field.value ?? ""} />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

export function SelectFormField({
  control,
  name,
  label,
  options,
  allowNone = true,
  placeholder = "Select…",
}: {
  control: any;
  name: string;
  label: string;
  options: { value: string; label: string }[];
  allowNone?: boolean;
  placeholder?: string;
}) {
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <FormLabel>{label}</FormLabel>
          <Select
            value={field.value || (allowNone ? NONE : "")}
            onValueChange={(v) => field.onChange(v === NONE ? "" : v)}
          >
            <FormControl>
              <SelectTrigger>
                <SelectValue placeholder={placeholder} />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              {allowNone ? <SelectItem value={NONE}>None</SelectItem> : null}
              {options.map((o) => (
                <SelectItem key={o.value} value={o.value} className="capitalize">
                  {o.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}
