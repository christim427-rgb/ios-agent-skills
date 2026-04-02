#!/usr/bin/env python3
"""
Grade benchmark responses against assertions from eval_metadata.json.

This script provides programmatic grading based on keyword/pattern matching.
For assertions that require semantic understanding (content_check, structure_check),
it flags them for manual or AI-agent review.

Standalone -- uses only Python standard library. No Claude Code or plugin dependencies.

Usage:
    python grade_responses.py <iteration_dir>
    python grade_responses.py <iteration_dir> --eval eval-observable-viewmodel
    python grade_responses.py <iteration_dir> --config with_skill
    python grade_responses.py <iteration_dir> --dry-run

Examples:
    # Grade all responses in an iteration
    python grade_responses.py workspaces/ios/ios-testing/iteration-1/

    # Grade only a specific eval
    python grade_responses.py workspaces/ios/ios-testing/iteration-1/ --eval eval-xctest-migration

    # Grade only with_skill runs
    python grade_responses.py workspaces/ios/ios-testing/iteration-1/ --config with_skill

    # Preview what would be graded without writing files
    python grade_responses.py workspaces/ios/ios-testing/iteration-1/ --dry-run

Directory structure expected:
    <iteration_dir>/
    └── eval-<name>/
        ├── eval_metadata.json          # Contains prompt and assertions
        ├── with_skill/                 # Or any config name
        │   └── run-1/
        │       └── outputs/
        │           └── response.md     # The response to grade
        └── without_skill/
            └── run-1/
                └── outputs/
                    └── response.md

Output:
    Writes grading.json to each run directory (sibling to outputs/):
    <iteration_dir>/eval-<name>/<config>/run-N/grading.json
"""

import argparse
import json
import re
import sys
from pathlib import Path


def load_assertions(eval_metadata_path: Path) -> tuple:
    """
    Load assertions from eval_metadata.json.

    Returns (eval_id, eval_name, assertions_list) or raises on error.
    """
    with open(eval_metadata_path) as f:
        metadata = json.load(f)

    eval_id = metadata.get("eval_id", 0)
    eval_name = metadata.get("eval_name", "unknown")
    assertions = metadata.get("assertions", [])

    return eval_id, eval_name, assertions


def check_keyword_present(response_text: str, check_str: str) -> tuple:
    """
    Check if keywords from a 'check' string are present in the response.

    Handles patterns like:
        "output contains '@Test' or '@Suite'"
        "output contains 'addTeardownBlock' or 'weak sut' or 'weak vm'"
        "output contains '#expect'"

    Returns (passed: bool, evidence: str).
    """
    # Extract quoted strings from the check description
    keywords = re.findall(r"'([^']+)'", check_str)

    if not keywords:
        return False, f"Could not parse keywords from check: {check_str}"

    # Determine if it's an OR or AND check
    is_or = " or " in check_str.lower()

    found = []
    missing = []

    for keyword in keywords:
        if keyword.lower() in response_text.lower():
            # Find the actual occurrence for evidence
            idx = response_text.lower().index(keyword.lower())
            start = max(0, idx - 40)
            end = min(len(response_text), idx + len(keyword) + 40)
            context = response_text[start:end].replace("\n", " ").strip()
            found.append((keyword, context))
        else:
            missing.append(keyword)

    if is_or:
        # At least one keyword must be present
        if found:
            kw, ctx = found[0]
            return True, f"Found '{kw}' in response: ...{ctx}..."
        else:
            return False, f"None of the keywords found: {', '.join(missing)}"
    else:
        # All keywords must be present
        if not missing:
            kw, ctx = found[0]
            return True, f"All keywords found. Example: '{kw}' in: ...{ctx}..."
        else:
            return False, f"Missing keywords: {', '.join(missing)}"


def grade_assertion(response_text: str, assertion: dict) -> dict:
    """
    Grade a single assertion against the response text.

    Returns a grading dict with fields: text, passed, evidence.
    """
    assertion_type = assertion.get("type", "content_check")
    description = assertion.get("description", "Unknown assertion")
    check_str = assertion.get("check", "")

    if assertion_type == "keyword_present":
        passed, evidence = check_keyword_present(response_text, check_str)
        return {
            "text": description,
            "passed": passed,
            "evidence": evidence
        }

    elif assertion_type in ("content_check", "structure_check"):
        # For content/structure checks, attempt basic keyword matching first.
        # Extract quoted keywords from the check string for a best-effort match.
        keywords = re.findall(r"'([^']+)'", check_str)
        if keywords:
            passed, evidence = check_keyword_present(response_text, check_str)
            if passed:
                return {
                    "text": description,
                    "passed": True,
                    "evidence": f"[auto-graded] {evidence}"
                }

        # If no keywords or keywords not found, flag for AI review
        return {
            "text": description,
            "passed": False,
            "evidence": f"[needs-ai-review] This assertion requires semantic evaluation. Check: {check_str}"
        }

    else:
        return {
            "text": description,
            "passed": False,
            "evidence": f"[unknown-type] Assertion type '{assertion_type}' not supported by auto-grader. Needs AI review."
        }


def grade_response(response_path: Path, assertions: list) -> dict:
    """
    Grade a response file against a list of assertions.

    Returns a complete grading dict ready to write as grading.json.
    """
    try:
        response_text = response_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return {
            "expectations": [
                {
                    "text": a.get("description", "Unknown"),
                    "passed": False,
                    "evidence": f"Could not read response file: {e}"
                }
                for a in assertions
            ],
            "summary": {
                "passed": 0,
                "failed": len(assertions),
                "total": len(assertions),
                "pass_rate": 0.0
            }
        }

    expectations = []
    for assertion in assertions:
        result = grade_assertion(response_text, assertion)
        expectations.append(result)

    passed_count = sum(1 for e in expectations if e["passed"])
    failed_count = len(expectations) - passed_count
    total = len(expectations)
    pass_rate = round(passed_count / total, 4) if total > 0 else 0.0

    needs_review = sum(1 for e in expectations if "[needs-ai-review]" in e.get("evidence", ""))

    grading = {
        "expectations": expectations,
        "summary": {
            "passed": passed_count,
            "failed": failed_count,
            "total": total,
            "pass_rate": pass_rate
        }
    }

    if needs_review > 0:
        grading["auto_grader_notes"] = {
            "needs_ai_review": needs_review,
            "message": (
                f"{needs_review} of {total} assertions require semantic evaluation "
                f"and could not be auto-graded. Use grader-prompt.md with an AI agent "
                f"to grade these assertions accurately."
            )
        }

    return grading


def find_response_files(iteration_dir: Path, eval_filter: str = None,
                        config_filter: str = None) -> list:
    """
    Find all (eval_dir, config_dir, run_dir, response_path) tuples in an iteration.

    Returns list of tuples: (eval_dir, config_name, run_dir, response_path)
    """
    results = []

    for eval_dir in sorted(iteration_dir.glob("eval-*")):
        if not eval_dir.is_dir():
            continue
        if eval_filter and eval_dir.name != eval_filter:
            continue

        for config_dir in sorted(eval_dir.iterdir()):
            if not config_dir.is_dir():
                continue
            if config_filter and config_dir.name != config_filter:
                continue

            for run_dir in sorted(config_dir.glob("run-*")):
                # Check both possible response locations
                response_path = run_dir / "outputs" / "response.md"
                if not response_path.exists():
                    # Also check for response.md directly in run_dir
                    response_path = run_dir / "response.md"
                if response_path.exists():
                    results.append((eval_dir, config_dir.name, run_dir, response_path))

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Grade benchmark responses against assertions from eval_metadata.json"
    )
    parser.add_argument(
        "iteration_dir",
        type=Path,
        help="Path to the iteration directory containing eval-* subdirectories"
    )
    parser.add_argument(
        "--eval",
        dest="eval_filter",
        default=None,
        help="Only grade a specific eval (e.g. eval-observable-viewmodel)"
    )
    parser.add_argument(
        "--config",
        dest="config_filter",
        default=None,
        help="Only grade a specific config (e.g. with_skill, without_skill)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be graded without writing files"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing grading.json files"
    )

    args = parser.parse_args()

    if not args.iteration_dir.exists():
        print(f"Error: Directory not found: {args.iteration_dir}")
        sys.exit(1)

    # Find all response files
    response_files = find_response_files(
        args.iteration_dir,
        eval_filter=args.eval_filter,
        config_filter=args.config_filter
    )

    if not response_files:
        print(f"No response files found in {args.iteration_dir}")
        if args.eval_filter:
            print(f"  (filtered to eval: {args.eval_filter})")
        if args.config_filter:
            print(f"  (filtered to config: {args.config_filter})")
        sys.exit(1)

    print(f"Found {len(response_files)} response(s) to grade\n")

    graded_count = 0
    skipped_count = 0
    review_needed = 0

    for eval_dir, config_name, run_dir, response_path in response_files:
        grading_path = run_dir / "grading.json"
        metadata_path = eval_dir / "eval_metadata.json"

        # Check for existing grading
        if grading_path.exists() and not args.force:
            if args.dry_run:
                print(f"  SKIP (exists): {grading_path.relative_to(args.iteration_dir)}")
            skipped_count += 1
            continue

        # Load assertions
        if not metadata_path.exists():
            print(f"  WARNING: No eval_metadata.json in {eval_dir.name}, skipping")
            skipped_count += 1
            continue

        try:
            eval_id, eval_name, assertions = load_assertions(metadata_path)
        except (json.JSONDecodeError, OSError) as e:
            print(f"  ERROR: Could not read {metadata_path}: {e}")
            skipped_count += 1
            continue

        if not assertions:
            print(f"  WARNING: No assertions in {metadata_path}, skipping")
            skipped_count += 1
            continue

        if args.dry_run:
            print(f"  WOULD GRADE: {response_path.relative_to(args.iteration_dir)}")
            print(f"    -> {grading_path.relative_to(args.iteration_dir)}")
            print(f"    assertions: {len(assertions)}")
            graded_count += 1
            continue

        # Grade the response
        grading = grade_response(response_path, assertions)
        grading["eval_id"] = eval_id
        grading["eval_name"] = eval_name
        grading["config"] = config_name

        # Write grading.json
        grading_path.parent.mkdir(parents=True, exist_ok=True)
        with open(grading_path, "w") as f:
            json.dump(grading, f, indent=2)

        pass_rate = grading["summary"]["pass_rate"]
        ai_review = grading.get("auto_grader_notes", {}).get("needs_ai_review", 0)
        review_needed += ai_review

        status = f"pass_rate={pass_rate:.0%}"
        if ai_review > 0:
            status += f" ({ai_review} need AI review)"

        print(f"  GRADED: {eval_dir.name}/{config_name}/run-{run_dir.name.split('-')[1]} -> {status}")
        graded_count += 1

    # Summary
    print(f"\nDone: {graded_count} graded, {skipped_count} skipped")
    if review_needed > 0:
        print(f"\nNote: {review_needed} assertion(s) across all runs need AI review.")
        print("Use grader-prompt.md with an AI agent for accurate semantic grading.")
    if args.dry_run:
        print("\n(Dry run -- no files were written)")


if __name__ == "__main__":
    main()
