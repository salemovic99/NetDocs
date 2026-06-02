"""Unit tests for schema validation (IP/MAC/VLAN/severity) and helpers."""

from datetime import UTC

import pytest
from pydantic import ValidationError

from app.core.concurrency import check_etag, make_etag
from app.core.exceptions import ConflictError
from app.core.pagination import Page, PageParams
from app.schemas.device import DeviceCreate, VlanCreate
from app.schemas.problem import ProblemCreate


def test_device_rejects_bad_ip_and_mac():
    with pytest.raises(ValidationError):
        DeviceCreate(hostname="sw1", management_ip="999.1.1.1")
    with pytest.raises(ValidationError):
        DeviceCreate(hostname="sw1", mac_address="zz:zz")


def test_device_accepts_valid_ip_and_mac():
    d = DeviceCreate(
        hostname="sw1", management_ip="10.0.0.1", mac_address="aa:bb:cc:dd:ee:ff"
    )
    assert d.hostname == "sw1"


def test_device_status_validated():
    with pytest.raises(ValidationError):
        DeviceCreate(hostname="x", status="banana")


def test_vlan_tag_range():
    with pytest.raises(ValidationError):
        VlanCreate(vlan_id=5000)
    VlanCreate(vlan_id=10, subnet="10.0.0.0/24", gateway="10.0.0.1")


def test_problem_severity_and_status_validated():
    with pytest.raises(ValidationError):
        ProblemCreate(title="t", severity="catastrophic")
    with pytest.raises(ValidationError):
        ProblemCreate(title="t", status="closed")
    ProblemCreate(title="t", severity="high", status="known_issue")


def test_pagination_offsets():
    p = PageParams(page=3, page_size=25)
    assert p.offset == 50
    assert p.limit == 25
    page = Page.create(items=[1, 2], total=99, params=p)
    assert page.total == 99 and page.page == 3 and page.items == [1, 2]


def test_etag_concurrency():
    from datetime import datetime

    ts = datetime(2026, 6, 2, tzinfo=UTC)
    etag = make_etag(ts)
    check_etag(ts, etag)  # matching -> ok
    check_etag(ts, None)  # missing header -> skipped
    with pytest.raises(ConflictError):
        check_etag(ts, '"stale"')
