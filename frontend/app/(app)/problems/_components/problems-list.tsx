"use client";

import * as React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Search } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
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
import { EmptyState } from "@/components/shared/empty-state";
import { Pagination } from "@/components/shared/pagination";
import { ProblemStatusBadge, SeverityBadge } from "@/components/shared/badges";
import { useProblems } from "@/lib/hooks/use-problems";
import { useCategories } from "@/lib/hooks/use-lookups";
import { useUrlFilters } from "@/lib/hooks/use-url-filters";
import { fadeUpItem, staggerContainer } from "@/lib/motion/variants";

const PAGE_SIZE = 25;
const ALL = "__all__";

export function ProblemsList() {
  const { get, setMany, page } = useUrlFilters();
  const categories = useCategories();

  // Debounce the free-text search.
  const [q, setQ] = React.useState(get("q"));
  React.useEffect(() => {
    const t = setTimeout(() => {
      if (q !== get("q")) setMany({ q });
    }, 350);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q]);

  const { data, isLoading } = useProblems({
    page,
    page_size: PAGE_SIZE,
    q: get("q") || undefined,
    severity: get("severity") || undefined,
    status: get("status") || undefined,
    category: get("category") || undefined,
  });

  return (
    <Card>
      <CardContent className="space-y-4 pt-6">
        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-56 flex-1">
            <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-on-surface-variant/60" />
            <Input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search title, symptoms, root cause…"
              className="pl-9"
            />
          </div>
          <FilterSelect
            value={get("severity") || ALL}
            placeholder="Severity"
            onChange={(v) => setMany({ severity: v === ALL ? "" : v })}
            options={[
              { value: "low", label: "Low" },
              { value: "medium", label: "Medium" },
              { value: "high", label: "High" },
              { value: "critical", label: "Critical" },
            ]}
          />
          <FilterSelect
            value={get("status") || ALL}
            placeholder="Status"
            onChange={(v) => setMany({ status: v === ALL ? "" : v })}
            options={[
              { value: "open", label: "Open" },
              { value: "resolved", label: "Resolved" },
              { value: "known_issue", label: "Known issue" },
            ]}
          />
          <FilterSelect
            value={get("category") || ALL}
            placeholder="Category"
            onChange={(v) => setMany({ category: v === ALL ? "" : v })}
            options={(categories.data?.items ?? []).map((c) => ({
              value: c.id,
              label: c.name,
            }))}
          />
        </div>

        {/* Table */}
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 8 }).map((_, i) => (
              <Skeleton key={i} className="h-9 w-full" />
            ))}
          </div>
        ) : !data?.items.length ? (
          <EmptyState
            title="No problems found"
            description="Try adjusting your filters, or create a new problem."
          />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead className="w-28">Severity</TableHead>
                <TableHead className="w-32">Status</TableHead>
                <TableHead className="w-40">Category</TableHead>
                <TableHead className="w-28">Devices</TableHead>
              </TableRow>
            </TableHeader>
            <motion.tbody
              variants={staggerContainer}
              initial="hidden"
              animate="visible"
            >
              {data.items.map((p) => (
                <motion.tr
                  key={p.id}
                  variants={fadeUpItem}
                  className="border-b border-border/60 transition-colors odd:bg-surface-container/40 hover:bg-surface-container-high"
                >
                  <TableCell>
                    <Link
                      href={`/problems/${p.id}`}
                      className="text-on-surface hover:text-primary"
                    >
                      {p.title}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <SeverityBadge severity={p.severity} />
                  </TableCell>
                  <TableCell>
                    <ProblemStatusBadge status={p.status} />
                  </TableCell>
                  <TableCell className="text-on-surface-variant">
                    {p.category?.name ?? "—"}
                  </TableCell>
                  <TableCell className="text-mono text-on-surface-variant">
                    {p.devices.length}
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

function FilterSelect({
  value,
  placeholder,
  onChange,
  options,
}: {
  value: string;
  placeholder: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="w-44">
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value={ALL}>All {placeholder.toLowerCase()}</SelectItem>
        {options.map((o) => (
          <SelectItem key={o.value} value={o.value}>
            {o.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
