#!/bin/bash
# Runs the improve-skills skill headless in report-only mode, for the scheduled
# launchd job or by hand. Nobody approves diffs in an unattended run, so the
# session drafts proposals into one HTML report and stops: it edits no skill,
# logs no decision and marks no session. Apply the proposals later with an
# interactive /improve-skills.
#
# The session gets only what the review needs: read access to ~/.claude
# (transcripts, skills, state), the read-only helper subcommands (scan,
# excerpts, history, where, context), the writing-for-agents skill, and Write
# inside the reports directory. --strict-mcp-config drops MCP servers;
# dontAsk denies anything not allowed, since nobody answers prompts;
# --no-session-persistence keeps this run out of the next run's scan. The
# session starts in the skill directory so the helper runs by its relative
# path, as SKILL.md writes it; a cd chained in front would not match the rules.
#
# The skill is user-invoked only, so the session is told to read SKILL.md
# rather than load the skill through the Skill tool.
#
# Environment:
#   IMPROVE_SKILLS_CLAUDE   claude binary (default: claude on PATH)
#   IMPROVE_SKILLS_LOG      log file (default: ~/Library/Logs/improve-skills.log)
#   IMPROVE_SKILLS_REPORTS  report directory (default: ~/.claude/skills/improve-skills/reports)
#   IMPROVE_SKILLS_DAYS     look-back window in days (default: 7)
#   IMPROVE_SKILLS_OPEN     1 opens the report in the default browser (default: 1)
set -u

CLAUDE_BIN="${IMPROVE_SKILLS_CLAUDE:-claude}"
LOG="${IMPROVE_SKILLS_LOG:-$HOME/Library/Logs/improve-skills.log}"
REPORTS="${IMPROVE_SKILLS_REPORTS:-$HOME/.claude/skills/improve-skills/reports}"
DAYS="${IMPROVE_SKILLS_DAYS:-7}"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd -P)"
HELPER="$SKILL_DIR/scripts/skill_feedback.py"
SINCE="$(date -v-"${DAYS}"d +%F)"
REPORT="$REPORTS/$(date +%F).html"

PROMPT="Read $SKILL_DIR/SKILL.md and run the improve-skills skill it defines with the arguments: --since $SINCE --report $REPORT"
PROMPT="$PROMPT The working directory is the skill directory: call the helper as python3 -I scripts/skill_feedback.py <subcommand>, with no cd and no other command chained to it."
PROMPT="$PROMPT Nobody is watching this run: do not ask questions, finish the pass and stop."

mkdir -p "$(dirname "$LOG")" "$REPORTS"
log() { printf '%s %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$*" >>"$LOG"; }

log "start since=$SINCE report=$REPORT"
cd "$SKILL_DIR" || { log "fail: cannot enter $SKILL_DIR"; exit 1; }

"$CLAUDE_BIN" -p "$PROMPT" \
  --strict-mcp-config \
  --no-session-persistence \
  --permission-mode dontAsk \
  --tools "Read,Write,Glob,Grep,Bash,Skill" \
  --add-dir "$HOME/.claude" "$SKILL_DIR" "$REPORTS" \
  --allowedTools \
    "Read(/$HOME/.claude/**)" "Read(/$SKILL_DIR/**)" "Write(/$REPORTS/**)" \
    "Glob" "Grep" "Skill(writing-for-agents)" \
    "Bash(python3 -I $HELPER scan *)" "Bash(python3 -I $HELPER excerpts *)" \
    "Bash(python3 -I $HELPER history *)" "Bash(python3 -I $HELPER where *)" \
    "Bash(python3 -I $HELPER context *)" \
    "Bash(python3 -I scripts/skill_feedback.py scan *)" "Bash(python3 -I scripts/skill_feedback.py excerpts *)" \
    "Bash(python3 -I scripts/skill_feedback.py history *)" "Bash(python3 -I scripts/skill_feedback.py where *)" \
    "Bash(python3 -I scripts/skill_feedback.py context *)" \
  --output-format json </dev/null >>"$LOG" 2>&1
status=$?
echo >>"$LOG"
log "end exit=$status"

if [ -s "$REPORT" ]; then
  [ "${IMPROVE_SKILLS_OPEN:-1}" = 1 ] && open "$REPORT"
else
  log "fail: no report at $REPORT"
  osascript -e "display notification \"No report written; see $LOG\" with title \"improve-skills\"" >/dev/null 2>&1
fi
exit "$status"
