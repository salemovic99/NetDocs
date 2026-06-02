#!/usr/bin/env bash
# NetDocs restore: load a DB dump + attachments archive into a clean stack (PRD §14).
# Targets RTO ≤ 4h. Run against an empty database.
#
# Usage: restore.sh <db-dump-file> <files-archive.tar.gz>
# Env:   DATABASE_URL, UPLOAD_DIR (default /data/attachments)
set -euo pipefail

DB_FILE="${1:?usage: restore.sh <db.dump> <files.tar.gz>}"
FILES_FILE="${2:?usage: restore.sh <db.dump> <files.tar.gz>}"
UPLOAD_DIR="${UPLOAD_DIR:-/data/attachments}"
PG_URL="${DATABASE_URL/+asyncpg/}"

echo "[restore] restoring database from $DB_FILE"
pg_restore --clean --if-exists --no-owner --dbname="$PG_URL" "$DB_FILE"

echo "[restore] restoring attachments from $FILES_FILE -> $UPLOAD_DIR"
mkdir -p "$UPLOAD_DIR"
tar -xzf "$FILES_FILE" -C "$UPLOAD_DIR"

echo "[restore] done. Verify: GET /readyz reports migrations_current=true."
