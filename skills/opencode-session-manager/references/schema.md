# OpenCode Database Schema

Database: `${OPENCODE_DATA_DIR:-~/.local/share/opencode}/opencode.db`

## Tables

### `session`
| Column | Type | Notes |
|--------|------|-------|
| id | text PK | e.g. `ses_...` |
| project_id | text FK→project | required; CASCADE on delete |
| parent_id | text | optional sub-session parent |
| slug | text | |
| directory | text | cwd at session creation |
| title | text | |
| version | text | |
| share_url | text | |
| summary_additions / deletions / files / diffs | int/text | |
| revert | text | |
| permission | text | |
| time_created / time_updated | integer | Unix ms |
| time_compacting / time_archived | integer | Unix ms, nullable |
| workspace_id | text | |
| path | text | |
| agent / model | text | |
| cost | real | |
| tokens_input / output / reasoning / cache_read / cache_write | integer | |
| metadata | text | JSON |

### `message`
| Column | Type | Notes |
|--------|------|-------|
| id | text PK | |
| session_id | text FK→session | CASCADE on delete |
| time_created / time_updated | integer | Unix ms |
| data | text | JSON |

### `part`
| Column | Type | Notes |
|--------|------|-------|
| id | text PK | |
| message_id | text FK→message | CASCADE on delete |
| session_id | text | denormalized for fast lookup |
| time_created / time_updated | integer | Unix ms |
| data | text | JSON — actual message content lives here |

### `project`
| Column | Type | Notes |
|--------|------|-------|
| id | text PK | |
| worktree | text | |
| vcs | text | |
| name / icon_url / icon_color | text | |
| time_created / time_updated / time_initialized | integer | Unix ms |
| sandboxes | text | JSON |
| commands | text | JSON |
| icon_url_override | text | |

## Key Relationships

- `session.project_id` → `project.id` (required FK; project must exist before restoring a session)
- `message.session_id` → `session.id`
- `part.message_id` → `message.id`
- `part.session_id` → `session.id` (denormalized index)

## Backup File Mapping

| File | Table |
|------|-------|
| `session.json` | `session` |
| `messages.json` | `message` |
| `parts.json` | `part` |

All files are JSON arrays exported via `sqlite3 .mode json`.
