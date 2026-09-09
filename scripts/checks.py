"""
Skill-agnostic check library used by grade_engine.py.

Each expectation in a skill's evals.json is an object:

    {"text": "<human-readable statement>", "check": "<type>", ...params}

`text` is what humans and the viewer see; `check` plus params is what the
engine executes. Nothing in this file knows about any particular skill.

Check types
-----------
regex
    Pass when at least one pattern matches.
    params: pattern | patterns, scope ("all" | "first_line"), flags (["i","s"])

no_regex
    Pass when no pattern matches anywhere. Evidence lists the matches.
    params: pattern | patterns, flags

line_pattern
    Every line matching `select` must also match `match` (and must not match
    `not_match`). Fails if fewer than `min_matches` lines are selected.
    params: select, match, not_match, min_matches (default 1)

line_sequence
    For lines matching `after`, look at the following line (optionally skipping
    blank lines) and require it to match `next` and/or not match `next_not`.
    mode "all": every anchor line must satisfy; mode "any": at least one must.
    An anchor on the last line counts as satisfied.
    params: after, next, next_not, skip_blank (default false), mode (default "all")

json_values_absent
    Read a JSON array file from the eval outputs directory, select records where
    every key in `where` equals the given value, and require that the value of
    `field` from each selected record does not appear in the output content.
    params: file, where, field, missing_file ("pass" | "fail", default "pass")

all_of
    Pass only when every nested check passes.
    params: checks (list of check objects without `text`)

Pattern presets
---------------
Any pattern string of the form "preset:<name>" is replaced by a built-in
pattern. Presets exist for things that are painful to write in JSON:

    emoji, markdown, slack_markup, divider, url

MULTILINE is always enabled so ^ and $ anchor to lines.
"""

import json
import os
import re

PRESETS = {
    "emoji": (
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002600-\U000027BF"
        "\U0001F900-\U0001F9FF"
        "\U0000FE00-\U0000FE0F"
        "]"
    ),
    "markdown": r"\*\*|__|\[[^\]\n]+\]\([^)\n]+\)|^#{1,6}\s",
    "slack_markup": r"<https?://[^|>\s]+\|[^>\n]+>|(?<!\*)\*[^*\n]+\*(?!\*)|`[^`\n]+`",
    "divider": r"^[-=*_]{3,}\s*$",
    "url": r"https?://\S+",
}

_FLAG_MAP = {"i": re.IGNORECASE, "s": re.DOTALL, "x": re.VERBOSE}


def _flags(spec):
    value = re.MULTILINE
    for f in spec.get("flags", []):
        value |= _FLAG_MAP[f]
    return value


def _expand(pattern):
    if pattern.startswith("preset:"):
        name = pattern.split(":", 1)[1]
        if name not in PRESETS:
            raise ValueError(f"unknown pattern preset {name!r}; known: {sorted(PRESETS)}")
        return PRESETS[name]
    return pattern


def _patterns(spec, key="pattern"):
    raw = spec.get(key + "s") or spec.get(key)
    if raw is None:
        raise ValueError(f"check {spec.get('check')!r} requires {key!r} or {key}s")
    if isinstance(raw, str):
        raw = [raw]
    return [re.compile(_expand(p), _flags(spec)) for p in raw]


def _rx(spec, key, required=True):
    raw = spec.get(key)
    if raw is None:
        if required:
            raise ValueError(f"check {spec.get('check')!r} requires {key!r}")
        return None
    return re.compile(_expand(raw), _flags(spec))


# ---------------------------------------------------------------------------
# Check implementations: (spec, content, outputs_dir) -> (passed, evidence)
# ---------------------------------------------------------------------------

def check_regex(spec, content, _outputs_dir):
    scope = spec.get("scope", "all")
    if scope == "first_line":
        stripped = content.strip()
        target = stripped.splitlines()[0] if stripped else ""
    else:
        target = content
    for rx in _patterns(spec):
        m = rx.search(target)
        if m:
            return True, f"matched {m.group()!r}"
    label = "first line" if scope == "first_line" else "output"
    return False, f"no pattern matched in {label}: {target[:80]!r}"


def check_no_regex(spec, content, _outputs_dir):
    found = []
    for rx in _patterns(spec):
        found.extend(m.group() for m in rx.finditer(content))
    if found:
        return False, f"found: {found[:5]}"
    return True, "no matches"


def check_line_pattern(spec, content, _outputs_dir):
    select = _rx(spec, "select")
    match = _rx(spec, "match", required=False)
    not_match = _rx(spec, "not_match", required=False)
    min_matches = spec.get("min_matches", 1)

    selected = [(i + 1, l) for i, l in enumerate(content.splitlines()) if select.search(l)]
    if len(selected) < min_matches:
        return False, f"only {len(selected)} line(s) match select, need {min_matches}"
    for n, line in selected:
        if match and not match.search(line):
            return False, f"line {n} does not match required form: {line!r}"
        if not_match and not_match.search(line):
            return False, f"line {n} matches forbidden form: {line!r}"
    return True, f"{len(selected)} line(s) checked"


def check_line_sequence(spec, content, _outputs_dir):
    after = _rx(spec, "after")
    nxt = _rx(spec, "next", required=False)
    next_not = _rx(spec, "next_not", required=False)
    if nxt is None and next_not is None:
        raise ValueError("line_sequence requires 'next' and/or 'next_not'")
    skip_blank = spec.get("skip_blank", False)
    mode = spec.get("mode", "all")

    lines = content.splitlines()
    anchors = 0
    satisfied = 0
    first_violation = None
    for i, line in enumerate(lines):
        if not after.search(line):
            continue
        anchors += 1
        j = i + 1
        while skip_blank and j < len(lines) and not lines[j].strip():
            j += 1
        if j >= len(lines):
            satisfied += 1
            continue
        following = lines[j]
        ok = True
        if nxt and not nxt.search(following):
            ok = False
        if next_not and next_not.search(following):
            ok = False
        if ok:
            satisfied += 1
        elif first_violation is None:
            first_violation = f"line {i+1} {line!r} followed by line {j+1} {following!r}"

    if anchors == 0:
        return False, "no line matched 'after'"
    if mode == "any":
        if satisfied:
            return True, f"{satisfied}/{anchors} anchor(s) satisfied"
        return False, f"no anchor satisfied; e.g. {first_violation}"
    if satisfied == anchors:
        return True, f"all {anchors} anchor(s) satisfied"
    return False, first_violation


def check_json_values_absent(spec, content, outputs_dir):
    path = os.path.join(outputs_dir, spec["file"])
    if not os.path.isfile(path):
        if spec.get("missing_file", "pass") == "pass":
            return True, f"{spec['file']} not present; nothing to verify"
        return False, f"{spec['file']} not present"
    with open(path, encoding="utf-8") as f:
        try:
            records = json.load(f)
        except json.JSONDecodeError as e:
            return False, f"{spec['file']} is not valid JSON: {e}"
    where = spec.get("where", {})
    field = spec["field"]
    selected = [
        r for r in records
        if isinstance(r, dict) and all(r.get(k) == v for k, v in where.items())
    ]
    if not selected:
        return True, f"no records match {where}; nothing to exclude"
    leaked = [r[field] for r in selected if r.get(field) and str(r[field]) in content]
    if leaked:
        return False, f"excluded values appear in output: {leaked[:5]}"
    return True, f"{len(selected)} excluded record(s), none appear in output"


def check_all_of(spec, content, outputs_dir):
    evidence = []
    for sub in spec.get("checks", []):
        passed, ev = run_check(sub, content, outputs_dir)
        evidence.append(f"{sub['check']}: {ev}")
        if not passed:
            return False, "; ".join(evidence)
    return True, "; ".join(evidence)


CHECKS = {
    "regex": check_regex,
    "no_regex": check_no_regex,
    "line_pattern": check_line_pattern,
    "line_sequence": check_line_sequence,
    "json_values_absent": check_json_values_absent,
    "all_of": check_all_of,
}


def validate(spec, where=""):
    """Return a list of problems with a check spec (empty list = valid)."""
    problems = []
    name = spec.get("check")
    if not name:
        problems.append(f"{where}: missing 'check'")
        return problems
    if name not in CHECKS:
        problems.append(f"{where}: unknown check {name!r}; known: {sorted(CHECKS)}")
        return problems
    if name == "all_of":
        subs = spec.get("checks")
        if not subs:
            problems.append(f"{where}: all_of requires a non-empty 'checks' list")
        else:
            for i, sub in enumerate(subs):
                problems.extend(validate(sub, f"{where} -> checks[{i}]"))
        return problems
    try:
        # Compile patterns eagerly so typos surface before any grading happens
        for key in ("pattern", "select", "match", "not_match", "after", "next", "next_not"):
            if key in spec:
                _rx(spec, key)
        if "patterns" in spec:
            _patterns(spec)
        if name == "json_values_absent":
            for key in ("file", "field"):
                if key not in spec:
                    problems.append(f"{where}: json_values_absent requires {key!r}")
    except (re.error, ValueError, KeyError) as e:
        problems.append(f"{where}: {e}")
    return problems


def run_check(spec, content, outputs_dir):
    return CHECKS[spec["check"]](spec, content, outputs_dir)
