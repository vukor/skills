---
status: accepted
date: 2026-09-09
decision-makers: vukor
---

# Produce plain-text output for skills that write chat messages

## Context and Problem Statement

`pr-review-request` produces a message the user pastes into a team chat. The first version targeted Slack specifically: it used emoji in the greeting, an emoji per repository header, box-drawing divider lines (`──────`), and the description mentioned Slack by name.

Users paste into different tools (Slack, Microsoft Teams, Discord, Mattermost, email). Each has its own markup dialect: Slack uses `*bold*` and `<url|text>` links, Teams and Discord use Markdown-style `**bold**`, email clients render neither. Emoji render inconsistently and read as unprofessional in some workplaces. Box-drawing characters wrap badly on narrow clients.

Eval baselines confirmed the problem: with no skill, the model produced Slack mrkdwn links (`<https://...|#3846>`), `:wave:` shortcodes, `*bold*` headers, and emoji in every run, even when the prompt said "Teams".

## Decision

Any skill in this repo whose output is meant to be pasted into a messaging tool produces plain text:

- No emoji, including shortcode forms like `:wave:`
- No Markdown or mrkdwn syntax: no `**bold**`, `*bold*`, `#` headings, `[text](url)`, `<url|text>`
- No decorative characters: no box-drawing lines, no runs of `-`, `=`, or `*` used as dividers
- Structure comes from line breaks, indentation, and simple `-` bullets only
- URLs appear bare on their own line so every client auto-links them
- Blank lines separate logical blocks (in `pr-review-request`: between repository groups and between individual PR entries)
- The skill description names several messengers or says "any messenger" rather than one product

The final message is emitted inside a single fenced code block so the user copies exactly what was generated, with no surrounding commentary.

## Consequences

* Good, because one output works everywhere; the user does not have to say which tool they use
* Good, because the eval assertions for "no emoji / no Markdown / no dividers" are mechanically checkable
* Bad, because the output cannot use bold repo headers, which some users may find less scannable; whitespace carries the structure instead
* Neutral, because users who want emoji can add them after pasting

## Implementation Plan

* **Affected paths**: `skills/pr-review-request/SKILL.md` (Step 3 "Format the message" and Step 4 "Output"), `skills/pr-review-request/evals/evals.json`
* **Dependencies**: none
* **Patterns to follow**: the "Formatting rules" list and the "Example output" block in `skills/pr-review-request/SKILL.md`
* **Patterns to avoid**: an "emoji guide" or per-tool formatting branches inside a skill; if a future skill truly needs tool-specific markup, it should be a separate skill with the tool in its name (see ADR-0002)
* **Evals**: every chat-output skill includes assertions for "no emoji", "no Markdown syntax", and "no decorative divider lines"

### Verification

- [x] `grep -P "[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]" skills/*/SKILL.md` returns nothing outside negative-rule text
- [x] `evals.json` for `pr-review-request` contains no-emoji, no-Markdown, and no-divider expectations
- [x] With-skill eval runs pass all formatting assertions (iteration 2: 28/28)
- [x] Skill description does not name a single messenger as the only target

## Alternatives Considered

* Ask the user which tool and format accordingly: rejected because it adds a round-trip to every invocation and multiplies the formatting rules and evals per tool.
* Keep Slack-flavoured output as the default: rejected because Slack mrkdwn renders as literal `<url|text>` garbage in Teams and email.
* Lightweight Markdown (bold headers only): rejected because `*text*` and `**text**` mean different things in Slack vs Teams, so there is no single safe form.

## More Information

* Eval evidence: `pr-review-request-workspace/iteration-1/` and `iteration-2/` (local only, see ADR-0003); baseline runs scored 61–62% on formatting assertions, with-skill runs 100%.
* Related: ADR-0002 (naming), ADR-0005 (eval workflow)
