/**
 * Mirror of the backend permission catalog (app/core/permissions.py).
 * UI gating only — the server is always authoritative.
 */
export const PERMISSIONS = {
  PROBLEMS_READ: "problems.read",
  PROBLEMS_WRITE: "problems.write",
  PROBLEMS_DELETE: "problems.delete",
  INVENTORY_READ: "inventory.read",
  INVENTORY_MANAGE: "inventory.manage",
  ATTACHMENTS_UPLOAD: "attachments.upload",
  ATTACHMENTS_DOWNLOAD: "attachments.download",
  TAGS_MANAGE: "tags.manage",
  USERS_MANAGE: "users.manage",
  ROLES_MANAGE: "roles.manage",
  AUDIT_READ: "audit.read",
} as const;

export type PermissionCode = (typeof PERMISSIONS)[keyof typeof PERMISSIONS];

/** True if the effective permission set includes `code`. */
export function can(permissions: string[], code: PermissionCode): boolean {
  return permissions.includes(code);
}

export function canAny(permissions: string[], codes: PermissionCode[]): boolean {
  return codes.some((c) => permissions.includes(c));
}
