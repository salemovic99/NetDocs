"use client";

import * as React from "react";
import { useRouter } from "next/navigation";

import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { usePermissions } from "@/lib/auth/session-context";
import { NAV } from "./nav-items";

export function CommandPalette({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const router = useRouter();
  const { can } = usePermissions();
  const [query, setQuery] = React.useState("");

  const go = (href: string) => {
    onOpenChange(false);
    router.push(href);
  };

  const items = NAV.flatMap((s) => s.items).filter(
    (i) => !i.permission || can(i.permission),
  );

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput
        placeholder="Jump to a page or search problems…"
        value={query}
        onValueChange={setQuery}
      />
      <CommandList>
        <CommandEmpty>No results.</CommandEmpty>
        {query.trim() && can("problems.read") ? (
          <CommandGroup heading="Search">
            <CommandItem
              onSelect={() =>
                go(`/search?q=${encodeURIComponent(query.trim())}`)
              }
            >
              Search for “{query.trim()}”
            </CommandItem>
          </CommandGroup>
        ) : null}
        <CommandGroup heading="Navigate">
          {items.map((item) => {
            const Icon = item.icon;
            return (
              <CommandItem
                key={item.href}
                value={item.label}
                onSelect={() => go(item.href)}
              >
                <Icon />
                {item.label}
              </CommandItem>
            );
          })}
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
