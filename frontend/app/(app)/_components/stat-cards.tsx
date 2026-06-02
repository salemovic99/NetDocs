"use client";

import { motion } from "framer-motion";
import {
  CircleAlert,
  CircleCheck,
  Server,
  TriangleAlert,
} from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useProblems } from "@/lib/hooks/use-problems";
import { useDevices } from "@/lib/hooks/use-devices";
import { fadeUpItem, staggerContainer } from "@/lib/motion/variants";

function useCount(params: Record<string, string | number>) {
  const { data, isLoading } = useProblems({ ...params, page_size: 1 });
  return { count: data?.total ?? 0, isLoading };
}

function StatCard({
  label,
  value,
  icon,
  accent,
  loading,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
  accent: string;
  loading: boolean;
}) {
  return (
    <motion.div variants={fadeUpItem}>
      <Card>
        <CardContent className="flex items-center justify-between gap-4 pt-6">
          <div className="space-y-1">
            <p className="text-label-caps text-on-surface-variant">{label}</p>
            {loading ? (
              <Skeleton className="h-7 w-12" />
            ) : (
              <p className="text-h1 text-on-surface">{value}</p>
            )}
          </div>
          <div
            className={`flex size-10 items-center justify-center rounded-md ${accent}`}
          >
            {icon}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

export function StatCards() {
  const open = useCount({ status: "open" });
  const critical = useCount({ severity: "critical" });
  const resolved = useCount({ status: "resolved" });
  const devices = useDevices({ page_size: 1 });

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
    >
      <StatCard
        label="Open problems"
        value={open.count}
        loading={open.isLoading}
        icon={<TriangleAlert className="size-5 text-warning" />}
        accent="bg-warning/15"
      />
      <StatCard
        label="Critical severity"
        value={critical.count}
        loading={critical.isLoading}
        icon={<CircleAlert className="size-5 text-error" />}
        accent="bg-destructive/15"
      />
      <StatCard
        label="Resolved"
        value={resolved.count}
        loading={resolved.isLoading}
        icon={<CircleCheck className="size-5 text-success" />}
        accent="bg-success/15"
      />
      <StatCard
        label="Devices"
        value={devices.data?.total ?? 0}
        loading={devices.isLoading}
        icon={<Server className="size-5 text-primary" />}
        accent="bg-primary-container/15"
      />
    </motion.div>
  );
}
