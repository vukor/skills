---
name: improve-skills
description: Review past Claude Code sessions for feedback on the skills used in them, and propose small, approved fixes to those skills.
argument-hint: "[skill-name] [--since YYYY-MM-DD] [--session <id>]"
disable-model-invocation: true
---

The user has asked you to **improve their skills** from evidence in past sessions. You are a reviewer with an approval gate: you read transcripts, decide per candidate lesson, and change a skill only after the user approves the exact diff. The default outcome for any candidate is **no change**; a patch has to earn its place with evidence.

Scope boundary: this skill edits skill packages (`SKILL.md`, `references/`, `scripts/`). Findings about the wider environment (CLAUDE.md, repo docs, linters, tool access) belong to `/retro`; list them in the final report and leave them alone.

The helper is `scripts/skill_feedback.py` (python3, stdlib, read-only over `~/.claude/projects`). Call it as `python3 -I <this skill dir>/scripts/skill_feedback.py <subcommand>`; `--help` on any subcommand lists its flags. State lives in `~/.claude/improve-skills/`.

## Guardrails

- **Approval gate.** Every file write to a skill follows an explicit Apply on that exact diff, in this session.
- **Read-before-write.** Read the target file fresh right before drafting a diff, and build `old` from what you just read. Transcript quotes of a skill are history, not its current text.
- **Additive only.** Skills are patched, never deleted, renamed or moved. A merge folds content into the umbrella and leaves the sibling in place with a pointer; deleting the sibling is the user's call.
- **Ownership.** Lock a skill by adding its name to `~/.claude/improve-skills/locked.txt`. `where` reports `editable`, `editable-git:<repo>` or `propose-only:<reason>` (`locked`, `synced`, `plugin`, `package`). For `propose-only`, present the diff for the user to apply upstream; write nothing.
- **Git.** In an `editable-git` repo, leave changes uncommitted and say so. Commit only if the user asks (follow the `git-commit` skill and the user's CLAUDE.md); never push.
- **Secrets and privacy.** Evidence quotes are short (under ~150 chars), redacted, and stay in chat and the decisions log. Skill text carries rules, never quotes, tokens, hostnames of private systems, or ticket numbers.

## Steps

### 1. Load the writing guide

Call the Skill tool with `writing-for-agents`. Every diff you draft follows it: leading words, positive phrasing, single source of truth, no sediment.

**Done when** the guide is in context.

### 2. Scope and scan

Map the arguments to flags: a skill name → `--skill <name>`; a date → `--since <date>`; a session id → `--session <id>`. No arguments → the default scope: sessions not yet marked processed (first run: the last 14 days).

```sh
python3 -I scripts/skill_feedback.py scan [flags]
```

The table lists each skill with the sessions it appeared in and signal counts. Pick the skills to review: the focused skill if one was named, otherwise skills with `explicit` or `correction` signals, or with signals in 2+ sessions. A skill with only `tool_error`/`rework` in one session is usually environment noise; skip it unless its excerpts show the skill's own steps failing.

**Done when** you have a ranked list of skills to review (it may be empty: then go to step 6).

### 3. Gather evidence, one skill at a time

For each selected skill:

```sh
python3 -I scripts/skill_feedback.py excerpts --skill <name> [same scope flags]
python3 -I scripts/skill_feedback.py history --skill <name>
python3 -I scripts/skill_feedback.py where <name>
```

When an excerpt is ambiguous, read only its neighbourhood: `context <session> <idx>`. Read a whole transcript only when `context` cannot settle what happened. How to read each signal kind, and its false positives: [references/signals.md](references/signals.md).

**Done when** every excerpt for the skill is classified as a candidate lesson or as noise.

### 4. Decide each candidate

Give each candidate a **pattern key** (`<skill>.<kebab-topic>`, reused from `history` when the same lesson was seen before) and one decision: **discard**, **pending**, **patch**, **merge** or **create**. The evidence grades, the recurrence threshold, the do-not-capture list, the preference order (patch the skill in play > existing umbrella > `references/` file > new class-level skill) and the lesson shape are in [references/decisions.md](references/decisions.md). Read it before deciding the first candidate.

Short version: an explicit user correction of a skill counts once; any other signal needs the same pattern key in 2+ distinct sessions within 30 days (current excerpts plus `history`). Below the bar → **pending**, logged so the next run can count it. A key the user already skipped stays skipped unless new evidence is explicit.

**Done when** every candidate has a key, a decision, short evidence quotes and session ids.

### 5. Propose and apply, one skill at a time

For each skill with a **patch**, **merge** or **create** decision, present one proposal in the format of [references/proposals.md](references/proposals.md): the evidence, then the minimal old→new diff(s), then the choice **Apply / Edit / Skip**. Wait for the answer before moving to the next skill.

- **Apply**: re-read the target; if it changed since you drafted, redraft. Back it up (`backup <skill> <file>`), make the edit, re-read to confirm it landed, then `log --decision applied`.
- **Edit**: take the user's change, redraft, ask again.
- **Skip**: `log --decision skip` with the user's reason as `--note`, so the key is not re-proposed.

**Done when** every proposal has an answer and a matching log line.

### 6. Log and mark

Log every remaining decision (`discard`, `pending`, and `proposed` for propose-only diffs), then mark the scanned sessions processed:

```sh
python3 -I scripts/skill_feedback.py log --skill <name> --key <key> --decision <d> --sessions <id...> --evidence "<short quote>" --note "<why>"
python3 -I scripts/skill_feedback.py mark [same scope flags as step 2]
```

Mark only after the decisions are logged, so an interrupted run re-scans instead of losing evidence.

**Done when** `history` shows a line for every candidate from step 4 and the scope's sessions are marked.

### 7. Report

Report briefly: sessions scanned; per skill, what was applied, skipped, pending (with recurrence so far) and discarded; propose-only diffs the user still has to apply upstream; uncommitted changes per git repo; environment findings handed to `/retro`; overlapping skills worth a later merge.
