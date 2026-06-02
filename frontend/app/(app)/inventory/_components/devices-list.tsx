"use client";

import * as React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Plus, Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DeviceStatusBadge } from "@/components/shared/badges";
import { EmptyState } from "@/components/shared/empty-state";
import { Pagination } from "@/components/shared/pagination";
import { usePermissions } from "@/lib/auth/session-context";
import { useDevices } from "@/lib/hooks/use-devices";
import { useUrlFilters } from "@/lib/hooks/use-url-filters";
import { PERMISSIONS } from "@/lib/permissions";
import { fadeUpItem, staggerContainer } from "@/lib/motion/variants";
import { DeviceForm } from "./device-form";

const PAGE_SIZE = 25;
const ALL = "__all__";

export function DevicesList() {
  const { get, setMany, page } = useUrlFilters();
  const { can } = usePermissions();
  const [createOpen, setCreateOpen] = React.useState(false);
  const [q, setQ] = React.useState(get("q"));

  React.useEffect(() => {
    const t = setTimeout(() => {
      if (q !== get("q")) setMany({ q });
    }, 350);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q]);

  const { data, isLoading } = useDevices({
    page,
    page_size: PAGE_SIZE,
    q: get("q") || undefined,
    status: get("status") || undefined,
  });

  return (
    <Card>
      <CardContent className="space-y-4 pt-6">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-56 flex-1">
            <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-on-surface-variant/60" />
            <Input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search hostname, IP, serial, asset tag…"
              className="pl-9"
            />
          </div>
          <Select
            value={get("status") || ALL}
            onValueChange={(v) => setMany({ status: v === ALL ? "" : v })}
          >
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={ALL}>All statuses</SelectItem>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="spare">Spare</SelectItem>
              <SelectItem value="retired">Retired</SelectItem>
            </SelectContent>
          </Select>
          {can(PERMISSIONS.INVENTORY_MANAGE) ? (
            <Dialog open={createOpen} onOpenChange={setCreateOpen}>
              <Button onClick={() => setCreateOpen(true)}>
                <Plus /> New device
              </Button>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>New device</DialogTitle>
                </DialogHeader>
                <DeviceForm onDone={() => setCreateOpen(false)} />
              </DialogContent>
            </Dialog>
          ) : null}
        </div>

        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 8 }).map((_, i) => (
              <Skeleton key={i} className="h-9 w-full" />
            ))}
          </div>
        ) : !data?.items.length ? (
          <EmptyState
            title="No devices found"
            description="Add a device to start building your inventory."
          />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Hostname</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Vendor</TableHead>
                <TableHead>Site</TableHead>
                <TableHead>Mgmt IP</TableHead>
                <TableHead className="w-28">Status</TableHead>
              </TableRow>
            </TableHeader>
            <motion.tbody
              variants={staggerContainer}
              initial="hidden"
              animate="visible"
            >
              {data.items.map((d) => (
                <motion.tr
                  key={d.id}
                  variants={fadeUpItem}
                  className="border-b border-border/60 odd:bg-surface-container/40 hover:bg-surface-container-high"
                >
                  <TableCell>
                    <Link
                      href={`/inventory/${d.id}`}
                      className="text-on-surface hover:text-primary"
                    >
                      {d.hostname}
                    </Link>
                  </TableCell>
                  <TableCell className="text-on-surface-variant">
                    {d.device_type?.name ?? "—"}
                  </TableCell>
                  <TableCell className="text-on-surface-variant">
                    {d.vendor?.name ?? "—"}
                  </TableCell>
                  <TableCell className="text-on-surface-variant">
                    {d.site?.name ?? "—"}
                  </TableCell>
                  <TableCell className="text-mono text-on-surface-variant">
                    {d.management_ip ?? "—"}
                  </TableCell>
                  <TableCell>
                    <DeviceStatusBadge status={d.status} />
                  </TableCell>
                </motion.tr>
              ))}
            </motion.tbody>
          </Table>
        )}

        {data ? (
          <Pagination
            page={page}
            pageSize={PAGE_SIZE}
            total={data.total}
            onPageChange={(p) => setMany({ page: p })}
          />
        ) : null}
      </CardContent>
    </Card>
  );
}
