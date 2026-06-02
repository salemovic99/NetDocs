import { zodResolver } from "@hookform/resolvers/zod";
import type { FieldValues, Resolver } from "react-hook-form";
import { z } from "zod";

/**
 * Typed resolver helper. zod v4 `coerce`/optional fields make a schema's input
 * and output types diverge, which trips react-hook-form's resolver generics.
 * We type the form on the OUTPUT type and cast the resolver to match.
 */
export function formResolver<TOut extends FieldValues>(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  schema: z.ZodType<TOut, any, any>,
): Resolver<TOut> {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return zodResolver(schema as any) as unknown as Resolver<TOut>;
}

// --- shared field validators (mirror backend Pydantic rules) ---
const ipv4 =
  /^(25[0-5]|2[0-4]\d|1?\d?\d)(\.(25[0-5]|2[0-4]\d|1?\d?\d)){3}$/;
const ipv6 = /^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$/;
const mac = /^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$/;
const cidr =
  /^(25[0-5]|2[0-4]\d|1?\d?\d)(\.(25[0-5]|2[0-4]\d|1?\d?\d)){3}\/\d{1,2}$/;

const optionalStr = z.string().trim().optional().or(z.literal(""));
const ipField = z
  .string()
  .trim()
  .refine((v) => !v || ipv4.test(v) || ipv6.test(v), "Invalid IP address")
  .optional()
  .or(z.literal(""));

export const SEVERITIES = ["low", "medium", "high", "critical"] as const;
export const PROBLEM_STATUSES = ["open", "resolved", "known_issue"] as const;
export const DEVICE_STATUSES = ["active", "spare", "retired"] as const;
export const CONNECTION_TYPES = [
  "Fiber",
  "DIA",
  "Broadband",
  "LTE",
  "MPLS",
] as const;
export const ISP_STATUSES = ["Active", "Down", "Provisioning"] as const;
export const SECURITY_TYPES = [
  "WPA2-PSK",
  "WPA2-Enterprise",
  "WPA3",
  "Open",
] as const;

// --- auth ---
export const loginSchema = z.object({
  identifier: z.string().min(1, "Required"),
  password: z.string().min(1, "Required"),
});
export type LoginInput = z.infer<typeof loginSchema>;

export const changePasswordSchema = z
  .object({
    current_password: z.string().min(1, "Required"),
    new_password: z.string().min(12, "At least 12 characters"),
    confirm_password: z.string().min(1, "Required"),
  })
  .refine((d) => d.new_password === d.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });
export type ChangePasswordInput = z.infer<typeof changePasswordSchema>;

// --- problems ---
export const problemSchema = z.object({
  title: z.string().min(1, "Required").max(500),
  symptoms: optionalStr,
  root_cause: optionalStr,
  resolution: optionalStr,
  severity: z.enum(SEVERITIES),
  status: z.enum(PROBLEM_STATUSES),
  category_id: z.string().uuid().optional().or(z.literal("")),
  tag_ids: z.array(z.string().uuid()),
  device_ids: z.array(z.string().uuid()),
  related_problem_ids: z.array(z.string().uuid()),
});
export type ProblemInput = z.infer<typeof problemSchema>;

// --- devices ---
export const deviceSchema = z.object({
  hostname: z.string().min(1, "Required").max(255),
  serial_number: optionalStr,
  asset_tag: optionalStr,
  device_type_id: z.string().uuid().optional().or(z.literal("")),
  vendor_id: z.string().uuid().optional().or(z.literal("")),
  site_id: z.string().uuid().optional().or(z.literal("")),
  rack_id: z.string().uuid().optional().or(z.literal("")),
  management_ip: ipField,
  mac_address: z
    .string()
    .trim()
    .refine((v) => !v || mac.test(v), "Invalid MAC (aa:bb:cc:dd:ee:ff)")
    .optional()
    .or(z.literal("")),
  model: optionalStr,
  firmware_version: optionalStr,
  os_version: optionalStr,
  rack_position: z.coerce.number().int().min(0).optional().or(z.nan()),
  status: z.enum(DEVICE_STATUSES),
  notes: optionalStr,
});
export type DeviceInput = z.infer<typeof deviceSchema>;

// --- vlans ---
export const vlanSchema = z.object({
  vlan_id: z.coerce.number().int().min(1).max(4094),
  name: optionalStr,
  description: optionalStr,
  subnet: z
    .string()
    .trim()
    .refine((v) => !v || cidr.test(v), "Invalid CIDR (e.g. 10.0.0.0/24)")
    .optional()
    .or(z.literal("")),
  gateway: ipField,
});
export type VlanInput = z.infer<typeof vlanSchema>;

// --- sites & rooms ---
export const siteSchema = z.object({
  name: z.string().min(1, "Required").max(255),
  city: optionalStr,
  country: optionalStr,
  timezone: optionalStr,
  google_map_location: optionalStr,
  notes: optionalStr,
});
export type SiteInput = z.infer<typeof siteSchema>;

export const roomSchema = z.object({
  name: optionalStr,
  floor: optionalStr,
  purpose: optionalStr,
});
export type RoomInput = z.infer<typeof roomSchema>;

// --- ISP / wireless ---
export const ispLinkSchema = z.object({
  site_id: z.string().uuid("Select a site"),
  provider_name: optionalStr,
  circuit_id: optionalStr,
  public_ip: ipField,
  bandwidth_mbps: z.coerce.number().int().min(0).optional().or(z.nan()),
  connection_type: z.enum(CONNECTION_TYPES).optional().or(z.literal("")),
  status: z.enum(ISP_STATUSES).optional().or(z.literal("")),
  notes: optionalStr,
});
export type IspLinkInput = z.infer<typeof ispLinkSchema>;

export const wirelessSchema = z.object({
  site_id: z.string().uuid("Select a site"),
  ssid: z.string().min(1, "Required").max(255),
  vlan_tag: z.coerce.number().int().min(1).max(4094).optional().or(z.nan()),
  security_type: z.enum(SECURITY_TYPES).optional().or(z.literal("")),
  hidden: z.boolean(),
});
export type WirelessInput = z.infer<typeof wirelessSchema>;

// --- lookups ---
export const namedLookupSchema = z.object({
  name: z.string().min(1, "Required").max(255),
});
export const vendorSchema = z.object({
  name: z.string().min(1, "Required").max(100),
  website: optionalStr,
  support_contact: optionalStr,
});
export type VendorInput = z.infer<typeof vendorSchema>;

export const rackSchema = z.object({
  name: z.string().min(1, "Required").max(100),
  site_id: z.string().uuid().optional().or(z.literal("")),
  height_units: z.coerce.number().int().min(1).max(60).optional().or(z.nan()),
  notes: optionalStr,
});
export type RackInput = z.infer<typeof rackSchema>;

// --- users & roles ---
export const userSchema = z.object({
  email: z.string().email(),
  username: z.string().min(1, "Required").max(100),
  full_name: optionalStr,
  password: z.string().min(12, "At least 12 characters"),
  role_names: z.array(z.string()),
  must_change_password: z.boolean(),
});
export type UserInput = z.infer<typeof userSchema>;

export const roleSchema = z.object({
  name: z.string().min(1, "Required").max(100),
  description: optionalStr,
});
export type RoleInput = z.infer<typeof roleSchema>;

/** Strip empty-string optionals to undefined / null for the API payload. */
export function clean<T extends Record<string, unknown>>(obj: T): Partial<T> {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(obj)) {
    if (v === "" || (typeof v === "number" && Number.isNaN(v))) continue;
    out[k] = v;
  }
  return out as Partial<T>;
}
