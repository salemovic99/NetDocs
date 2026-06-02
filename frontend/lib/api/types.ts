/** TypeScript mirrors of the backend Pydantic response models (PRD §10). */

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export type Severity = "low" | "medium" | "high" | "critical";
export type ProblemStatus = "open" | "resolved" | "known_issue";
export type DeviceStatus = "active" | "spare" | "retired";

export interface NamedRef {
  id: string;
  name: string;
}

export interface TagRef {
  id: string;
  name: string;
}

export interface ProblemDeviceRef {
  id: string;
  hostname: string;
}

export interface ProblemRelatedRef {
  id: string;
  title: string;
  status: ProblemStatus;
}

export interface Problem {
  id: string;
  title: string;
  symptoms: string | null;
  root_cause: string | null;
  resolution: string | null;
  severity: Severity;
  status: ProblemStatus;
  is_archived: boolean;
  category: NamedRef | null;
  reported_by: string | null;
  created_by: string | null;
  updated_by: string | null;
  created_at: string;
  updated_at: string;
  tags: TagRef[];
  devices: ProblemDeviceRef[];
  related_problems: ProblemRelatedRef[];
}

export interface DeviceType {
  id: string;
  name: string;
}

export interface Vendor {
  id: string;
  name: string;
  website: string | null;
  support_contact: string | null;
}

export interface Rack {
  id: string;
  name: string;
  site_id: string | null;
  height_units: number | null;
  notes: string | null;
}

export interface Device {
  id: string;
  hostname: string;
  serial_number: string | null;
  asset_tag: string | null;
  management_ip: string | null;
  mac_address: string | null;
  model: string | null;
  firmware_version: string | null;
  os_version: string | null;
  rack_position: number | null;
  status: DeviceStatus;
  notes: string | null;
  device_type: DeviceType | null;
  vendor: Vendor | null;
  site: Site | null;
  rack: Rack | null;
}

export interface Vlan {
  id: string;
  device_id: string;
  vlan_id: number;
  name: string | null;
  description: string | null;
  subnet: string | null;
  gateway: string | null;
}

export interface Room {
  id: string;
  site_id: string;
  name: string | null;
  floor: string | null;
  purpose: string | null;
}

export interface Site {
  id: string;
  name: string;
  google_map_location: string | null;
  city: string | null;
  country: string | null;
  timezone: string | null;
  notes: string | null;
}

export interface SiteDetail extends Site {
  rooms: Room[];
  devices: Device[];
  racks: Rack[];
  isp_links: IspLink[];
  wireless_networks: Wireless[];
}

export interface IspLink {
  id: string;
  site_id: string;
  provider_name: string | null;
  circuit_id: string | null;
  public_ip: string | null;
  bandwidth_mbps: number | null;
  connection_type: string | null;
  status: string | null;
  notes: string | null;
}

export interface Wireless {
  id: string;
  site_id: string;
  ssid: string;
  vlan_tag: number | null;
  security_type: string | null;
  hidden: boolean;
}

export interface Tag {
  id: string;
  name: string;
}

export interface Category {
  id: string;
  name: string;
}

export interface Permission {
  id: string;
  code: string;
  description: string | null;
}

export interface Role {
  id: string;
  name: string;
  description: string | null;
  is_system: boolean;
  permissions: Permission[];
}

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  must_change_password: boolean;
  roles: Role[];
  created_at: string;
  updated_at: string;
}

export interface Attachment {
  id: string;
  problem_id: string | null;
  device_id: string | null;
  filename: string;
  mime_type: string;
  size_bytes: number;
  av_status: "pending" | "clean" | "infected";
  uploaded_by: string | null;
  created_at: string;
}

export interface AuditLog {
  id: string;
  actor_id: string | null;
  action: string;
  entity_type: string | null;
  entity_id: string | null;
  diff: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}
