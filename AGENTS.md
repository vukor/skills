# AGENTS.md

Instructions for AI agents working in this repository. Humans are welcome to read it too.

## What this repo is

A collection of reusable agent skills, each a `SKILL.md` with YAML front matter plus evals. The repo is published publicly. Skills are written to be loaded by agent runtimes (OpenCode, Claude Code, and similar) and must work for any user, not only the author.

## Read before editing

1. `docs/decisions/README.md` and any accepted ADR that touches the area you are changing. ADRs are short and contain an Implementation Plan and Verification checklist.
2. The `SKILL.md` and `evals/evals.json` of the skill you are editing.

If your change would contradict an accepted ADR, stop and propose a superseding ADR rather than diverging silently.

## Layout

```
skills/<skill-name>/
  SKILL.md              required
  evals/evals.json      required
  scripts/ references/ assets/   optional
docs/decisions/         ADRs
AGENTS.md               this file
<skill-name>-workspace/ local eval artifacts, gitignored, never commit
```

See ADR-0002 for naming rules. In short: lowercase kebab-case, name the user's intent, and keep the directory name, `name:` front matter, and `skill_name` in evals identical.

## Rules that apply to every skill

### Content must be publishable (ADR-0003)

- No employer names, internal repo names, real ticket keys, or real usernames in any tracked file
- Use placeholders: `PROJ-1234`, `acme/billing-service`, `@reviewer`, "wiki", "issue tracker"
- Public product names (GitHub, Slack, Jira, Terraform) are fine when they are the subject of the instruction
- Before committing, grep tracked files for the identifiers you were exposed to during eval runs

### Chat-message output is plain text (ADR-0004)

If a skill produces text meant to be pasted into a messenger or email:
- No emoji (including `:shortcode:` forms)
- No Markdown or Slack mrkdwn (`**bold**`, `*bold*`, `#`, `[text](url)`, `<url|text>`)
- No divider lines or decorative characters
- Bare URLs on their own line; `-` bullets; blank lines between blocks
- Emit the final message in one fenced code block with no commentary around it

### Skill writing style

- Description front matter carries all "when to trigger" information and should be a little pushy; the body carries "how"
- Explain why a rule exists instead of stacking MUSTs; the model follows reasoning better than shouting
- Keep `SKILL.md` under about 500 lines; move long material to `references/`
- Include at least one full example output
- Use imperative voice

## Testing a skill (ADR-0005)

Every non-trivial edit to a `SKILL.md` gets an eval run before it is considered done.

1. Update `evals/evals.json` first. Turn any new requirement into a mechanically checkable expectation.
2. Spawn, in the same turn, one `with_skill` and one `without_skill` subagent per prompt. Save outputs under `<skill-name>-workspace/iteration-N/eval-<id>-<slug>/{with_skill,without_skill}/outputs/`.
3. Grade with a script (`grade.py`, one checker per expectation, regexes over the output). Write `run-1/grading.json` with `text`, `passed`, `evidence`, and a `summary` block.
4. Aggregate and open the viewer using the `skill-creator` skill:
   ```bash
   cd ~/.agents/skills/skill-creator
   python3 -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   python3 eval-viewer/generate_review.py <workspace>/iteration-N --skill-name <name> \
     --benchmark <workspace>/iteration-N/benchmark.json [--previous-workspace <workspace>/iteration-N-1]
   ```
5. Wait for the human to review, read `feedback.json`, edit the skill, repeat with a new iteration directory.

Done means: with-skill passes 100% of expectations, baseline is meaningfully lower, and the reviewer has no further feedback.

Reference implementation: the newest `grade.py` under `pr-review-request-workspace/` (local only; recreate from ADR-0005 if missing).

## Installing skills from this repo

Skills in this repo are installable via the [`skills` CLI](https://github.com/vercel-labs/skills) without any build step or npm publish. The CLI discovers every `SKILL.md` under `skills/` automatically.

```bash
# List available skills
npx skills add <owner>/<repo> --list

# Install a specific skill globally
npx skills add <owner>/<repo> --skill <skill-name> --global

# Install all skills globally, targeting a specific agent
npx skills add <owner>/<repo> --global --agent opencode
```

The only fields the `skills` CLI reads from `SKILL.md` are `name` and `description` in the YAML front matter. The `evals/` directory is copied alongside the skill but is ignored at runtime — it is only used during development.

## Adding a new skill

1. Load the `skill-creator` skill and follow its interview to capture intent.
2. Create `skills/<name>/SKILL.md` and `skills/<name>/evals/evals.json` following ADR-0002.
3. Apply the content and output rules above.
4. Run the eval loop until done.
5. If the new skill introduces a cross-cutting convention (new output type, new dependency, new directory), write an ADR for it.

## Git

- Conventional commits: `<type>(<scope>): <description>`, e.g. `feat(pr-review-request): add blank line between PR entries`
- Scope is the skill name, or `adr`, `agents`, `repo`
- Never commit `*-workspace/` directories
- Do not push or open PRs unless asked

## Tooling notes

- `gh` (GitHub CLI) is required by `pr-review-request`; it runs against whatever account `gh auth status` reports. Skills that depend on an external CLI say so in a "Requirements" section near the top of `SKILL.md` and tell the model what to do when the tool is missing.
- Do not pin tool versions in skills, ADRs, or this file. Skills are used on machines we do not control; write instructions that work with whatever current version the user has. If a script genuinely needs a minimum version, say "requires Node 20 or later" rather than one exact version.
- Node: run `nvm use latest` (or use the system Node) before `node`/`npm`/`npx` commands; the `adr-skill` scripts need Node available on PATH.
- Python 3 stdlib is enough for graders; no virtualenv required
