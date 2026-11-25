#!/usr/bin/env python3
"""Extract per-skill feedback excerpts from Claude Code session transcripts.

Read-only over ~/.claude/projects. Writes only to the state dir
(~/.claude/improve-skills by default) and only from the mark / log / backup
subcommands. Python 3 stdlib only.

Subcommands:
  scan      table of sessions x skills with signal counts (cheap triage)
  excerpts  short evidence excerpts per skill, grouped by session
  context   clipped conversation around one event index (#idx from excerpts)
  where     resolve a skill name to its directory and ownership
  history   prior decisions for a skill (pattern keys, recurrence)
  mark      record session ids as processed
  log       append one decision to decisions.jsonl
  backup    copy a file into the state dir before it is edited
"""
import argparse, datetime as dt, glob, hashlib, json, os, re, shutil, subprocess, sys

HOME = os.path.expanduser("~")
PROJECTS = os.path.join(HOME, ".claude", "projects")
STATE_DIR = os.environ.get("IMPROVE_SKILLS_STATE", os.path.join(HOME, ".claude", "improve-skills"))
SELF = "improve-skills"
WINDOW_DAYS = 30  # recurrence window for pending candidates
FIRST_RUN_DAYS = 14  # default look-back when no state exists yet

# --- signal patterns (EN + RU). Heuristic: they nominate excerpts, the model judges them.
CORRECTION = re.compile(
    r"(?i)(^\s*(no|nope|wrong|stop|wait)\b|\bdon'?t\b|\bdo not\b|\binstead\b|\bactually\b|\bnot what\b|"
    r"\bwhy (did|do|are) you\b|\byou should\b|\bshould(n'?t)? have\b|\bagain\b|\brevert\b|\bundo\b|"
    r"\bthat'?s not\b|\bincorrect\b|\bmissed\b|\byou forgot\b|\bnever\b|\balways\b|\bfrom now on\b|\bremember\b|"
    r"^\s*нет\b|не так|неправильн|неверн|зачем|почему ты|опять|снова|стоп|не надо|не нужно|верни|откат|"
    r"я же|должен был|вместо|забыл|всегда|никогда|впредь|запомни)")
EXPLICIT = re.compile(r"(?i)(\bskill\b|skill\.md|скилл|навык|from now on|remember|запомни|впредь|next time|в следующий раз)")
AGENT_NOTE = re.compile(
    r"(?i)(the skill (says|doesn'?t|does not|is missing|lacks|assumes|expects)|skill'?s (instructions?|step)|"
    r"not covered by the skill|skill (is )?(outdated|wrong|stale)|workaround|the documented (step|command) (fails|failed))")
USE_SKILL = re.compile(r"(?i)^\s*(please\s+)?(use|run|load|invoke)\s+(the\s+)?\S+\s+skill\b")
INTERRUPT = "[Request interrupted by user"
REJECTED = ("doesn't want to proceed", "user rejected", "was rejected", "permission denied by user")
SECRET = re.compile(
    r"(sk-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|xox[abpr]-[A-Za-z0-9-]{10,}|"
    r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}|(?i:(password|passwd|secret|token|api[_-]?key)\s*[=:]\s*)\S+)")
NOISE_PREFIX = ("<command-", "<local-command", "<bash-", "<task-notification", "<system-reminder", "Caveat:")
CMD_NAME = re.compile(r"<command-name>/?([^<\s]+)</command-name>")
CMD_ARGS = re.compile(r"<command-args>(.*?)</command-args>", re.S)
BASE_DIR = re.compile(r"^Base directory for this skill: (\S+)")


def redact(s):
    return SECRET.sub("[REDACTED]", s)


def clip(s, n):
    s = redact(" ".join(s.split()))
    return s if len(s) <= n else s[: n - 1] + "…"


def iso(ts):
    try:
        return dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


# --- state
def state_path(name):
    return os.path.join(STATE_DIR, name)


def load_state():
    try:
        with open(state_path("state.json")) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"version": 1, "last_run": None, "sessions": {}}


def save_state(st):
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = state_path("state.json.tmp")
    with open(tmp, "w") as f:
        json.dump(st, f, indent=1, sort_keys=True)
    os.replace(tmp, state_path("state.json"))


def load_decisions():
    out = []
    try:
        with open(state_path("decisions.jsonl")) as f:
            for line in f:
                if line.strip():
                    out.append(json.loads(line))
    except FileNotFoundError:
        pass
    return out


def load_locks():
    try:
        with open(state_path("locked.txt")) as f:
            return {l.split("#")[0].strip() for l in f if l.split("#")[0].strip()}
    except FileNotFoundError:
        return set()


# --- skill location and ownership
def skill_roots(cwd=None):
    roots = [os.path.join(HOME, ".claude", "skills")]
    roots += glob.glob(os.path.join(HOME, ".claude", "skills", "synced", "*"))
    if cwd:
        roots.append(os.path.join(cwd, ".claude", "skills"))
    return roots


def git_root(path):
    d = path if os.path.isdir(path) else os.path.dirname(path)
    while d and d != "/":
        if os.path.exists(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    return None


def tracked(repo, path):
    """True when git tracks path (an ignored skill inside a dotfiles repo is not versioned)."""
    try:
        r = subprocess.run(["git", "-C", repo, "ls-files", "--error-unmatch", path],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def ownership(skill_dir, name):
    """editable | editable-git:<root> | propose-only:<reason>"""
    if name in load_locks():
        return "propose-only:locked"
    real = os.path.realpath(skill_dir)
    synced = os.path.realpath(os.path.join(HOME, ".claude", "skills", "synced"))
    plugins = os.path.realpath(os.path.join(HOME, ".claude", "plugins"))
    if real.startswith(synced + os.sep) or os.path.realpath(skill_dir).startswith(synced):
        return "propose-only:synced"
    if real.startswith(plugins + os.sep):
        return "propose-only:plugin"
    if "site-packages" in real or "/node_modules/" in real or "/.local/share/" in real:
        return "propose-only:package"
    g = git_root(real)
    if g and tracked(g, os.path.join(real, "SKILL.md")):
        return "editable-git:" + g
    return "editable"


def resolve_skill(name, hint=None, cwd=None):
    cands = []
    if hint and os.path.isfile(os.path.join(hint, "SKILL.md")):
        cands.append(hint)
    bare = name.split(":")[-1]
    for r in skill_roots(cwd):
        p = os.path.join(r, bare)
        if os.path.isfile(os.path.join(p, "SKILL.md")):
            cands.append(p)
    if ":" in name:  # plugin skill, plugin:skill
        plug = name.split(":")[0]
        cands += [os.path.dirname(p) for p in glob.glob(
            os.path.join(HOME, ".claude", "plugins", "cache", "*", plug, "*", "skills", bare, "SKILL.md"))]
    seen, out = set(), []
    for c in cands:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


# --- transcript parsing
def human_text(o):
    """Text of a message the human typed, else None."""
    if o.get("type") != "user" or o.get("isMeta") or o.get("isCompactSummary"):
        return None
    origin = o.get("origin")
    if isinstance(origin, dict) and origin.get("kind") not in (None, "human"):
        return None
    c = (o.get("message") or {}).get("content")
    if isinstance(c, list):
        if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c):
            return None
        c = "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
    if not isinstance(c, str) or not c.strip():
        return None
    if c.lstrip().startswith(NOISE_PREFIX):
        m = CMD_ARGS.search(c)  # slash-command args can carry feedback
        return m.group(1).strip() or None if m else None
    return c


def parse_session(path, subagents=False):
    """Yield normalised events: (idx, ts, kind, payload)."""
    files = [path]
    if subagents:
        files += sorted(glob.glob(os.path.join(path[:-6], "subagents", "*.jsonl")))
    idx = 0
    for fp in files:
        side = fp != path
        try:
            fh = open(fp, errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                if '"type":"user"' not in line and '"type":"assistant"' not in line:
                    continue
                try:
                    o = json.loads(line)
                except ValueError:
                    continue
                idx += 1
                ts = o.get("timestamp")
                meta = {"cwd": o.get("cwd"), "branch": o.get("gitBranch"), "side": side or bool(o.get("isSidechain"))}
                c = (o.get("message") or {}).get("content")
                if o.get("type") == "user":
                    raw = c if isinstance(c, str) else "\n".join(
                        b.get("text", "") for b in (c or []) if isinstance(b, dict) and b.get("type") == "text")
                    m = BASE_DIR.match(raw or "")
                    if m:
                        yield idx, ts, "skill_body", {"dir": m.group(1).rstrip("/"), **meta}
                        continue
                    for nm in CMD_NAME.findall(raw or "")[:1]:
                        yield idx, ts, "slash", {"name": nm, **meta}
                    if INTERRUPT in (raw or ""):
                        yield idx, ts, "interrupt", meta
                        continue
                    h = None if side else human_text(o)
                    if h:
                        yield idx, ts, "human", {"text": h, **meta}
                    if isinstance(c, list):
                        for b in c:
                            if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("is_error"):
                                t = b.get("content")
                                t = t if isinstance(t, str) else json.dumps(t)[:600]
                                low = t.lower()
                                kind = ("rejected" if any(r in low for r in REJECTED) else
                                        "denied" if low.startswith("permission to use") else "tool_error")
                                yield idx, ts, kind, {"text": t, **meta}
                else:
                    for b in c or []:
                        if not isinstance(b, dict):
                            continue
                        if b.get("type") == "text" and b.get("text"):
                            yield idx, ts, "assistant", {"text": b["text"], **meta}
                        elif b.get("type") == "tool_use":
                            inp = b.get("input") or {}
                            name = b.get("name")
                            if name == "Skill" and inp.get("skill"):
                                yield idx, ts, "skill_tool", {"name": inp["skill"], **meta}
                            elif name in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
                                yield idx, ts, "edit", {"path": inp.get("file_path") or inp.get("notebook_path"), **meta}
                            elif name == "Read":
                                p = inp.get("file_path") or ""
                                m = re.search(r"(.*/skills/(?:[^/]+/)*?([^/]+))/(SKILL\.md|references/.+)$", p)
                                if m:
                                    yield idx, ts, "skill_read", {"dir": m.group(1), "name": m.group(2), **meta}


def analyse(path, args):
    """Return {skill: record} for one session."""
    sid = os.path.basename(path)[:-6]
    events = list(parse_session(path, args.subagents))
    loads = []  # (idx, ts, name, dir, how)
    pending_tool = None
    for idx, ts, kind, p in events:
        if kind == "skill_tool":
            pending_tool = p["name"]
            loads.append((idx, ts, p["name"], None, "skill-tool"))
        elif kind == "skill_body":
            name = os.path.basename(p["dir"])
            if loads and loads[-1][3] is None and loads[-1][2].split(":")[-1] == name:
                i0, t0, n0, _, how = loads[-1]
                loads[-1] = (i0, t0, n0, p["dir"], how)
            else:
                loads.append((idx, ts, name, p["dir"], "slash" if not pending_tool else "skill-tool"))
            pending_tool = None
        elif kind == "skill_read":
            loads.append((idx, ts, p["name"], p["dir"], "read"))
    if not loads:
        return sid, events, {}
    if any(l[2] == SELF for l in loads):  # a run of this skill reads many SKILL.md files: not usage
        loads = [l for l in loads if l[2] == SELF]
    cwd = next((p.get("cwd") for _, _, _, p in events if p.get("cwd")), None)
    branch = next((p.get("branch") for _, _, _, p in events if p.get("branch")), None)
    out = {}
    starts = sorted({l[0] for l in loads if l[4] != "read"} | {i for i, _, k, _ in events if k == "slash"})
    for n, (i0, ts, name, d, how) in enumerate(loads):
        if args.skill and name.split(":")[-1] != args.skill.split(":")[-1]:
            continue
        rec = out.setdefault(name, {"session": sid, "skill": name, "dir": d, "how": set(), "first_ts": ts,
                                    "cwd": cwd, "branch": branch, "signals": [], "edits": {}, "_seen": set()})
        rec["how"].add(how)
        rec["dir"] = rec["dir"] or d
        nxt = [s for s in starts if s > i0]
        end = nxt[0] if nxt else float("inf")
        humans, last_asst = 0, ""
        for idx, ets, kind, p in events:
            if idx <= i0:
                if kind == "assistant":
                    last_asst = p["text"]
                continue
            if idx >= end or humans >= args.turns:
                break
            if kind == "assistant":
                last_asst = p["text"]
                if AGENT_NOTE.search(p["text"]):
                    add(rec, idx, ets, "agent_note", p["text"], "", args)
            elif kind == "human":
                humans += 1
                t = p["text"]
                if CORRECTION.search(t) and not USE_SKILL.match(t):
                    named = EXPLICIT.search(t) or name.split(":")[-1] in t
                    k = "explicit" if named and not USE_SKILL.match(t) else "correction"
                    add(rec, idx, ets, k, t, last_asst, args)
            elif kind in ("interrupt", "rejected"):
                add(rec, idx, ets, kind, p.get("text", "interrupted"), last_asst, args)
            elif kind == "denied" and not args.denials:
                continue
            elif kind in ("tool_error", "denied"):
                if sum(1 for s in rec["signals"] if s["kind"] == "tool_error") < args.max_errors:
                    add(rec, idx, ets, kind, p["text"], "", args)
            elif kind == "edit" and p.get("path"):
                rec["edits"][p["path"]] = rec["edits"].get(p["path"], 0) + 1
    for rec in out.values():
        for pth, cnt in rec["edits"].items():
            if cnt >= 3:
                rec["signals"].append({"kind": "rework", "idx": None, "ts": None,
                                       "text": "%s edited %d times" % (os.path.basename(pth), cnt), "before": ""})
        rec["how"] = sorted(rec["how"])
        del rec["_seen"], rec["edits"]
    return sid, events, out


def add(rec, idx, ts, kind, text, before, args):
    if idx in rec["_seen"]:
        return
    rec["_seen"].add(idx)
    rec["signals"].append({"kind": kind, "idx": idx, "ts": ts, "text": clip(text, args.chars),
                           "before": clip(before, args.chars // 2) if before else ""})


def select_sessions(args, st):
    paths = sorted(glob.glob(os.path.join(args.projects, "*", "*.jsonl")))
    if args.session:
        want = set(args.session)
        return [p for p in paths if os.path.basename(p)[:-6] in want or any(os.path.basename(p).startswith(w) for w in want)]
    since = None
    if args.since:
        since = dt.datetime.fromisoformat(args.since).timestamp()
    elif not args.all:  # default: unprocessed sessions newer than the floor (first run: last N days)
        since = st.get("floor") or (dt.datetime.now() - dt.timedelta(days=FIRST_RUN_DAYS)).timestamp()
        since -= 1
        return [p for p in _live_filter(args, [
            p for p in paths if os.path.getmtime(p) >= since and (
                os.path.basename(p)[:-6] not in st["sessions"]
                or os.path.getmtime(p) > st["sessions"][os.path.basename(p)[:-6]].get("mtime", 0) + 1)])]
    out = []
    for p in paths:
        sid, mt = os.path.basename(p)[:-6], os.path.getmtime(p)
        if since is not None:
            if mt >= since:
                out.append(p)
        elif args.all or sid not in st["sessions"] or mt > st["sessions"][sid].get("mtime", 0) + 1:
            out.append(p)
    return _live_filter(args, out)


def _live_filter(args, paths):
    if getattr(args, "include_live", False):
        return paths
    now = dt.datetime.now().timestamp()  # a session still being written is not finished feedback
    return [p for p in paths if now - os.path.getmtime(p) > 600]


def collect(args):
    st = load_state()
    paths = select_sessions(args, st)
    results = []
    for p in paths:
        sid, _, recs = analyse(p, args)
        for r in recs.values():
            r["file"] = p
            results.append(r)
    return paths, results


def cmd_scan(args):
    paths, results = collect(args)
    if args.json:
        json.dump({"sessions": [os.path.basename(p)[:-6] for p in paths], "results": results}, sys.stdout, default=str)
        return
    by_skill = {}
    for r in results:
        by_skill.setdefault(r["skill"], []).append(r)
    print("sessions scanned: %d   sessions with skills: %d" % (len(paths), len({r['session'] for r in results})))
    print("%-28s %4s %4s  %s" % ("skill", "sess", "sig", "signal kinds (sessions with any signal)"))
    for name, rs in sorted(by_skill.items(), key=lambda kv: -sum(len(r["signals"]) for r in kv[1])):
        kinds = {}
        for r in rs:
            for s in r["signals"]:
                kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
        with_sig = sum(1 for r in rs if r["signals"])
        print("%-28s %4d %4d  %s (%d)" % (name[:28], len(rs), sum(kinds.values()),
                                         ", ".join("%s=%d" % kv for kv in sorted(kinds.items())) or "-", with_sig))


def cmd_excerpts(args):
    paths, results = collect(args)
    by_skill = {}
    for r in results:
        if r["signals"] or args.verbose:
            by_skill.setdefault(r["skill"], []).append(r)
    if args.json:
        json.dump(by_skill, sys.stdout, indent=1, default=str)
        return
    for name, rs in sorted(by_skill.items()):
        d = next((r["dir"] for r in rs if r["dir"]), None)
        print("## %s  (%d sessions with signals)" % (name, len(rs)))
        print("dir: %s" % (d or "?"))
        for r in sorted(rs, key=lambda r: r["first_ts"] or ""):
            print("\n### session %s  %s  via=%s  cwd=%s" % (
                r["session"], (r["first_ts"] or "")[:10], ",".join(r["how"]), r["cwd"]))
            for s in r["signals"]:
                print("- [%s] #%s %s" % (s["kind"], s["idx"], s["text"]))
                if s["before"]:
                    print("    after assistant: %s" % s["before"])
        print()


def cmd_context(args):
    """Print the conversation around one event index, clipped: the minimal read beyond an excerpt."""
    paths = [p for p in glob.glob(os.path.join(args.projects, "*", "*.jsonl"))
             if os.path.basename(p).startswith(args.session)]
    if len(paths) != 1:
        print("session not found or ambiguous: %s (%d matches)" % (args.session, len(paths)))
        return 1
    lo, hi = args.idx - args.around, args.idx + args.around
    for idx, ts, kind, p in parse_session(paths[0]):
        if idx < lo:
            continue
        if idx > hi:
            break
        if kind in ("human", "assistant", "interrupt", "rejected", "tool_error", "slash", "skill_tool", "skill_body", "edit"):
            body = p.get("text") or p.get("name") or p.get("dir") or p.get("path") or ""
            print("#%d %-10s %s" % (idx, kind, clip(body, args.chars)))


def cmd_where(args):
    hits = resolve_skill(args.name, cwd=args.cwd)
    if not hits:
        print("not found: %s" % args.name)
        return 1
    for h in hits:
        print("%s\t%s\t%s" % (h, os.path.realpath(h), ownership(h, args.name.split(":")[-1])))


def cmd_history(args):
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=WINDOW_DAYS)
    rows = [d for d in load_decisions() if not args.skill or d.get("skill") == args.skill]
    keys = {}
    for d in rows:
        k = d.get("key") or "?"
        e = keys.setdefault(k, {"skill": d.get("skill"), "sessions": set(), "fresh": set(), "last": None, "decisions": []})
        when = iso(d.get("ts", "")) or cutoff
        for s in d.get("sessions", []):
            e["sessions"].add(s)
            if when >= cutoff:
                e["fresh"].add(s)
        e["last"] = d.get("decision")
        e["decisions"].append(d.get("decision"))
    for k, e in sorted(keys.items()):
        print("%-40s skill=%-20s last=%-8s recurrence=%d (in %dd: %d)  note=%s" % (
            k, e["skill"], e["last"], len(e["sessions"]), WINDOW_DAYS, len(e["fresh"]),
            next((d.get("note", "") for d in reversed(rows) if d.get("key") == k), "")[:80]))


def cmd_mark(args):
    st = load_state()
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    paths = {os.path.basename(p)[:-6]: p for p in glob.glob(os.path.join(args.projects, "*", "*.jsonl"))}
    if not args.ids:  # no ids: mark the same scope a scan with these flags would read
        args.ids = [os.path.basename(p)[:-6] for p in select_sessions(args, st)]
    for sid in args.ids:
        p = paths.get(sid)
        st["sessions"][sid] = {"mtime": os.path.getmtime(p) if p else 0, "processed_at": now}
    st["last_run"] = now
    mts = [st["sessions"][s]["mtime"] for s in args.ids if st["sessions"][s]["mtime"]]
    default_floor = (dt.datetime.now() - dt.timedelta(days=FIRST_RUN_DAYS)).timestamp()
    st["floor"] = min([st.get("floor") or default_floor] + mts)
    save_state(st)
    print("marked %d sessions" % len(args.ids))


def cmd_log(args):
    os.makedirs(STATE_DIR, exist_ok=True)
    rec = {"ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "skill": args.skill,
           "key": args.key, "decision": args.decision, "sessions": args.sessions or [],
           "evidence": [redact(e)[:200] for e in (args.evidence or [])], "note": redact(args.note or "")[:300]}
    with open(state_path("decisions.jsonl"), "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("logged %s %s %s" % (args.decision, args.skill, args.key))


def cmd_backup(args):
    src = os.path.realpath(args.path)
    h = hashlib.sha256(open(src, "rb").read()).hexdigest()[:12]
    stamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    dst = os.path.join(STATE_DIR, "backups", args.skill, "%s-%s-%s" % (stamp, h, os.path.basename(src)))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(dst)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nm in ("scan", "excerpts"):
        s = sub.add_parser(nm)
        s.add_argument("--skill")
        s.add_argument("--since", help="YYYY-MM-DD: sessions modified since, ignores state")
        s.add_argument("--session", action="append", help="session id or prefix (repeatable)")
        s.add_argument("--all", action="store_true", help="ignore processed-session state")
        s.add_argument("--include-live", action="store_true", help="include sessions modified in the last 10 min")
        s.add_argument("--subagents", action="store_true", help="also read <session>/subagents/*.jsonl")
        s.add_argument("--turns", type=int, default=3, help="human turns attributed to a skill after it loads")
        s.add_argument("--chars", type=int, default=320)
        s.add_argument("--max-errors", type=int, default=3)
        s.add_argument("--denials", action="store_true", help="include permission-classifier denials (usually noise)")
        s.add_argument("--projects", default=PROJECTS)
        s.add_argument("--json", action="store_true")
        s.add_argument("--verbose", action="store_true", help="excerpts: include skills with no signals")
    cx = sub.add_parser("context"); cx.add_argument("session"); cx.add_argument("idx", type=int)
    cx.add_argument("--around", type=int, default=4); cx.add_argument("--chars", type=int, default=500)
    cx.add_argument("--projects", default=PROJECTS)
    w = sub.add_parser("where"); w.add_argument("name"); w.add_argument("--cwd")
    h = sub.add_parser("history"); h.add_argument("--skill")
    m = sub.add_parser("mark", help="mark session ids processed; with no ids, the scope the flags select")
    m.add_argument("ids", nargs="*"); m.add_argument("--projects", default=PROJECTS)
    m.add_argument("--since"); m.add_argument("--session", action="append"); m.add_argument("--all", action="store_true")
    m.add_argument("--include-live", action="store_true")
    lg = sub.add_parser("log")
    lg.add_argument("--skill", required=True); lg.add_argument("--key", required=True)
    lg.add_argument("--decision", required=True,
                    choices=["pending", "discard", "skip", "patch", "merge", "create", "applied", "proposed"])
    lg.add_argument("--sessions", nargs="*"); lg.add_argument("--evidence", action="append"); lg.add_argument("--note")
    b = sub.add_parser("backup"); b.add_argument("skill"); b.add_argument("path")
    args = ap.parse_args()
    return {"scan": cmd_scan, "excerpts": cmd_excerpts, "context": cmd_context, "where": cmd_where, "history": cmd_history,
            "mark": cmd_mark, "log": cmd_log, "backup": cmd_backup}[args.cmd](args) or 0


if __name__ == "__main__":
    sys.exit(main())
