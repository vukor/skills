---
name: opencode-session-finder
description: Locate past OpenCode sessions by searching text within their chat messages, optionally filtered by date range. Use when the user wants to find, resume, or inspect an OpenCode session but only remembers something that was said in it (a phrase, identifier, file path, error message) and has forgotten the session id, title, or working directory. Triggers on requests like "find my opencode session about X", "which session did I discuss Y in", "I forgot the work directory but I have a search text".
---

# OpenCode Session Finder

## Overview

Search the local OpenCode SQLite database for sessions whose message content matches a text query, and print a table of matches (session id, last updated, directory, title) so the user can resume the right one.

## Database location

`${OPENCODE_DATA_DIR:-~/.local/share/opencode}/opencode.db` on macOS and Linux (XDG).

Relevant schema:

- `session(id, project_id, directory, title, time_updated, ...)` — one row per session. `directory` is the cwd at session creation.
- `message(id, session_id, data, time_created, ...)` — one row per chat message.
- `part(id, message_id, session_id, data, time_created, ...)` — message content lives in `part.data` as JSON; this is where to search.

## Workflow

1. Run the bundled script with the user's query. Forward `--since` / `--until` if they gave a date range, and `--nocase` if they want case-insensitive matching.

   ```bash
   scripts/find_sessions.sh "<query>" [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--nocase]
   ```

2. Present the table as-is. If multiple rows match, ask the user which one they want; otherwise confirm the single match.

3. Offer the resume command for the chosen session. From inside the session's directory:

   ```bash
   cd <directory>
   opencode --session <session_id>
   ```

## Notes

- The script matches on the raw JSON of `part.data`. Queries containing SQL wildcards (`%`, `_`) will behave as wildcards — warn the user or escape them if that is not intended.
- `part.data` may include base64-encoded attachments; extremely long queries that happen to match inside binary blobs are unlikely but possible.
- Exit codes: `0` match found, `1` usage error, `2` database not found, `3` no matches.
- If the DB is not at the default path, pass `--db <path>` or set `OPENCODE_DATA_DIR`.
