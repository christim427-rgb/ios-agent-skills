#!/usr/bin/env python3
"""
scaffold.py — Prepare a benchmark iteration workspace.

Usage:
  python scaffold.py <skill_root> <iteration_root> <model_slug>

  skill_root     : e.g. skills/ios/gcd-operationqueue
  iteration_root : e.g. skills/ios/gcd-operationqueue-workspace/iteration-2
  model_slug     : e.g. gpt-5-4  (only alphanumeric + hyphens)

Creates:
  iteration_root/
    eval-<name>/
                                                eval_metadata.json          ← normalized snapshot of eval from evals.json
      <model_slug>-with/run-1/outputs/   ← empty, ready for response.md
      <model_slug>-without/run-1/outputs/
"""

import argparse
import json
import re
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold benchmark iteration workspace")
    parser.add_argument("skill_root", help="Path to skill directory (e.g. skills/ios/gcd-operationqueue)")
    parser.add_argument("iteration_root", help="Output path for this iteration")
    parser.add_argument("model_slug", help="Lowercase hyphenated model identifier (e.g. gpt-5-4)")
    parser.add_argument("--runs", type=int, default=3, help="Number of independent runs to scaffold per eval (default: 3)")
    args = parser.parse_args()

    skill_root = Path(args.skill_root).resolve()
    iteration_root = Path(args.iteration_root).resolve()
    model_slug = args.model_slug
    num_runs = args.runs

    if not re.fullmatch(r"[a-z0-9][a-z0-9\-]*", model_slug):
        sys.exit(f"[scaffold] Invalid model_slug '{model_slug}'. Use lowercase alphanumeric + hyphens only.")

    # Eval definitions live in evals/<platform>/<skill-name>/ (sibling of skills/).
    # skill_root is e.g. skills/ios/gcd-operationqueue → platform=ios, skill=gcd-operationqueue
    parts = skill_root.parts
    try:
        skills_idx = next(i for i, p in enumerate(parts) if p == "skills")
        platform = parts[skills_idx + 1]
        skill_name_part = parts[skills_idx + 2]
        repo_root = Path(*parts[:skills_idx]) if skills_idx > 0 else Path(".")
        evals_dir = repo_root / "evals" / platform / skill_name_part
    except (StopIteration, IndexError):
        evals_dir = skill_root / "evals"

    evals_path = evals_dir / "evals.json"
    if not evals_path.exists():
        sys.exit(f"[scaffold] No eval definition file found at {evals_path}")

    data = json.loads(evals_path.read_text(encoding="utf-8"))
    evals = data.get("evals")
    if not isinstance(evals, list) or not evals:
        sys.exit(f"[scaffold] No 'evals' array found in {evals_path}")

    print(f"[scaffold] Skill      : {skill_root.name}")
    print(f"[scaffold] Model slug : {model_slug}")
    print(f"[scaffold] Iteration  : {iteration_root}")
    print(f"[scaffold] Eval set   : {evals_path.name}")
    print(f"[scaffold] Evals      : {len(evals)}")
    print(f"[scaffold] Runs/eval  : {num_runs}")
    print()

    created = 0
    skipped = 0

    for ev in evals:
        name = ev.get("name")
        if not name:
            print(f"  [!] Eval id={ev.get('id')} has no 'name' field — skipped", file=sys.stderr)
            continue

        eval_dir = iteration_root / f"eval-{name}"

        # Create output dirs for both variants and all runs
        for variant in (f"{model_slug}-with", f"{model_slug}-without"):
            for run_num in range(1, num_runs + 1):
                out_dir = eval_dir / variant / f"run-{run_num}" / "outputs"
                out_dir.mkdir(parents=True, exist_ok=True)

        # Write eval_metadata.json (only if not already present)
        meta_path = eval_dir / "eval_metadata.json"
        if not meta_path.exists():
            eval_record = dict(ev)
            eval_record["topic"] = eval_record.get("topic") or eval_record.get("reference") or name

            raw_assertions = eval_record.get("assertions", [])
            if isinstance(raw_assertions, list):
                normalized_assertions = []
                for index, assertion in enumerate(raw_assertions, start=1):
                    if isinstance(assertion, dict):
                        normalized_assertions.append(assertion)
                    elif isinstance(assertion, str):
                        normalized_assertions.append({"id": f"A{index}", "text": assertion})
                eval_record["assertions"] = normalized_assertions

            eval_record.setdefault("source_eval_set", evals_path.name)
            meta_path.write_text(json.dumps(eval_record, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  [+] eval-{name}/eval_metadata.json")
            created += 1
        else:
            print(f"  [=] eval-{name}/eval_metadata.json (exists, not overwritten)")
            skipped += 1

    print()
    print(f"[scaffold] Created: {created}  Skipped (already present): {skipped}")
    print(f"[scaffold] Next step: generate with_skill and without_skill responses.")
    runs_label = "/".join(f"run-{i}" for i in range(1, num_runs + 1))
    print(f"[scaffold] Output dirs ready: eval-*/{model_slug}-with/{{{runs_label}}}/outputs/")
    print(f"[scaffold]                    eval-*/{model_slug}-without/{{{runs_label}}}/outputs/")


if __name__ == "__main__":
    main()
