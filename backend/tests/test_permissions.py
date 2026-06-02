"""Unit tests for the permission catalog and effective-permission union."""

from app.core import permissions as perms
from app.models.user import Permission, Role, User


def test_network_admin_has_all_permissions():
    granted = set(perms.SYSTEM_ROLES["Network Admin"]["permissions"])
    assert granted == set(perms.PERMISSION_CATALOG.keys())


def test_viewer_is_read_only():
    granted = set(perms.SYSTEM_ROLES["Viewer"]["permissions"])
    assert perms.PROBLEMS_WRITE not in granted
    assert perms.PROBLEMS_DELETE not in granted
    assert perms.INVENTORY_MANAGE not in granted
    assert perms.PROBLEMS_READ in granted
    assert perms.ATTACHMENTS_DOWNLOAD in granted


def test_helpdesk_cannot_delete_or_manage_inventory():
    granted = set(perms.SYSTEM_ROLES["Helpdesk"]["permissions"])
    assert perms.PROBLEMS_WRITE in granted
    assert perms.PROBLEMS_DELETE not in granted
    assert perms.INVENTORY_MANAGE not in granted


def test_effective_permissions_is_union_across_roles():
    p_read = Permission(code=perms.PROBLEMS_READ)
    p_write = Permission(code=perms.PROBLEMS_WRITE)
    p_inv = Permission(code=perms.INVENTORY_MANAGE)
    role_a = Role(name="A", permissions=[p_read, p_write])
    role_b = Role(name="B", permissions=[p_write, p_inv])
    user = User(email="a@b.c", username="ab", password_hash="x", roles=[role_a, role_b])
    assert user.effective_permissions == {
        perms.PROBLEMS_READ,
        perms.PROBLEMS_WRITE,
        perms.INVENTORY_MANAGE,
    }
