"""
Grade a skill's eval outputs.

    python3 scripts/grade.py --skill <name> --workspace <path/to/iteration-N>
    python3 scripts/grade.py --skill <name> --validate
    python3 scripts/grade.py --list

--skill      Directory name under skills/ (e.g. pr-review-request)
--workspace  Iteration directory holding eval-<id>-<slug>/ output folders.
             Defaults to the highest-numbered eval-workspaces/<skill>/iteration-N.
--validate   Only check that every expectation in evals.json is gradable;
             do not touch the workspace. Useful right after editing evals.json.
--list       Print skills that have an evals.json and exit.

All grading logic is generic. To add grading for a new skill, give every
expectation in its evals.json a `check` spec (see scripts/checks.py for the
available check types). No Python changes are needed.
"""

import argparse
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from scripts import grade_engine  # noqa: E402

SKILLS_DIR = os.path.join(REPO_ROOT, "skills")
WORKSPACES_DIR = os.path.join(REPO_ROOT, "eval-workspaces")


def evals_path(skill):
    return os.path.join(SKILLS_DIR, skill, "evals", "evals.json")


def available_skills():
    if not os.path.isdir(SKILLS_DIR):
        return []
    return sorted(s for s in os.listdir(SKILLS_DIR) if os.path.isfile(evals_path(s)))


def latest_iteration(skill):
    """Return eval-workspaces/<skill>/iteration-N with the highest N, or None."""
    root = os.path.join(WORKSPACES_DIR, skill)
    if not os.path.isdir(root):
        return None
    numbered = []
    for name in os.listdir(root):
        m = re.fullmatch(r"iteration-(\d+)", name)
        if m and os.path.isdir(os.path.join(root, name)):
            numbered.append((int(m.group(1)), name))
    if not numbered:
        return None
    return os.path.join(root, max(numbered)[1])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skill", "-s", help="skill name (directory under skills/)")
    parser.add_argument("--workspace", "-w", help="iteration directory with eval outputs")
    parser.add_argument("--validate", action="store_true", help="validate evals.json only")
    parser.add_argument("--list", action="store_true", help="list skills with an evals.json")
    args = parser.parse_args()

    if args.list:
        skills = available_skills()
        print("\n".join(skills) if skills else "No skills with evals.json found.")
        return

    if not args.skill:
        parser.error("--skill is required (or use --list)")

    path = evals_path(args.skill)
    if not os.path.isfile(path):
        known = ", ".join(available_skills()) or "(none)"
        parser.error(f"no evals.json for skill {args.skill!r} at {path}\nknown skills: {known}")

    if args.validate:
        problems = grade_engine.validate_evals(grade_engine.load_evals(path))
        if problems:
            print("evals.json has expectations the engine cannot grade:", file=sys.stderr)
            for p in problems:
                print(f"  {p}", file=sys.stderr)
            sys.exit(1)
        print(f"{path}: all expectations are gradable")
        return

    workspace = args.workspace or latest_iteration(args.skill)
    if not workspace:
        parser.error(
            f"no iteration directories found under {os.path.join(WORKSPACES_DIR, args.skill)}; "
            f"pass --workspace explicitly"
        )
    grade_engine.run(path, workspace)


if __name__ == "__main__":
    main()
