"use client";
import { formResolver } from "@/lib/schemas";

import { useForm } from "react-hook-form";

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
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useDeviceTypes, useRacks, useVendors } from "@/lib/hooks/use-lookups";
import { useSites } from "@/lib/hooks/use-sites";
import { useCreateDevice, useUpdateDevice } from "@/lib/hooks/use-devices";
import {
  clean,
  deviceSchema,
  DEVICE_STATUSES,
  type DeviceInput,
} from "@/lib/schemas";
import type { Device } from "@/lib/api/types";

const NONE = "__none__";

export function DeviceForm({
  device,
  etag,
  onDone,
}: {
  device?: Device;
  etag?: string | null;
  onDone: (id?: string) => void;
}) {
  const isEdit = Boolean(device);
  const create = useCreateDevice();
  const update = useUpdateDevice(device?.id ?? "");
  const deviceTypes = useDeviceTypes();
  const vendors = useVendors();
  const racks = useRacks();
  const sites = useSites({ page_size: 100 });

  const form = useForm<DeviceInput>({
    resolver: formResolver(deviceSchema),
    defaultValues: {
      hostname: device?.hostname ?? "",
      serial_number: device?.serial_number ?? "",
      asset_tag: device?.asset_tag ?? "",
      device_type_id: device?.device_type?.id ?? "",
      vendor_id: device?.vendor?.id ?? "",
      site_id: device?.site?.id ?? "",
      rack_id: device?.rack?.id ?? "",
      management_ip: device?.management_ip ?? "",
      mac_address: device?.mac_address ?? "",
      model: device?.model ?? "",
      firmware_version: device?.firmware_version ?? "",
      os_version: device?.os_version ?? "",
      rack_position: device?.rack_position ?? undefined,
      status: device?.status ?? "active",
      notes: device?.notes ?? "",
    },
  });

  async function onSubmit(values: DeviceInput) {
    const payload = clean(values);
    if (isEdit && device) {
      await update.mutateAsync({ body: payload, etag });
      onDone(device.id);
    } else {
      const created = await create.mutateAsync(payload);
      onDone(created.id);
    }
  }

  const lookupOptions = (
    items: { id: string; name?: string; hostname?: string }[] | undefined,
  ) => items ?? [];

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="grid max-h-[70vh] gap-4 overflow-y-auto px-1 sm:grid-cols-2"
      >
        <TextField form={form} name="hostname" label="Hostname *" />
        <SelectField
          form={form}
          name="status"
          label="Status"
          options={DEVICE_STATUSES.map((s) => ({ value: s, label: s }))}
          allowNone={false}
        />
        <SelectField
          form={form}
          name="device_type_id"
          label="Type"
          options={lookupOptions(deviceTypes.data?.items).map((d) => ({
            value: d.id,
            label: d.name!,
          }))}
        />
        <SelectField
          form={form}
          name="vendor_id"
          label="Vendor"
          options={lookupOptions(vendors.data?.items).map((d) => ({
            value: d.id,
            label: d.name!,
          }))}
        />
        <SelectField
          form={form}
          name="site_id"
          label="Site"
          options={(sites.data?.items ?? []).map((s) => ({
            value: s.id,
            label: s.name,
          }))}
        />
        <SelectField
          form={form}
          name="rack_id"
          label="Rack"
          options={lookupOptions(racks.data?.items).map((d) => ({
            value: d.id,
            label: d.name!,
          }))}
        />
        <TextField form={form} name="management_ip" label="Management IP" />
        <TextField form={form} name="mac_address" label="MAC address" />
        <TextField form={form} name="model" label="Model" />
        <TextField form={form} name="serial_number" label="Serial number" />
        <TextField form={form} name="firmware_version" label="Firmware" />
        <TextField form={form} name="os_version" label="OS version" />
        <TextField form={form} name="asset_tag" label="Asset tag" />
        <TextField
          form={form}
          name="rack_position"
          label="Rack position (U)"
          type="number"
        />
        <div className="sm:col-span-2">
          <FormField
            control={form.control}
            name="notes"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Notes</FormLabel>
                <FormControl>
                  <Textarea rows={2} {...field} value={field.value ?? ""} />
                </FormControl>
              </FormItem>
            )}
          />
        </div>
        <div className="flex justify-end gap-2 sm:col-span-2">
          <Button type="button" variant="outline" onClick={() => onDone()}>
            Cancel
          </Button>
          <Button type="submit" disabled={form.formState.isSubmitting}>
            {isEdit ? "Save changes" : "Create device"}
          </Button>
        </div>
      </form>
    </Form>
  );
}

/* eslint-disable @typescript-eslint/no-explicit-any */
function TextField({
  form,
  name,
  label,
  type,
}: {
  form: any;
  name: keyof DeviceInput;
  label: string;
  type?: string;
}) {
  return (
    <FormField
      control={form.control}
      name={name}
      render={({ field }: { field: any }) => (
        <FormItem>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <Input
              type={type}
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

function SelectField({
  form,
  name,
  label,
  options,
  allowNone = true,
}: {
  form: any;
  name: keyof DeviceInput;
  label: string;
  options: { value: string; label: string }[];
  allowNone?: boolean;
}) {
  return (
    <FormField
      control={form.control}
      name={name}
      render={({ field }: { field: any }) => (
        <FormItem>
          <FormLabel>{label}</FormLabel>
          <Select
            value={field.value || (allowNone ? NONE : field.value)}
            onValueChange={(v) => field.onChange(v === NONE ? "" : v)}
          >
            <FormControl>
              <SelectTrigger>
                <SelectValue placeholder="Select…" />
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
