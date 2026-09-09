# skills

A collection of reusable agent skills for AI coding assistants (OpenCode, Claude Code, Cursor, and others).

Skills are loaded by the runtime and tell the agent when and how to do specific things. This repo is installable with the [`skills` CLI](https://github.com/vercel-labs/skills).

## Install a skill

```bash
# Install all skills globally (auto-detects your agent)
npx skills add vukor/skills --global

# Install a specific skill
npx skills add vukor/skills --skill pr-review-request --global

# Preview what is available without installing
npx skills add vukor/skills --list
```

You can also target a specific agent:

```bash
npx skills add vukor/skills --skill pr-review-request --agent opencode --global
```

## Skills

### pr-review-request

Fetches the current user's open GitHub pull requests and formats them as a clean, plain-text message ready to paste into any team chat (Slack, Teams, Discord, Mattermost) or email.

Trigger phrases: "list my open PRs", "write a message to my team about my PRs", "draft a PR review request", "what PRs do I have open"

**Requirements:** [GitHub CLI (`gh`)](https://cli.github.com/) installed and authenticated (`gh auth login`).

## Repository layout

```
skills/<skill-name>/
  SKILL.md              skill instructions and front matter
  evals/evals.json      test prompts and assertions (for development use)
  scripts/              optional helper scripts
  references/           optional reference docs
  assets/               optional templates or files
docs/decisions/         architecture decision records
AGENTS.md               instructions for AI agents working in this repo
```

## Contributing

See `AGENTS.md` for the conventions that govern this repository (naming rules, publishability requirements, plain-text output rules, and the eval workflow).

## License

MIT
