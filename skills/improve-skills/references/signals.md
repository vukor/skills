# Reading the signals

What `skill_feedback.py` reports and how to judge it. The script **nominates** excerpts with cheap heuristics (English and Russian keyword patterns); you decide what each one means. Expect most nominations to be noise.

## How a skill counts as used

A skill is attributed to a session when any of these appears in the main transcript:

- the injected skill body (`Base directory for this skill: <dir>`), which covers both the Skill tool and `/slash` invocation (`via=skill-tool` or `via=slash`);
- a Skill tool call whose body never arrived (`via=skill-tool`, no `dir`);
- a Read of a `.../skills/<name>/SKILL.md` or `references/...` file (`via=read`): consulted, not run. Weight its signals lower.

A skill's **window** runs from its load to the next skill or slash command, capped at `--turns` human messages (default 3). Signals in the window are attributed to it. Sessions where `improve-skills` itself ran count only for `improve-skills`, since a review reads many SKILL.md files without using them.

Sessions modified in the last 10 minutes are skipped (`--include-live` overrides): they are still being written. Subagent transcripts (`<session>/subagents/`) are read only with `--subagents`; they have no human turns, so they add only tool errors.

## Signal kinds

| kind | detected by | strong when | usually noise when |
|---|---|---|---|
| `explicit` | human message with a correction word **and** the skill's name, "skill"/"скилл", "remember", "from now on", "next time" | the user names the skill or asks for a standing change | the user is giving a new task that names a skill (messages like "use the X skill ..." are filtered out) |
| `correction` | human message with a correction word (no, wrong, don't, instead, again, why did you, нет, не так, зачем, опять, вместо ...) | the message rejects or redoes what the skill told the agent to do; read `after assistant` to see what was rejected | the words are part of a fresh request ("don't run plan, just inventory") |
| `interrupt` | `[Request interrupted by user` | the next human turn redirects the approach | the user stopped a slow command or changed topic |
| `rejected` | a tool result saying the user declined the call | the skill's step proposes a call the user keeps declining | one-off caution |
| `tool_error` | `is_error` tool results (first 3 per window) | a command the skill prescribes fails the same way in 2+ sessions | environment state: missing binary, auth, network, a non-zero exit from a later command in a pipeline |
| `denied` | permission-classifier refusals (`--denials` only) | the skill prescribes a command the permission config forbids | almost always: this is policy, not skill content |
| `rework` | the same file edited 3+ times in the window | the skill's output format needed repeated fixing | normal iteration on code |
| `agent_note` | assistant text like "the skill says/doesn't/is missing", "workaround" | the agent improvised around a gap or a wrong step | the agent quoting the skill neutrally |

An explicit correction is the only kind that can justify a patch from one session; every other kind needs recurrence (see [decisions.md](decisions.md)).

## Reading more than the excerpt

`context <session-prefix> <idx> [--around N]` prints the clipped conversation around the event. Use it to see what the assistant did before a correction and whether the session ended with a working method. Prefer it to opening the JSONL; when you must, slice with `sed -n` around the line rather than reading the file whole.

## Known blind spots

- Feedback given in a later session ("last time the pr skill ...") is attributed to whatever skill is loaded then, or to none. Scan with `--skill` and a wider `--since` when the user says a skill has been annoying them.
- Corrections in languages other than English and Russian are missed; only `interrupt` and `rework` catch them.
- A skill used silently (no load event, e.g. its rules copied into CLAUDE.md) is invisible.
