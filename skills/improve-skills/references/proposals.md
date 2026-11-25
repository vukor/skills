# Proposals, approval and state

## Proposal format

One skill per message. Present it like this, then stop and wait:

````markdown
### <skill>: <decision> (<ownership>)

Target: <absolute path of the file, re-read just now>

| key | grade | sessions | evidence |
|---|---|---|---|
| <skill>.<topic> | explicit | <id8> | "<quote, 150 chars max, redacted>" |
| <skill>.<topic> | corroborated | <id8>, <id8> | "<short quote>"; "<short quote>" |

Why: <one or two sentences tying the evidence to the sentence being changed>

```diff
- <exact old line(s) from the file>
+ <new line(s)>
```

Apply / Edit / Skip?
````

Rules for the diff:

- `old` is copied from the file as just read, enough lines to be unique, no more.
- One hunk per lesson; several hunks in one proposal only when they are in the same file and the same skill.
- A new `references/` file is shown whole, plus the one-line pointer hunk in SKILL.md.
- Pending and discarded candidates for the skill are listed under the proposal in one line each (key, reason), so the user can promote one with "apply that too".

## Ownership

`where <skill>` prints `<path> <real path> <ownership>`. Act on it:

| ownership | meaning | action |
|---|---|---|
| `editable` | user's own skill, not versioned | apply after approval |
| `editable-git:<repo>` | tracked in a git repo (often via a symlink) | apply to the real path after approval; leave it uncommitted and say so |
| `propose-only:locked` | listed in `~/.claude/improve-skills/locked.txt` | show the diff, write nothing, log `proposed` |
| `propose-only:synced` | under `~/.claude/skills/synced/` (managed by sync) | same; the user changes it at the source |
| `propose-only:plugin` | under `~/.claude/plugins/` | same; a plugin update would overwrite a local edit |
| `propose-only:package` | installed from a package (e.g. a uv tool's site-packages) | same |

When `where` returns several paths for one name, the one in the excerpt's `dir` is the one that was used; propose against that. A `broken-link` line means the install symlink points at a missing target (often a skill on an unmerged branch): report it and propose nothing for that skill.

`log` rejects a session id that matches no transcript, or a prefix that matches several, and stores full ids; fix the id and log again.

## Applying

1. Re-read the target. If the `old` text is no longer present verbatim, redraft from the new text and ask again.
2. `backup <skill> <real path>` copies the file to `~/.claude/improve-skills/backups/<skill>/`.
3. Edit the file at its real path.
4. Re-read the changed region to confirm it landed.
5. `log --skill <s> --key <k> --decision applied --sessions <ids> --evidence "<quote>"`.

## State files

All under `~/.claude/improve-skills/` (override with `IMPROVE_SKILLS_STATE`). Keep secrets and long transcript text out of them.

- `state.json`: `sessions` maps session id to `{mtime, processed_at}`; `floor` is the oldest mtime the tool covers; `last_run`. A session that grew since it was marked (resumed) is scanned again.
- `decisions.jsonl`: one line per decision: `ts, skill, key, decision, sessions, evidence, note`. Decisions: `pending`, `discard`, `skip` (user said no), `proposed` (propose-only, shown), `applied`. `history` reads it to count recurrence per key.
- `locked.txt`: one skill name per line (`#` comments). Locked skills are proposal-only.
- `backups/<skill>/<timestamp>-<sha>-<file>`: pre-edit copies. To roll back, copy one over the real path.

A key whose last decision is `skip` is not proposed again unless new **explicit** evidence arrives; mention it in the report instead.
