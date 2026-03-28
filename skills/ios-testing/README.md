# iOS Swift Testing Skill

Enterprise-grade testing skill for iOS/Swift covering 11 areas across all architectures. Covers F.I.R.S.T principles, Swift Testing framework (Xcode 16+), XCTest patterns, async testing, architecture-specific patterns (MVVM, VIPER, TCA), UI testing, snapshot testing, integration testing, and enterprise patterns.

## Benchmark Results

Tested on **27 scenarios** with **77 discriminating assertions**.

### Results Summary

| Model | With Skill | Without Skill | Delta | A/B Quality |
| --- | --- | --- | --- | --- |
| **Sonnet 4.6** | 77/77 (100%) | 43/77 (55.8%) | **+44.2%** | **23W 7T 0L** (avg 8.9 vs 8.0) |
| **GPT-5.4** | 100% | 70% | **+30%** | **25/30 wins**, 5 ties (avg 8.4 vs 7.0) |
| **Gemini 3.1 Pro** | 100% | 66.4% | **+33.6%** | **21/30 wins**, 9 ties (avg 8.2 vs 7.4) |

> A/B Quality: blind judge scores each response 0–10 and picks the better one without knowing which used the skill. Position (A/B) is randomized across evals to prevent bias.

### Results (Sonnet 4.6)

| Metric | Value |
| --- | --- |
| With Skill | 77/77 (100%) |
| Without Skill | 43/77 (55.8%) |
| Delta | **+44.2%** |
| A/B Quality | **23W 7T 0L** (avg 8.9 vs 8.0) |

**Interpretation:** Sonnet 4.6 without the skill misses 34 of 77 assertions that it consistently passes with the skill. The +44.2% delta reflects the skill's value on assertions that actually matter — anti-pattern severity codes, niche API details (withSnapshotTesting, perceptualPrecision, CustomTestStringConvertible), edge case warnings, framework-mixing hazards, and XCTest-to-Swift-Testing lifecycle differences. A/B confirms with 23 wins and zero losses.

### Results (GPT-5.4)

| Difficulty | With Skill | Without Skill | Delta | A/B Quality |
| --- | --- | --- | --- | --- |
| Simple | 25/25 (100%) | 25/25 (100%) | **0%** | **7/10 wins**, 3 ties (avg 8.0 vs 6.8) |
| Medium | 35/35 (100%) | 21/35 (60%) | **+40%** | **9/10 wins**, 1 tie (avg 8.5 vs 7.0) |
| Complex | 47/47 (100%) | 29/47 (62%) | **+38%** | **9/10 wins**, 1 tie (avg 8.7 vs 7.3) |
| **Total** | **107/107 (100%)** | **75/107 (70%)** | **+30%** | **25/30 wins**, 5 ties (avg 8.4 vs 7.0) |

### Results (Gemini 3.1 Pro)

| Difficulty | With Skill | Without Skill | Delta | A/B Quality |
| --- | --- | --- | --- | --- |
| Simple | 25/25 (100%) | 25/25 (100%) | **0%** | **2/10 wins**, 8 ties (avg 7.8 vs 7.6) |
| Medium | 35/35 (100%) | 19/35 (54.3%) | **+45.7%** | **9/10 wins**, 1 tie (avg 8.3 vs 7.3) |
| Complex | 47/47 (100%) | 27/47 (57.5%) | **+42.5%** | **10/10 wins** (avg 8.6 vs 7.3) |
| **Total** | **107/107 (100%)** | **71/107 (66.4%)** | **+33.6%** | **21/30 wins**, 9 ties (avg 8.2 vs 7.4) |

**Interpretation:** Simple iOS testing patterns are saturated, while the measurable uplift appears in medium and complex scenarios. The additional gains come from framework-specific testing details and migration edge cases such as `withMainSerialExecutor`, `confirmation()` semantics, TCA version requirements for Swift Testing, framework-mixing hazards, and XCTest-to-Swift-Testing lifecycle differences.

### Tiered Key Discriminating Assertions (GPT-5.4)

| Topic | Assertion | Why It Matters |
| --- | --- | --- |
| async-testing | `withMainSerialExecutor` + `@MainActor` on test type | Deterministic actor-isolated test execution |
| swift-testing | `confirmation()` for async event expectations | Swift Testing's async-native replacement for XCTExpectation |
| observable-testing | Combine testing pattern for `@Published` | Subscription timing and `dropFirst()` semantics |
| tca-testing | TCA >= 1.12 for Swift Testing compatibility | TestStore uses `Issue.record()` instead of `XCTFail` |

### Tiered Key Discriminating Assertions (Gemini 3.1 Pro)

Gemini 3.1 Pro is a comparable baseline to GPT-5.4 on simple tests (100% for both) but has 36 gaps at medium/complex tiers — many targeting framework-specific and Apple-specific nuances:

| Topic | ID | Assertion | Why It Matters |
| --- | --- | --- | --- |
| anti-patterns | P3.6 | `#expect` inside XCTestCase silently ignored (anti-pattern C6) | Mixing Swift Testing assertions inside XCTest context never fires |
| async-testing | A2.2 | `withMainSerialExecutor` from `swift-concurrency-extras` | Serializes Tasks on main actor for deterministic async tests |
| async-testing | A2.3 | `Task.yield()` inside mock for deterministic suspension | Controls exact suspension point without real async delays |
| async-testing | A3.3 | `withMainSerialExecutor` for serializing Task execution | Required for reliable async test execution on `@MainActor` |
| integration-testing | I2.1 | In-memory Core Data store: `NSInMemoryStoreType` | Avoids disk I/O in tests, prevents state leakage between runs |
| integration-testing | I2.3 | `NSPersistentStoreDescription` with `url = URL(fileURLWithPath: "/dev/null")` | Explicit in-memory store configuration for modern Core Data setup |
| integration-testing | I3.4 | Keychain state persists across app installs on simulator | Causes false failures; must be cleared manually or in `setUp` |
| observable-testing | O3.1 | `withObservationTracking` in a loop or multiple times | Tracks individual observation cycles for `@Observable` ViewModels |
| swift-testing | S3.1 | `XCTAssert` in `@Test` silently passes (no XCTestCase context) | Framework mixing produces false green tests |
| swift-testing | S3.2 | `confirmation()` counts when closure **returns**, not when callback fires | Prevents subtle false-positive confirmation tests |
| test-organization | G3.1 | Quarantine flaky tests in separate Test Plan | Prevents flaky tests from blocking PRs while preserving visibility |
| xctest-migration | M3.2 | XCTest runs tests in **separate processes**; Swift Testing in **one process** | Shared state between tests causes failures only visible after migration |

> Raw data:
> `ios-testing-workspace/iteration-6/benchmark-gpt-5-4-tiered.json`
>
> `ios-testing-workspace/iteration-6/benchmark-gemini-3-1-pro-tiered.json`
>
> `ios-testing-workspace/iteration-1/benchmark-opus-4-5-tiered.json`
>
> `ios-testing-workspace/iteration-2/benchmark-sonnet-4-6.json`

---

## What This Skill Does

- Writes F.I.R.S.T-compliant unit tests using Swift Testing (`@Test`, `@Suite`, `#expect`) or XCTest
- Builds protocol-based mocks with stub + spy pattern
- Tests `@MainActor` ViewModels with proper isolation and memory leak detection
- Handles async testing: `withMainSerialExecutor`, `Clock` injection, `AsyncStream`, `confirmation()`
- Tests @Observable ViewModels with `withObservationTracking`
- Tests VIPER modules: Presenter, Interactor, Router with weak reference enforcement
- Tests TCA features with `TestStore`, exhaustive assertions, `TestClock`
- Creates parameterized tests, test tags, and Test Plans
- Writes XCUITest UI tests with Page Object Model pattern
- Configures snapshot tests with device pinning and CI recording modes
- Tests integration layers: URLProtocol mocking, Core Data, SwiftData, Keychain, UserDefaults
- Implements enterprise patterns: OAuth testing, feature flags, analytics spies, accessibility auditing
- Audits existing test suites for anti-patterns (framework mixing dangers, deadlocks, shared state)
- Plans and executes phased XCTest to Swift Testing migration
- Sets up CI test pipelines with coverage targets and flaky test quarantine

## References

| File | Purpose |
| --- | --- |
| `SKILL.md` | Decision trees, do/don'ts, workflows, confidence checks |
| `references/swift-testing-framework.md` | @Test, @Suite, #expect, #require, parameterized, tags, confirmation(), coexistence |
| `references/xctest-patterns.md` | XCTestCase structure, mocks, Combine @Published testing, scheduler injection |
| `references/async-testing.md` | withMainSerialExecutor, Clock injection, AsyncStream, confirmation() semantics |
| `references/observable-testing.md` | withObservationTracking, willSet semantics, @Observable testing patterns |
| `references/viper-testing.md` | Presenter/Interactor/Router testing, weak references, module assembly |
| `references/tca-testing.md` | TestStore, exhaustive assertions, TestClock, navigation, dependencies |
| `references/ui-testing.md` | Page Object Model, waitForExistence, system alerts, launch arguments |
| `references/snapshot-testing.md` | Device pinning, recording modes, CI config, SwiftUI hosting |
| `references/integration-testing.md` | URLProtocol, Core Data /dev/null, SwiftData, Keychain, UserDefaults |
| `references/enterprise-testing.md` | OAuth, feature flags, analytics, deep linking, memory leaks, accessibility |
| `references/anti-patterns.md` | Detection checklist with grep patterns, severity-ranked |
| `references/refactoring-workflow.md` | XCTest to Swift Testing migration, assertion mapping, PR sizing |
| `references/test-organization.md` | File structure, naming, Test Plans, CI, coverage targets, flaky tests |

## Requirements

- Xcode 16+ for Swift Testing (`@Test`, `@Suite`, `#expect`)
- XCTest available on all Xcode versions
- Optional: `swift-concurrency-extras` (Point-Free) for `withMainSerialExecutor`
- Optional: `swift-clocks` (Point-Free) for `ImmediateClock` / `TestClock`
- Optional: `swift-snapshot-testing` (Point-Free) for snapshot tests
- Optional: TCA >= 1.12 for Swift Testing compatibility with TestStore
