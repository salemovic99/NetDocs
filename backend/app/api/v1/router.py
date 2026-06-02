"""Aggregates all v1 route modules under /api/v1."""

from fastapi import APIRouter

from app.api.v1.routes import (
    attachments,
    audit,
    auth,
    devices,
    lookups,
    network,
    problems,
    roles,
    sites,
    users,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(problems.router)
api_router.include_router(devices.router)
api_router.include_router(attachments.router)
api_router.include_router(sites.router)
api_router.include_router(network.router)
api_router.include_router(lookups.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(audit.router)
