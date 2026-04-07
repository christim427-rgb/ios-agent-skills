# iOS Swift Testing Skill

Enterprise-grade testing skill for iOS/Swift covering 11 areas across all architectures. Covers F.I.R.S.T principles, Swift Testing framework (Xcode 16+), XCTest patterns, async testing, architecture-specific patterns (MVVM, VIPER, TCA), UI testing, snapshot testing, integration testing, and enterprise patterns.

## Benchmark Results

Tested on **27 scenarios** with **77 discriminating assertions**.

### Results Summary

| Model | With Skill | Without Skill | Delta | A/B Quality |
| --- | --- | --- | --- | --- |
| **Sonnet 4.6** | 76/77 (98.7%) | 41/77 (53.2%) | **+45.5%** | **23W 7T 0L** (avg 8.9 vs 8.0) |
| **GPT-5.4** | 77/77 (100%) | 73/77 (94.8%) | **+5.2%** | 6W 21T 0L |
| **Gemini 3.1 Pro** | 70/77 (90.9%) | 26/77 (33.8%) | **+57.1%** | **27W** 0T 0L (avg 9.2 vs 6.5) |

> A/B Quality: blind judge scores each response 0–10 and picks the better one without knowing which used the skill. Position (A/B) is randomized across evals to prevent bias.

### Results (Sonnet 4.6)

| Metric | Value |
| --- | --- |
| With Skill | 76/77 (98.7%) |
| Without Skill | 41/77 (53.2%) |
| Delta | **+45.5%** |
| A/B Quality | **23W 7T 0L** (avg 8.9 vs 8.0) |

**Interpretation:** Sonnet 4.6 without the skill misses 36 of 77 assertions that it consistently passes with the skill. The +45.5% delta reflects the skill's value on assertions that actually matter — anti-pattern severity codes, niche API details (withSnapshotTesting, perceptualPrecision, CustomTestStringConvertible), edge case warnings, framework-mixing hazards, and XCTest-to-Swift-Testing lifecycle differences. A/B confirms with 23 wins and zero losses.

### Results (GPT-5.4)

| Metric | Value |
| --- | --- |
| With Skill | 77/77 (100%) |
| Without Skill | 73/77 (94.8%) |
| Delta | **+5.2%** |
| A/B | 6W 21T 0L |

**Interpretation:** GPT-5.4 is a strong baseline (94.8% without skill). The skill provides a clean +5.2% lift — primarily adding structured classification (severity levels, named anti-pattern categories), the confirmation() vs withCheckedContinuation decision tree, and lifecycle mapping tables that GPT omits without guidance. (Graded: Claude Sonnet 4.6, strict, iteration-9)

### Key Discriminating Assertions (GPT-5.4)

| Topic | Assertion | Why It Matters |
| --- | --- | --- |
| async-testing | `withMainSerialExecutor` + `@MainActor` on test type | Deterministic actor-isolated test execution |
| swift-testing | `confirmation()` for async event expectations | Swift Testing's async-native replacement for XCTExpectation |
| observable-testing | Combine testing pattern for `@Published` | Subscription timing and `dropFirst()` semantics |
| tca-testing | TCA >= 1.12 for Swift Testing compatibility | TestStore uses `Issue.record()` instead of `XCTFail` |

### Results (Gemini 3.1 Pro)

| Metric | Value |
| --- | --- |
| With Skill | **70/77 (90.9%)** |
| Without Skill | 26/77 (33.8%) |
| Delta | **+57.1%** |
| A/B Quality | — (not collected) |

**Interpretation:** Gemini 3.1 Pro has the lowest baseline (33.8%) but the largest skill delta (+57.1%) of the three models tested. Without the skill, it correctly handles basic test structure but misses: Swift Testing framework APIs (`@Test`, `@Suite`, `#expect`, `confirmation()`), `withMainSerialExecutor` for deterministic async testing, `addTeardownBlock` for memory leak detection, TCA `TestStore` patterns, and snapshot testing configuration. With the skill, it recovers to 90.9%. Two anti-patterns evals (anti-patterns-medium, anti-patterns-complex) had mismatched responses — Gemini answered MVVM architecture questions instead of the test anti-patterns prompt — contributing to the 7 with-skill failures. (Graded: Claude Sonnet 4.6, strict, iteration-10)

> Raw data:
> `workspaces/ios/ios-testing/iteration-10/`
> `ios-testing-workspace/iteration-6/benchmark-gpt-5-4.json`
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
