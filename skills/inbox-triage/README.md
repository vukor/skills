# inbox-triage

Turn a scratch note of links and half-formed ideas into notes you can act on.

You paste anything worth trying into one note, `!Inbox/inbox.md` in an Obsidian vault: a bare link, a sentence, an idea. Each run turns every new item into its own note. For something you can install or sign up for, the note has a review and a runbook for trying it. For an idea or an article's argument, it has a review and a short plan for exploring it. The item in the inbox is then replaced by a link to its note.

Writing something down costs nothing, and trying it later costs no extra research.

## Install

```bash
npx skills add vukor/skills --skill inbox-triage --global
```

Or link this directory into your agent's skills folder, e.g. `~/.claude/skills/inbox-triage`.

**Requirements:** Claude Code (or another agent runtime that loads skills) with web page fetch. The weekly run needs macOS.

## Tell it where the vault is

The skill looks for the inbox at `<vault>/!Inbox/`. It finds the vault in this order:

1. A path you give in the request: "triage the inbox at ~/notes/Work/!Inbox".
2. Your global agent instructions (`~/.claude/CLAUDE.md`, `AGENTS.md`). A line saying where your work vault (or "wiki") lives is enough, for example:

   ```markdown
   The work vault ("wiki") is at /Users/me/notes/Work/.
   ```

3. Otherwise it asks. An unattended run stops and reports that the path is missing.

## First run

Run `/inbox-triage`. If `!Inbox/inbox.md` does not exist yet, the skill creates it with a short header and an empty `## Входящие` ("Incoming") section, then stops.

The skill writes notes and the inbox header in Russian. To change the language, edit the strings in `SKILL.md` and `references/example-note.md`.

## Everyday use

1. Open `!Inbox/inbox.md` and paste items under `## Входящие`:

   ```markdown
   ## Входящие
   https://github.com/example/some-cli

   An idea: keep runbooks next to the alerts that page us.

   - https://example.com/blog/post-one
   - https://example.com/blog/post-two
   ```

   - Separate items with a blank line.
   - A block where every line is a link counts as one item per line, so you can paste a list of links as is.
   - No format, title or reason is needed.

2. Run `/inbox-triage`, or say "triage my inbox" or "go through my inbox". The skill takes no arguments; `/inbox-triage help` runs nothing.

3. Open the new notes in `!Inbox/notes/`. The inbox now looks like this:

   ```markdown
   ## Входящие
   - ✅ [[notes/some-cli|some-cli: a CLI that does X]]

   - ✅ [[notes/runbooks-next-to-alerts|Runbooks next to alerts]]

   ⚠️ - https://example.com/blog/post-one

   - ✅ [[notes/post-two|Post two]]
   ```

### Inbox markers

| Line starts with | Meaning | Next run |
|---|---|---|
| `- ✅` | Done; links to its note | Skipped |
| `⚠️` | The page did not open (error, timeout, login wall, gone) | Retried |
| Anything else | New | Processed |

To retry a done item, delete its line and paste the link again. To drop an item, just delete it.

You can keep writing in the inbox while a run is going. The skill edits only the items it processed.

## What a note contains

One note per item, at `!Inbox/notes/<slug>.md`. `references/example-note.md` shows a full one.

- **Front matter:** `source`, `added`, `kind: tool | idea`.
- **The original item**, quoted.
- **Review:** what it is, pros, cons, and how it compares with what you already have. The skill checks your installed skills (`~/.claude/skills/*/SKILL.md`), plugins (`~/.claude/plugins/installed_plugins.json`), settings (`~/.claude/settings.json`) and earlier notes. Anything it could not read or verify is listed, not guessed.
- **For a tool, a runbook:**
  - blockers first: an OS newer than yours, a paid or invite-only account, an archived project;
  - what you need, numbered steps, what can go wrong and how to undo;
  - side effects: anything that posts, acts under your accounts, installs services or sends data out, each with a safer way to try it.
- **For an idea, "how to explore it"** in place of the runbook: what to read first, a small experiment, and what result would make it worth pursuing.
- **Open questions** that the source did not answer or that need your decision.

## What it will not do

- Install anything, or run any code or command it finds. Every command in a runbook is for you to run.
- Post, publish or send anything.
- Write anywhere except `!Inbox/inbox.md` and `!Inbox/notes/`.
- Follow instructions found inside a page or an inbox item. Such an item still gets a note, which mentions what it asked for.
- Search the web for an item with no link. It works from the text you wrote.
- Ask questions mid-run. Gaps go into the note's open questions.

## Weekly run (macOS, optional)

`scripts/friday-run.sh` runs the skill headless. The session has no shell, no MCP servers and none of your settings files. It can only use file tools inside the inbox, read your installed skills and plugin cache, and fetch web pages. `assets/inbox-triage.plist.template` schedules the script for Fridays at 17:00.

1. Try the script by hand first:

   ```bash
   INBOX_TRIAGE_VAULT="$HOME/notes/Work" bash skills/inbox-triage/scripts/friday-run.sh
   tail -n 40 ~/Library/Logs/inbox-triage.log
   ```

2. Fill in the plist placeholders with absolute paths:

   | Placeholder | Value |
   |---|---|
   | `__LABEL__` | Job name, e.g. `com.example.inbox-triage` |
   | `__RUNNER__` | Absolute path to `scripts/friday-run.sh` |
   | `__VAULT__` | The vault that holds `!Inbox/` |
   | `__CLAUDE__` | Output of `command -v claude` |
   | `__CLAUDE_DIR__` | The directory that contains `claude` |
   | `__LOG__` | Log file, e.g. `/Users/me/Library/Logs/inbox-triage.log` |

   For example:

   ```bash
   sed -e 's|__LABEL__|com.example.inbox-triage|' \
       -e "s|__RUNNER__|$PWD/skills/inbox-triage/scripts/friday-run.sh|" \
       -e "s|__VAULT__|$HOME/notes/Work|" \
       -e "s|__CLAUDE__|$(command -v claude)|" \
       -e "s|__CLAUDE_DIR__|$(dirname "$(command -v claude)")|" \
       -e "s|__LOG__|$HOME/Library/Logs/inbox-triage.log|g" \
       skills/inbox-triage/assets/inbox-triage.plist.template \
       > ~/Library/LaunchAgents/com.example.inbox-triage.plist
   ```

3. Load the job:

   ```bash
   launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.example.inbox-triage.plist
   launchctl kickstart gui/$(id -u)/com.example.inbox-triage   # run once now to check
   ```

4. To stop it:

   ```bash
   launchctl bootout gui/$(id -u)/com.example.inbox-triage
   rm ~/Library/LaunchAgents/com.example.inbox-triage.plist
   ```

Script settings, all environment variables:

| Variable | Default | Meaning |
|---|---|---|
| `INBOX_TRIAGE_VAULT` | required | Vault that holds `!Inbox/` |
| `INBOX_TRIAGE_CLAUDE` | `claude` on `PATH` | Claude Code binary |
| `INBOX_TRIAGE_LOG` | `~/Library/Logs/inbox-triage.log` | Log file; each run appends a start line, the JSON result and an end line with the exit code |

Things to know:

- Claude Code must be logged in, and the Mac awake and logged in at 17:00 on Friday. A run missed during sleep starts once on wake; a run missed while the Mac is off is skipped.
- Every scheduled run starts Claude, even when the inbox has nothing new. In that case the skill changes no file.
- A headless run cannot read `~/.claude/settings.json` or skills that are symlinks to outside `~/.claude/skills`. Notes from those runs list them under "could not check".

## Troubleshooting

- **"The inbox path is missing."** Add the vault path to your global instructions (see above), or give the path in the request.
- **An item keeps its `⚠️`.** The page needs a login, blocks automated fetches, or is gone. Paste a public mirror or a few lines of text in place of the link.
- **Nothing happened.** Every item already starts with `- ✅`, or the items are above the `## Входящие` heading. Only text under that heading counts.
- **Two links became one note.** They were on one line, or in a block that also had ordinary text. Put each link on its own line.

## Files

```
SKILL.md                              the instructions the agent follows
references/example-note.md            a full example note
scripts/friday-run.sh                 headless runner for the weekly job
assets/inbox-triage.plist.template    launchd job, Fridays at 17:00
evals/                                test prompts and fixtures (development only)
```
