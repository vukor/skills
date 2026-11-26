---
name: pr-digest
description: Use when the user reviews a pull request someone else opened, often agent-authored, and wants to understand it, give feedback on it, or approve it. Make sure to use it for requests like "help me review this PR", "should I approve PR #123", "walk me through this pull request" or "digest this PR", and whenever the user pastes a PR URL and asks what to do with it, even if they never say "review".
---

# PR digest

For pull requests the user reviews but did not write, often agent-authored: a polished description over a diff nobody has walked. The reviewer's attention is the scarce resource, so answer a large diff with a short, ranked report.

Before your first reply, look in the user's instructions (`CLAUDE.md`, `AGENTS.md`) for a language named for this skill: it overrides the language the user writes in. Otherwise reply in the language the user writes in. Keep paths, identifiers, quotes, `comments.md` and `pr-conventions.md` in the repository's language: comments go to the author, and conventions outlive this review.

Work one step at a time. After each step stop and wait; move on when the user says so ("next") or names a step.

## Requirements

- [GitHub CLI (`gh`)](https://cli.github.com/), authenticated (check with `gh auth status`): reads the PR, its checks and its diff.
- The `explain-diff-html` skill (`npx skills add vukor/skills --skill explain-diff-html --global`): writes the HTML explanation at Step 1b.
- [Plannotator](https://github.com/backnotprop/plannotator): the diff reader at Step 3 (`/plannotator-review <pr url>`).

When one is missing, name it, say where to get it, and ask whether to continue without it. Without `explain-diff-html`, skip Step 1b; without Plannotator, the user reads the diff in their own tool and pastes their notes. A missing tool should not end a review halfway.

## Files

Review files live in the user's wiki under `pr-reviews/<repo-name>/`, where `<repo-name>` is the repository name without the owner: reviewing `octo-org/payments-api` writes to `pr-reviews/payments-api/`. The user's instructions (`CLAUDE.md`, `AGENTS.md`) say where the wiki is; when they don't, ask once before writing anything. Keep these files out of the repository's working directory.

- `<repo-name>/pr-conventions.md`: what this reviewer has already settled about this codebase — accepted patterns, known debt, rules they always enforce. Read it before Step 1, append to it at Step 6.
- One folder per PR: `<repo-name>/pr-<number>/brief.md`, `notes.md`, `comments.md`, and `YYYY-MM-DD-explain.html` from Step 1b.

`notes.md` is the user's private working file; only `comments.md` is meant to be posted.

## Before you start

- Get the PR with the `gh` CLI: its title, body, author, checks and diff. Check out the branch when the repository is there, because the diff alone hides what is not in it.
- Say plainly what you could not reach (no repo, no `gh`, no network) rather than reviewing the description alone and calling it a review.
- Know whether the user's approval is what merges this.

## Step 0: Triage (always; often the whole review)

Three lines: size (files, lines, how much is generated or mechanical), surface (what can break and for whom), reversibility (behind a flag, a data migration, one-way). Then recommend a path:

- **Short** — mechanical, reversible, covered by tests: Steps 1 and 2 only.
- **Full** — shared code, data, auth, infra, or anything hard to undo: every step.
- **Stop** — too large to review as one unit, or nobody can answer for it: say so, and name what to split or whom to ask.

When you recommend the Full path and the PR is part of a stack (its base branch is the head of another open PR), list the stack and offer to start Step 1b for every PR in it now, so the user can read ahead. The Short path makes no HTML, so it gets no offer. The other PRs have no brief yet, so their subagents get no reading map. When the review reaches one of those PRs, its HTML already exists: skip Step 1b there.

## Step 1: Brief (at most 25 lines, plus the reading map)

Write to `brief.md` and show it. For the shape and length of a triage and a brief, see [`references/example-brief.md`](references/example-brief.md). The 25 lines do not count the reading map, which lists every file. Leave explaining how the code works to the HTML from Step 1b: on the Full path the user reads both, and saying it twice spends the attention this skill exists to save.

1. **What it claims, and what is asked of you.** Approve, merge, or only comment.
2. **Description against diff.** Does the diff do what the description says, nothing less and nothing more? Name each claim with no code behind it, and each change the description does not mention. For an agent-authored PR this is the first check, not a formality.
3. **What changes** for the caller, the user or whoever operates this.
4. **Reading map.** Every file tagged read closely / skim / skip, grouped as logic, tests, mechanical (lockfiles, generated clients, snapshots, formatting, vendored). Be decisive: a diff is ordered alphabetically, not by importance.
5. **Who can answer for this change** if a question comes back.

## Step 1b: Explain (Full path)

Right after the brief, unless this PR's HTML already exists from a stack batch at Step 0, start the `explain-diff-html` skill in a background subagent and go on to Step 2 without waiting for it. Give the subagent:

- the PR URL and the diff range: against the base branch, or, in a stack, against the PR below it;
- the reading map from `brief.md`;
- the language to write in, from the top of this skill: the subagent sees only your message, not the user's;
- the HTML path from Files;
- "do not open": you open it at Step 3, when the user is ready to read it, not while they read check results.

Record the HTML path in `brief.md`.

## Step 2: Checks (run them; do not judge code by reading alone)

Append to `brief.md`. Run what the repository offers — build, type check, lint, tests — and report each in one line. Name what you could not run.

Then:

- **Not in the diff.** Search the repository for callers, implementers, config, docs, feature flags and migrations this change needs but does not touch. This is where agent-authored PRs fail most.
- **Tests.** Do they exercise the risky behavior, or only the happy path? Say what a test actually asserts versus what the change claims.
- **Repeats.** Functionality the repository already has elsewhere.
- **Conventions.** Where the change departs from `pr-conventions.md`.

Label each finding *from the code* or *my inference*, and rank by what it costs if wrong.

Treat your own reading of the code as the weakest evidence here: you and the PR's author write the same way and share blind spots. A failing check or a missing caller outweighs an impression that the code looks fine.

## Step 3: Read together

When Step 1b ran, the HTML comes first. If its subagent is still running, say so and wait for it. Then open the file (`open <path>` on macOS, `xdg-open <path>` on Linux) and print its path. The user reads it and takes its quiz before they look at the diff.

Then the user reads the diff by the map with Plannotator (`/plannotator-review <pr url>`). Their annotations may arrive as Plannotator feedback or as a file; save them to `notes.md`. They are the user's own notes and outrank your findings.

Answer their questions briefly, point to the file and line, quote the code. When the change's intent is not recoverable from the code, say so and record it as a question for the author. Do not invent the author's reasoning.

## Step 4: Defend the change (offer it; Full path only)

The HTML quiz already checked that the user understands the change. This step checks whether the change holds up, so its most useful result is "nothing handles this", which becomes a comment. Read the HTML's quiz first and do not ask about a scenario it already covers.

The user answers as if they wrote it, using only the diff and the repository. Four questions, one at a time, each aimed at the riskiest part:

1. **Failure.** What happens when this call fails or the data is missing?
2. **Falsifiability.** Which test fails if this logic is wrong?
3. **Reversibility.** How is this undone after it ships?
4. **Worst case.** Walk through the worst case in production.

When a smaller alternative or a cost (latency, money, coupling, operability) comes up along the way, note it in `notes.md` for Step 5.

Ask each one as a quiz with `AskUserQuestion`:

- Anchor the question in a concrete scenario on this diff: name the file and line, the input and the state.
- Give 3–4 options, each a plausible reading of the code, with exactly one that the code supports. When the code does not handle the case, the correct option says so ("Nothing handles it: …").
- Pitch it at medium difficulty: answering requires understanding the change, but there are no gotchas. Vary where the correct option sits, and keep every label neutral.
- The user can still type their own answer with "Other"; grade it the same way.

After each answer, give one of three verdicts and quote the code:

- **Correct:** the answer is in the code; name the file and line.
- **Missed:** the code holds the answer, but the user picked something else; point to where it is.
- **Not in the code:** record it in `notes.md` as a candidate comment.

Then ask the next question.

## Step 5: Comments and decision

Write `comments.md`. The user's own notes first, then the findings they agreed with. At most seven, ranked. Each one: file and line; the issue in one sentence; the concrete change or question; severity — blocker / should fix / question / nit. Short, in the user's voice.

End with the decision: approve, approve with comments, or request changes. Split conditions into before merge and after merge with an owner.

Never post comments, resolve threads, approve or merge without the user's explicit go-ahead naming what to post. The approval is theirs.

## Step 6: Conventions

Append to `pr-conventions.md` only what generalizes beyond this PR: a pattern the user accepted or rejected, a rule they enforced, a trap this codebase repeats. Not this PR's details.
