# GCD & OperationQueue Concurrency

Enterprise-grade concurrency skill for Grand Central Dispatch and OperationQueue on Apple platforms (iOS, macOS, watchOS, tvOS, visionOS). Prevents the most dangerous concurrency bugs — deadlocks, thread explosion, and data races — through actionable patterns and detection checklists.

## Benchmark Results

Tested on **13 scenarios** with **19 discriminating assertions**.

### Results Summary

| Model | With Skill | Without Skill | Delta | A/B Quality |
| --- | --- | --- | --- | --- |
| **Sonnet 4.6** | 19/19 (100%) | 10/19 (52.6%) | **+47.4%** | **15W 9T 0L** (avg 8.6 vs 8.1) |
| **GPT-5.4** | 100% | 95.2% | **+4.8%** | **24/24 wins** (avg 9.0 vs 7.3) |
| **Gemini 3.1 Pro** | 100% | 83.9% | **+16.1%** | **10/24 wins**, 13 ties, 1 loss (avg 8.0 vs 7.6) |

> A/B Quality: blind judge scores each response 0–10 and picks the better one without knowing which used the skill. Position (A/B) is randomized across evals to prevent bias.

### Results (Sonnet 4.6)

| Metric | Value |
| --- | --- |
| With Skill | 19/19 (100%) |
| Without Skill | 10/19 (52.6%) |
| Delta | **+47.4%** |
| A/B Quality | **15W 9T 0L** (avg 8.6 vs 8.1) |

**Interpretation:** Sonnet 4.6 without the skill misses 9 of 19 assertions that it consistently passes with the skill. The +47.4% delta reveals that while Sonnet knows GCD basics, it misses Apple-specific production details — WWDC 2017-706 queue architecture guidance, target-queue deadlock patterns, `.background` behavior in Low Power Mode, barriers silently ignored on global queues, AsyncOperation KVO requirements, and `dispatchPrecondition` as a proactive debugging guard. A/B confirms with 15 wins and zero losses.

### Results (GPT-5.4)

| Difficulty | With Skill | Without Skill | Delta | A/B Quality (with vs without) |
| --- | --- | --- | --- | --- |
| Simple | 10/10 (100%) | 10/10 (100%) | **0%** | **8/8 wins** (avg 8.5 vs 6.9) |
| Medium | 22/22 (100%) | 20/22 (90.9%) | **+9.1%** | **8/8 wins** (avg 9.2 vs 7.2) |
| Complex | 30/30 (100%) | 29/30 (96.7%) | **+3.3%** | **8/8 wins** (avg 9.4 vs 7.7) |
| **Total** | **62/62 (100%)** | **59/62 (95.2%)** | **+4.8%** | **24/24 wins** (avg 9.0 vs 7.3) |

### Results (Gemini 3.1 Pro)

| Difficulty | With Skill | Without Skill | Delta |
| --- | --- | --- | --- |
| Simple | 10/10 (100%) | 10/10 (100%) | **0%** |
| Medium | 22/22 (100%) | 17/22 (77.3%) | **+22.7%** |
| Complex | 30/30 (100%) | 25/30 (83.3%) | **+16.7%** |
| **Total** | **62/62 (100%)** | **52/62 (83.9%)** | **+16.1%** |

**Interpretation:** Most models handle GCD basics cleanly. The skill adds value at the Apple-specific and production-hardening layer. GPT-5.4 is a very strong baseline (95.2% without skill) — only 3 specific nuances remain reliably skill-dependent for that model.

> Raw data:
> `gcd-operationqueue-workspace/iteration-3/benchmark-gpt-5-4-tiered.json` (3 runs, majority vote)
> `gcd-operationqueue-workspace/iteration-2/benchmark-sonnet-4-6.json`
> `gcd-operationqueue-workspace/iteration-2/benchmark-opus-4-5-tiered.json`
> `gcd-operationqueue-workspace/iteration-2/benchmark-gemini-3-1-pro-tiered.json`

### Benchmark Cost Estimate

| Step | Formula | Tokens |
| --- | --- | --- |
| Eval runs (with_skill) | 24 × 35k | 840k |
| Eval runs (without_skill) | 24 × 12k | 288k |
| Grading (48 runs × 5k) | 48 × 5k | 240k |
| **Total** | | **~1.4M** |
| **Est. cost (Opus 4.5)** | ~$30/1M | **~$41** |
| **Est. cost (Sonnet 4.6)** | ~$5.4/1M | **~$8** |

> Token estimates based on sampled timing.json files. Blended rate ~$30/1M for Opus ($15 input + $75 output, ~80/20 ratio); ~$5.4/1M for Sonnet 4.6 ($3 input + $15 output, ~80/20 ratio).

### Key Discriminating Assertions (GPT-5.4 — missed without skill)

GPT-5.4 is now an extremely strong baseline — 95.2% without the skill. Only 3 specific Apple-platform details consistently missed (fail in 2 of 3 runs without skill):

| ID | Topic | Assertion | Why It Matters |
| --- | --- | --- | --- |
| Q2.3 | queue-creation | Target queue hierarchies for funneling work | Consolidates subsystem queues into a root — controls total thread count |
| G2.3 | debugging | `dispatchPrecondition` removed in release builds | Must not be used as production logic — only a debug-time assertion |
| G3.4 | debugging | `dispatchPrecondition` at API boundaries | Proactive contract enforcement at every public concurrent API |

### Key Discriminating Assertions (Gemini 3.1 Pro — missed without skill)

Gemini 3.1 Pro is a stronger baseline (83.9% vs GPT-5.4's 72.6%), handling all simple cases and most production patterns correctly. The 10 remaining gaps are exclusively Apple-specific and WWDC-level details:

| Topic | ID | Assertion | Why It Matters |
| --- | --- | --- | --- |
| queue-creation | Q2.1 | Scattered `global()` calls cause thread explosion and lack control | Root cause of the most common thread explosion pattern |
| queue-creation | Q2.2 | WWDC 2017-706 or 3-4 subsystem queues recommendation | Apple's authoritative guidance for queue architecture |
| queue-creation | Q2.3 | Target queue hierarchies for funneling work | Controls total thread count across subsystems |
| queue-creation | Q3.3 | `.background` QoS may halt in Low Power Mode | Apple silently throttles/halts background queues |
| thread-explosion | E2.2 | `DispatchSemaphore` as mutex lacks priority donation | Priority inversion; NSLock or `os_unfair_lock` required |
| thread-explosion | E3.2 | `.background` QoS may halt entirely in Low Power Mode | Same Apple-specific halting behavior |
| thread-explosion | E3.3 | WWDC 2017-706 / scattered `global()` calls problem | Architecture-level fix for thread explosion |
| thread-safety | T3.3 | `global()` calls may return different queue instances | Barrier writes on assumed-same queue silently become no-ops |
| debugging | G2.3 | `dispatchPrecondition` is removed in release builds | Must not be used as production logic — only as a debug assertion |
| debugging | G3.4 | `dispatchPrecondition` at API boundaries | Proactive contract enforcement at every public concurrent API |

## What This Skill Changes

| Without Skill | With Skill |
| --- | --- |
| AI scatters `DispatchQueue.global().async` throughout codebase | 3-4 well-defined queue subsystems with target queue hierarchies (WWDC 2017-706) |
| AI uses `DispatchQueue.main.sync` causing deadlocks | `async` by default, `dispatchPrecondition` at API boundaries |
| AI stores `os_unfair_lock` as Swift property (memory corruption) | `OSAllocatedUnfairLock` (iOS 16+) or `NSLock` (any iOS) — safe by construction |
| AI uses `DispatchSemaphore` as a mutex (no priority donation) | Lock selection hierarchy: NSLock for general, barrier for R/W, semaphore only for rate-limiting |
| AI uses barriers on global queues (silently ignored) | Custom concurrent queues with explicit barrier for reader-writer pattern |
| AI creates `AsyncOperation` without KVO or thread-safe state | Complete AsyncOperation base class with KVO, barrier-protected state, cancel-before-start handling |
| AI leaves `DispatchGroup.enter()` without `defer { group.leave() }` | Balanced enter/leave with `defer` on every code path |
| AI mixes `DispatchSemaphore.wait()` with Swift Concurrency (deadlock) | Clear migration mapping: what to migrate vs keep as GCD |
| AI generates concurrent code without Thread Sanitizer verification | TSan in CI, `dispatchPrecondition` at boundaries, stress tests with `concurrentPerform` |

## Install

```bash
npx skills add git@git.epam.com:epm-ease/research/agent-skills.git --skill gcd-operationqueue --copy
```

Verify installation by asking your AI agent to review concurrent code — it should detect deadlock patterns, recommend proper lock selection, and reference `dispatchPrecondition`.

## When to Use

- Reviewing or writing GCD/OperationQueue concurrent code
- Fixing deadlocks, data races, or thread explosion issues
- Implementing thread-safe collections or caches
- Creating AsyncOperation subclasses for OperationQueue
- Selecting the right lock type (NSLock, OSAllocatedUnfairLock, barriers)
- Using DispatchGroup, DispatchWorkItem, or DispatchSemaphore correctly
- Setting up DispatchSource timers or DispatchIO file operations
- Debugging concurrency issues with Thread Sanitizer and Instruments
- Migrating specific GCD patterns to Swift Concurrency
- Establishing concurrency standards across a team

## Author

[Ruslan Popesku](https://git.epam.com/Ruslan_Popesku)
