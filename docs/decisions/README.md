# Architecture Decision Records (ADR)

An Architecture Decision Record (ADR) captures an important decision along with its context, consequences, and an implementation plan detailed enough for a coding agent to act on.

## Conventions

- Directory: `docs/decisions`
- Naming: numbered files, `NNNN-verb-phrase-title.md`
- Front matter: `status`, `date`, `decision-makers`
- Status values: `proposed`, `accepted`, `rejected`, `deprecated`, `superseded`
- Every ADR has an Implementation Plan and a Verification checklist

## Workflow

- Create a new ADR as `proposed`.
- Discuss and iterate.
- When committed: mark it `accepted` (or `rejected`).
- If replaced later: create a new ADR and mark the old one `superseded` with a link.
- Agents: read the relevant accepted ADRs before editing a skill. If a change contradicts one, propose a superseding ADR instead of silently diverging.

## ADRs

- [Adopt architecture decision records](0001-adopt-architecture-decision-records.md) (accepted, 2026-09-09)
- [Organize skills under `skills/<name>/` with intent-based kebab-case names](0002-organize-skills-directory-and-naming.md) (accepted, 2026-09-09)
- [Keep skill content free of employer-specific identifiers](0003-keep-content-free-of-employer-identifiers.md) (accepted, 2026-09-09)
- [Produce plain-text output for skills that write chat messages](0004-plain-text-output-for-chat-skills.md) (accepted, 2026-09-09)
- [Test skills with paired with-skill and baseline runs graded by script](0005-eval-workflow-with-baseline-and-script-grading.md) (accepted, 2026-09-09)
