# Fixtures

Synthetic sessions for the improve-skills evals. Run the helper with `HOME` pointed here so it reads only these files:

```sh
HOME=<this dir>/home python3 -I -B scripts/skill_feedback.py scan --all --include-live
```

The broken-link case is created at eval time (`ln -s missing-target <home>/.claude/skills/gone-skill`), since git does not keep a dangling link portably.

The skill body path in the transcripts is the literal `HOME/.claude/skills/demo-notes`; `where demo-notes` resolves the installed copy under `home/.claude/skills/`.
