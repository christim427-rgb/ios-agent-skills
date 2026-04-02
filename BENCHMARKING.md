# Benchmarking Guide

This document explains how skill benchmarks work, how to run them for any model, and the methodology behind assertion design.

---

## What We Measure

Skill benchmarks test a narrow, high-value question: **does the skill make the model better at the task it was built for?**

Each eval targets practical knowledge a developer needs:

- **Anti-pattern detection** — "Here is real iOS code. What is wrong?" The model must name the specific bug, race condition, or misuse.
- **API behaviour knowledge** — "Which API prevents this crash?" The model must state the exact symbol and explain why.
- **Edge case awareness** — "What happens under this specific condition?" The model must warn about traps the skill explicitly teaches.

---

## Evaluation Methodology

We use two complementary methods. Each captures a different dimension of skill value.

### Method 1: Binary Assertion Benchmark

The core measurement. Each eval prompt has a set of **assertions** — specific claims the response must explicitly state.

```
Eval prompt: "What's wrong with this code? [code snippet]"
Assertion:   "Identifies os_unfair_lock as stored property causes memory corruption"
```

**How it works:**
1. The same model answers each prompt twice: once after reading the skill (WITH), once without (WITHOUT)
2. An isolated grader checks each response against assertions — PASS only on explicit content, never on implication
3. Results are aggregated as pass rates: `WITH: 100% | WITHOUT: 53% | Delta: +47%`

**What it captures:** Whether the model knows the specific concept the skill teaches.
**What it misses:** Depth, code examples, precision, actionability (see Method 2).

### Method 2: Blind A/B Quality Comparison

Binary assertions can't distinguish "mentions the concept" from "provides a structured, production-ready explanation with code examples." Blind A/B judging fills this gap.

**How it works:**
1. Both responses (WITH and WITHOUT) are shown to a blind judge as "Response A" and "Response B"
2. Position is **randomized** per eval to prevent position bias
3. The judge scores each response 0-10 on: correctness, completeness, specificity, structure, actionability
4. The judge declares a winner (or tie if scores differ by <= 0.5)
5. The judge does **not know** which response used the skill

**What it captures:** Quality differences invisible to binary pass/fail.

**Shown in README as:** `15W 9T 0L` (wins, ties, losses) with average scores `8.9-8.5`.

### How Methods Combine

| Scenario | Binary | A/B | Interpretation |
| --- | --- | --- | --- |
| Large delta, high A/B | +40% | 24/24 wins | Skill fills major knowledge gaps AND improves quality |
| Meaningful delta, high A/B | +15% | 20/24 wins | Skill teaches practical patterns, quality is consistently better |
| Small delta, high A/B | +5% | 15/24 wins | Model knows basics but skill adds depth and structure |
| Zero delta, no A/B | +0% | 0/24 wins | Skill teaches nothing new |

---

## Assertion Design Philosophy

Not all assertions are equal. We follow three rules to keep benchmarks honest:

### Rule 1: Only discriminating assertions

An assertion is kept **only if at least one model fails it without the skill** across all benchmarked models. If every model passes an assertion both WITH and WITHOUT the skill, that assertion is noise — it inflates the denominator and dilutes the delta. It gets removed.

```
# This assertion stays (Sonnet WITHOUT fails it):
"Recommends OSAllocatedUnfairLock for iOS 16+ as safe alternative"

# This assertion gets removed (everyone passes it):
"Identifies that blocking the main thread causes UI freeze"
```

### Rule 2: Test practical knowledge, not vocabulary

Assertions must test understanding, not whether the model reproduces the skill's specific taxonomy.

```
# Bad (tests skill vocabulary):
"References anti-pattern code C3"

# Good (tests the same concept):
"Classifies the issue with an explicit severity level"
```

### Rule 3: No trivia or library name-dropping

Assertions that test for citing specific library names, WWDC session numbers, or RFC references are removed unless the reference IS the practical knowledge.

```
# Bad (trivia):
"Mentions Alamofire real-world bug as precedent"

# Good (the reference IS the knowledge):
"Recommends LIBDISPATCH_COOPERATIVE_POOL_STRICT=1 for detecting blocking in tests"
```

### The cleanup process

After each benchmark round:
1. Collect all grading data across all models
2. Find assertions passing 100% everywhere — remove them
3. Soften taxonomy-specific assertions to test behavior
4. Remove library name-dropping and trivia
5. Re-grade with cleaned set

This makes delta go in two directions simultaneously:
- **UP** from removing non-discriminating noise (smaller denominator)
- **DOWN** from removing overfitted assertions (smaller numerator)

The net result is closer to truth.

---

## Evidence-Only Grading

Every assertion is graded on a strict contract:

> **PASS only when the claim is explicitly stated in the response. FAIL on implication, charitable interpretation, or omission.**

Example: If the assertion is "recommends `withTaskGroup` as the fix", a response that says "use a task group" scores **FAIL** (missing the exact symbol). "Use `withTaskGroup`" scores **PASS**.

This strictness prevents inflation and makes results reproducible.

---

## Grader Isolation

```
GENERATOR context                    GRADER context (separate agent)
├── SKILL.md  <-- loaded             ├── eval assertions
├── references/*.md  <-- loaded      ├── response.md (from generator)
└── prompt --> response.md           └── NO access to SKILL.md
```

The grader must never see the skill. If it does, it marks responses as passing when they merely "sound like the skill" rather than explicitly stating the claims.

---

## Running a Benchmark

### Phase 1: Generate responses

For each eval, the model answers the prompt twice:
- **WITH skill**: read SKILL.md + reference files first, then answer
- **WITHOUT skill**: answer directly, no skill files

Save responses to:
```
workspaces/ios/<skill>/iteration-N/eval-<name>/<slug>-with/run-1/outputs/response.md
workspaces/ios/<skill>/iteration-N/eval-<name>/<slug>-without/run-1/outputs/response.md
```

For non-Claude models, generate responses externally and use `unpack-outputs.py` to place them.

### Phase 2: Grade

Grade with an isolated grader agent that has NOT seen the skill:

```bash
# Auto-grade keyword assertions
python scripts/benchmarking/grade_responses.py \
  workspaces/ios/<skill>/iteration-N \
  --config <slug>

# For content/structure assertions, use AI grader
# See scripts/benchmarking/references/grader-prompt.md
```

### Phase 3: Aggregate

```bash
python scripts/benchmarking/aggregate_benchmark.py \
  workspaces/ios/<skill>/iteration-N \
  --skill-name <name>
```

### Phase 4: A/B Comparison

Run blind A/B judging on the same response pairs. See `scripts/benchmarking/references/comparator-prompt.md`.

---

## File Structure

```
evals/ios/<skill>/
├── evals.json              # Canonical eval definitions (prompts + assertions)
└── *-outputs.json          # Pre-generated responses for non-Claude models

workspaces/ios/<skill>/     # Gitignored — raw outputs
├── iteration-N/
│   ├── eval-<name>/
│   │   ├── eval_metadata.json       # Snapshot used for isolated grading
│   │   ├── <model>-with/run-1/
│   │   │   ├── outputs/response.md
│   │   │   ├── grading.json          # Original grading
│   │   │   ├── grading-v2.json       # After harder assertions
│   │   │   └── grading-v3.json       # After cleanup
│   │   ├── <model>-without/run-1/
│   │   │   └── (same structure)
│   │   └── ab-<model>.json           # A/B comparison result
│   └── benchmark-<model>.json
```

### What gets committed vs ignored

| Tracked | Ignored |
|---------|---------|
| `evals/ios/<skill>/evals.json` | `workspaces/` (all raw outputs) |
| `skills/<skill>/README.md` (results) | `*-workspace/` |
| Root `README.md` (summary table) | |

---

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `scripts/benchmarking/scaffold.py` | Create workspace directories |
| `scripts/benchmarking/unpack-outputs.py` | Write response.md from pre-generated JSON |
| `scripts/benchmarking/ingest-grades.py` | Write grading.json from batch grader output |
| `scripts/benchmarking/aggregate_benchmark.py` | Compute deltas, write benchmark JSON |
| `scripts/benchmarking/grade_responses.py` | Auto-grade keyword assertions |

---

## Adding a New Model

1. Generate responses (direct or external)
2. Grade with the isolated Claude grader
3. Run `aggregate_benchmark.py`
4. Add results to skill README and root README

See [EVALUATION.md](EVALUATION.md) for the full pipeline and [CONTRIBUTING.md](CONTRIBUTING.md) for skill development.
