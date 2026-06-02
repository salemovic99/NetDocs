"use client";

import * as React from "react";

import { can, canAny, type PermissionCode } from "@/lib/permissions";
import type { Session } from "@/lib/auth/session";

const SessionContext = React.createContext<Session | null>(null);

export function SessionProvider({
  session,
  children,
}: {
  session: Session;
  children: React.ReactNode;
}) {
  return (
    <SessionContext.Provider value={session}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession(): Session {
  const ctx = React.useContext(SessionContext);
  if (!ctx) throw new Error("useSession must be used within SessionProvider");
  return ctx;
}

/** Permission helpers bound to the current session. */
export function usePermissions() {
  const { permissions } = useSession();
  return {
    permissions,
    can: (code: PermissionCode) => can(permissions, code),
    canAny: (codes: PermissionCode[]) => canAny(permissions, codes),
  };
}
