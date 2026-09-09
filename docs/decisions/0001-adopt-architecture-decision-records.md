---
status: accepted
date: 2026-09-09
decision-makers: vukor
---

# Adopt architecture decision records

## Context and Problem Statement

This repository holds reusable agent skills (`SKILL.md` files plus evals) that are intended to be published publicly. The decisions that shape a skill (its name, output format, what content is allowed in it, how it is tested) were made in conversation with an AI agent and would otherwise live only in chat history.

Future work on this repo will also be done largely by AI agents. Without a written record, an agent editing a skill has no way to know whether a pattern is deliberate (for example, "no emoji in output") or accidental, and may undo it.

We need a lightweight, version-controlled way to capture the "why" next to the skills themselves.

## Decision

Adopt Architecture Decision Records (ADRs), stored in `docs/decisions/`.

Conventions:
- One ADR per file, named `NNNN-title-with-dashes.md`, numbered sequentially
- Front matter with `status`, `date`, `decision-makers`
- New ADRs start as `proposed`, move to `accepted` or `rejected`; superseded ADRs link to their replacement
- Every ADR contains an Implementation Plan and Verification checklist so an agent can act on it without follow-up questions
- The index at `docs/decisions/README.md` lists every ADR with status and date
- `AGENTS.md` at the repo root points agents to this directory and requires them to read relevant accepted ADRs before editing a skill

## Consequences

* Good, because design intent survives across sessions and agents
* Good, because an agent can check a proposed change against accepted ADRs instead of guessing
* Good, because publishing the repo also publishes the reasoning, which helps outside contributors
* Bad, because each cross-cutting change now needs a short ADR, adding a few minutes of work
* Neutral, because ADRs need occasional review to mark stale ones deprecated or superseded

## Implementation Plan

* **Affected paths**: `docs/decisions/` (new), `docs/decisions/README.md` (index), `AGENTS.md` (pointer)
* **Dependencies**: none; ADRs are plain Markdown
* **Patterns to follow**: the simple ADR template (Context, Decision, Consequences, Implementation Plan, Verification, Alternatives, More Information)
* **Patterns to avoid**: ADRs for routine edits inside a skill (typo fixes, example tweaks); those do not need a record

### Verification

- [x] `docs/decisions/` exists with a `README.md` index
- [x] Every ADR file has `status`, `date`, and `decision-makers` front matter
- [x] `AGENTS.md` references `docs/decisions/` and instructs agents to consult it
- [x] Each ADR has a Verification section with checkboxes

## Alternatives Considered

* No formal records, rely on chat history and `SKILL.md` comments: rejected because chat history is not in the repo and skill files should stay lean for the model that loads them.
* Put all conventions in `AGENTS.md` only: rejected because `AGENTS.md` should be short operational guidance; it cannot hold the reasoning and alternatives for each decision without becoming unreadable.
* Wiki or external doc: rejected because it would not travel with the public repo.

## More Information

* MADR: <https://adr.github.io/madr/>
* Michael Nygard, "Documenting Architecture Decisions": <https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions>
