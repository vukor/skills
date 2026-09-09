---
status: accepted
date: 2026-09-09
decision-makers: vukor
---

# Keep skill content free of employer-specific identifiers

## Context and Problem Statement

The skills in this repo are authored while working inside a company and are tested against real internal repositories. The first draft of `pr-review-request` contained internal Jira project keys, internal repository names, and references to internal tooling and documentation systems in its examples. The repo is meant to be published publicly, so anything that identifies the employer, its projects, or its infrastructure must not be committed.

Two separate concerns:
1. **Committed skill files** (`SKILL.md`, `evals.json`, `scripts/`, `references/`) must use neutral placeholders.
2. **Eval run artifacts** (workspace directories produced when running evals) necessarily contain real data from the author's GitHub account and must never be committed.

## Decision

Committed content uses only generic placeholders:

| Kind | Use | Do not use |
|---|---|---|
| Ticket keys | `PROJ-1234`, `ABC-42` | real Jira project keys |
| GitHub owner | `acme` | employer org names |
| Repo names | `billing-service`, `infra-terraform`, `docs`, `web-app` | real internal repo names |
| People | `@reviewer`, "the team" | real usernames |
| Internal systems | "wiki", "issue tracker", "runbook" | product or instance names that reveal the employer |

Well-known public product names (Slack, Teams, Jira, GitHub, Terraform) are allowed when they are the subject of the instruction, since they do not identify the employer.

Eval workspaces (`*-workspace/` next to `skills/`) are listed in `.gitignore` and stay local.

Before any commit, scan the tracked files for the employer's org name, Jira keys, and internal repo names.

## Consequences

* Good, because the repo can be published without a redaction pass
* Good, because examples read as generic to outside users, which is how a public skill should read
* Bad, because the author must remember to translate real examples into placeholders when adding new ones; the pre-commit scan is the safety net
* Neutral, because eval results (which do contain real data) are not shareable as-is; a sanitized sample would need to be created deliberately

## Implementation Plan

* **Affected paths**: `skills/*/SKILL.md`, `skills/*/evals/evals.json`, `.gitignore`
* **Dependencies**: none
* **Patterns to follow**: the examples in `skills/pr-review-request/SKILL.md` (`PROJ-3128`, `acme/billing-service`)
* **Patterns to avoid**: copying a real PR title or URL from an eval run into a skill example without replacing owner, repo, and ticket key
* **Pre-commit check** (run from repo root, expect no output):

  ```bash
  grep -rniE "<employer-org>|<jira-key-prefix>-[0-9]+" skills/ docs/ AGENTS.md
  ```

  Replace the placeholders with the actual identifiers to scan for; do not commit the filled-in command.

### Verification

- [x] `grep -rn` for the employer org name over tracked files returns nothing
- [x] `grep -rnE "[A-Z]{2,}-[0-9]+"` over `skills/` returns only `PROJ-*` or `ABC-*` style placeholders
- [x] `.gitignore` contains `*-workspace/`
- [x] `git status` shows no `*-workspace/` paths as untracked or staged

## Alternatives Considered

* Keep real examples and redact before publishing: rejected because redaction is error-prone and would need to be repeated on every release.
* Maintain two branches (internal with real examples, public with placeholders): rejected as unnecessary maintenance; placeholders are just as instructive for the model.

## More Information

* Related: ADR-0005 (eval workflow) explains why eval workspaces contain real data.
