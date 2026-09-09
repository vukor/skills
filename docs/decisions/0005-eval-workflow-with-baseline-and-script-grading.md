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
- An `expectations` list per prompt; each item is a single, mechanically checkable statement ("No PR numbers like #3846 appear in the output"), not a vibe ("output looks clean")
- When a review round produces new feedback, add it as a new expectation before re-running so the fix is measured, not assumed

**Runs**: for each prompt spawn two independent subagents in the same turn:
- `with_skill`: reads `SKILL.md` first, then does the task
- `without_skill`: same prompt, no skill loaded (baseline)

Both save the user-facing output to `message.txt` (or the artifact the skill produces) plus raw tool output for auditing.

**Workspace layout** (sibling of `skills/`, gitignored):

```
<skill-name>-workspace/
  iteration-N/
    grade.py                         grader for this iteration
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

**Grading** is a Python script (`grade.py`) with one checker function per expectation using regexes over the output. `grading.json` uses the fields `text`, `passed`, `evidence` and a `summary` block, so `skill-creator`'s `aggregate_benchmark` and `generate_review.py` can consume it. Assertion text in `grade.py` is copied verbatim from `evals.json`.

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

* **Affected paths**: `skills/<name>/evals/evals.json`, `<name>-workspace/` (local), `.gitignore`
* **Dependencies**: Python 3 (stdlib only) for `grade.py`; the `skill-creator` skill at `~/.agents/skills/skill-creator/` for `scripts.aggregate_benchmark` and `eval-viewer/generate_review.py`
* **Patterns to follow**: `pr-review-request-workspace/iteration-2/grade.py` is the reference grader; copy and extend it for new skills or iterations
* **Patterns to avoid**: grading by eyeballing; adding expectations that need human judgment to `evals.json` (keep those for viewer feedback); running with-skill first and baselines later (spawn all together so conditions match)
* **Commands** (from `~/.agents/skills/skill-creator/`):

  ```bash
  python3 -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
  python3 eval-viewer/generate_review.py <workspace>/iteration-N --skill-name <name> \
    --benchmark <workspace>/iteration-N/benchmark.json \
    [--previous-workspace <workspace>/iteration-N-1]
  ```

### Verification

- [x] `skills/pr-review-request/evals/evals.json` has 3 prompts, each with mechanically checkable expectations
- [x] Each iteration directory contains `grade.py`, `benchmark.json`, and per-eval `run-1/grading.json` for both configurations
- [x] `grading.json` entries have `text`, `passed`, `evidence`
- [x] Iteration 2 with-skill pass rate is 100% (28/28); baseline 61%
- [x] `*-workspace/` is gitignored and absent from `git status`

## Alternatives Considered

* Manual review only, no assertions: rejected because it does not catch regressions and cannot be compared across iterations.
* With-skill runs only, no baseline: rejected because it cannot show whether the skill adds anything; the baseline run for eval 3 showed the model already picks plain text when "Teams" is mentioned, which is useful to know.
* LLM-as-grader for every assertion: rejected for these skills because the assertions are string-pattern checks that a regex does faster and deterministically; reserve LLM grading for subjective criteria.

## More Information

* `skill-creator` skill: `~/.agents/skills/skill-creator/SKILL.md`, sections "Running and evaluating test cases" and "Improving the skill"
* Related: ADR-0002 (evals path), ADR-0003 (workspace stays local), ADR-0004 (formatting assertions)
