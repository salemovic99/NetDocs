#!/usr/bin/env bash
# NetDocs backup: dump the database + archive the attachments volume (PRD §14).
# Targets RPO ≤ 24h when run nightly via cron. Optionally encrypts with gpg.
#
# Env:
#   DATABASE_URL         postgres URL (postgresql[+asyncpg]://user:pass@host:port/db)
#   UPLOAD_DIR           attachments directory (default /data/attachments)
#   BACKUP_DIR           output directory (default /backups)
#   GPG_RECIPIENT        if set, encrypt artifacts to this recipient
set -euo pipefail

UPLOAD_DIR="${UPLOAD_DIR:-/data/attachments}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$BACKUP_DIR"

# Normalize the SQLAlchemy URL to a libpq-compatible one for pg_dump.
PG_URL="${DATABASE_URL/+asyncpg/}"

DB_FILE="$BACKUP_DIR/netdocs-db-$STAMP.dump"
FILES_FILE="$BACKUP_DIR/netdocs-files-$STAMP.tar.gz"

echo "[backup] dumping database -> $DB_FILE"
pg_dump --format=custom --no-owner --dbname="$PG_URL" --file="$DB_FILE"

echo "[backup] archiving attachments -> $FILES_FILE"
tar -czf "$FILES_FILE" -C "$UPLOAD_DIR" . 2>/dev/null || echo "[backup] (no attachments dir yet)"

if [[ -n "${GPG_RECIPIENT:-}" ]]; then
  echo "[backup] encrypting artifacts for $GPG_RECIPIENT"
  gpg --yes --encrypt --recipient "$GPG_RECIPIENT" "$DB_FILE"
  gpg --yes --encrypt --recipient "$GPG_RECIPIENT" "$FILES_FILE"
  rm -f "$DB_FILE" "$FILES_FILE"
fi

# Retention: keep 30 daily DB dumps (and matching file archives).
echo "[backup] pruning old backups (retain 30)"
ls -1t "$BACKUP_DIR"/netdocs-db-* 2>/dev/null | tail -n +31 | xargs -r rm -f
ls -1t "$BACKUP_DIR"/netdocs-files-* 2>/dev/null | tail -n +31 | xargs -r rm -f

echo "[backup] done: $STAMP"
