#!/usr/bin/env bash
# Restore an OpenCode session from a backup directory.
#
# Usage:
#   restore_session.sh <backup_dir> [--db PATH] [--force]
#
# Options:
#   --db PATH    Path to SQLite DB (default: ~/.local/share/opencode/opencode.db)
#   --force      Overwrite existing session if it already exists in the DB
#
# backup_dir must contain session.json, messages.json, parts.json

set -euo pipefail

BACKUP_DIR=""
DB="${OPENCODE_DATA_DIR:-$HOME/.local/share/opencode}/opencode.db"
FORCE=0

usage() { sed -n '2,13p' "$0"; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --db)    DB="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    -h|--help) usage ;;
    *)
      if [[ -z "$BACKUP_DIR" ]]; then BACKUP_DIR="$1"; shift
      else echo "Unexpected argument: $1" >&2; usage
      fi
      ;;
  esac
done

[[ -z "$BACKUP_DIR" ]] && { echo "Error: backup_dir is required." >&2; usage; }
[[ -d "$BACKUP_DIR" ]] || { echo "Backup directory not found: $BACKUP_DIR" >&2; exit 2; }
[[ -f "$DB" ]]         || { echo "Database not found: $DB" >&2; exit 2; }

for f in session.json messages.json parts.json; do
  [[ -f "${BACKUP_DIR}/${f}" ]] || { echo "Missing backup file: ${BACKUP_DIR}/${f}" >&2; exit 2; }
done

SESSION_ID=$(python3 -c "
import json, sys
data = json.load(open('${BACKUP_DIR}/session.json'))
rows = data if isinstance(data, list) else [data]
if not rows: sys.exit(1)
print(rows[0]['id'])
")
[[ -z "$SESSION_ID" ]] && { echo "Could not determine session ID from backup." >&2; exit 2; }

echo "Restoring session: $SESSION_ID"
echo "Source:   $BACKUP_DIR"
echo "Database: $DB"

EXISTING=$(sqlite3 "$DB" "SELECT COUNT(*) FROM session WHERE id = '${SESSION_ID}';")
if [[ "$EXISTING" -gt 0 ]]; then
  if [[ "$FORCE" -eq 0 ]]; then
    echo "" && echo "Error: session already exists in DB: $SESSION_ID" >&2
    echo "Use --force to overwrite." >&2; exit 4
  fi
  echo "Warning: overwriting existing session (--force)."
fi

PROJECT_ID=$(python3 -c "
import json
data = json.load(open('${BACKUP_DIR}/session.json'))
rows = data if isinstance(data, list) else [data]
print(rows[0]['project_id'])
")
PROJECT_EXISTS=$(sqlite3 "$DB" "SELECT COUNT(*) FROM project WHERE id = '${PROJECT_ID}';")
if [[ "$PROJECT_EXISTS" -eq 0 ]]; then
  echo "" && echo "Error: referenced project not found in DB: $PROJECT_ID" >&2
  echo "The target DB may belong to a different OpenCode installation." >&2; exit 5
fi

python3 <<PYEOF
import json, sqlite3, sys

con = sqlite3.connect("${DB}")
cur = con.cursor()

def load(filename):
    with open(f"${BACKUP_DIR}/{filename}") as fh:
        data = json.load(fh)
    return data if isinstance(data, list) else [data]

def upsert(table, rows):
    if not rows:
        print(f"  {table}: no rows to restore"); return
    cols = list(rows[0].keys())
    placeholders = ", ".join("?" * len(cols))
    col_names    = ", ".join(f'"{c}"' for c in cols)
    verb = "INSERT OR REPLACE" if ${FORCE} else "INSERT OR IGNORE"
    sql  = f'{verb} INTO "{table}" ({col_names}) VALUES ({placeholders})'
    cur.executemany(sql, [[row.get(c) for c in cols] for row in rows])
    print(f"  {table}: {cur.rowcount} row(s) restored")

try:
    con.execute("BEGIN")
    upsert("session",  load("session.json"))
    upsert("message",  load("messages.json"))
    upsert("part",     load("parts.json"))
    con.commit()
    print("\nRestore complete.")
except Exception as e:
    con.rollback()
    print(f"Error during restore: {e}", file=sys.stderr); sys.exit(1)
finally:
    con.close()
PYEOF
