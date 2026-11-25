# improve-skills

Learn from your own sessions which skills misled the agent, and fix them with small diffs you approve.

The skill reads past Claude Code transcripts for feedback on the skills used in them: your corrections, interrupts, failed steps, missing instructions. It turns each real lesson into a minimal old-to-new diff against the skill, one skill at a time, and writes nothing until you approve the diff. A single explicit correction is enough; other signals must recur across sessions first.

## Install

```bash
npx skills add vukor/skills --skill improve-skills --global
```

Or link this directory into your agent's skills folder, e.g. `~/.claude/skills/improve-skills`.

**Requirements:** Claude Code and `python3` on `PATH`. The scheduled run needs macOS.

## Everyday use

The skill is user-invoked only; the agent never starts it on its own.

```text
/improve-skills                      sessions not yet reviewed (first run: last 14 days)
/improve-skills <skill-name>         one skill
/improve-skills --since YYYY-MM-DD   sessions modified since a date, ignoring review state
/improve-skills --session <id>       one session (id or unique prefix)
/improve-skills --report <file.html> report-only: write proposals to an HTML file, change nothing
/improve-skills help                 usage
```

For each skill worth changing you get the evidence, the exact diff and the choice **Apply / Edit / Skip**. Applied edits are backed up first. In a git repo they are left uncommitted.

To keep a skill out of reach, add its name to `~/.claude/improve-skills/locked.txt`: its diffs are shown, never written.

## Scheduled report (macOS, optional)

`scripts/scheduled-run.sh` runs the skill headless with `--report`. Nobody can approve a diff in an unattended run, so the session drafts the proposals into one HTML page and stops. It edits no skill, logs no decision and marks no session as reviewed, so your next `/improve-skills` sees the same evidence and you apply the proposals there. When the report exists, the script opens it in your default browser; when it does not, it shows a notification.

The session gets read access to `~/.claude`, only the read-only helper subcommands (`scan`, `excerpts`, `history`, `where`, `context`), the `writing-for-agents` skill, and Write inside the reports directory. It has no MCP servers, denies anything else without asking, and is not saved as a session, so it never shows up in a later scan.

`assets/improve-skills.plist.template` schedules the script for Mondays at 12:00. To pick another time, edit `Weekday` (0 or 7 is Sunday, 1 is Monday), `Hour` and `Minute`; after loading, reload the job (`launchctl bootout`, then `bootstrap`) for the change to take effect.

1. Try the script by hand first:

   ```bash
   bash skills/improve-skills/scripts/scheduled-run.sh
   tail -n 40 ~/Library/Logs/improve-skills.log
   ```

2. Fill in the plist placeholders. The job finds the runner through `$HOME`, so it holds no user paths, but it expects the skill installed at `~/.claude/skills/improve-skills`:

   | Placeholder | Value |
   |---|---|
   | `__LABEL__` | Job name, e.g. `com.example.improve-skills` |
   | `__CLAUDE_DIR__` | The directory that contains `claude`; it must also hold `python3`, or add that directory to `PATH` |

   For example:

   ```bash
   sed -e 's|__LABEL__|com.example.improve-skills|' \
       -e "s|__CLAUDE_DIR__|$(dirname "$(command -v claude)")|" \
       skills/improve-skills/assets/improve-skills.plist.template \
       > ~/Library/LaunchAgents/com.example.improve-skills.plist
   ```

3. Load the job:

   ```bash
   launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.example.improve-skills.plist
   launchctl kickstart gui/$(id -u)/com.example.improve-skills   # run once now to check
   ```

4. To stop it:

   ```bash
   launchctl bootout gui/$(id -u)/com.example.improve-skills
   rm ~/Library/LaunchAgents/com.example.improve-skills.plist
   ```

Script settings, all environment variables:

| Variable | Default | Meaning |
|---|---|---|
| `IMPROVE_SKILLS_CLAUDE` | `claude` on `PATH` | Claude Code binary |
| `IMPROVE_SKILLS_LOG` | `~/Library/Logs/improve-skills.log` | Log file; each run appends a start line, the JSON result and an end line with the exit code |
| `IMPROVE_SKILLS_REPORTS` | `~/.claude/skills/improve-skills/reports` | Where `YYYY-MM-DD.html` reports go; the default is inside the skill directory, which the repo gitignores |
| `IMPROVE_SKILLS_DAYS` | `7` | Look-back window; the run passes `--since` that many days ago |
| `IMPROVE_SKILLS_OPEN` | `1` | `1` opens the report in the browser; anything else only writes it |

Things to know:

- Claude Code must be logged in, and the Mac awake and logged in at the scheduled time. A run missed during sleep starts once on wake; a run missed while the Mac is off is skipped.
- `--since` ignores review state, so a week's report can repeat a proposal you have not acted on yet. Apply or skip it with `/improve-skills` to retire it.

## Files

```
SKILL.md                                the instructions the agent follows
references/                             signal reading, decision rules, proposal format
scripts/skill_feedback.py               read-only transcript helper (stdlib python3)
scripts/scheduled-run.sh                headless report-only runner for the scheduled job
reports/                                scheduled reports (default location, not tracked)
assets/improve-skills.plist.template    launchd job, Mondays at 12:00
evals/                                  test prompts and fixtures (development only)
```
