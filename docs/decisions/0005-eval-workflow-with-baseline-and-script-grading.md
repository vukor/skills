---
status: accepted
date: 2026-09-09
decision-makers: vukor
---

# Test skills with paired with-skill and baseline runs graded by script

## Context and Problem Statement

A skill is a prompt, and prompts regress silently: an edit that reads fine can change model behaviour in ways the author does not notice. We need a repeatable way to check that a skill (a) does what its `evals.json` promises and (b) actually adds value over the model with no skill loaded.

Constraints:
- Skills in this repo call live tools (`gh`) against the author's real accounts, so eval outputs contain private data
- Runs cost model time; the workflow should be cheap enough to repeat after every meaningful edit
- Grading by reading outputs is slow and inconsistent across iterations

## Decision

Follow the `skill-creator` eval loop with these specifics:

**Test definitions** live in `skills/<name>/evals/evals.json`:
- 3 or more realistic prompts phrased the way a user would type them
- An `expectations` list per prompt; each item is an object with a human-readable `text` ("No PR numbers like #3846 appear in the output", not a vibe like "output looks clean") and a declarative `check` spec that says how to verify it mechanically:

  ```json
  {"text": "No PR numbers like #3846 appear in the output", "check": "no_regex", "pattern": "#\\d{2,}"}
  ```

  The check types (`regex`, `no_regex`, `line_pattern`, `line_sequence`, `json_values_absent`, `all_of`) and pattern presets (`preset:emoji`, `preset:markdown`, ...) are documented in `scripts/checks.py`. Keeping the statement and its check together in one place means there is no second file to fall out of sync when an expectation is added or reworded
- When a review round produces new feedback, add it as a new expectation before re-running so the fix is measured, not assumed

**Runs**: for each prompt spawn two independent subagents in the same turn:
- `with_skill`: reads `SKILL.md` first, then does the task
- `without_skill`: same prompt, no skill loaded (baseline)

Both save the user-facing output to `message.txt` (or the artifact the skill produces) plus raw tool output for auditing.

**Workspace layout** (`eval-workspaces/` at the repo root, gitignored; one subdirectory per skill so all local artifacts sit under a single ignored path):

```
eval-workspaces/
  <skill-name>/
    iteration-N/
      benchmark.json / benchmark.md    aggregate produced by skill-creator
      feedback.json                    human review from the viewer
      eval-<id>-<slug>/
        eval_metadata.json
        with_skill/
          outputs/
          run-1/grading.json
        without_skill/
          outputs/
          run-1/grading.json
```

**Grading** uses three committed, skill-agnostic scripts under `scripts/`:

- `grade.py` — entry point; `--skill <name> --workspace <path>` grades, `--validate` only checks that `evals.json` is gradable, `--list` shows skills that have an `evals.json`
- `grade_engine.py` — validates every expectation, resolves eval directories, runs checks against each output, writes `grading.json`
- `checks.py` — the library of check types and pattern presets that `evals.json` refers to

There is no per-skill Python. Everything specific to a skill is expressed as check specs inside its own `evals.json`, so adding grading for a new skill means writing `evals.json`, nothing else. No executable code lives inside `skills/`, which keeps the published, installable tree free of scripts.

`grading.json` uses `expectations: [{text, passed, evidence}]` and a `summary` block with `passed`, `failed`, `total`, `pass_rate`, matching the `skill-creator` schema so `aggregate_benchmark` and `generate_review.py` can consume it.

### Grader contract

- Run from the repo root: `python3 scripts/grade.py --skill <name>`; `--workspace` defaults to the highest-numbered `eval-workspaces/<name>/iteration-N` and can be passed explicitly to grade an older iteration
- After editing `evals.json`, run `python3 scripts/grade.py --skill <name> --validate`; it fails on bare-string expectations, unknown check types, missing parameters, and regexes that do not compile
- Eval directory names are `eval-<id>-<slug>` where `slug` is the eval's `slug` field if present, otherwise the prompt lowercased, non-alphanumerics collapsed to `-`, truncated to about 40 characters
- The engine reads `<eval-dir>/<config>/outputs/message.txt`; checks that need other artifacts (for example `json_values_absent` reading `raw_gh.json`) resolve them relative to that `outputs/` directory
- Eval directories without a `message.txt` are skipped with a printed warning, so a partially run iteration still grades what it has; if nothing at all is graded the exit code is 2
- Stdlib only (`argparse`, `json`, `os`, `re`, `sys`)

**Human review** happens in the `skill-creator` viewer after every iteration; feedback drives the next skill edit. Later iterations pass `--previous-workspace` so the reviewer sees the diff.

**Done criteria**: with-skill passes 100% of expectations on all prompts and the reviewer submits no further feedback. Baseline pass rate is recorded as evidence the skill is doing work.

## Consequences

* Good, because a regression shows up as a failing assertion, not a subjective impression
* Good, because baseline runs prove the skill is needed; if baseline also scores 100% the skill is redundant
* Good, because the grader is reusable across iterations with small additions
* Bad, because each iteration spends six subagent runs and a few minutes of wall time
* Bad, because regex checkers can produce false results on unexpected output shapes; spot-check failing baseline assertions each iteration to confirm they are real
* Neutral, because eval outputs contain real data and must stay local (ADR-0003)

## Implementation Plan

* **Affected paths**: `skills/<name>/evals/evals.json`, `scripts/grade.py`, `scripts/grade_engine.py`, `scripts/checks.py`, `eval-workspaces/<name>/` (local), `.gitignore`
* **Dependencies**: Python 3 (stdlib only) for the graders; the `skill-creator` skill at `~/.agents/skills/skill-creator/` for `scripts.aggregate_benchmark` and `eval-viewer/generate_review.py`
* **Patterns to follow**: `skills/pr-review-request/evals/evals.json` is the reference for writing check specs. When a new skill needs a kind of check that `scripts/checks.py` does not offer, add a generic check type there (with a docstring entry) rather than anything skill-specific
* **Patterns to avoid**: grading by eyeballing; adding expectations that need human judgment to `evals.json` (keep those for viewer feedback); running with-skill first and baselines later (spawn all together so conditions match); bare-string expectations with no `check`; per-skill Python anywhere, including under `scripts/`
* **Commands**:

  ```bash
  # from the repo root
  python3 scripts/grade.py --skill <name> --validate
  python3 scripts/grade.py --skill <name>                                   # newest iteration
  python3 scripts/grade.py --skill <name> --workspace eval-workspaces/<name>/iteration-N

  # from ~/.agents/skills/skill-creator/
  python3 -m scripts.aggregate_benchmark <repo>/eval-workspaces/<name>/iteration-N --skill-name <name>
  python3 eval-viewer/generate_review.py <repo>/eval-workspaces/<name>/iteration-N --skill-name <name> \
    --benchmark <repo>/eval-workspaces/<name>/iteration-N/benchmark.json \
    [--previous-workspace <repo>/eval-workspaces/<name>/iteration-N-1]
  ```

### Verification

- [x] `skills/pr-review-request/evals/evals.json` has 3 or more prompts; every expectation is an object with `text` and a `check` spec, and `scripts/grade.py --skill pr-review-request --validate` passes
- [x] Each iteration directory contains `benchmark.json` and per-eval `run-1/grading.json` for both configurations
- [x] `grading.json` uses `expectations: [{text, passed, evidence}]` and `summary: {passed, failed, total, pass_rate}`
- [x] Iteration 2 with-skill pass rate is 100% (28/28); baseline 61%
- [x] `eval-workspaces/` is gitignored and absent from `git status`
- [x] `scripts/grade.py`, `scripts/grade_engine.py`, and `scripts/checks.py` contain no skill names or skill-specific logic
- [x] No executable code lives inside `skills/`
- [x] A synthetic good output passes all checks and a synthetic bad output (Markdown, emoji, PR number, CC prefix, description line, leaked draft URL) fails each corresponding check
- [x] Every eval in `evals.json` has a graded run in the newest iteration (iteration 3 covers evals 1 through 4; with-skill 35/35, baseline 25/35)

## Alternatives Considered

* Manual review only, no assertions: rejected because it does not catch regressions and cannot be compared across iterations.
* With-skill runs only, no baseline: rejected because it cannot show whether the skill adds anything; the baseline run for eval 3 showed the model already picks plain text when "Teams" is mentioned, which is useful to know.
* LLM-as-grader for every assertion: rejected for these skills because the assertions are string-pattern checks that a regex does faster and deterministically; reserve LLM grading for subjective criteria.

## More Information

* `skill-creator` skill: `~/.agents/skills/skill-creator/SKILL.md`, sections "Running and evaluating test cases" and "Improving the skill"
* Related: ADR-0002 (evals path), ADR-0003 (workspace stays local), ADR-0004 (formatting assertions)
