# Benchmarking Guide

This document explains how skill benchmarks work, how to run them for any model, and the methodology behind assertion design.

All benchmarks are run using **Claude Code** with subagents for context isolation. No external scripts or tooling required.

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
4. The judge declares a winner (or tie if scores differ by ≤ 0.5)
5. The judge does **not know** which response used the skill

**What it captures:** Quality differences invisible to binary pass/fail.

**Shown in README as:** `15W 9T 0L` (wins, ties, losses) with average scores `8.9↑8.5`.

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
# This assertion stays (model WITHOUT fails it):
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

---

## Evidence-Only Grading

Every assertion is graded on a strict contract:

> **PASS only when the claim is explicitly stated in the response. FAIL on implication, charitable interpretation, or omission.**

Example: If the assertion is "recommends `withTaskGroup` as the fix", a response that says "use a task group" scores **FAIL** (missing the exact symbol). "Use `withTaskGroup`" scores **PASS**.

This strictness prevents inflation and makes results reproducible.

---

## Grader Isolation

```
GENERATOR context                    GRADER context (separate Claude Code subagent)
├── SKILL.md  <-- loaded             ├── eval assertions
├── references/*.md  <-- loaded      ├── response.md (from generator)
└── prompt --> response.md           └── NO access to SKILL.md
```

The grader must never see the skill. If it does, it marks responses as passing when they merely "sound like the skill" rather than explicitly stating the claims.

---

## Running a Benchmark with Claude Code

All benchmark phases run inside Claude Code using subagents for context isolation.

### Phase 1: Generate responses

Open this repo in Claude Code and run:

```
Benchmark the skill skills/ios-testing/ against evals/ios/ios-testing/evals.json.

For each eval:
1. Spawn a WITH-skill subagent: give it SKILL.md + all references/*.md, then the eval prompt. Save response to workspaces/ios/ios-testing/iteration-1/eval-<name>/with/response.md
2. Spawn a WITHOUT-skill subagent: give it only the eval prompt (no skill files). Save response to workspaces/ios/ios-testing/iteration-1/eval-<name>/without/response.md

Run max 2-3 subagents in parallel to avoid rate limits.
```

For non-Claude models (GPT, Gemini), generate responses externally and place them at the same paths manually.

### Phase 2: Grade

```
Grade the responses in workspaces/ios/ios-testing/iteration-1/ against the assertions in evals/ios/ios-testing/evals.json.

Use an isolated grader subagent that has NOT seen the skill files. For each response:
- Check each assertion: PASS only if explicitly stated, include a direct quote as evidence
- FAIL if implied, close but missing exact API/term, or not mentioned
- Save results to grading.json alongside each response
```

### Phase 3: A/B Comparison

```
Run blind A/B comparison for workspaces/ios/ios-testing/iteration-1/.

For each eval pair (with/without):
- Randomize which is "Response A" and "Response B" (odd evals: with=A, even evals: with=B)
- Score each 0-10 on: correctness, completeness, specificity, structure, actionability
- Declare winner if score gap > 0.5, otherwise tie
- Save to ab-result.json
```

### Phase 4: Aggregate and update READMEs

```
Aggregate results from workspaces/ios/ios-testing/iteration-1/ and update:
- skills/ios-testing/README.md with the benchmark table
- Root README.md with the updated row for ios-testing
```

---

## File Structure

```
evals/ios/<skill>/
├── evals.json              # Canonical eval definitions (prompts + assertions)
└── *-outputs.json          # Pre-generated responses for non-Claude models

workspaces/ios/<skill>/     # Raw outputs — not committed
├── iteration-N/
│   ├── eval-<name>/
│   │   ├── with/response.md
│   │   ├── without/response.md
│   │   ├── grading.json
│   │   └── ab-result.json
│   └── benchmark-summary.json
```

### What gets committed vs ignored

| Tracked | Ignored |
|---------|---------|
| `evals/ios/<skill>/evals.json` | `workspaces/` (all raw outputs) |
| `skills/<skill>/README.md` (results) | |
| Root `README.md` (summary table) | |

---

## Adding a New Model

1. Generate responses for each eval (externally for non-Claude models, or via Claude Code subagents for Claude)
2. Place responses at `workspaces/ios/<skill>/iteration-N/eval-<name>/with/response.md` and `without/response.md`
3. Ask Claude Code to grade and run A/B comparison
4. Ask Claude Code to update skill README and root README with results

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to create a new skill.
