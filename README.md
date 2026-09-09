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
  evals/evals.json      test prompts and checkable expectations (development only)
  scripts/              optional helper scripts the skill itself uses
  references/           optional reference docs
  assets/               optional templates or files
scripts/
  grade.py              entry point: python3 scripts/grade.py --skill <name>
  grade_engine.py       runs the checks from evals.json against eval outputs
  checks.py             generic check types (regex, no_regex, line_pattern, ...)
eval-workspaces/        local eval run outputs, gitignored (contains real account data)
docs/decisions/         architecture decision records
AGENTS.md               instructions for AI agents working in this repo
```

Grading code never lives inside `skills/`; it sits under the repo-level `scripts/` and is skill-agnostic, so installing a skill does not pull in the test harness.

## Running evals

Each skill's `evals/evals.json` lists prompts and, for each prompt, a set of expectations. Every expectation pairs a human-readable statement with a declarative check the grader can run:

```json
{"text": "No PR numbers like #3846 appear in the output", "check": "no_regex", "pattern": "#\\d{2,}"}
```

Available check types (`regex`, `no_regex`, `line_pattern`, `line_sequence`, `json_values_absent`, `all_of`) and pattern presets (`preset:emoji`, `preset:markdown`, ...) are documented in `scripts/checks.py`. Adding grading for a new skill means writing its `evals.json`; no Python is needed.

Requires Python 3 (standard library only).

```bash
# confirm every expectation in evals.json is gradable
python3 scripts/grade.py --skill pr-review-request --validate

# run an eval iteration with your agent (see AGENTS.md for the with-skill / baseline procedure);
# outputs go to eval-workspaces/<skill>/iteration-N/eval-<id>-<slug>/{with_skill,without_skill}/outputs/

# grade the newest iteration (or pass --workspace to pick one)
python3 scripts/grade.py --skill pr-review-request

# list skills that have evals
python3 scripts/grade.py --list
```

The grader writes `run-1/grading.json` next to each output in the format the `skill-creator` eval viewer expects (see `AGENTS.md` for the aggregate and review steps). Eval outputs come from live tools against your own accounts, so `eval-workspaces/` is gitignored and must stay local.

## Contributing

See `AGENTS.md` for the conventions that govern this repository (naming rules, publishability requirements, plain-text output rules, and the eval workflow).

## License

MIT
