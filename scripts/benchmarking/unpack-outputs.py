#!/usr/bin/env python3
"""
unpack-outputs.py — Write response.md files from a pre-existing batch outputs JSON.

Handles any model's pre-generated batch file that follows the standard format:

  {
    "model": "<model-slug>",
    "skill": "<skill-name>",
    "outputs": [
      {
        "eval_name": "queue-creation-simple",
        "response_with_skill": "...",
        "response_without_skill": "..."
      },
      ...
    ]
  }

Usage:
  python unpack-outputs.py <outputs_json_file> <iteration_root> [<model_slug>] [--run N]

  outputs_json_file : path to the batch outputs JSON
  iteration_root    : e.g. workspaces/ios/gcd-operationqueue/iteration-2
  model_slug        : override slug (default: taken from outputs JSON "model" field)
  --run N           : which run number to write responses into (default: 1)

Writes:
  <iteration_root>/eval-<eval_name>/<slug>-with/run-1/outputs/response.md
  <iteration_root>/eval-<eval_name>/<slug>-without/run-1/outputs/response.md

Requires scaffold.py to have already been run (eval dirs must exist).
"""

import argparse
import json
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Write response.md files from a pre-existing batch outputs JSON")
    parser.add_argument("outputs_json_file", help="Path to the batch outputs JSON file")
    parser.add_argument("iteration_root", help="Path to iteration directory")
    parser.add_argument("model_slug", nargs="?", default=None, help="Model slug override (default: taken from JSON 'model' field)")
    parser.add_argument("--run", type=int, default=1, help="Run number to write responses into (default: 1)")
    args = parser.parse_args()

    outputs_file = Path(args.outputs_json_file)
    iteration_root = Path(args.iteration_root).resolve()
    slug_override = args.model_slug
    run_number = args.run

    if not outputs_file.exists():
        sys.exit(f"[unpack] Outputs file not found: {outputs_file}")

    data = json.loads(outputs_file.read_text(encoding="utf-8"))

    slug = slug_override or data.get("model")
    if not slug:
        sys.exit("[unpack] Cannot determine model slug — pass it as 3rd argument or add a 'model' field to the JSON")

    outputs = data.get("outputs")
    if not isinstance(outputs, list) or not outputs:
        sys.exit("[unpack] 'outputs' array not found or empty in JSON file")

    # Validate required fields exist on first item
    sample = outputs[0]
    if "response_with_skill" not in sample or "response_without_skill" not in sample:
        sys.exit(
            "[unpack] Outputs JSON must have 'response_with_skill' and 'response_without_skill' fields. "
            "Got: " + str(list(sample.keys()))
        )
    if "eval_name" not in sample:
        sys.exit("[unpack] Outputs JSON must have 'eval_name' field. Got: " + str(list(sample.keys())))

    print(f"[unpack] Model     : {slug}")
    print(f"[unpack] Iteration : {iteration_root}")
    print(f"[unpack] Outputs   : {len(outputs)}")
    print()

    written = 0
    missing_dirs = []

    for item in outputs:
        eval_name = item["eval_name"]
        eval_dir = iteration_root / f"eval-{eval_name}"

        if not eval_dir.exists():
            missing_dirs.append(eval_name)
            continue

        for variant, key in [(f"{slug}-with", "response_with_skill"), (f"{slug}-without", "response_without_skill")]:
            out_dir = eval_dir / variant / f"run-{run_number}" / "outputs"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / "response.md"
            out_path.write_text(item[key], encoding="utf-8")
            print(f"  [+] eval-{eval_name}/{variant}/run-1/outputs/response.md")
            written += 1

    print()
    if missing_dirs:
        print(f"[unpack] WARNING: {len(missing_dirs)} eval dirs not found (run scaffold.py first):", file=sys.stderr)
        for name in missing_dirs:
            print(f"  - eval-{name}", file=sys.stderr)

    print(f"[unpack] Written: {written} response.md files")
    print(f"[unpack] Next step: run Phase 3 (grading subagent)")


if __name__ == "__main__":
    main()
