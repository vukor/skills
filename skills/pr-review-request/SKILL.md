---
name: pr-review-request
description: "List the current user's open GitHub pull requests and format them as a clean, plain-text message grouped by repository, ready to paste into any team messenger (Slack, Teams, Discord, Mattermost, email). Use this skill whenever the user wants to see or list their open PRs, share them with the team, or ask teammates for reviews. Trigger on phrases like 'list my open PRs', 'what PRs do I have open', 'show my pull requests', 'write a message to my team about my PRs', 'draft a PR review request', 'look at my github PRs and write to team', or 'tell the team what needs reviewing'. Trigger on any request to list, summarize, or share the user's open PRs, regardless of whether a chat tool is mentioned."
---

# PR Review Request

Generate a short, plain-text message listing the current user's open pull requests, grouped by repository, ready to paste into any team chat or email. The same output works when the user simply wants to see what they have open.

## Requirements

This skill depends on the GitHub CLI, `gh`, being installed and authenticated. Check before doing anything else:

```bash
gh auth status
```

If `gh` is missing, tell the user to install it from https://cli.github.com/ and stop. If it is installed but not logged in, tell the user to run `gh auth login` and stop. Do not try to work around a missing or unauthenticated `gh` by scraping GitHub pages or asking for a token in chat; the CLI handles auth safely and the search command below relies on it.

## What this skill does

1. Fetch all open, non-draft PRs authored by the current user via `gh`
2. Filter out stale PRs (older than 30 days) and archived or clearly unrelated repos
3. Group by repository, sort repos by number of PRs descending
4. Format as plain text: no PR numbers, no descriptions, just ticket + title + URL

## Step 1: Fetch PRs

```bash
gh search prs --author @me --state open \
  --json number,title,url,repository,isDraft,createdAt,body \
  --limit 50
```

Filter the results:
- Exclude `isDraft: true`
- Exclude PRs older than 30 days (compare `createdAt` to today)
- Exclude repos from archived orgs or clearly unrelated personal repos (use judgment)

## Step 2: Extract ticket numbers

For each PR, scan `title` and `body` for an issue-tracker key such as `PROJ-1234` or `ABC-42` (Jira-style `KEY-NUMBER`). The title is the most reliable source, since it is usually in the format `type(TICKET-123): description`.

If no ticket is found, omit the ticket prefix and just use the cleaned title text.

## Step 3: Format the message

Use plain text only. No emoji, no Markdown syntax (`**bold**`, `#` headings, `[links](url)`), and no chat-specific formatting. The output must render identically in Slack, Teams, Discord, Mattermost, and email.

Use this exact structure:

```
Hi team, I have a few PRs open that need review. Would appreciate a look when you have a moment.

<repo-name>
- <TICKET>: <clean title>
  <url>

- <TICKET>: <clean title>
  <url>

<repo-name>
- <TICKET>: <clean title>
  <url>
```

Formatting rules:
- One blank line between repository groups, and one blank line between individual PR entries within a group — each PR is a two-line block (bullet line + URL line), so the blank line is what keeps adjacent PRs visually separate when pasted into a chat
- Repository name on its own line, using the short name (`billing-service`, not `acme/billing-service`) unless the same short name appears under two different owners
- Each PR is a hyphen bullet: `- TICKET: Title` on one line, URL indented two spaces on the next line
- No trailing sign-off, no divider lines, no decorative characters

**Title cleaning**: Strip the conventional-commit prefix from the title. The PR title is often `type(TICKET): actual description`; keep only `actual description`, with the first letter capitalized.

Examples:
- `fix(PROJ-3128): demote probe logs to DEBUG` → `PROJ-3128: Demote probe logs to DEBUG`
- `chore(PROJ-2532): move runbook to wiki` → `PROJ-2532: Move runbook to wiki`
- `feat: add retry to webhook client` (no ticket) → `Add retry to webhook client`
- `fix Argo Workflows RBAC error` (no ticket, no prefix) → `Fix Argo Workflows RBAC error`

**What to omit**:
- PR numbers (`#3846`); the URL already carries them
- Descriptions or summaries; the title says enough
- Merge-order or dependency notes; keep it simple
- Reviewer mentions (`@name`); the user can add those after pasting

## Step 4: Output

Print the final message as a single plain code block so the user can copy-paste it directly. No extra commentary before or after, just the message.

Example output:

```
Hi team, I have a few PRs open that need review. Would appreciate a look when you have a moment.

billing-service
- PROJ-3128: Demote probe logs to DEBUG
  https://github.com/acme/billing-service/pull/412

- PROJ-3140: Add retry to webhook client
  https://github.com/acme/billing-service/pull/418

infra-terraform
- PROJ-2990: Rotate KMS key for audit bucket
  https://github.com/acme/infra-terraform/pull/77

docs
- Fix broken links in onboarding guide
  https://github.com/acme/docs/pull/19
```
