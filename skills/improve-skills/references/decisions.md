# Deciding a candidate

Rules for turning nominated excerpts into decisions. The bias is toward **no change**: a skill edited on thin evidence collects sediment and self-imposed constraints faster than it improves.

## Candidate lesson

A candidate is one statement of what the skill should say differently, phrased as the rule it would become. Several excerpts can support one candidate; one excerpt can yield none.

**Pattern key**: `<skill>.<kebab-topic>`, e.g. `pr.template-lookup`. Stable once assigned: before minting a key, read `history --skill <name>` and reuse a key that names the same lesson. The key is how recurrence accumulates across runs.

## Evidence grade

- **Explicit**: the user corrected the skill's behaviour and marked it standing ("the skill should ...", "always/never ...", "from now on", "remember", or named the skill while correcting it). Counts on its own.
- **Corroborated**: a correction, rework or failure whose cause you can trace to a specific sentence (or a missing step) in the skill, shown by `context`.
- **Weak**: a failure or improvisation with no traceable cause in the skill, an inferred preference, a one-off request, assistant-only reasoning, or politeness/silence. Never enough alone.

## Recurrence threshold

| grade | needs |
|---|---|
| explicit | 1 session |
| corroborated | the same key in 2+ distinct sessions within 30 days |
| weak | the same key in 3+ distinct sessions within 30 days, and you can now trace the cause |

Count sessions from the current excerpts plus `history` (its `in 30d` column). Below the bar the decision is **pending**: log it with its sessions so a later run can count it. Pending entries older than 30 days stop counting.

## Do not capture

These become self-imposed constraints that outlive their cause. Discard them, with a one-line note:

- **Environment state**: missing binaries, unconfigured credentials, network or auth failures, permission-config denials, path mismatches after a move. The user fixes these; the skill does not. If the fix is a durable setup step the skill should run, capture the step, not "X does not work".
- **Negative claims about tools** ("tool Y is broken", "Z cannot be used"). They harden into refusals long after the problem is fixed.
- **Transient errors** that resolved within the session. If a retry worked, the lesson is the retry, not the failure.
- **Unresolved failures**: the session ended without a working method. Dead ends are not a procedure. Capture only an alternative you know works.
- **One-off task content**: this ticket, this PR, this file, this person. A skill holds the class of task.
- **Restated environment**: what CLAUDE.md, the repo's docs, a tool's schema or `--help` already says. Route a CLAUDE.md gap to `/retro`.
- **Preferences framed as universal** when the evidence is one context; keep the scope the evidence supports.
- **Anything the user asked not to keep** ("just this once", "don't remember this").

## Decisions

- **discard**: fails the do-not-capture list, is already stated in the skill, or is too vague to write as a rule. Log it so it is not re-judged.
- **pending**: plausible but below the threshold. Log it.
- **patch**: the skill that was in play is wrong, missing a step, or stale. The default target.
- **merge**: the lesson belongs in an existing umbrella skill, or two skills keep being loaded together for the same job with overlapping steps. Fold the unique content into the umbrella and add a pointer from the sibling; leave the sibling in place.
- **create**: a recurring class of task (3+ sessions) that no skill covers, with a clear trigger. Name it at the class level; a name that only fits one task means the lesson is a patch or a reference file instead.

## Preference order

Take the earliest target that fits:

1. **Patch the skill in play**, the one loaded when the feedback happened.
2. **Patch an existing umbrella** that covers the class of task, found by reading the descriptions of the user's skills.
3. **Add or extend a `references/<topic>.md`** under an existing skill, for depth only some runs need, with a one-line pointer from its SKILL.md. Extend an existing topical file before creating one; name files by topic, never by date or incident.
4. **Create a new class-level skill.** Draft it with the `skill-creator` conventions and `writing-for-agents`.

## Lesson shape

What the diff adds or changes, so the skill reads as instructions and not as a diary:

- Fix the sentence that misled, in place. An "UPDATE: actually ..." under the old text is sediment.
- A pitfall is a rule plus one clause of why, attached to the step it affects.
- Same lesson twice is one rule: search the skill and its references first, and sharpen the existing sentence.
- No incident detail: no dates, ticket or PR numbers, session ids, quoted chat. Those go in the decisions log.
- Always-on rules sit in SKILL.md; occasional depth goes to `references/`.
- Keep the target skill's language and voice.
- Smallest diff that carries the rule: one sentence beats a new section.

## Signals of overlap

When two skills keep appearing in the same sessions for the same job, or a candidate fits two skills equally, note it in the report as a merge candidate. Consolidation across the library is a separate, deliberate pass, not a side effect of a feedback patch.
