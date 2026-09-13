---
name: opencode-permissions
description: Use when the user asks to update, add, or fix OpenCode tool permissions in their config file (~/.config/opencode/opencode.json). Triggers include requests like "allow this command", "update permissions for commands I asked about", "add permission for X", "fix opencode config permissions", or when bash commands were repeatedly prompted for confirmation during a session and the user wants to auto-allow them going forward.
---

# OpenCode Permissions

Manage bash command permissions in `~/.config/opencode/opencode.json` so that frequently-used safe commands are auto-allowed without interactive confirmation prompts.

## Config Location

The config file is at `~/.config/opencode/opencode.json`. Read it first to understand the current state.

## Permission Structure

The `permission.bash` object maps glob patterns to actions:

```jsonc
"bash": {
  "*": "ask",                    // default: prompt for unknown commands
  "git status*": "allow",       // allow without prompting
  "git push --force*": "deny",  // always block
  "docker run*": "ask"          // always prompt
}
```

**Actions:** `"allow"` (auto-approve), `"ask"` (prompt user), `"deny"` (block).

**Pattern matching:** Glob-style with `*` as wildcard. Patterns match from the start of the command string.

## Workflow

1. **Read** `~/.config/opencode/opencode.json`
2. **Identify** which bash commands from the session triggered confirmation prompts (i.e., commands that were executed but had no matching `allow` pattern)
3. **Draft** new permission entries — choose the most general safe pattern that covers the command without being overly broad
4. **Check safety** — never add `allow` for destructive commands (see guardrails below)
5. **Edit** the config file, inserting new entries in the appropriate location (group with similar commands)
6. **Verify** the final file is valid JSON (no trailing commas, proper structure)

## Pattern Design Rules

### Broaden conservatively

When a command like `git branch --show-current` isn't covered by `"git branch *"` (which requires a space+arg), broaden to `"git branch*"` to cover both cases.

| Command blocked | Existing pattern | Fix |
|---|---|---|
| `git branch --show-current` | `"git branch *"` | `"git branch*"` (drop trailing space before `*`) |
| `git diff` (no args) | `"git diff *"` | `"git diff*"` |
| `gh api user --jq .login` | (none) | `"gh api *"` |
| `pre-commit run --all-files` | (none) | `"pre-commit *"` |

### Group by tool

Insert new entries near related commands. Keep all `git *` patterns together, all `gh *` together, all `kubectl *` together, etc.

### Use trailing `*` for subcommands

```
"gh api *": "allow"         — covers gh api user, gh api repos/...
"flux get *": "allow"       — covers flux get kustomizations, flux get sources, etc.
```

### Never auto-allow with broad patterns

Bad: `"*": "allow"` — allows everything.
Bad: `"rm *": "allow"` — allows deleting anything.

## Safety Guardrails

Never add `"allow"` for these categories — they must stay `"deny"` or `"ask"`:

| Category | Examples | Action |
|---|---|---|
| Destructive git | `git push --force*`, `git push -f*`, `git reset --hard*`, `git clean -fd*` | `deny` |
| File deletion | `rm -rf *`, `sudo rm*` | `deny` |
| System-level | `chmod -R*`, `chown -R*`, `dd *`, `mkfs*`, `> /dev/*` | `deny` |
| Container mutation | `docker run*`, `docker rm*`, `docker rmi*` | `ask` |
| Checkout (can lose work) | `git checkout *` (non `-b`) | `ask` |
| Fork bombs | `": (){ :\|:& };:"` | `deny` |

If a requested command falls into a guarded category, inform the user instead of adding it.

## Example Session

User: "allow the commands you asked about in this session"

Commands that triggered prompts during the session:
- `git branch --show-current` — not covered by `"git branch *"`
- `gh api user --jq '.login'` — no `gh api` rule exists

Actions taken:
1. Broaden `"git branch *"` → `"git branch*"`
2. Add `"gh api *": "allow"` next to other `gh` entries
