---
name: explain-diff-html
description: Use when the user asks for a rich or HTML explanation of a code change: a diff, branch, commit or PR. Produces one interactive HTML page with background, intuition, a code walkthrough and a quiz. Make sure to use it for requests like "explain this PR in HTML", "explain this diff", "help me understand what this branch changes" or "explain this commit in depth", even if they never say "HTML".
---

# Explain Diff

Make a rich, interactive explanation of the specified code change.

## Requirements

- [GitHub CLI (`gh`)](https://cli.github.com/), authenticated (check with `gh auth status`): needed only when the change is a PR URL. Without it, ask for a local branch or a diff instead.
- A way to open the page: `open` on macOS, `xdg-open` on Linux. Without one, print the path and let the user open it.

## Sections

- **Background:** Explain the existing system relevant to this change. Broadly explore the surrounding code for this. You don't know how much the reader already knows, so include a deep background for beginners (note that it can be skipped if the reader is already familiar), and then a narrower background directly relevant to the change.
- **Intuition:** Explain the core intuition for the code change. Focus on the essence, not the full details. Use concrete examples with toy data. Use figures and diagrams liberally.
- **Code:** Do a high-level walkthrough of the changes to the code. Group and order the changes in an understandable way.
- **Quiz:** Write five questions that test the reader's knowledge of this change. Pitch them at medium difficulty: hard enough that the reader needs to understand the substance of the change to answer, but no gotchas. The goal is to help the reader make sure they have actually understood. Present them as interactive multiple-choice questions; when the reader clicks an option, say whether it is correct and give feedback.

For the shape of a finished page, see [`references/example-outline.md`](references/example-outline.md).

## When another skill calls this one

A reviewing skill (for example `pr-digest`) may run this skill in a background subagent and pass some of these:

- **Diff range.** Explain exactly that range. When the change sits on top of another unmerged change (a stacked PR), the Background section says what it builds on instead of explaining the lower change again.
- **Reading map.** A list of files tagged read closely / skim / skip. Order the Code section by it: files to read closely first, mechanical files last or not at all.
- **Output path.** Write the file there instead of the default path.
- **Language.** Write the page in it.
- **"Do not open."** Skip opening the file at the end; the caller opens it when the reader is ready.

Keep the page to explanation. Review findings, such as failing checks or missing callers, belong to the caller's own report.

## Language

- Before writing, look for a language named for this skill, in the caller's message or the user's instructions (`CLAUDE.md`, `AGENTS.md`): it overrides the language of the prompt. Otherwise write in the language the user writes in. This covers all prose, headings, the table of contents, diagram labels, callouts, quiz questions, answer options and feedback messages. Set the `<html lang>` attribute to match.
- Keep code, file paths, commit hashes, command-line flags, configuration directives and other identifiers in their original form; do not translate or transliterate them.
- Use the established technical terminology of that language where it exists, and keep widely used English terms as they are when a translation would be unclear (for example "pull request", "merge", "deploy").

## Format

- Output a single self-contained HTML file that includes its CSS and JavaScript. Make it one long page with section headers and a table of contents. Add basic responsive styling so it reads on a phone.
- Write with the clarity and flow of Martin Kleppmann, in classic style. Make the transitions between sections smooth.
- Diagrams: pick a small number of diagram families and reuse them throughout to explain different cases. Useful kinds:
  - A very simplified version of the UI the user sees, to explain UI changes.
  - A system diagram showing data flow or communication between components. Include example data.
- Build diagrams from simple HTML elements, and lists from HTML lists.
- For code blocks, use `<pre>` tags. A custom styled `div` instead **must** have `white-space: pre-wrap` in its CSS, or the browser collapses all newlines into one line. Before saving the file, scan each code block in the HTML source and confirm its CSS includes `white-space: pre` or `pre-wrap`.
- Use callouts for key concepts and definitions, important edge cases and the like.

## Where the file goes

Save it in the user's wiki, next to any review notes for the same change, so one change's material stays in one place:

- For a PR: `pr-reviews/<repo-name>/pr-<number>/YYYY-MM-DD-explain.html`, where `<repo-name>` is the repository name without the owner (`octo-org/payments-api` → `pr-reviews/payments-api/`).
- For a branch, a commit or local changes: `pr-reviews/<repo-name>/<branch-slug>/YYYY-MM-DD-explain.html`. For a detached commit, use its short hash as the slug.

The filename starts with today's date so the files sort by time. The user's instructions (`CLAUDE.md`, `AGENTS.md`) say where the wiki is; when they don't, ask once before writing. Keep the file outside the repository's working directory, so it stays out of version control.

## Finishing

- After the file is written and the code-block check has passed, open it in the default browser (`open <path>` on macOS, `xdg-open <path>` on Linux), unless the caller said not to. Do this last, so the page opens once and only after the check.
- In the final message, print the full file path so the user can reopen it later.
