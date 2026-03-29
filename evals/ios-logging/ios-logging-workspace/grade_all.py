#!/usr/bin/env python3
"""
Grades all ios-logging eval runs against assertions.
Reads each response.md and checks if assertions are met.
Outputs grading.json per run + aggregate benchmark.json.
"""
import json, os, re, sys
from pathlib import Path

WORKSPACE = Path(__file__).parent / "iteration-1"
EVALS_PATH = Path(__file__).parent.parent / "evals.json"

def load_evals():
    with open(EVALS_PATH) as f:
        return json.load(f)

def read_response(eval_name, variant):
    path = WORKSPACE / eval_name / variant / "outputs" / "response.md"
    if path.exists():
        return path.read_text()
    return ""

def check_assertion(response_text, assertion_id, assertion_text):
    """Check if an assertion is satisfied by the response text.
    Returns (passed: bool, evidence: str)."""
    r = response_text.lower().replace("*", "").replace("`", "")

    checks = {
        # Silent Failures - Simple
        "SF1.1": lambda r: any(x in r for x in ["@discardableresult", "discardable", "task {} swallow", "task swallow", "silently discard", "error is silently"]),
        "SF1.2": lambda r: any(x in r for x in ["try? erases", "try? destroys", "diagnostic information", "error type", "all information lost", "all context lost", "destroys the error"]),
        "SF1.3": lambda r: any(x in r for x in ["logger.error", "logger.", "os.logger", "os_log", "import os"]) and any(x in r for x in ["privacy:", "privacy annotation", ".public", ".private"]),
        "SF1.4": lambda r: any(x in r for x in ["errorreporter", "recordnonfatal", "sentry", "crashlytics", "sentrysdK", "crash report", "crash sdk"]),

        # Silent Failures - Medium
        "SF2.1": lambda r: any(x in r for x in ["kills the", "terminates the", "pipeline permanently", "stops publishing", "failure type to never", "cancels itself"]),
        "SF2.2": lambda r: any(x in r for x in ["inside flatmap", "within flatmap", "error handling inside", "catch inside", "inside the flatmap"]),
        "SF2.3": lambda r: any(x in r for x in ["errorreporter", "recordnonfatal", "sentry", "crashlytics", "crash report", "error report"]),

        # Silent Failures - Complex
        "SF3.1": lambda r: all(x in r for x in ["loadorders", "placeorder"]) and any(x in r for x in ["deleteorder", "all three", "all 3"]),
        "SF3.2": lambda r: any(x in r for x in ["confirmation email", "sendemail", "sendconfirmation"]) and any(x in r for x in ["still runs", "still executes", "even if", "regardless", "logic error", "stale"]),
        "SF3.3": lambda r: any(x in r for x in ["print(", "print is not", "invisible in production", "stdout", "not part of"]),
        "SF3.4": lambda r: any(x in r for x in ["task.detached", "detached"]) and any(x in r for x in ["priority", "cancellation", "strips", "rarely"]),
        "SF3.5": lambda r: any(x in r for x in ["logger.", "os.logger"]) and any(x in r for x in ["privacy:", ".public", ".private", "privacy annotation"]),
        "SF3.6": lambda r: any(x in r for x in ["errorreporter", "recordnonfatal", "sentry", "crashlytics", "crash report", "sentrysdK.capture"]),

        # Logger Setup - Simple
        "LS1.1": lambda r: any(x in r for x in ["os.logger", "import os", "logger(subsystem"]),
        "LS1.2": lambda r: "bundle.main.bundleidentifier" in r and any(x in r for x in ["category", "networking", "auth"]),
        "LS1.3": lambda r: any(x in r for x in ["privacy annotation", "privacy:", ".private", "redacted", "<private>"]),
        "LS1.4": lambda r: any(x in r for x in [".debug", "debug level", "debug messages"]) and any(x in r for x in ["zero cost", "free", "no cost", "optimized away", "no overhead", "no performance"]),

        # Logger Setup - Medium
        "LS2.1": lambda r: any(x in r for x in ["authtoken", "token"]) and any(x in r for x in ["should not", "don't log", "never log", "must not", "remove", "shouldn't", ".sensitive"]),
        "LS2.2": lambda r: "mask: .hash" in r or "mask:.hash" in r or "private(mask:" in r,
        "LS2.3": lambda r: any(x in r for x in ["<private>", "redacted", "without annotation", "default"]) and any(x in r for x in ["production", "log"]),

        # Logger Setup - Complex
        "LS3.1": lambda r: any(x in r for x in ["hipaa", "health", "phi", "protected health", "medical"]),
        "LS3.2": lambda r: any(x in r for x in ["privacyinfo", "privacy manifest", ".xcprivacy", "may 2024"]),
        "LS3.3": lambda r: any(x in r for x in ["redactor", "@redacted", "property wrapper", "redaction utility", "mask"]) and any(x in r for x in ["model", "string", "pii"]),
        "LS3.4": lambda r: "metrickit" in r,

        # Crash SDK - Simple
        "CS1.1": lambda r: any(x in r for x in ["8 non-fatal", "eight non-fatal", "8 exceptions", "limit"]) and "crashlytics" in r,
        "CS1.2": lambda r: any(x in r for x in ["signal handler", "conflict", "both for fatal", "both for crash"]),
        "CS1.3": lambda r: any(x in r for x in ["protocol", "abstraction", "errorreporter", "wrapper"]),

        # Crash SDK - Medium
        "CS2.1": lambda r: any(x in r for x in ["4xx", "5xx", "statuscode", "status code", "http error"]) and any(x in r for x in ["doesn't throw", "does not throw", "not throw", "won't throw"]),
        "CS2.2": lambda r: any(x in r for x in ["breadcrumb", "addbreadcrumb"]),
        "CS2.3": lambda r: any(x in r for x in ["logger.", "os.logger"]) and any(x in r for x in ["privacy:", ".public", "privacy annotation"]),
        "CS2.4": lambda r: any(x in r for x in ["errorreporter", "recordnonfatal", "sentrysdK.capture", "crashlytics", "record(error"]),

        # Crash SDK - Complex
        "CS3.1": lambda r: any(x in r for x in ["signal handler", "sigabrt", "sigsegv", "sigbus"]) and any(x in r for x in ["conflict", "last registered", "only one", "overwrite"]),
        "CS3.2": lambda r: "nssetuncaughtexceptionhandler" in r and any(x in r for x in ["one handler", "only one", "replaces", "single"]),
        "CS3.3": lambda r: any(x in r for x in ["enablecrashhandler", "disable crash", "crash handler"]) and any(x in r for x in ["false", "disable"]),
        "CS3.4": lambda r: "metrickit" in r and any(x in r for x in ["oom", "watchdog", "out-of-process", "out of process"]),

        # Enterprise - Simple
        "EP1.1": lambda r: any(x in r for x in ["errorhandler", "error handler", "errorhandling"]) and any(x in r for x in ["observableobject", "observable", "environment"]),
        "EP1.2": lambda r: any(x in r for x in ["categorizederror", "categorized"]) and any(x in r for x in ["retryable", "nonretryable", "requireslogout", "logout"]),
        "EP1.3": lambda r: any(x in r for x in ["error boundar", "react", "swiftui lacks", "no error boundar"]),

        # Enterprise - Medium
        "EP2.1": lambda r: any(x in r for x in ["after all retries", "all retries exhausted", "only after", "final failure", "last attempt"]) and any(x in r for x in ["report", "crash", "sentry", "nonfatal"]),
        "EP2.2": lambda r: any(x in r for x in ["breadcrumb", "addbreadcrumb"]) and any(x in r for x in ["retry", "attempt"]),
        "EP2.3": lambda r: any(x in r for x in [".warning", "warning"]) and any(x in r for x in ["retry", "attempt", "intermediate"]),
        "EP2.4": lambda r: "jitter" in r and any(x in r for x in ["random", "double.random", ".random(in"]),

        # Enterprise - Complex
        "EP3.1": lambda r: any(x in r for x in ["separate process", "own process", "sandboxed process", "different process"]),
        "EP3.2": lambda r: any(x in r for x in ["initialize separately", "init separately", "own initialization", "initialize crash", "sentrysdK.start"]) and any(x in r for x in ["extension", "widget"]),
        "EP3.3": lambda r: any(x in r for x in ["dsym", "dsyms"]) and any(x in r for x in ["extension", "each target", "each extension"]),
        "EP3.4": lambda r: "app group" in r or "appgroup" in r or "userdefaults(suitename" in r or "suitename" in r,
        "EP3.5": lambda r: any(x in r for x in ["autosessiontracking", "session tracking", "enableautosessiontracking"]) and any(x in r for x in ["disable", "false"]),

        # MetricKit - Simple
        "MK1.1": lambda r: any(x in r for x in ["out-of-process", "out of process", "separate process", "system process"]),
        "MK1.2": lambda r: any(x in r for x in ["oom", "out of memory", "watchdog"]) and any(x in r for x in ["miss", "catch", "detect"]),
        "MK1.3": lambda r: any(x in r for x in ["share with app developer", "opt-in", "opt in"]),
        "MK1.4": lambda r: any(x in r for x in ["use both", "alongside", "complement", "in addition"]),

        # ObjC Exceptions - Simple
        "OE1.1": lambda r: any(x in r for x in ["nsexception", "objective-c exception", "objc exception"]) and any(x in r for x in ["not caught", "won't catch", "doesn't catch", "cannot catch", "will not catch", "never execute", "never catch", "will never", "do/catch will not", "do-catch will not"]),
        "OE1.2": lambda r: sum(1 for x in ["out-of-bounds", "out of bounds", "kvo", "unrecognized selector", "nsrangeexception"] if x in r) >= 2,
        "OE1.3": lambda r: any(x in r for x in ["force unwrap", "sigtrap", "exc_bad_access", "signal handler"]),

        # PII Compliance - Simple
        "PC1.1": lambda r: any(x in r for x in ["http bod", "request bod", "response bod", "auth header", "url path"]) and any(x in r for x in ["leak", "contain", "expos"]),
        "PC1.2": lambda r: any(x in r for x in ["privacyinfo", "privacy manifest", ".xcprivacy", "may 2024"]),
        "PC1.3": lambda r: any(x in r for x in ["att", "app tracking transparency"]) and any(x in r for x in ["not require", "doesn't require", "does not require", "not tracking", "not considered"]),
        "PC1.4": lambda r: "mask: .hash" in r or "mask:.hash" in r or "private(mask:" in r,
    }

    checker = checks.get(assertion_id)
    if checker:
        passed = checker(r)
        return passed, "Keyword-based assertion check"
    return False, f"No checker defined for {assertion_id}"


def grade_run(eval_entry, variant):
    eval_name = eval_entry["name"]
    response = read_response(eval_name, variant)
    if not response:
        return None

    expectations = []
    for assertion in eval_entry["assertions"]:
        passed, evidence = check_assertion(response, assertion["id"], assertion["text"])
        expectations.append({
            "text": assertion["text"],
            "passed": passed,
            "evidence": evidence
        })

    grading = {
        "eval_id": eval_entry["id"],
        "eval_name": eval_name,
        "variant": variant,
        "expectations": expectations,
        "pass_count": sum(1 for e in expectations if e["passed"]),
        "total": len(expectations)
    }

    # Save grading.json
    out_path = WORKSPACE / eval_name / variant / "grading.json"
    with open(out_path, "w") as f:
        json.dump(grading, f, indent=2)

    return grading


def generate_benchmark(all_gradings, evals_data):
    with_skill = [g for g in all_gradings if g and g["variant"] == "with_skill"]
    without_skill = [g for g in all_gradings if g and g["variant"] == "without_skill"]

    ws_pass = sum(g["pass_count"] for g in with_skill)
    ws_total = sum(g["total"] for g in with_skill)
    wo_pass = sum(g["pass_count"] for g in without_skill)
    wo_total = sum(g["total"] for g in without_skill)

    # By reference (topic)
    refs = {}
    for ev in evals_data["evals"]:
        ref = ev["reference"]
        if ref not in refs:
            refs[ref] = {"with_skill": {"pass": 0, "total": 0}, "without_skill": {"pass": 0, "total": 0}}

    for g in all_gradings:
        if not g:
            continue
        ev = next((e for e in evals_data["evals"] if e["name"] == g["eval_name"]), None)
        if ev:
            ref = ev["reference"]
            refs[ref][g["variant"]]["pass"] += g["pass_count"]
            refs[ref][g["variant"]]["total"] += g["total"]

    by_reference = {}
    for ref, data in refs.items():
        ws = data["with_skill"]
        wo = data["without_skill"]
        ws_rate = (ws["pass"] / ws["total"] * 100) if ws["total"] > 0 else 0
        wo_rate = (wo["pass"] / wo["total"] * 100) if wo["total"] > 0 else 0
        by_reference[ref] = {
            "with_skill": {**ws, "rate": round(ws_rate, 1)},
            "without_skill": {**wo, "rate": round(wo_rate, 1)},
            "delta": round(ws_rate - wo_rate, 1)
        }

    # Per-eval breakdown
    per_eval = []
    for ev in evals_data["evals"]:
        ws_g = next((g for g in with_skill if g["eval_name"] == ev["name"]), None)
        wo_g = next((g for g in without_skill if g["eval_name"] == ev["name"]), None)
        entry = {"eval_name": ev["name"], "reference": ev["reference"]}
        if ws_g:
            entry["with_skill"] = {"pass": ws_g["pass_count"], "total": ws_g["total"],
                                    "rate": round(ws_g["pass_count"]/ws_g["total"]*100, 1) if ws_g["total"] > 0 else 0}
        if wo_g:
            entry["without_skill"] = {"pass": wo_g["pass_count"], "total": wo_g["total"],
                                       "rate": round(wo_g["pass_count"]/wo_g["total"]*100, 1) if wo_g["total"] > 0 else 0}
        if ws_g and wo_g:
            entry["delta"] = round(entry["with_skill"]["rate"] - entry["without_skill"]["rate"], 1)
        per_eval.append(entry)

    benchmark = {
        "skill_name": "ios-logging",
        "model": "opus-4.6",
        "summary": {
            "with_skill": {"pass": ws_pass, "total": ws_total, "rate": round(ws_pass/ws_total*100, 1) if ws_total > 0 else 0},
            "without_skill": {"pass": wo_pass, "total": wo_total, "rate": round(wo_pass/wo_total*100, 1) if wo_total > 0 else 0},
            "delta": round((ws_pass/ws_total - wo_pass/wo_total)*100, 1) if ws_total > 0 and wo_total > 0 else 0
        },
        "by_reference": by_reference,
        "per_eval": per_eval
    }

    # Save benchmark.json
    bench_path = WORKSPACE / "benchmark.json"
    with open(bench_path, "w") as f:
        json.dump(benchmark, f, indent=2)

    # Generate benchmark.md
    md_lines = [
        f"# ios-logging Benchmark (Opus 4.6)",
        f"",
        f"## Summary",
        f"",
        f"| Config | Pass | Total | Rate |",
        f"|--------|------|-------|------|",
        f"| **With Skill** | {ws_pass} | {ws_total} | {benchmark['summary']['with_skill']['rate']}% |",
        f"| **Without Skill** | {wo_pass} | {wo_total} | {benchmark['summary']['without_skill']['rate']}% |",
        f"| **Delta** | | | **+{benchmark['summary']['delta']}%** |",
        f"",
        f"## By Reference",
        f"",
        f"| Reference | With Skill | Without Skill | Delta |",
        f"|-----------|-----------|--------------|-------|",
    ]
    for ref, data in sorted(by_reference.items()):
        md_lines.append(f"| {ref} | {data['with_skill']['rate']}% | {data['without_skill']['rate']}% | +{data['delta']}% |")

    md_lines += [
        f"",
        f"## Per Eval",
        f"",
        f"| Eval | Reference | With Skill | Without Skill | Delta |",
        f"|------|-----------|-----------|--------------|-------|",
    ]
    for pe in per_eval:
        ws_rate = pe.get("with_skill", {}).get("rate", "—")
        wo_rate = pe.get("without_skill", {}).get("rate", "—")
        delta = pe.get("delta", "—")
        md_lines.append(f"| {pe['eval_name']} | {pe['reference']} | {ws_rate}% | {wo_rate}% | +{delta}% |")

    md_path = WORKSPACE / "benchmark.md"
    with open(md_path, "w") as f:
        f.write("\n".join(md_lines) + "\n")

    return benchmark


def main():
    evals_data = load_evals()
    all_gradings = []

    missing = []
    for ev in evals_data["evals"]:
        for variant in ["with_skill", "without_skill"]:
            resp_path = WORKSPACE / ev["name"] / variant / "outputs" / "response.md"
            if not resp_path.exists():
                missing.append(f"{ev['name']}/{variant}")

    if missing:
        print(f"WARNING: {len(missing)} missing responses:")
        for m in missing:
            print(f"  - {m}")
        print()

    for ev in evals_data["evals"]:
        for variant in ["with_skill", "without_skill"]:
            grading = grade_run(ev, variant)
            if grading:
                all_gradings.append(grading)
                status = f"{grading['pass_count']}/{grading['total']}"
                print(f"  {ev['name']:30s} {variant:15s} -> {status}")
            else:
                print(f"  {ev['name']:30s} {variant:15s} -> MISSING")

    if all_gradings:
        benchmark = generate_benchmark(all_gradings, evals_data)
        print(f"\n=== BENCHMARK ===")
        print(f"With Skill:    {benchmark['summary']['with_skill']['pass']}/{benchmark['summary']['with_skill']['total']} ({benchmark['summary']['with_skill']['rate']}%)")
        print(f"Without Skill: {benchmark['summary']['without_skill']['pass']}/{benchmark['summary']['without_skill']['total']} ({benchmark['summary']['without_skill']['rate']}%)")
        print(f"Delta:         +{benchmark['summary']['delta']}%")


if __name__ == "__main__":
    main()
