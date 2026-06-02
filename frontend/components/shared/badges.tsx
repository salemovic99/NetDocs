import { Badge } from "@/components/ui/badge";
import type {
  DeviceStatus,
  ProblemStatus,
  Severity,
} from "@/lib/api/types";

const severityMap: Record<Severity, { label: string; variant: "default" | "primary" | "warning" | "destructive" }> = {
  low: { label: "Low", variant: "default" },
  medium: { label: "Medium", variant: "primary" },
  high: { label: "High", variant: "warning" },
  critical: { label: "Critical", variant: "destructive" },
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  const m = severityMap[severity];
  return (
    <Badge variant={m.variant} dot>
      {m.label}
    </Badge>
  );
}

const statusMap: Record<
  ProblemStatus,
  { label: string; variant: "warning" | "success" | "default" }
> = {
  open: { label: "Open", variant: "warning" },
  resolved: { label: "Resolved", variant: "success" },
  known_issue: { label: "Known issue", variant: "default" },
};

export function ProblemStatusBadge({ status }: { status: ProblemStatus }) {
  const m = statusMap[status];
  return (
    <Badge variant={m.variant} dot>
      {m.label}
    </Badge>
  );
}

const deviceStatusMap: Record<
  DeviceStatus,
  { label: string; variant: "success" | "default" | "destructive" }
> = {
  active: { label: "Active", variant: "success" },
  spare: { label: "Spare", variant: "default" },
  retired: { label: "Retired", variant: "destructive" },
};

export function DeviceStatusBadge({ status }: { status: DeviceStatus }) {
  const m = deviceStatusMap[status] ?? deviceStatusMap.active;
  return (
    <Badge variant={m.variant} dot>
      {m.label}
    </Badge>
  );
}

export function AvStatusBadge({ status }: { status: string }) {
  const map: Record<string, "success" | "warning" | "destructive"> = {
    clean: "success",
    pending: "warning",
    infected: "destructive",
  };
  return <Badge variant={map[status] ?? "default"}>{status}</Badge>;
}
