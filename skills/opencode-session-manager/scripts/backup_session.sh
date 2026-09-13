#!/usr/bin/env bash
# Backup an OpenCode session by session ID.
#
# Usage:
#   backup_session.sh <session_id> [--db PATH] [--out DIR]
#
# Options:
#   --db PATH    Path to SQLite DB (default: ~/.local/share/opencode/opencode.db)
#   --out DIR    Output directory (default: ~/_work/opencode/backup/sessions/)
#
# Creates <out>/<session_id>/ with session.json, messages.json, parts.json

set -euo pipefail

SESSION_ID=""
DB="${OPENCODE_DATA_DIR:-$HOME/.local/share/opencode}/opencode.db"
OUT_DIR="$HOME/_work/opencode/backup/sessions"

usage() { sed -n '2,12p' "$0"; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --db)  DB="$2"; shift 2 ;;
    --out) OUT_DIR="$2"; shift 2 ;;
    -h|--help) usage ;;
    *)
      if [[ -z "$SESSION_ID" ]]; then SESSION_ID="$1"; shift
      else echo "Unexpected argument: $1" >&2; usage
      fi
      ;;
  esac
done

[[ -z "$SESSION_ID" ]] && { echo "Error: session_id is required." >&2; usage; }
[[ -f "$DB" ]] || { echo "Database not found: $DB" >&2; exit 2; }

COUNT=$(sqlite3 "$DB" "SELECT COUNT(*) FROM session WHERE id = '${SESSION_ID}';")
[[ "$COUNT" -eq 0 ]] && { echo "Session not found: $SESSION_ID" >&2; exit 3; }

BACKUP_DIR="${OUT_DIR}/${SESSION_ID}"
mkdir -p "$BACKUP_DIR"

echo "Backing up session: $SESSION_ID"
echo "Destination: $BACKUP_DIR"

sqlite3 "$DB" <<EOF
.mode json
.output ${BACKUP_DIR}/session.json
SELECT * FROM session WHERE id = '${SESSION_ID}';
.output ${BACKUP_DIR}/messages.json
SELECT * FROM message WHERE session_id = '${SESSION_ID}';
.output ${BACKUP_DIR}/parts.json
SELECT * FROM part WHERE session_id = '${SESSION_ID}';
EOF

echo ""
echo "Backup complete:"
ls -lh "$BACKUP_DIR"
