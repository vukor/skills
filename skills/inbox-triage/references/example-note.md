# Example note

A note for the inbox item `https://github.com/example/mdtidy`, written by a scheduled run with the default notes language (English). The tool is made up; the structure and level of detail are what matter. With another notes language the headings stay as they are and only the prose changes.

```markdown
---
source: https://github.com/example/mdtidy
added: 2026-11-27
kind: tool
---

# mdtidy

> https://github.com/example/mdtidy

## Review

### What it is
A CLI that formats Markdown files to one style: headings, lists, line width. It has a `--check` mode for CI and a pre-commit hook.

### Pros
- A single binary, no Node or Python.
- `--check` changes nothing and fits CI.
- Rules live in one `.mdtidy.toml`.

### Cons
- Wraps long lines by default; in Obsidian notes that breaks links, so it has to be turned off.
- Last release six months ago, 40 open issues about tables.

### Compared with what you have
Found nothing similar: no installed skill or plugin formats Markdown. The closest is the `obsidian-markdown` skill, but it describes Obsidian syntax and formats nothing.

### Could not check
- `~/.claude/settings.json`: not readable in this run.
- Skills linked as symlinks: their descriptions were not read.
- Whether mdtidy handles Obsidian callout blocks: the README does not say.

## Runbook

### Blockers
Found none: there is a macOS build for Apple silicon and no OS version requirement.

### What you need
- Homebrew.
- A folder with copies of a few notes to try it on.

### Steps
1. `brew install example/tap/mdtidy`
2. Copy three or four notes into a temporary folder.
3. `mdtidy --check <folder>`: see what it reports.
4. `mdtidy --no-wrap <folder>` and diff the files against the originals.

### What can go wrong
- Without `--no-wrap` it wraps lines and breaks long links.
- To remove: `brew uninstall mdtidy`.

### Side effects
- Without `--check` it rewrites files in place. Safer: try it only on copies, never on the vault.
- Installs a Homebrew package; no services and no account access.

## Open questions
- How does it handle front matter with nested lists?
- Run it on the whole vault or only on new notes? Your call.
```

The matching line in `inbox.md` after the run:

```markdown
- ✅ [[notes/mdtidy|mdtidy: a Markdown formatter]]
```
