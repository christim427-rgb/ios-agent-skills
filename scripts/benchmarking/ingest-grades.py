#!/usr/bin/env python3
"""
ingest-grades.py — Write individual grading.json files from a batch grade JSON array.

Usage:
  python ingest-grades.py <grades_json_file> <iteration_root> <model_slug> [--run N]

grades_json_file : path to a JSON file containing an array of grading objects
                   as returned by the grader subagent
iteration_root   : e.g. workspaces/ios/gcd-operationqueue/iteration-2
model_slug       : e.g. gemini-3-1-pro
--run N          : which run number to write into (default: 1)
"""

import argparse
import json
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Write grading.json files from a batch grade JSON array")
    parser.add_argument("grades_json_file", help="Path to JSON file with array of grading objects")
    parser.add_argument("iteration_root", help="Path to iteration directory")
    parser.add_argument("model_slug", help="Model slug (e.g. gemini-3-1-pro)")
    parser.add_argument("--run", type=int, default=1, help="Run number to write into (default: 1)")
    args = parser.parse_args()

    grades_file = Path(args.grades_json_file)
    iteration_root = Path(args.iteration_root).resolve()
    model_slug = args.model_slug
    run_number = args.run

    if not grades_file.exists():
        sys.exit(f"Grades file not found: {grades_file}")

    raw = grades_file.read_text(encoding="utf-8").strip()
    # Strip markdown code blocks if present
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
    if raw.endswith("```"):
        raw = "\n".join(raw.split("\n")[:-1])

    try:
        grades = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.exit(f"JSON parse error in grades file: {e}")

    if not isinstance(grades, list):
        sys.exit("Expected a JSON array at the top level of grades file")

    written = 0
    errors = 0

    for grade in grades:
        eval_name = grade.get("eval_name")
        variant_raw = grade.get("variant", "")

        if not eval_name:
            print(f"  [!] Missing eval_name in grade entry, skipping: {str(grade)[:80]}", file=sys.stderr)
            errors += 1
            continue

        # Determine with/without from variant label
        if variant_raw in ("SET_A", f"{model_slug}-with") or "with" in variant_raw.lower() and "without" not in variant_raw.lower():
            variant_dir = f"{model_slug}-with"
        elif variant_raw in ("SET_B", f"{model_slug}-without") or "without" in variant_raw.lower():
            variant_dir = f"{model_slug}-without"
        else:
            print(f"  [!] Cannot determine with/without from variant '{variant_raw}' for {eval_name}", file=sys.stderr)
            errors += 1
            continue

        out_dir = iteration_root / f"eval-{eval_name}" / variant_dir / f"run-{run_number}"
        out_dir.mkdir(parents=True, exist_ok=True)

        # Normalise the grading record before writing
        grading_record = {
            "eval_id": grade.get("eval_id"),
            "variant": variant_dir,
            "assertions": grade.get("assertions", []),
            "summary": grade.get("summary", {}),
        }

        out_path = out_dir / "grading.json"
        out_path.write_text(json.dumps(grading_record, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  [+] {out_path.relative_to(Path.cwd())}")
        written += 1

    print()
    print(f"[ingest] Written: {written}  Errors: {errors}")


if __name__ == "__main__":
    main()
