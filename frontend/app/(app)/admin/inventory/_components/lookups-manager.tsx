"use client";

import * as React from "react";
import { Plus, Trash2 } from "lucide-react";
import type { UseQueryResult } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { EmptyState } from "@/components/shared/empty-state";
import {
  useCategories,
  useDeviceTypes,
  useLookupMutations,
  useRacks,
  useTags,
  useVendors,
} from "@/lib/hooks/use-lookups";
import type { Page } from "@/lib/api/types";

interface LookupConfig {
  key: string;
  label: string;
  resource: string;
  useList: () => UseQueryResult<Page<{ id: string; name: string }>>;
}

const LOOKUPS: LookupConfig[] = [
  { key: "device-types", label: "Device types", resource: "device-types", useList: useDeviceTypes },
  { key: "vendors", label: "Vendors", resource: "vendors", useList: useVendors },
  { key: "racks", label: "Racks", resource: "racks", useList: useRacks },
  { key: "tags", label: "Tags", resource: "tags", useList: useTags },
  {
    key: "categories",
    label: "Categories",
    resource: "problem-categories",
    useList: useCategories,
  },
];

export function LookupsManager() {
  return (
    <Tabs defaultValue="device-types">
      <TabsList className="flex-wrap">
        {LOOKUPS.map((l) => (
          <TabsTrigger key={l.key} value={l.key}>
            {l.label}
          </TabsTrigger>
        ))}
      </TabsList>
      {LOOKUPS.map((l) => (
        <TabsContent key={l.key} value={l.key}>
          <LookupPanel config={l} />
        </TabsContent>
      ))}
    </Tabs>
  );
}

function LookupPanel({ config }: { config: LookupConfig }) {
  const list = config.useList();
  const { create, remove } = useLookupMutations(config.resource, config.key);
  const [name, setName] = React.useState("");

  const add = () => {
    if (!name.trim()) return;
    create.mutate({ name: name.trim() });
    setName("");
  };

  return (
    <Card>
      <CardContent className="space-y-4 pt-6">
        <div className="flex gap-2">
          <Input
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && add()}
            placeholder={`New ${config.label.toLowerCase().replace(/s$/, "")}…`}
            className="max-w-xs"
          />
          <Button onClick={add} disabled={!name.trim()}>
            <Plus /> Add
          </Button>
        </div>

        {list.isLoading ? (
          <Skeleton className="h-32 w-full" />
        ) : !list.data?.items.length ? (
          <EmptyState title={`No ${config.label.toLowerCase()}`} />
        ) : (
          <div className="flex flex-wrap gap-2">
            {list.data.items.map((item) => (
              <div
                key={item.id}
                className="flex items-center gap-2 rounded-md border border-border bg-surface-container-low py-1 pl-3 pr-1 text-body-lg text-on-surface"
              >
                {item.name}
                <ConfirmDialog
                  trigger={
                    <Button variant="ghost" size="icon-sm">
                      <Trash2 className="size-3.5 text-error" />
                    </Button>
                  }
                  title={`Delete "${item.name}"?`}
                  confirmLabel="Delete"
                  onConfirm={() => remove.mutate(item.id)}
                />
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
