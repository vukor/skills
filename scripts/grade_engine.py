"""
Skill-agnostic grading engine.

Reads a skill's evals.json, where every expectation is an object with a
human-readable `text` and a declarative `check` spec (see scripts/checks.py),
runs the checks against each eval's outputs, and writes grading.json files
that skill-creator's aggregate_benchmark and viewer can consume.

Workspace layout expected (eval-workspaces/ is gitignored):

    eval-workspaces/<skill-name>/iteration-N/   the workspace passed to run()
      eval-<id>-<slug>/
        with_skill/outputs/message.txt
        with_skill/run-1/grading.json      written by this engine
        without_skill/outputs/message.txt
        without_skill/run-1/grading.json

Nothing here is specific to any skill. Skill-specific behaviour lives in
the check specs inside evals.json.
"""

import json
import os
import re
import sys

from scripts import checks

CONFIGS = ("with_skill", "without_skill")
OUTPUT_FILE = "message.txt"


def load_evals(evals_json_path):
    with open(evals_json_path, encoding="utf-8") as f:
        return json.load(f)["evals"]


def eval_dir_name(ev):
    slug = ev.get("slug")
    if not slug:
        slug = re.sub(r"[^a-z0-9]+", "-", ev.get("prompt", "").lower()).strip("-")[:40]
    return f"eval-{ev['id']}-{slug}"


def validate_evals(evals):
    """Return a list of problems; every expectation must be a checkable object."""
    problems = []
    for ev in evals:
        for i, exp in enumerate(ev.get("expectations", [])):
            where = f"eval-{ev['id']} expectations[{i}]"
            if not isinstance(exp, dict):
                problems.append(
                    f"{where}: expectation is a bare string; it must be an object "
                    f"with 'text' and 'check' ({exp!r})"
                )
                continue
            if not exp.get("text"):
                problems.append(f"{where}: missing 'text'")
            problems.extend(checks.validate(exp, where))
    return problems


def grade_content(content, outputs_dir, expectations):
    results = []
    for exp in expectations:
        try:
            passed, evidence = checks.run_check(exp, content, outputs_dir)
        except Exception as exc:  # a broken check must not abort the whole run
            passed, evidence = False, f"check raised {type(exc).__name__}: {exc}"
        results.append({"text": exp["text"], "passed": bool(passed), "evidence": evidence})
    return results


def write_grading(path, results):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    payload = {
        "expectations": results,
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "pass_rate": round(passed / total, 3) if total else 0.0,
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return passed, total


def run(evals_json_path, workspace):
    if not os.path.isfile(evals_json_path):
        print(f"ERROR: evals.json not found at {evals_json_path}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(workspace):
        print(f"ERROR: workspace directory not found: {workspace}", file=sys.stderr)
        sys.exit(1)

    evals = load_evals(evals_json_path)

    problems = validate_evals(evals)
    if problems:
        print("ERROR: evals.json has expectations the engine cannot grade:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        sys.exit(1)

    rows = []
    for ev in evals:
        dir_name = eval_dir_name(ev)
        for config in CONFIGS:
            outputs_dir = os.path.join(workspace, dir_name, config, "outputs")
            message_path = os.path.join(outputs_dir, OUTPUT_FILE)
            grading_path = os.path.join(workspace, dir_name, config, "run-1", "grading.json")

            if not os.path.isfile(message_path):
                print(f"SKIP: {dir_name}/{config}/outputs/{OUTPUT_FILE} not found", file=sys.stderr)
                continue

            with open(message_path, encoding="utf-8") as f:
                content = f.read()

            results = grade_content(content, outputs_dir, ev.get("expectations", []))
            passed, total = write_grading(grading_path, results)
            rows.append((dir_name, config, passed, total))

    if not rows:
        print("No eval outputs found; nothing graded.", file=sys.stderr)
        sys.exit(2)

    print(f"{'eval':<36} {'config':<14} {'passed':>6} {'total':>6} {'rate':>6}")
    print("-" * 72)
    for dir_name, config, passed, total in rows:
        rate = f"{passed / total:.0%}" if total else "n/a"
        print(f"{dir_name:<36} {config:<14} {passed:>6} {total:>6} {rate:>6}")
    return rows
