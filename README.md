# skills

A collection of reusable agent skills for AI coding assistants (OpenCode, Claude Code, Cursor, and others).

Skills are loaded by the runtime and tell the agent when and how to do specific things. This repo is installable with the [`skills` CLI](https://github.com/vercel-labs/skills).

## Install a skill

```bash
# Install all skills globally (auto-detects your agent)
npx skills add vukor/skills --global

# Install a specific skill
npx skills add vukor/skills --skill pr-review-request --global
npx skills add vukor/skills --skill tech-design-doc --global
npx skills add vukor/skills --skill doc-digest --global
npx skills add vukor/skills --skill opencode-permissions --global
npx skills add vukor/skills --skill opencode-session-finder --global
npx skills add vukor/skills --skill opencode-session-manager --global
npx skills add vukor/skills --skill improve-skills --global
npx skills add vukor/skills --skill inbox-triage --global

# Preview what is available without installing
npx skills add vukor/skills --list
```

You can also target a specific agent:

```bash
npx skills add vukor/skills --skill pr-review-request --agent opencode --global
```

## Skills

### pr-review-request

Fetches the current user's open GitHub pull requests and formats them as a clean, plain-text message ready to paste into any team chat (Slack, Teams, Discord, Mattermost) or email.

Trigger phrases: "list my open PRs", "write a message to my team about my PRs", "draft a PR review request", "what PRs do I have open"

**Requirements:** [GitHub CLI (`gh`)](https://cli.github.com/) installed and authenticated (`gh auth login`).

### tech-design-doc

Writes Technical Design Documents (TDDs) — the architectural blueprints that explain how a system or feature will be built before a single line of production code is written. Asks 3–5 clarifying questions first, then generates a structured document saved to `docs/design/`.

Trigger phrases: "write a TDD", "create a technical design document", "design doc", "tech spec", "system design document", "architectural design doc"

### doc-digest

Helps a reviewer get through a long tech spec, design doc, requirements doc, or proposal (file, Notion link, or URL). Works one step at a time and keeps every output much shorter than the document: a brief, a consistency check, stress-test questions, draft review comments, and a decision.

Trigger phrases: "help me review this spec", "digest this design doc", "I need to give feedback on this proposal", "sign off on this RFC"

### opencode-permissions

Manages bash command permissions in `~/.config/opencode/opencode.json`. Adds, broadens, or reviews glob-pattern permission entries so that frequently-used safe commands are auto-allowed without repeated confirmation prompts.

Trigger phrases: "allow this command", "update permissions for commands I asked about", "add permission for X", "fix opencode config permissions"

### opencode-session-finder

Searches the local OpenCode SQLite database for past sessions whose message content matches a text query. Returns a table of matching sessions (id, last updated, directory, title) so the user can resume the right one.

Trigger phrases: "find my opencode session about X", "which session did I discuss Y in", "I forgot the work directory but I remember something that was said"

**Requirements:** `sqlite3` CLI available on PATH.

### opencode-session-manager

Backs up and restores OpenCode sessions from the local SQLite database. Exports a session to JSON files and re-imports it into the same or a different installation.

Trigger phrases: "backup session ses_...", "restore session from backup", "migrate session to another machine", "save a copy of this session"

**Requirements:** `sqlite3` and `python3` available on PATH.

### improve-skills

Reviews past Claude Code session transcripts for feedback on the skills used in them (corrections, interrupts, failed steps, missing instructions) and proposes minimal old-to-new diffs, one skill at a time. Nothing is written until the user approves each diff. A single explicit correction is enough; other signals must recur across sessions first. User-invoked only: run `/improve-skills`, `/improve-skills <skill-name>`, `/improve-skills --since YYYY-MM-DD` or `/improve-skills help`.

**Requirements:** `python3` on PATH. Reads `~/.claude/projects`; keeps its state in `~/.claude/improve-skills/`.

### inbox-triage

Turns everything pasted into one scratch note in an Obsidian vault (`!Inbox/inbox.md`: links, sentences, half-formed ideas, no format) into one note per item with a review (pros, cons, comparison with the skills and plugins already installed) and a runbook for trying it, blockers first. Each item is replaced by a link to its note; a page that does not open stays marked and is retried next run. Notes are written in English by default; set another language in the request or your global instructions. `inbox.md` always uses the English format. It reads pages and writes only inside `!Inbox/`; it installs and runs nothing.

Trigger phrases: "triage my inbox", "go through my inbox", "I dropped some links into the inbox", `/inbox-triage`

**Scheduled run (optional, macOS):** `scripts/scheduled-run.sh` runs the skill headless with no shell, no user settings or MCP servers, and file access limited to the inbox, installed skills and the plugin cache. `assets/inbox-triage.plist.template` schedules it for Monday to Friday at 10:00: fill in its placeholders with absolute paths, save it to `~/Library/LaunchAgents/`, and load it with `launchctl bootstrap gui/$(id -u) <plist>`. Runs are logged to `~/Library/Logs/inbox-triage.log` by default.

**Requirements:** Claude Code logged in. The scheduled run needs macOS and the Mac awake and logged in at the scheduled time.

See [`skills/inbox-triage/README.md`](skills/inbox-triage/README.md) for setup, everyday use and the scheduled run.

## Repository layout

```
skills/<skill-name>/
  SKILL.md              skill instructions and front matter
  evals/evals.json      test prompts and assertions (for development use)
  scripts/              optional helper scripts
  references/           optional reference docs
  assets/               optional templates or files
docs/decisions/         architecture decision records
AGENTS.md               instructions for AI agents working in this repo
```

## Contributing

See `AGENTS.md` for the conventions that govern this repository (naming rules, publishability requirements, plain-text output rules, and the eval workflow).

## License

MIT
