---
status: accepted
date: 2026-09-09
decision-makers: vukor
---

# Organize skills under `skills/<name>/` with intent-based kebab-case names

## Context and Problem Statement

The repository will hold more than one skill over time. Two things need to be settled before more are added:

1. Where a skill's files live and what a skill directory must contain.
2. How skills are named. The first skill was initially called `pr-slack-digest`. That name encoded a delivery channel (Slack) and an artifact type (digest) rather than what the user wants, and it became wrong as soon as the output was made messenger-agnostic.

The `name` field in `SKILL.md` front matter is also how agent runtimes list and trigger the skill, so the directory name, the `name` field, and the `skill_name` in evals must all match.

## Decision

Layout:

```
skills/
  <skill-name>/
    SKILL.md          required; YAML front matter with name + description, then instructions
    evals/
      evals.json      required; test prompts and expectations for the skill
    scripts/          optional; helper scripts the skill tells the model to run
    references/       optional; long docs loaded on demand
    assets/           optional; templates or files used in output
docs/
  decisions/          ADRs (see ADR-0001)
AGENTS.md             agent instructions for this repo
```

Naming:
- Directory name, `name:` front matter, and `skill_name` in `evals/evals.json` are identical
- Lowercase kebab-case, ASCII only
- Name describes the user's intent, not the tool or channel: `pr-review-request`, not `pr-slack-digest`; `pdf-merge`, not `pypdf-helper`
- Avoid product names (Slack, Jira, Teams) in the skill name unless the skill only works with that product

Renaming an existing skill means renaming the directory and updating both `name` fields in the same change.

Portability:
- A skill that needs an external tool (`gh`, `node`, `python3`) declares it in a "Requirements" section near the top of `SKILL.md`, with the check to run and what to tell the user if the tool is missing or unauthenticated
- Skills, ADRs, and `AGENTS.md` do not pin exact tool versions. Users run skills on machines we do not control; instructions must work with whatever current version they have. A genuine minimum is expressed as "X or later", never as a single version

## Consequences

* Good, because a skill can be installed by copying one directory
* Good, because names stay valid when a skill is generalized to more tools
* Good, because agents can locate evals for any skill at a predictable path
* Bad, because renaming a published skill breaks users who installed it under the old name; choose names carefully before publishing
* Neutral, because intent-based names are sometimes longer than tool-based ones

## Implementation Plan

* **Affected paths**: `skills/*/SKILL.md`, `skills/*/evals/evals.json`
* **Dependencies**: none
* **Patterns to follow**: `skills/pr-review-request/` is the reference layout
* **Patterns to avoid**: skill files at the repo root; skills nested more than one level under `skills/`; a `name` that differs from the directory name

### Verification

- [x] Every directory under `skills/` contains `SKILL.md` and `evals/evals.json`
- [x] For each skill, directory name == `name:` in `SKILL.md` == `skill_name` in `evals.json`
- [x] All skill names match `^[a-z0-9]+(-[a-z0-9]+)*$`
- [x] No skill name contains a chat or ticketing product name
- [x] `grep -rnE "v?[0-9]+\.[0-9]+\.[0-9]+" skills/ AGENTS.md` returns no tool version pins
- [x] Every skill that shells out to an external CLI has a "Requirements" section

## Alternatives Considered

* Flat layout, one `SKILL.md` per skill at repo root: rejected because evals, scripts, and references need a home next to the skill.
* Names that describe the artifact (`open-prs-digest`) or channel (`pr-slack-digest`): rejected because they age badly when the skill's scope changes; the user's goal ("ask for reviews") is more stable.

## More Information

* Related: ADR-0001 (ADRs), ADR-0005 (eval workflow, which relies on `evals/evals.json` being at this path)
* Skill anatomy follows the structure described by the `skill-creator` skill (SKILL.md plus optional `scripts/`, `references/`, `assets/`)
