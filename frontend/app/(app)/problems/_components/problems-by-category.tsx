"use client";

import * as React from "react";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown, FolderOpen, Inbox, Search } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { ProblemStatusBadge, SeverityBadge } from "@/components/shared/badges";
import { useProblems } from "@/lib/hooks/use-problems";
import { useCategories } from "@/lib/hooks/use-lookups";
import { fadeUpItem, staggerContainer } from "@/lib/motion/variants";
import { cn } from "@/lib/utils";
import type { Problem } from "@/lib/api/types";

const UNCATEGORIZED = "__uncategorized__";

type Group = {
  id: string;
  name: string;
  problems: Problem[];
};

export function ProblemsByCategory() {
  const categories = useCategories();
  const { data, isLoading } = useProblems({ page_size: 200 });
  const [query, setQuery] = React.useState("");
  const [open, setOpen] = React.useState<Set<string>>(() => new Set());

  const q = query.trim().toLowerCase();

  // Group problems by their category, keeping category order from the lookup.
  const groups = React.useMemo<Group[]>(() => {
    const problems = data?.items ?? [];
    const matches = (p: Problem) =>
      !q ||
      p.title.toLowerCase().includes(q) ||
      (p.symptoms ?? "").toLowerCase().includes(q) ||
      (p.root_cause ?? "").toLowerCase().includes(q);

    const filtered = problems.filter(matches);
    const byCategory = new Map<string, Problem[]>();
    for (const p of filtered) {
      const key = p.category?.id ?? UNCATEGORIZED;
      const bucket = byCategory.get(key);
      if (bucket) bucket.push(p);
      else byCategory.set(key, [p]);
    }

    const out: Group[] = [];
    for (const c of categories.data?.items ?? []) {
      const items = byCategory.get(c.id);
      if (items?.length) out.push({ id: c.id, name: c.name, problems: items });
    }
    const orphans = byCategory.get(UNCATEGORIZED);
    if (orphans?.length) {
      out.push({ id: UNCATEGORIZED, name: "Uncategorized", problems: orphans });
    }
    return out;
  }, [data, categories.data, q]);

  // When searching, every matching category is expanded so results are visible.
  const isOpen = (id: string) => (q ? true : open.has(id));
  const toggle = (id: string) =>
    setOpen((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  return (
    <div className="space-y-4">
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-on-surface-variant/60" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search problems across all categories…"
          className="pl-9"
        />
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      ) : !groups.length ? (
        <EmptyState
          icon={<Inbox className="size-5" />}
          title={q ? "No matching problems" : "No problems yet"}
          description={
            q
              ? "Try a different search term."
              : "Create a new problem to get started."
          }
        />
      ) : (
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="grid items-start gap-4 sm:grid-cols-2"
        >
          {groups.map((g) => (
            <CategoryCard
              key={g.id}
              group={g}
              open={isOpen(g.id)}
              onToggle={() => toggle(g.id)}
            />
          ))}
        </motion.div>
      )}
    </div>
  );
}

function CategoryCard({
  group,
  open,
  onToggle,
}: {
  group: Group;
  open: boolean;
  onToggle: () => void;
}) {
  return (
    <motion.div variants={fadeUpItem}>
      <Card className="overflow-hidden">
        <button
          type="button"
          onClick={onToggle}
          aria-expanded={open}
          className="flex w-full items-center gap-3 p-4 text-left transition-colors hover:bg-surface-container-high"
        >
          <FolderOpen className="size-5 shrink-0 text-primary" />
          <span className="flex-1 truncate text-h4 text-on-surface">
            {group.name}
          </span>
          <Badge variant="outline">{group.problems.length}</Badge>
          <ChevronDown
            className={cn(
              "size-4 shrink-0 text-on-surface-variant transition-transform duration-200",
              open && "rotate-180",
            )}
          />
        </button>

        <AnimatePresence initial={false}>
          {open ? (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
              className="overflow-hidden"
            >
              <ul className="border-t border-border/60">
                {group.problems.map((p) => (
                  <li
                    key={p.id}
                    className="border-b border-border/60 last:border-b-0"
                  >
                    <Link
                      href={`/problems/${p.id}`}
                      className="flex items-center gap-3 px-4 py-2.5 transition-colors hover:bg-surface-container/60"
                    >
                      <span className="flex-1 truncate text-body-lg text-on-surface hover:text-primary">
                        {p.title}
                      </span>
                      <SeverityBadge severity={p.severity} />
                      <ProblemStatusBadge status={p.status} />
                    </Link>
                  </li>
                ))}
              </ul>
            </motion.div>
          ) : null}
        </AnimatePresence>
      </Card>
    </motion.div>
  );
}
