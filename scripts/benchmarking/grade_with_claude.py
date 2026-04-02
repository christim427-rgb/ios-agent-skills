#!/usr/bin/env python3
"""
Grade benchmark responses against assertions using Claude as judge.

Strict, no-charity grading: each assertion either has clear evidence in the
response or it fails. The burden of proof is on the response to pass.

Usage:
    python grade_with_claude.py <iteration_dir> [--config gpt-5-4-with gpt-5-4-without]
    python grade_with_claude.py <iteration_dir> --force

Examples:
    python grade_with_claude.py workspaces/ios/swift-concurrency/iteration-5/
    python grade_with_claude.py workspaces/ios/ios-testing/iteration-9/ --force
"""

import argparse
import json
import sys
import time
from pathlib import Path

import anthropic

MODEL = "claude-sonnet-4-6"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

GRADER_SYSTEM = """You are a strict, impartial grader evaluating an AI assistant's response to a coding question.

Your job: determine whether each assertion is clearly satisfied by the response.

Grading rules:
- PASS only if the response contains clear, unambiguous evidence the assertion is true
- FAIL if the evidence is absent, partial, or you have to infer it
- No partial credit. No charity. No "probably meant to".
- Base your verdict solely on what is written in the response, not what you think is implied
- Cite the specific text that proves PASS, or explain what is missing for FAIL

Return a JSON array with one object per assertion:
[
  {"text": "<assertion text>", "passed": true/false, "evidence": "<quote or explanation>"},
  ...
]

Return ONLY the JSON array, no other text."""


def grade_assertions(client: anthropic.Anthropic, prompt: str, response_text: str,
                     assertions: list) -> list:
    """Grade assertions against a response using Claude."""
    assertions_text = "\n".join(
        f"{i+1}. {a['text']}" for i, a in enumerate(assertions)
    )

    user_msg = f"""## Original question
{prompt}

## Response to grade
{response_text}

## Assertions to grade (answer each)
{assertions_text}"""

    for attempt in range(MAX_RETRIES):
        try:
            msg = client.messages.create(
                model=MODEL,
                max_tokens=2048,
                system=GRADER_SYSTEM,
                messages=[{"role": "user", "content": user_msg}]
            )
            raw = msg.content[0].text.strip()

            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1]
                raw = raw.rsplit("```", 1)[0]

            results = json.loads(raw)

            # Validate we got the right number of results
            if len(results) != len(assertions):
                # Try to match by text
                text_map = {r["text"]: r for r in results if "text" in r}
                aligned = []
                for a in assertions:
                    if a["text"] in text_map:
                        aligned.append(text_map[a["text"]])
                    else:
                        aligned.append({
                            "text": a["text"],
                            "passed": False,
                            "evidence": f"[grader-error] Could not align result (got {len(results)}, expected {len(assertions)})"
                        })
                results = aligned

            return results

        except (json.JSONDecodeError, anthropic.APIError) as e:
            if attempt < MAX_RETRIES - 1:
                print(f"    Retry {attempt+1}/{MAX_RETRIES}: {e}")
                time.sleep(RETRY_DELAY)
            else:
                # Return fail-all on final failure
                return [
                    {
                        "text": a["text"],
                        "passed": False,
                        "evidence": f"[grader-error] {type(e).__name__}: {e}"
                    }
                    for a in assertions
                ]


def build_grading_json(eval_id: int, variant: str, expectations: list) -> dict:
    passed = sum(1 for e in expectations if e["passed"])
    total = len(expectations)
    return {
        "eval_id": eval_id,
        "variant": variant,
        "expectations": expectations,
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "pass_rate": round(passed / total, 4) if total > 0 else 0.0
        }
    }


def find_runs(iteration_dir: Path, config_filter: list = None) -> list:
    """Return list of (eval_dir, config_name, run_dir, response_path)."""
    results = []
    for eval_dir in sorted(iteration_dir.glob("eval-*")):
        if not eval_dir.is_dir():
            continue
        for config_dir in sorted(eval_dir.iterdir()):
            if not config_dir.is_dir():
                continue
            if config_filter and config_dir.name not in config_filter:
                continue
            for run_dir in sorted(config_dir.glob("run-*")):
                resp = run_dir / "outputs" / "response.md"
                if resp.exists():
                    results.append((eval_dir, config_dir.name, run_dir, resp))
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("iteration_dir", type=Path)
    parser.add_argument("--config", nargs="*", default=None,
                        help="Only grade these config dirs (e.g. gpt-5-4-with gpt-5-4-without)")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing grading.json")
    args = parser.parse_args()

    if not args.iteration_dir.exists():
        print(f"Error: {args.iteration_dir} not found")
        sys.exit(1)

    client = anthropic.Anthropic()

    runs = find_runs(args.iteration_dir, args.config)
    if not runs:
        print(f"No runs found in {args.iteration_dir}")
        sys.exit(1)

    print(f"Found {len(runs)} run(s) to grade in {args.iteration_dir.name}")

    graded = skipped = errors = 0

    for eval_dir, config_name, run_dir, resp_path in runs:
        grading_path = run_dir / "grading.json"

        if grading_path.exists() and not args.force:
            skipped += 1
            continue

        meta_path = eval_dir / "eval_metadata.json"
        if not meta_path.exists():
            print(f"  SKIP (no metadata): {eval_dir.name}")
            skipped += 1
            continue

        with open(meta_path) as f:
            meta = json.load(f)

        assertions = meta.get("assertions", [])
        if not assertions:
            print(f"  SKIP (no assertions): {eval_dir.name}")
            skipped += 1
            continue

        prompt = meta.get("prompt", "")
        eval_id = meta.get("id", 0)

        response_text = resp_path.read_text(encoding="utf-8")

        print(f"  Grading {eval_dir.name}/{config_name} ({len(assertions)} assertions)...", end=" ", flush=True)

        expectations = grade_assertions(client, prompt, response_text, assertions)

        grading = build_grading_json(eval_id, config_name, expectations)

        with open(grading_path, "w") as f:
            json.dump(grading, f, indent=2)

        passed = grading["summary"]["passed"]
        total = grading["summary"]["total"]
        print(f"{passed}/{total} passed")
        graded += 1

    print(f"\nDone: {graded} graded, {skipped} skipped, {errors} errors")


if __name__ == "__main__":
    main()
