"""Import all models so Base.metadata is fully populated (Alembic autogenerate)."""

from app.models.attachment import Attachment
from app.models.audit_log import AuditLog
from app.models.base import Base
from app.models.device import Device, Vlan
from app.models.inventory import DeviceType, Rack, Vendor
from app.models.network import IspLink, WirelessNetwork
from app.models.problem import (
    Problem,
    ProblemCategory,
    Tag,
    problem_devices,
    problem_relations,
    problem_tags,
)
from app.models.site import Room, Site
from app.models.user import (
    Permission,
    Role,
    User,
    role_permissions,
    user_roles,
)

__all__ = [
    "Attachment",
    "AuditLog",
    "Base",
    "Device",
    "DeviceType",
    "IspLink",
    "Permission",
    "Problem",
    "ProblemCategory",
    "Rack",
    "Role",
    "Room",
    "Site",
    "Tag",
    "User",
    "Vendor",
    "Vlan",
    "WirelessNetwork",
    "problem_devices",
    "problem_relations",
    "problem_tags",
    "role_permissions",
    "user_roles",
]
