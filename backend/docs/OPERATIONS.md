# NetDocs — Operations Runbook

Backup, restore, disaster recovery, and observability for the self-hosted stack (PRD §13–§14).

## Observability

- **Liveness:** `GET /healthz` → `200 {"status":"ok"}` (process up).
- **Readiness:** `GET /readyz` → checks DB reachable, Redis reachable, and **migrations current**
  (`alembic` head matches the DB). Returns `degraded` if any check fails — wire it to the reverse
  proxy / orchestrator so traffic only routes to ready instances.
- **Metrics:** `GET /metrics` → Prometheus exposition (`netdocs_http_requests_total`,
  `netdocs_http_request_duration_seconds`). Scrape with Prometheus; restrict network access in prod.
- **Logs:** structured JSON with `request_id`, route, latency, status (`app/core/logging.py`).
- **Audit log:** every write + auth event in `audit_log`, surfaced at `GET /api/v1/audit-log`
  (`audit.read`).

## Backup (RPO ≤ 24h)

`scripts/backup.sh` runs `pg_dump` (custom format) and tars the attachments volume, then prunes to
a 30-copy retention. Schedule nightly via cron:

```cron
0 2 * * *  DATABASE_URL=... UPLOAD_DIR=/data/attachments BACKUP_DIR=/backups \
           GPG_RECIPIENT=ops@example.com /app/scripts/backup.sh >> /var/log/netdocs-backup.log 2>&1
```

- Set `GPG_RECIPIENT` to encrypt artifacts at rest.
- Copy `/backups` off-host (object storage / second volume) so at least one copy survives host loss.
- For tighter RPO, additionally enable **WAL archiving / PITR** on PostgreSQL
  (`archive_mode=on`, `archive_command=...`) and base-backups via `pg_basebackup`.

## Restore (RTO ≤ 4h)

Into a clean stack with an empty DB:

```bash
docker compose up -d db redis
DATABASE_URL=... UPLOAD_DIR=/data/attachments \
  scripts/restore.sh /backups/netdocs-db-<stamp>.dump /backups/netdocs-files-<stamp>.tar.gz
docker compose up -d api worker
curl -fsS localhost:8000/readyz   # expect migrations_current=true
```

## Restore drill (do this periodically)

1. Spin up a throwaway stack pointed at a scratch DB + volume.
2. Run `restore.sh` with the latest artifacts.
3. Verify `/readyz` is `ready`, log in, and confirm a known problem + its attachment download.
4. Record the wall-clock time to confirm it stays under the 4h RTO.

## Retention

Default 30 daily DB dumps + 30 file archives (script prune). For monthly retention (12 copies),
copy the first-of-month artifact to a separate `monthly/` prefix before pruning.
