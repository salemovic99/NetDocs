"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Network } from "lucide-react";

import { cn } from "@/lib/utils";
import { usePermissions } from "@/lib/auth/session-context";
import { NAV } from "./nav-items";

function isActive(pathname: string, href: string, prefix?: boolean) {
  if (href === "/") return pathname === "/";
  return prefix ? pathname.startsWith(href) : pathname === href;
}

export function SidebarNav({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  const { can, permissions } = usePermissions();

  return (
    <nav className="flex flex-1 flex-col gap-6 overflow-y-auto px-3 py-4">
      {NAV.map((section, i) => {
        const items = section.items.filter(
          (item) => !item.permission || can(item.permission),
        );
        if (!items.length) return null;
        return (
          <div key={i} className="space-y-1">
            {section.heading ? (
              <p className="px-2 pb-1 text-label-caps text-on-surface-variant/70">
                {section.heading}
              </p>
            ) : null}
            {items.map((item) => {
              const active = isActive(pathname, item.href, item.matchPrefix);
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={onNavigate}
                  className={cn(
                    "flex items-center gap-3 rounded-md px-2.5 py-2 text-h4 transition-colors",
                    active
                      ? "bg-primary-container/15 text-primary"
                      : "text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface",
                  )}
                >
                  <Icon className="size-4 shrink-0" />
                  {item.label}
                </Link>
              );
            })}
          </div>
        );
      })}
      {/* keep `permissions` referenced for clarity / future use */}
      <span className="sr-only">{permissions.length} permissions</span>
    </nav>
  );
}

export function AppSidebar() {
  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r border-sidebar-border bg-sidebar lg:flex">
      <div className="flex h-14 items-center gap-2 border-b border-sidebar-border px-4">
        <div className="flex size-7 items-center justify-center rounded-md bg-primary-container text-primary-foreground">
          <Network className="size-4" />
        </div>
        <span className="text-h3 text-on-surface">NetDocs</span>
      </div>
      <SidebarNav />
    </aside>
  );
}
