#!/usr/bin/env bash
# Find OpenCode sessions containing a text query in chat messages.
#
# Usage:
#   find_sessions.sh <query> [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--nocase] [--db PATH]
#
# Output (TSV, piped through column for table rendering):
#   session_id    updated    directory    title
#
# The database lives at ${OPENCODE_DATA_DIR:-~/.local/share/opencode}/opencode.db
# on macOS and Linux (XDG layout).

set -euo pipefail

QUERY=""
SINCE=""
UNTIL=""
NOCASE=0
DB="${OPENCODE_DATA_DIR:-$HOME/.local/share/opencode}/opencode.db"

usage() {
  sed -n '2,12p' "$0"
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --since) SINCE="$2"; shift 2 ;;
    --until) UNTIL="$2"; shift 2 ;;
    --nocase) NOCASE=1; shift ;;
    --db) DB="$2"; shift 2 ;;
    -h|--help) usage ;;
    *)
      if [[ -z "$QUERY" ]]; then QUERY="$1"; shift
      else echo "Unexpected argument: $1" >&2; usage
      fi
      ;;
  esac
done

[[ -z "$QUERY" ]] && usage
[[ -f "$DB" ]] || { echo "Database not found: $DB" >&2; exit 2; }

# Escape single quotes for SQL literal
esc() { printf "%s" "$1" | sed "s/'/''/g"; }
Q=$(esc "$QUERY")

if [[ "$NOCASE" -eq 1 ]]; then
  MATCH="LOWER(pt.data) LIKE LOWER('%${Q}%')"
else
  MATCH="pt.data LIKE '%${Q}%'"
fi

WHERE="$MATCH"
if [[ -n "$SINCE" ]]; then
  WHERE="$WHERE AND s.time_updated >= strftime('%s','${SINCE}') * 1000"
fi
if [[ -n "$UNTIL" ]]; then
  # interpret as end-of-day exclusive: +1 day
  WHERE="$WHERE AND s.time_updated <  strftime('%s','${UNTIL}','+1 day') * 1000"
fi

SQL="SELECT
  s.id                                                  AS session_id,
  datetime(s.time_updated/1000,'unixepoch','localtime') AS updated,
  s.directory                                           AS directory,
  s.title                                               AS title
FROM part pt
JOIN session s ON s.id = pt.session_id
WHERE ${WHERE}
GROUP BY s.id
ORDER BY s.time_updated DESC;"

OUT=$(sqlite3 -cmd ".headers on" -cmd ".mode tabs" "$DB" "$SQL")

if [[ -z "$OUT" || "$(printf "%s" "$OUT" | wc -l)" -le 1 ]]; then
  echo "No sessions matched: $QUERY" >&2
  exit 3
fi

printf "%s\n" "$OUT" | column -t -s $'\t'
