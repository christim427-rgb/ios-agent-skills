#!/usr/bin/env python3
"""
aggregate.py — Aggregate grading artifacts into benchmark-<model>.json.

Usage:
  python aggregate.py <iteration_root> <model_slug>

  iteration_root : e.g. skills/ios/gcd-operationqueue-workspace/iteration-2
  model_slug     : e.g. gpt-5-4

Reads:
  eval-<name>/eval_metadata.json
  eval-<name>/<model_slug>-with/run-1/grading.json
  eval-<name>/<model_slug>-without/run-1/grading.json

Writes:
    benchmark-<model_slug>.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

def load_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"  [!] JSON parse error in {path}: {exc}", file=sys.stderr)
        return None


def sum_summaries(summaries: list[dict]) -> dict:
    passed = sum(s["passed"] for s in summaries)
    total = sum(s["total"] for s in summaries)
    failed = total - passed
    return {
        "passed": passed,
        "failed": failed,
        "total": total,
        "pass_rate": round(passed / total, 4) if total else 0.0,
    }


def load_runs(variant_dir: Path) -> list[dict]:
    """Load all grading.json files from run-* subdirectories, sorted by run number."""
    gradings = []
    for run_dir in sorted(variant_dir.glob("run-*")):
        g = load_json(run_dir / "grading.json")
        if g is not None:
            gradings.append(g)
    return gradings


def average_summary(gradings: list[dict]) -> dict:
    """Average pass_rate across multiple runs; assertion counts scaled from run-1 total."""
    total = gradings[0]["summary"]["total"]
    avg_rate = round(sum(g["summary"]["pass_rate"] for g in gradings) / len(gradings), 4)
    avg_passed = round(avg_rate * total)
    return {
        "passed": avg_passed,
        "failed": total - avg_passed,
        "total": total,
        "pass_rate": avg_rate,
        "runs": len(gradings),
    }


def infer_topic(meta: dict) -> str:
    for key in ("topic", "reference", "name"):
        value = meta.get(key)
        if isinstance(value, str) and value:
            return value
    return "ungrouped"


def build_assertion_text_index(meta: dict) -> dict[str, str]:
    assertion_texts: dict[str, str] = {}
    for index, assertion in enumerate(meta.get("assertions", []), start=1):
        if isinstance(assertion, dict):
            assertion_id = assertion.get("id", f"A{index}")
            assertion_texts[assertion_id] = assertion.get("text", "")
        elif isinstance(assertion, str):
            assertion_texts[f"A{index}"] = assertion
    return assertion_texts


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate grading artifacts into benchmark JSON")
    parser.add_argument("iteration_root", help="Path to iteration directory")
    parser.add_argument("model_slug", help="Lowercase hyphenated model identifier (e.g. gpt-5-4)")
    args = parser.parse_args()

    root = Path(args.iteration_root).resolve()
    slug = args.model_slug

    if not root.is_dir():
        sys.exit(f"[aggregate] Iteration root does not exist: {root}")

    eval_dirs = sorted(d for d in root.iterdir() if d.is_dir() and d.name.startswith("eval-"))
    if not eval_dirs:
        sys.exit(f"[aggregate] No eval-* directories found in {root}")

    topic_with: dict[str, list[dict]] = {}
    topic_without: dict[str, list[dict]] = {}
    discriminating: list[dict] = []
    eval_set_name: Optional[str] = None
    missing: list[str] = []

    for eval_dir in eval_dirs:
        meta = load_json(eval_dir / "eval_metadata.json")
        if meta is None:
            missing.append(f"{eval_dir.name}: missing eval_metadata.json")
            continue

        topic = infer_topic(meta)

        if eval_set_name is None:
            eval_set_name = meta.get("source_eval_set", "evals.json")

        eval_name = meta.get("name", eval_dir.name.removeprefix("eval-"))

        with_gradings = load_runs(eval_dir / f"{slug}-with")
        without_gradings = load_runs(eval_dir / f"{slug}-without")

        if not with_gradings or not without_gradings:
            missing.append(f"{eval_dir.name}: missing grading.json for '{slug}'")
            continue

        topic_with.setdefault(topic, []).append(average_summary(with_gradings))
        topic_without.setdefault(topic, []).append(average_summary(without_gradings))

        # Build assertion text index from eval_metadata (ground truth)
        assertion_texts = build_assertion_text_index(meta)

        # Collect discriminating assertions: use run-1 (first available run)
        with_index = {a["id"]: a for a in with_gradings[0].get("assertions", [])}
        for a in without_gradings[0].get("assertions", []):
            if not a["passed"]:
                with_a = with_index.get(a["id"])
                if with_a and with_a["passed"]:
                    discriminating.append({
                        "eval": eval_name,
                        "id": a["id"],
                        "text": assertion_texts.get(a["id"], a.get("notes", "")),
                    })

    if missing:
        print("[aggregate] MISSING grading artifacts — benchmark will be incomplete:", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        print("[aggregate] Grade the missing evals first, then re-run aggregate.", file=sys.stderr)
        sys.exit(1)

    # Build topic results
    topic_results = {}
    overall_with_total = {"passed": 0, "failed": 0, "total": 0}
    overall_without_total = {"passed": 0, "failed": 0, "total": 0}

    for topic in sorted(set(topic_with) | set(topic_without)):
        with_summaries = topic_with.get(topic, [])
        without_summaries = topic_without.get(topic, [])
        if not with_summaries or not without_summaries:
            topic_results[topic] = {"with_skill": None, "without_skill": None, "delta": None}
            continue

        ws = sum_summaries(with_summaries)
        wos = sum_summaries(without_summaries)
        delta = round(ws["pass_rate"] - wos["pass_rate"], 4)
        topic_results[topic] = {"with_skill": ws, "without_skill": wos, "delta": delta}

        for key in ("passed", "failed", "total"):
            overall_with_total[key] += ws[key]
            overall_without_total[key] += wos[key]

    ow = overall_with_total
    owt = overall_without_total
    ow["pass_rate"] = round(ow["passed"] / ow["total"], 4) if ow["total"] else 0.0
    owt["pass_rate"] = round(owt["passed"] / owt["total"], 4) if owt["total"] else 0.0

    skill_name = root.parent.name
    runs_per_eval = max(
        (
            summary.get("runs", 1)
            for summary_list in list(topic_with.values()) + list(topic_without.values())
            for summary in summary_list
        ),
        default=1,
    )
    benchmark = {
        "model": slug,
        "skill": skill_name,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "eval_set": eval_set_name or "evals.json",
        "runs_per_eval": runs_per_eval,
        "topic_results": topic_results,
        "overall": {
            "with_skill": ow,
            "without_skill": owt,
            "delta": round(ow["pass_rate"] - owt["pass_rate"], 4),
        },
        "discriminating_assertions_failed_by_baseline": discriminating,
    }

    out_path = root / f"benchmark-{slug}.json"
    out_path.write_text(json.dumps(benchmark, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[aggregate] Written : {out_path.relative_to(Path.cwd())}")
    print(f"[aggregate] Overall : with={ow['pass_rate']:.1%}  without={owt['pass_rate']:.1%}  delta={benchmark['overall']['delta']:+.1%}")
    print(f"[aggregate] Evals   : {len(eval_dirs)} total | runs/eval: {runs_per_eval} | discriminating assertions: {len(discriminating)}")


if __name__ == "__main__":
    main()
