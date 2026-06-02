import {
  Boxes,
  LayoutDashboard,
  type LucideIcon,
  Network,
  Radio,
  Search,
  Server,
  ShieldCheck,
  TriangleAlert,
  Users,
} from "lucide-react";

import { PERMISSIONS, type PermissionCode } from "@/lib/permissions";

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  /** If set, item shows only when the user holds one of these permissions. */
  permission?: PermissionCode;
  /** Match nested routes as active. */
  matchPrefix?: boolean;
}

export interface NavSection {
  heading?: string;
  items: NavItem[];
}

export const NAV: NavSection[] = [
  {
    items: [
      { label: "Dashboard", href: "/", icon: LayoutDashboard },
      {
        label: "Problems",
        href: "/problems",
        icon: TriangleAlert,
        permission: PERMISSIONS.PROBLEMS_READ,
        matchPrefix: true,
      },
      { label: "Search", href: "/search", icon: Search },
    ],
  },
  {
    heading: "Infrastructure",
    items: [
      {
        label: "Inventory",
        href: "/inventory",
        icon: Server,
        permission: PERMISSIONS.INVENTORY_READ,
        matchPrefix: true,
      },
      {
        label: "ISP & WAN",
        href: "/inventory/isp-links",
        icon: Network,
        permission: PERMISSIONS.INVENTORY_READ,
      },
      {
        label: "Wireless",
        href: "/inventory/wireless",
        icon: Radio,
        permission: PERMISSIONS.INVENTORY_READ,
      },
      {
        label: "Sites",
        href: "/sites",
        icon: Boxes,
        permission: PERMISSIONS.INVENTORY_READ,
        matchPrefix: true,
      },
    ],
  },
  {
    heading: "Administration",
    items: [
      {
        label: "Users",
        href: "/admin/users",
        icon: Users,
        permission: PERMISSIONS.USERS_MANAGE,
      },
      {
        label: "Roles",
        href: "/admin/roles",
        icon: ShieldCheck,
        permission: PERMISSIONS.ROLES_MANAGE,
      },
      {
        label: "Lookups",
        href: "/admin/inventory",
        icon: Boxes,
        permission: PERMISSIONS.INVENTORY_MANAGE,
      },
    ],
  },
];
