"use client";

import * as React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { MapPin, Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { EmptyState } from "@/components/shared/empty-state";
import { usePermissions } from "@/lib/auth/session-context";
import { useSites } from "@/lib/hooks/use-sites";
import { PERMISSIONS } from "@/lib/permissions";
import { fadeUpItem, staggerContainer } from "@/lib/motion/variants";
import { SiteFormDialog } from "./site-form-dialog";

export function SitesList() {
  const { can } = usePermissions();
  const { data, isLoading } = useSites({ page_size: 100, sort: "name" });
  const [open, setOpen] = React.useState(false);

  return (
    <Card>
      <CardContent className="space-y-4 pt-6">
        {can(PERMISSIONS.INVENTORY_MANAGE) ? (
          <div className="flex justify-end">
            <Button onClick={() => setOpen(true)}>
              <Plus /> New site
            </Button>
          </div>
        ) : null}

        {isLoading ? (
          <Skeleton className="h-40 w-full" />
        ) : !data?.items.length ? (
          <EmptyState title="No sites" description="Add your first site." />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>City</TableHead>
                <TableHead>Country</TableHead>
                <TableHead>Timezone</TableHead>
              </TableRow>
            </TableHeader>
            <motion.tbody
              variants={staggerContainer}
              initial="hidden"
              animate="visible"
            >
              {data.items.map((s) => (
                <motion.tr
                  key={s.id}
                  variants={fadeUpItem}
                  className="border-b border-border/60 odd:bg-surface-container/40 hover:bg-surface-container-high"
                >
                  <TableCell>
                    <Link
                      href={`/sites/${s.id}`}
                      className="flex items-center gap-2 text-on-surface hover:text-primary"
                    >
                      <MapPin className="size-4 text-on-surface-variant" />
                      {s.name}
                    </Link>
                  </TableCell>
                  <TableCell className="text-on-surface-variant">
                    {s.city ?? "—"}
                  </TableCell>
                  <TableCell className="text-on-surface-variant">
                    {s.country ?? "—"}
                  </TableCell>
                  <TableCell className="text-mono text-on-surface-variant">
                    {s.timezone ?? "—"}
                  </TableCell>
                </motion.tr>
              ))}
            </motion.tbody>
          </Table>
        )}
      </CardContent>

      {can(PERMISSIONS.INVENTORY_MANAGE) ? (
        <SiteFormDialog open={open} onOpenChange={setOpen} />
      ) : null}
    </Card>
  );
}
