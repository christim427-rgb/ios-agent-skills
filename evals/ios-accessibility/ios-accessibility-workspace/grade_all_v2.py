#!/usr/bin/env python3
"""
Grades all ios-accessibility eval runs against assertions.
Reads each response.md and checks if assertions are met.
Outputs grading.json per run + aggregate benchmark.json.
"""
import json, os, re, sys
from pathlib import Path

WORKSPACE = Path(__file__).parent / "iteration-2"
EVALS_PATH = Path(__file__).parent.parent / "evals" / "ios-accessibility" / "evals.json"

def load_evals():
    with open(EVALS_PATH) as f:
        return json.load(f)

def read_response(eval_name, variant):
    """Read the response.md for a given eval and variant (with_skill/without_skill)."""
    path = WORKSPACE / eval_name / variant / "outputs" / "response.md"
    if path.exists():
        return path.read_text()
    return ""

def check_assertion(response_text, assertion):
    """Check if an assertion is satisfied by the response text.
    Returns (passed: bool, evidence: str)."""
    text = assertion["text"].lower()
    response_lower = response_text.lower()

    # Define keyword patterns for each assertion
    checks = {
        # VoiceOver Labels
        "VL1.1": lambda r: ("button" in text and ("should not" in text or "don't include" in text)) or
                           (not any(x in r for x in ['"play button"', '"heart icon button"', 'include the element type', "don't include", "should not include", "redundant"])),
        "VL1.2": lambda r: any(x in r for x in ["describe appearance", "describes appearance", "purpose", "not appearance", "don't describe", "heart icon"]),
        "VL1.3": lambda r: any(x in r for x in ["add to favorites", "favorite", "toggle favorite", "mark as favorite"]),
        "VL2.1": lambda r: any(x in r for x in [".accessibilityelement(children:", "children: .combine", "children: .ignore", "accessibilityelement"]),
        "VL2.2": lambda r: any(x in r for x in ["hide", "hidden", "decorative", "accessibilityhidden"]),
        "VL2.3": lambda r: any(x in r for x in ["out of 5", "out of five", "stars", "star rating"]),
        "VL3.1": lambda r: "accessibilitycustomaction" in r,
        "VL3.2": lambda r: any(x in r for x in [".accessibilityelement(children:", "children: .combine", "children: .ignore", "group"]),
        "VL3.3": lambda r: any(x in r for x in ["swipe up", "swipe down", "up/down", "up and down"]),
        "VL3.4": lambda r: "return true" in r or "-> bool" in r or "returns a bool" in r or "bool" in r,

        # VoiceOver Traits
        "VT1.1": lambda r: ".accessibilityaddtraits(.isheader)" in r or "isheader" in r or ".header" in r,
        "VT1.2": lambda r: "rotor" in r and "heading" in r,
        "VT2.1": lambda r: any(x in r for x in ["destroys", "replaces", "overwrites", "loses", "wipes", "removes existing"]),
        "VT2.2": lambda r: ".insert(" in r or "insert(." in r,
        "VT2.3": lambda r: ".accessibilitytraits.insert(.selected)" in r or "insert(.selected)" in r,
        "VT3.1": lambda r: "button" in r and any(x in r for x in ["ontapgesture", "replace", "instead"]),
        "VT3.2": lambda r: "accessibilityadjustableaction" in r or "adjustableaction" in r or "adjustable" in r,
        "VT3.3": lambda r: "accessibilityvalue" in r or ".accessibilityvalue" in r,
        "VT3.4": lambda r: any(x in r for x in [".accessibilityelement()", "accessibilityelement", "group", "single element"]),

        # VoiceOver Grouping
        "VG1.1": lambda r: any(x in r for x in ["pause", "comma", "joined", "concatenat", "merges"]),
        "VG1.2": lambda r: any(x in r for x in ["custom label", "provide", "manual", "your own label", "parent"]),
        "VG1.3": lambda r: any(x in r for x in ["natural", "sentence", "coherent", "readable"]),
        "VG2.1": lambda r: any(x in r for x in ["children: .combine", "children: .ignore", ".accessibilityelement"]),
        "VG2.2": lambda r: any(x in r for x in ["storage", "5 gigabyte", "5gb", "basic", "pro"]),
        "VG2.3": lambda r: any(x in r for x in ["shouldgroupaccessibilitychildren", "accessibilitysortpriority", "sort priority", "navigation order"]),
        "VG3.1": lambda r: ".accessibilitychildren" in r or "accessibilitychildren" in r,
        "VG3.2": lambda r: ".accessibilitylabel" in r and any(x in r for x in ["chart", "canvas", "graph"]),
        "VG3.3": lambda r: any(x in r for x in ["each", "per", "individual", "data point", "point.label"]),

        # VoiceOver Actions
        "VA1.1": lambda r: any(x in r for x in ["result", "outcome", "consequence", "what happens"]),
        "VA1.2": lambda r: any(x in r for x in ["verb", "begins with", "third person", "starts with"]),
        "VA1.3": lambda r: any(x in r for x in ["redundant", "tap to delete", "don't", "unnecessary", "obvious"]),
        "VA2.1": lambda r: any(x in r for x in ["accessibilitynotification.announcement", "uiaccessibility.post", ".announcement"]),
        "VA2.2": lambda r: any(x in r for x in [".layoutchanged", ".screenchanged", "layoutchanged", "screenchanged"]) and "announcement" in r,
        "VA2.3": lambda r: any(x in r for x in ["lost", "interrupted", "speaking", "already speaking", "can be lost"]),
        "VA3.1": lambda r: "accessibilityviewismodal" in r or "ismodal" in r,
        "VA3.2": lambda r: any(x in r for x in ["sibling", "only hides sibling", "siblings"]),
        "VA3.3": lambda r: any(x in r for x in ["hierarchy", "view hierarchy", "direct child", "parent", "nested"]),
        "VA3.4": lambda r: any(x in r for x in ["accessibilityperformescape", "performescape", "escape", "two-finger z"]),

        # Dynamic Type
        "DT1.1": lambda r: any(x in r for x in ["hardcoded", "fixed", "doesn't scale", "won't scale", "not scale"]),
        "DT1.2": lambda r: any(x in r for x in [".title", ".body", ".headline", "text style", "dynamic type"]),
        "DT1.3": lambda r: any(x in r for x in ["25%", "quarter", "many users", "significant", "percentage"]),
        "DT2.1": lambda r: "uifontmetrics" in r or "scaledfont" in r,
        "DT2.2": lambda r: "adjustsfontforcontentsizecategory" in r,
        "DT2.3": lambda r: "numberoflines" in r and "0" in r,
        "DT3.1": lambda r: any(x in r for x in ["dynamictypesize", "isaccessibilitysize", "isaccessibilitycategory", "isAccessibilitySize"]),
        "DT3.2": lambda r: any(x in r for x in ["viewthatfits", "anylayout", "vstack"]),
        "DT3.3": lambda r: "@scaledmetric" in r or "scaledmetric" in r,
        "DT3.4": lambda r: "scrollview" in r,

        # Color Contrast
        "CC1.1": lambda r: any(x in r for x in ["dark mode", "darkmode", "color scheme"]),
        "CC1.2": lambda r: any(x in r for x in [".foregroundstyle(.primary)", "foregroundstyle", "color(.systembackground)", "systembackground"]),
        "CC1.3": lambda r: any(x in r for x in ["deprecated", "foregroundstyle", ".foregroundcolor"]),
        "CC2.1": lambda r: any(x in r for x in ["color alone", "color-only", "sole indicator", "wcag 1.4.1", "not just color"]),
        "CC2.2": lambda r: any(x in r for x in ["shape", "icon", "text", "checkmark", "xmark", "label"]),
        "CC2.3": lambda r: "differentiatewithoutcolor" in r or "accessibilitydifferentiatewithoutcolor" in r,
        "CC3.1": lambda r: "4.5" in r and ("3:1" in r or "3.0" in r or "large text" in r),
        "CC3.2": lambda r: any(x in r for x in ["contrast ratio", "luminance", "calculate", "approximately", "does not pass", "fails"]),
        "CC3.3": lambda r: any(x in r for x in ["dark mode", "both", "light and dark", "independently"]),
        "CC3.4": lambda r: any(x in r for x in ["colorschemecontrast", "increased", "increase contrast", "7:1"]),

        # Motion Preferences
        "MP1.1": lambda r: "accessibilityreducemotion" in r or "reducemotion" in r,
        "MP1.2": lambda r: any(x in r for x in ["crossfade", "opacity", "don't remove all", "subtle", "replace"]),
        "MP2.1": lambda r: "reducemotion" in r and any(x in r for x in ["check", "environment", "@environment"]),
        "MP2.2": lambda r: any(x in r for x in [".none", "easeinout", "alternative", "fallback"]),
        "MP2.3": lambda r: "reducemotion ?" in r or "reducemotion?" in r or ("ternary" in r) or ("reducemotion" in r and "?" in r and ".spring" in r),
        "MP3.1": lambda r: "reducetransparency" in r and any(x in r for x in ["solid", "material", "background", "opaque"]),
        "MP3.2": lambda r: "differentiatewithoutcolor" in r,
        "MP3.3": lambda r: "legibilityweight" in r or "bold text" in r.lower(),
        "MP3.4": lambda r: "colorschemecontrast" in r or "increase contrast" in r.lower() or "increasecontrast" in r,
        "MP3.5": lambda r: "accessibilityignoresinvertcolors" in r or "ignoresinvertcolors" in r,

        # SwiftUI Controls
        "SC1.1": lambda r: any(x in r for x in ["invisible", "not accessible", "can't see", "won't see", "doesn't get", "no trait"]),
        "SC1.2": lambda r: "button" in r and "accessibilitylabel" in r,
        "SC1.3": lambda r: any(x in r for x in ["switch control", "eye tracking", "voice control", "assistive"]),
        "SC2.1": lambda r: any(x in r for x in ["replace", "button", "instead of ontapgesture"]),
        "SC2.2": lambda r: "istoggle" in r or ".istoggle" in r,
        "SC2.3": lambda r: "accessibilityvalue" in r and any(x in r for x in ["on", "off"]),
        "SC2.4": lambda r: ".accessibilityelement(children:" in r or "group" in r,
        "SC3.1": lambda r: ".accessibilitylabel" in r and any(x in r for x in ["textfield", "field", "input"]),
        "SC3.2": lambda r: any(x in r for x in ["accessibilitylabeledpair", "labeledpair", "accessibilitylabel"]),
        "SC3.3": lambda r: "textcontenttype" in r or ".username" in r or ".emailaddress" in r or ".password" in r,

        # UIKit Controls
        "UK1.1": lambda r: any(x in r for x in ["testing", "ui test", "automation", "not read", "not spoken"]),
        "UK1.2": lambda r: "accessibilitylabel" in r,
        "UK1.3": lambda r: "accessibilitylabel" in r and "accessibilityidentifier" in r,
        "UK2.1": lambda r: any(x in r for x in ["isaccessibilityelement = false", "hidden", "hides", "disappear", "invisible"]),
        "UK2.2": lambda r: any(x in r for x in ["notenabled", ".notenabled", "dimmed"]),
        "UK2.3": lambda r: any(x in r for x in ["dimmed", "user knows", "exists", "discover"]),
        "UK3.1": lambda r: "isaccessibilityelement" in r and "false" in r,
        "UK3.2": lambda r: "accessibilityelements" in r and any(x in r for x in ["uiaccessibilityelement", "array", "override"]),
        "UK3.3": lambda r: any(x in r for x in ["converttoscreencoordinates", "accessibilityframe", "screen coordinates"]),
        "UK3.4": lambda r: "accessibilitylabel" in r and "accessibilityvalue" in r,

        # WCAG Mapping
        "WC1.1": lambda r: "1.4.4" in r,
        "WC1.2": lambda r: any(x in r for x in ["preferredfont", "dynamic type", "text style", ".body", ".title"]),
        "WC2.1": lambda r: "2.5.7" in r,
        "WC2.2": lambda r: "accessibilitycustomaction" in r or "custom action" in r,
        "WC2.3": lambda r: any(x in r for x in ["24", "44", "target size", "touch target", "minimum"]),
        "WC3.1": lambda r: any(x in r for x in ["4.1.2", "2.5.2", "2.1.1", "automatically"]) and any(x in r for x in ["handled", "auto", "standard"]),
        "WC3.2": lambda r: "1.1.1" in r and any(x in r for x in ["manual", "require", "need"]),
        "WC3.3": lambda r: any(x in r for x in ["4.1.1", "2.4.1", "don't apply", "not applicable", "doesn't apply"]),
        "WC3.4": lambda r: any(x in r for x in ["2.5.7", "2.5.8", "3.3.7", "3.3.8", "wcag 2.2"]),

        # Testing
        "TE1.1": lambda r: "performaccessibilityaudit" in r,
        "TE1.2": lambda r: any(x in r for x in [".contrast", ".dynamictype", "selective", "specific types", "audit types"]),
        "TE2.1": lambda r: "teardown" in r or "teardownwitherror" in r,
        "TE2.2": lambda r: any(x in r for x in ["filter", "ignore", "known issue", "closure"]),
        "TE2.3": lambda r: any(x in r for x in ["zero", "no additional", "every ui test", "regression", "free"]),
        "TE3.1": lambda r: any(x in r for x in ["swipe right", "linear", "navigate through"]),
        "TE3.2": lambda r: "rotor" in r and "heading" in r,
        "TE3.3": lambda r: "screen curtain" in r or "screencurtain" in r,
        "TE3.4": lambda r: any(x in r for x in ["modal", "trapped", "focus", "escape"]),

        # System Preferences
        "SP1.1": lambda r: any(x in r for x in ["both", "hide", "hidden", "voiceover"]),
        "SP1.2": lambda r: any(x in r for x in ["image(decorative:", "decorative:", "preferred"]),
        "SP2.1": lambda r: "accessibilityreducetransparency" in r or "reducetransparency" in r,
        "SP2.2": lambda r: any(x in r for x in ["color(.systembackground)", "systembackground", "solid"]),
        "SP2.3": lambda r: any(x in r for x in ["anyshapestyle", "conditional", "type mismatch", "type erasure"]),
        "SP3.1": lambda r: "accessibilityignoresinvertcolors" in r or "ignoresinvertcolors" in r,
        "SP3.2": lambda r: any(x in r for x in ["cascade", "parent", "subview", "children"]),
        "SP3.3": lambda r: "accessibilityshowslargecontentviewer" in r or "largecontentviewer" in r or "large content viewer" in r,
        "SP3.4": lambda r: any(x in r for x in ["dynamictypesize(...", "xxxlarge", "cap", "limit"]) and any(x in r for x in ["large content", "largecontentviewer", "viewer"]),
    }

    aid = assertion["id"]
    if aid in checks:
        passed = checks[aid](response_lower)
        # Find evidence (first matching snippet)
        evidence = "Checked assertion keywords" if passed else "Keywords not found in response"
        return passed, evidence

    # Fallback: simple keyword matching from assertion text
    keywords = [w for w in text.split() if len(w) > 4]
    matches = sum(1 for k in keywords if k in response_lower)
    passed = matches >= len(keywords) * 0.5
    return passed, f"Matched {matches}/{len(keywords)} keywords"

def grade_run(eval_data, variant):
    """Grade a single run."""
    name = eval_data["name"]
    response = read_response(name, variant)

    if not response:
        return None

    results = []
    for assertion in eval_data["assertions"]:
        passed, evidence = check_assertion(response, assertion)
        results.append({
            "text": assertion["text"],
            "passed": passed,
            "evidence": evidence
        })

    grading = {
        "eval_id": eval_data["id"],
        "eval_name": name,
        "variant": variant,
        "expectations": results,
        "pass_count": sum(1 for r in results if r["passed"]),
        "total": len(results)
    }

    # Save grading.json
    out_path = WORKSPACE / name / variant / "grading.json"
    with open(out_path, "w") as f:
        json.dump(grading, f, indent=2)

    return grading

def aggregate_benchmark(all_gradings):
    """Create benchmark.json from all gradings."""
    with_skill = {"pass": 0, "total": 0, "by_topic": {}, "by_tier": {}}
    without_skill = {"pass": 0, "total": 0, "by_topic": {}, "by_tier": {}}

    per_eval = []

    for g in all_gradings:
        if g is None:
            continue

        name = g["eval_name"]
        variant = g["variant"]
        topic = name.rsplit("-", 1)[0]  # e.g., "voiceover-labels-simple" -> "voiceover-labels"
        # Actually need to extract topic properly
        # Look up topic from eval metadata
        topic = None
        for ev in data["evals"]:
            if ev["name"] == name:
                topic = ev.get("topic", name)
                break
        if not topic:
            topic = name
        tier = None  # No tiering

        target = with_skill if variant == "with_skill" else without_skill
        target["pass"] += g["pass_count"]
        target["total"] += g["total"]

        if topic not in target["by_topic"]:
            target["by_topic"][topic] = {"pass": 0, "total": 0}
        target["by_topic"][topic]["pass"] += g["pass_count"]
        target["by_topic"][topic]["total"] += g["total"]

        pass  # No tiering

        per_eval.append({
            "eval_name": name,
            "variant": variant,
            "pass_count": g["pass_count"],
            "total": g["total"],
            "assertions": g["expectations"]
        })

    ws_rate = with_skill["pass"] / with_skill["total"] * 100 if with_skill["total"] > 0 else 0
    wos_rate = without_skill["pass"] / without_skill["total"] * 100 if without_skill["total"] > 0 else 0

    benchmark = {
        "skill_name": "ios-accessibility",
        "model": "sonnet-4.6",
        "summary": {
            "with_skill": {"pass": with_skill["pass"], "total": with_skill["total"], "rate": round(ws_rate, 1)},
            "without_skill": {"pass": without_skill["pass"], "total": without_skill["total"], "rate": round(wos_rate, 1)},
            "delta": round(ws_rate - wos_rate, 1)
        },
        "by_tier": {},
        "by_topic": {},
        "per_eval": per_eval
    }

    for tier in ["simple", "medium", "complex"]:
        ws = with_skill["by_tier"][tier]
        wos = without_skill["by_tier"][tier]
        ws_r = ws["pass"] / ws["total"] * 100 if ws["total"] > 0 else 0
        wos_r = wos["pass"] / wos["total"] * 100 if wos["total"] > 0 else 0
        benchmark["by_tier"][tier] = {
            "with_skill": {"pass": ws["pass"], "total": ws["total"], "rate": round(ws_r, 1)},
            "without_skill": {"pass": wos["pass"], "total": wos["total"], "rate": round(wos_r, 1)},
            "delta": round(ws_r - wos_r, 1)
        }

    for topic in sorted(set(list(with_skill["by_topic"].keys()) + list(without_skill["by_topic"].keys()))):
        ws = with_skill["by_topic"].get(topic, {"pass": 0, "total": 0})
        wos = without_skill["by_topic"].get(topic, {"pass": 0, "total": 0})
        ws_r = ws["pass"] / ws["total"] * 100 if ws["total"] > 0 else 0
        wos_r = wos["pass"] / wos["total"] * 100 if wos["total"] > 0 else 0
        benchmark["by_topic"][topic] = {
            "with_skill": {"pass": ws["pass"], "total": ws["total"], "rate": round(ws_r, 1)},
            "without_skill": {"pass": wos["pass"], "total": wos["total"], "rate": round(wos_r, 1)},
            "delta": round(ws_r - wos_r, 1)
        }

    return benchmark

def main():
    data = load_evals()
    all_gradings = []

    for ev in data["evals"]:
        for variant in ["with_skill", "without_skill"]:
            g = grade_run(ev, variant)
            all_gradings.append(g)
            if g:
                status = "PASS" if g["pass_count"] == g["total"] else f"{g['pass_count']}/{g['total']}"
                print(f"  {ev['name']:40s} {variant:15s} {status}")
            else:
                print(f"  {ev['name']:40s} {variant:15s} MISSING")

    benchmark = aggregate_benchmark(all_gradings)

    # Save benchmark
    bench_path = WORKSPACE / "benchmark.json"
    with open(bench_path, "w") as f:
        json.dump(benchmark, f, indent=2)

    # Print summary
    s = benchmark["summary"]
    print(f"\n{'='*60}")
    print(f"BENCHMARK RESULTS — ios-accessibility (Sonnet 4.6)")
    print(f"{'='*60}")
    print(f"With Skill:    {s['with_skill']['pass']}/{s['with_skill']['total']} ({s['with_skill']['rate']}%)")
    print(f"Without Skill: {s['without_skill']['pass']}/{s['without_skill']['total']} ({s['without_skill']['rate']}%)")
    print(f"Delta:         +{s['delta']}%")
    print()

    print(f"{'Tier':<12} {'With Skill':>12} {'Without':>12} {'Delta':>8}")
    print(f"{'-'*44}")
    for tier in ["simple", "medium", "complex"]:
        t = benchmark["by_tier"][tier]
        print(f"{tier:<12} {t['with_skill']['rate']:>11.1f}% {t['without_skill']['rate']:>11.1f}% {t['delta']:>+7.1f}%")
    print()

    print(f"{'Topic':<25} {'With':>8} {'Without':>8} {'Delta':>8}")
    print(f"{'-'*49}")
    for topic, t in sorted(benchmark["by_topic"].items()):
        print(f"{topic:<25} {t['with_skill']['rate']:>7.1f}% {t['without_skill']['rate']:>7.1f}% {t['delta']:>+7.1f}%")

    # Generate benchmark.md
    md_lines = [
        f"# ios-accessibility Benchmark Results (Sonnet 4.6)\n",
        f"## Summary\n",
        f"| Metric | Value |",
        f"| --- | --- |",
        f"| With Skill | {s['with_skill']['pass']}/{s['with_skill']['total']} ({s['with_skill']['rate']}%) |",
        f"| Without Skill | {s['without_skill']['pass']}/{s['without_skill']['total']} ({s['without_skill']['rate']}%) |",
        f"| Delta | **+{s['delta']}%** |",
        f"",
        f"## By Difficulty Tier\n",
        f"| Tier | With Skill | Without Skill | Delta |",
        f"| --- | --- | --- | --- |",
    ]
    for tier in ["simple", "medium", "complex"]:
        t = benchmark["by_tier"][tier]
        md_lines.append(f"| {tier} | {t['with_skill']['rate']}% | {t['without_skill']['rate']}% | **+{t['delta']}%** |")

    md_lines.extend([
        f"",
        f"## By Topic\n",
        f"| Topic | With Skill | Without Skill | Delta |",
        f"| --- | --- | --- | --- |",
    ])
    for topic, t in sorted(benchmark["by_topic"].items()):
        md_lines.append(f"| {topic} | {t['with_skill']['rate']}% | {t['without_skill']['rate']}% | **+{t['delta']}%** |")

    md_path = WORKSPACE / "benchmark.md"
    md_path.write_text("\n".join(md_lines))

    print(f"\nSaved: {bench_path}")
    print(f"Saved: {md_path}")

if __name__ == "__main__":
    main()
