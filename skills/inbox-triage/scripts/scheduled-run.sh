#!/bin/bash
# Runs the inbox-triage skill headless, for the scheduled launchd job or by hand.
# Every run starts Claude; the skill itself changes nothing when the inbox has
# nothing new, and each run appends its result to the log.
#
# The session gets only what triage needs: read, write and edit inside the
# inbox folder, read access to installed skills and the plugin cache (for
# comparing a find with what is already installed), file search, web page
# fetch, and the skill itself. --restricted removes the shell, ignores the
# user's settings files (their allow rules would widen the session) and keeps
# file tools inside the working directories; --strict-mcp-config drops MCP
# servers; dontAsk denies anything not allowed, since nobody answers prompts.
#
# Restricted mode does not load ~/.claude/skills, so the skill is handed to
# the session as a one-run plugin that links this skill's directory.
#
# Environment:
#   INBOX_TRIAGE_VAULT   path to the vault that holds !Inbox/ (required)
#   INBOX_TRIAGE_CLAUDE  claude binary (default: claude on PATH)
#   INBOX_TRIAGE_LOG     log file (default: ~/Library/Logs/inbox-triage.log)
#   INBOX_TRIAGE_LANGUAGE  language for note prose, e.g. Russian (default:
#                        none, so the skill falls back to English; restricted
#                        mode may not load your global instructions)
set -u

VAULT="${INBOX_TRIAGE_VAULT:?set INBOX_TRIAGE_VAULT to the vault path}"
INBOX="$VAULT/!Inbox"
CLAUDE_BIN="${INBOX_TRIAGE_CLAUDE:-claude}"
LOG="${INBOX_TRIAGE_LOG:-$HOME/Library/Logs/inbox-triage.log}"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd -P)"
SKILL="inbox-triage-runner:inbox-triage"
PROMPT="Run the $SKILL skill on the inbox at $INBOX."
[ -n "${INBOX_TRIAGE_LANGUAGE:-}" ] && PROMPT="$PROMPT Write the notes in $INBOX_TRIAGE_LANGUAGE."
PROMPT="$PROMPT Nobody is watching this run: do not ask questions, finish the pass and stop."

mkdir -p "$(dirname "$LOG")" "$INBOX"
log() { printf '%s %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$*" >>"$LOG"; }

PLUGIN="$(mktemp -d "${TMPDIR:-/tmp}/inbox-triage-run.XXXXXX")" || { log "fail: mktemp"; exit 1; }
trap 'rm -rf "$PLUGIN"' EXIT
mkdir -p "$PLUGIN/.claude-plugin" "$PLUGIN/skills"
printf '{"name":"inbox-triage-runner","version":"1.0.0","description":"One-run wrapper for the inbox-triage skill"}\n' \
  >"$PLUGIN/.claude-plugin/plugin.json"
ln -s "$SKILL_DIR" "$PLUGIN/skills/inbox-triage"

log "start inbox=$INBOX"
cd "$INBOX" || { log "fail: cannot enter $INBOX"; exit 1; }

"$CLAUDE_BIN" -p "$PROMPT" \
  --restricted \
  --strict-mcp-config \
  --no-session-persistence \
  --permission-mode dontAsk \
  --plugin-dir "$PLUGIN" \
  --tools "Read,Write,Edit,Glob,Grep,WebFetch,Skill" \
  --add-dir "$HOME/.claude/skills" "$HOME/.claude/plugins/cache" \
  --allowedTools \
    "Read(/$INBOX/**)" "Edit(/$INBOX/**)" "Write(/$INBOX/**)" \
    "Read(/$HOME/.claude/skills/**)" "Read(/$HOME/.claude/plugins/cache/**)" \
    "Glob" "Grep" "WebFetch" "Skill($SKILL)" \
  --output-format json </dev/null >>"$LOG" 2>&1
status=$?
echo >>"$LOG"
log "end exit=$status"
exit "$status"
