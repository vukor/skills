---
name: opencode-session-manager
description: Backup and restore OpenCode sessions from the local SQLite database. Use when the user asks to backup, restore, migrate, or copy an OpenCode session by session ID. Triggers on requests like "backup session ses_...", "restore session from backup", "migrate session to another machine", "save a copy of this session".
---

# OpenCode Session Manager

Manage OpenCode sessions stored in the local SQLite database at `${OPENCODE_DATA_DIR:-~/.local/share/opencode}/opencode.db`.

Session data lives entirely in SQLite across three tables: `session`, `message`, and `part`. See [references/schema.md](references/schema.md) for the full schema.

## Backup a Session

```bash
bash scripts/backup_session.sh <session_id> [--out DIR] [--db PATH]
```

Default output directory: `~/_work/opencode/backup/sessions/`

Creates `<out>/<session_id>/` containing:
- `session.json` — session metadata
- `messages.json` — all messages
- `parts.json` — all message content (actual text)

**Exit codes:** `2` = DB/session not found, `3` = session ID not in DB

## Restore a Session

```bash
bash scripts/restore_session.sh <backup_dir> [--db PATH] [--force]
```

Default backup directory to restore from: `~/_work/opencode/backup/sessions/`

Reads the three JSON files from `<backup_dir>` and inserts rows into the target DB.

**Prerequisites:** The `project_id` referenced by the session must already exist in the target DB. If restoring to a different machine/installation, the project row will be missing — exit code `5`.

**Exit codes:** `2` = missing files/DB, `4` = session already exists (use `--force`), `5` = referenced project missing

## Lookup a Session ID

To find a session ID from the DB:

```bash
sqlite3 ~/.local/share/opencode/opencode.db \
  "SELECT id, title, directory, datetime(time_updated/1000,'unixepoch') FROM session ORDER BY time_updated DESC LIMIT 20;"
```

## Schema Reference

See [references/schema.md](references/schema.md) for full table definitions and column descriptions.
