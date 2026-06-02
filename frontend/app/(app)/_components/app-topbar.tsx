"use client";

import * as React from "react";
import { Menu, Network, Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { SidebarNav } from "./app-sidebar";
import { CommandPalette } from "./command-palette";
import { UserMenu } from "./user-menu";

export function AppTopbar() {
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const [paletteOpen, setPaletteOpen] = React.useState(false);

  React.useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setPaletteOpen((v) => !v);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-border bg-surface/80 px-4 backdrop-blur">
      {/* Mobile nav */}
      <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
        <SheetTrigger asChild>
          <Button variant="ghost" size="icon" className="lg:hidden">
            <Menu />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-64 p-0">
          <SheetTitle className="flex h-14 items-center gap-2 border-b border-border px-4">
            <div className="flex size-7 items-center justify-center rounded-md bg-primary-container text-primary-foreground">
              <Network className="size-4" />
            </div>
            NetDocs
          </SheetTitle>
          <SidebarNav onNavigate={() => setMobileOpen(false)} />
        </SheetContent>
      </Sheet>

      {/* Command trigger */}
      <button
        onClick={() => setPaletteOpen(true)}
        className="group flex h-9 w-full max-w-sm items-center gap-2 rounded-md border border-input bg-surface-container-low px-3 text-body-sm text-on-surface-variant/70 transition-colors hover:border-ring"
      >
        <Search className="size-4" />
        <span className="flex-1 text-left">Search or jump to…</span>
        <kbd className="rounded border border-border bg-surface-container px-1.5 py-0.5 text-mono text-on-surface-variant">
          ⌘K
        </kbd>
      </button>

      <div className="ml-auto">
        <UserMenu />
      </div>

      <CommandPalette open={paletteOpen} onOpenChange={setPaletteOpen} />
    </header>
  );
}
