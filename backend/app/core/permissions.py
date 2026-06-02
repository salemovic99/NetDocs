"""Canonical permission catalog and built-in role grants (PRD §6.6, §10 legend).

Authorization is permission-based: a user's effective permissions are the union
of permissions across all roles assigned to them. These constants drive both the
runtime checks (`require_permission`) and the first-run seed.
"""

# --- Permission codes (the catalog) ---
PROBLEMS_READ = "problems.read"
PROBLEMS_WRITE = "problems.write"
PROBLEMS_DELETE = "problems.delete"
INVENTORY_READ = "inventory.read"
INVENTORY_MANAGE = "inventory.manage"
ATTACHMENTS_UPLOAD = "attachments.upload"
ATTACHMENTS_DOWNLOAD = "attachments.download"
TAGS_MANAGE = "tags.manage"
USERS_MANAGE = "users.manage"
ROLES_MANAGE = "roles.manage"
AUDIT_READ = "audit.read"

PERMISSION_CATALOG: dict[str, str] = {
    PROBLEMS_READ: "Read and search problem entries",
    PROBLEMS_WRITE: "Create and edit problem entries",
    PROBLEMS_DELETE: "Archive (soft-delete) problem entries",
    INVENTORY_READ: "Read and search network inventory",
    INVENTORY_MANAGE: "Manage devices, VLANs, ISP/WAN, wireless, sites, racks, lookups",
    ATTACHMENTS_UPLOAD: "Upload attachments",
    ATTACHMENTS_DOWNLOAD: "Download attachments",
    TAGS_MANAGE: "Manage tags and problem categories",
    USERS_MANAGE: "Manage users and role assignments",
    ROLES_MANAGE: "Create and edit roles and their permissions",
    AUDIT_READ: "Read the audit log",
}

# --- Built-in roles and their default permission grants (the §6.6 seed matrix) ---
SYSTEM_ROLES: dict[str, dict[str, object]] = {
    "Network Admin": {
        "description": "Superuser: full content plus user/role administration.",
        "permissions": list(PERMISSION_CATALOG.keys()),  # all
    },
    "SysAdmin": {
        "description": "Full content and inventory rights; no user administration.",
        "permissions": [
            PROBLEMS_READ,
            PROBLEMS_WRITE,
            PROBLEMS_DELETE,
            INVENTORY_READ,
            INVENTORY_MANAGE,
            ATTACHMENTS_UPLOAD,
            ATTACHMENTS_DOWNLOAD,
            TAGS_MANAGE,
            AUDIT_READ,
        ],
    },
    "Security Analyst": {
        "description": "Documents and edits problems; no inventory or user management.",
        "permissions": [
            PROBLEMS_READ,
            PROBLEMS_WRITE,
            PROBLEMS_DELETE,
            INVENTORY_READ,
            ATTACHMENTS_UPLOAD,
            ATTACHMENTS_DOWNLOAD,
            TAGS_MANAGE,
            AUDIT_READ,
        ],
    },
    "Helpdesk": {
        "description": "Captures and edits problems; cannot delete or manage inventory.",
        "permissions": [
            PROBLEMS_READ,
            PROBLEMS_WRITE,
            INVENTORY_READ,
            ATTACHMENTS_UPLOAD,
            ATTACHMENTS_DOWNLOAD,
        ],
    },
    "Viewer": {
        "description": "Read-only access to problems and inventory.",
        "permissions": [
            PROBLEMS_READ,
            INVENTORY_READ,
            ATTACHMENTS_DOWNLOAD,
        ],
    },
}
