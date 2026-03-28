# Swift Concurrency

Enterprise-grade skill for Swift Concurrency on Apple platforms. Prevents the most dangerous production crash patterns — cooperative pool deadlocks, continuation misuse, actor reentrancy corruption, and Sendable violations — through actionable rules, decision trees, and detection checklists. Covers Swift 6.2 Approachable Concurrency, enterprise migration strategies, and security-specific concurrency patterns.

## What This Skill Changes

| Without Skill | With Skill |
| --- | --- |
| AI uses `DispatchSemaphore.wait()` in async contexts (deadlocks cooperative pool) | Continuation-based bridging with `withCheckedThrowingContinuation`, cooperative pool awareness |
| AI uses `@unchecked Sendable` to silence compiler (hides data races) | `sending` parameter, `Mutex<State>`, actor wrapping — compiler-verified safety |
| AI assumes actor state unchanged after `await` (reentrancy bugs) | Re-check-after-await pattern, in-flight Task coalescing for deduplication |
| AI creates `Task {}` inside `@MainActor` expecting background execution | Understands `Task.init` inherits caller isolation; uses `@concurrent` or `nonisolated` for background |
| AI forgets `continuation.finish()` in AsyncStream (resource leaks) | `onTermination` handler pattern, backpressure policy selection, `withDiscardingTaskGroup` for services |
| AI uses `MainActor.run {}` for isolation (runtime-only, unverifiable) | Static `@MainActor` annotation — compiler-verified at every call site |
| AI ignores Swift 6.2 caller-side isolation change (silent main-thread hangs) | Explicit `@concurrent` for CPU-intensive work, awareness of `nonisolated(nonsending)` default |
| AI generates async tests with timing dependencies (flaky CI) | `withMainSerialExecutor` for determinism, `Clock` injection, `AsyncStream.makeStream` for control |
| AI leaves security-critical code vulnerable to TOCTOU at `await` points | Transaction-style actor methods, token refresh serialization, Keychain actor wrapping |

## Install

```bash
npx skills add git@git.epam.com:epm-ease/research/agent-skills.git --skill swift-concurrency
```

Verify installation by asking your AI agent to review async/await code — it should detect cooperative pool blocking, check continuation safety, warn about actor reentrancy, and reference Swift 6.2 behavioral changes.

## When to Use

- Writing or reviewing async/await, actor, or TaskGroup code
- Diagnosing data races, deadlocks, or continuation crashes
- Migrating a codebase to `SWIFT_STRICT_CONCURRENCY=complete` or Swift 6 mode
- Adopting Swift 6.2 Approachable Concurrency (`@concurrent`, `nonisolated(nonsending)`)
- Implementing Sendable conformance or using `sending` parameters
- Using AsyncStream, AsyncSequence, or AsyncChannel correctly
- Fixing concurrency-related security issues (TOCTOU, token races, Keychain access)
- Setting up Thread Sanitizer and `LIBDISPATCH_COOPERATIVE_POOL_STRICT` in CI
- Creating deterministic async tests with Clock injection
- Establishing Swift Concurrency standards across a team

## Available Workflows

Ask your AI agent to run any of these workflows:

| Workflow | What It Does |
| --- | --- |
| **Audit Existing Codebase** | Scans for crash patterns, Sendable violations, actor reentrancy, AsyncStream leaks, and security issues. Creates a severity-ranked refactoring plan. |
| **Migrate Module to Strict Concurrency** | Bottom-up migration to `SWIFT_STRICT_CONCURRENCY=complete` or Swift 6 mode. Audits third-party SDKs, fixes global state, enables per-target flags. |
| **Create New Concurrent Feature** | Guides isolation model selection, concurrency structure, Sendable compliance, cancellation, and deterministic testing from scratch. |
| **Fix Production Crash** | Classifies crash type (continuation, deadlock, watchdog, reentrancy), reproduces with targeted test, applies fix with TSan verification. |

## Benchmark Results

Tested on **21 scenarios** with **40 discriminating assertions**.

### Results Summary

| Model | With Skill | Without Skill | Delta | A/B Quality |
| --- | --- | --- | --- | --- |
| **Sonnet 4.6** | 40/40 (100%) | 27/40 (67.5%) | **+32.5%** | **15W 9T 0L** (avg 8.9 vs 8.5) |
| **GPT-5.4** | 100% | 82.2% | **+17.8%** | **20/24 wins**, 4 ties (avg 8.5 vs 7.4) |
| **Gemini 3.1 Pro** | 100% | 64.4% | **+35.6%** | **23/24 wins**, 1 tie (avg 8.9 vs 7.1) |

> A/B Quality: blind judge scores each response 0–10 and picks the better one without knowing which used the skill. Position (A/B) is randomized across evals to prevent bias.

### Results (Sonnet 4.6)

| Metric | Value |
| --- | --- |
| With Skill | 40/40 (100%) |
| Without Skill | 27/40 (67.5%) |
| Delta | **+32.5%** |
| A/B Quality | **15W 9T 0L** (avg 8.9 vs 8.5) |

**Interpretation:** Sonnet 4.6 without the skill misses 13 of 40 assertions that it consistently passes with the skill. The +32.5% delta reflects the skill's value on assertions that actually matter — cooperative-pool sizing, `withDiscardingTaskGroup`, `sending` parameter, cancellation handler constraints, and security-specific concurrency patterns. A/B confirms with 15 wins and zero losses.

### Results (GPT-5.4)

| Difficulty | With Skill | Without Skill | Delta | A/B Quality |
| --- | --- | --- | --- | --- |
| Simple | 22/22 (100%) | 18/22 (81.8%) | **+18.2%** | **6/8 wins**, 2 ties (avg 8.3 vs 7.6) |
| Medium | 24/24 (100%) | 22/24 (91.7%) | **+8.3%** | **6/8 wins**, 2 ties (avg 8.5 vs 7.4) |
| Complex | 27/27 (100%) | 20/27 (74.1%) | **+25.9%** | **8/8 wins** (avg 8.9 vs 7.2) |
| **Total** | **73/73 (100%)** | **60/73 (82.2%)** | **+17.8%** | **20/24 wins**, 4 ties (avg 8.5 vs 7.4) |

### Results (Gemini 3.1 Pro)

| Difficulty | With Skill | Without Skill | Delta | A/B Quality |
| --- | --- | --- | --- | --- |
| Simple | 22/22 (100%) | 18/22 (81.8%) | **+18.2%** | **7/8 wins**, 1 tie (avg 8.7 vs 7.3) |
| Medium | 24/24 (100%) | 19/24 (79.2%) | **+20.8%** | **8/8 wins** (avg 8.8 vs 7.1) |
| Complex | 27/27 (100%) | 10/27 (37.0%) | **+63.0%** | **8/8 wins** (avg 9.1 vs 6.8) |
| **Total** | **73/73 (100%)** | **47/73 (64.4%)** | **+35.6%** | **23/24 wins**, 1 tie (avg 8.9 vs 7.1) |

### Key Discriminating Assertions — GPT-5.4

| Topic | Assertion | Why It Matters |
| --- | --- | --- |
| cooperative-pool | Pool capped at roughly CPU-core count | Explains why blocked async threads deadlock faster on device |
| cooperative-pool | Throttle child tasks to `ProcessInfo.processInfo.activeProcessorCount` | Prevents cooperative-pool exhaustion and watchdog kills |
| actor-isolation | In-flight task coalescing with `[URL: Task<Data, Error>]` | Fixes duplicate fetches caused by actor reentrancy |
| sendable | Public types are not inferred Sendable across module boundaries | Prevents misleading cross-module API design assumptions |
| sendable | `sending` parameter as a transfer alternative | Uses a Swift 6 ownership tool instead of unsafe sharing |
| asyncstream | `onTermination` cleanup for observers and location streams | Prevents infinite producers and leaked system resources |
| asyncstream | `withDiscardingTaskGroup` for `Void` child tasks | Avoids hidden TaskGroup memory accumulation |
| cancellation | Synchronous cancellation-handler constraint | Prevents invalid async cleanup inside `withTaskCancellationHandler` |
| migration | `SWIFT_STRICT_CONCURRENCY=complete` vs Swift 6 mode | Keeps staged migration realistic instead of turning warnings into errors too early |
| security-concurrency | `withTaskCancellationHandler` + `context.invalidate()` for biometrics | Prevents continuation hangs during cancellation |

### Key Discriminating Assertions — Gemini 3.1 Pro (26 total)

Gemini 3.1 Pro has a stronger simple/medium baseline (81.8%/79.2%) but only 37% on complex tier. The 26 gaps reveal the same cooperative-pool and cancellation specifics, plus additional Swift 6 migration nuances:

| Topic | ID | Assertion | Why It Matters |
| --- | --- | --- | --- |
| actor-isolation | AI3.1 | `Task.detached` strips `@MainActor` isolation — use `Task {}` to inherit | Prevents accidental off-main-actor mutations |
| actor-isolation | AI3.2 | `deinit` is `nonisolated`; accessing `@MainActor` property from `deinit` unsafe in Swift 6 | Critical Swift 6 rule for teardown code |
| actor-isolation | AI2.2 | In-flight Task coalescing with `[URL: Task<Data, Error>]` | Fixes duplicate fetches caused by actor reentrancy |
| asyncstream | AS3.1 | `withDiscardingTaskGroup` for Void results to avoid accumulation | Prevents hidden memory growth in long-running services |
| asyncstream | AS3.3 | Throttle concurrent tasks to `activeProcessorCount` | Prevents pool exhaustion under high concurrency |
| cancellation | CN3.2 | `withTaskCancellationHandler` to trigger `cancelUpload` on Task cancel | Enables clean resource teardown when caller cancels |
| cancellation | CN3.3 | Cancellation handler must be **synchronous** and may be called from any thread | Prevents invalid async cleanup inside the handler |
| cooperative-pool | CP3.1–CP3.4 | `Data(contentsOf:)` blocks cooperative pool; throttle with `activeProcessorCount` | Blocking I/O inside TaskGroup causes watchdog kills |
| migration | MI1.1 | `SWIFT_STRICT_CONCURRENCY=complete` (warnings) vs Swift 6 mode (errors) | Allows staged adoption without breaking the build |
| security | SC3.4 | `withTaskCancellationHandler` + `context.invalidate()` to prevent continuation hangs | Biometric auth must be explicitly cancelled |

> Raw data:
> `swift-concurrency-workspace/iteration-1/benchmark-gpt-5-4-tiered.json`
>
> `swift-concurrency-workspace/iteration-1/benchmark-gemini-3-1-pro-tiered.json`

## Author

[Ruslan Popesku](https://git.epam.com/Ruslan_Popesku)
