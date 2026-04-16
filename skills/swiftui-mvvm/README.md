# SwiftUI MVVM Architecture

Enterprise-grade SwiftUI MVVM architecture with @Observable (iOS 17+). Takes a **production-first iterative refactoring** approach — modernizing legacy codebases through small, reviewable PRs while also ensuring new features meet enterprise standards from day one.

## What This Skill Changes

| Without Skill | With Skill |
| --- | --- |
| `ObservableObject` + `@Published` | `@Observable @MainActor final class` |
| `isLoading` + `error` + `data` booleans | `ViewState<T>` enum (no impossible states) |
| `onAppear { Task { } }` | `.task { }` (managed lifecycle, auto-cancel) |
| `URLSession.shared` in ViewModel | Protocol-based Repository + HTTPClient injection |
| `NavigationLink("Details") { DetailView() }` | Typed `enum Route` + `AppRouter` |
| No tests | Mock pattern + async testing + memory leak detection |
| "Fix everything at once" PRs | Phased `refactoring/` directory with ≤200-line PRs |

## Install

```bash
npx skills add rusel95/ios-agent-skills --skill swiftui-mvvm-architecture
```

Verify installation by asking your AI agent to refactor a SwiftUI view — it should follow @Observable ViewModel + Router patterns and reference the `refactoring/` directory.

## When to Use

- **Refactoring legacy SwiftUI code** — iterative, phased PRs tracked in a `refactoring/` directory
- Migrating from ObservableObject to @Observable
- Writing ViewModel unit tests (async patterns)
- Diagnosing unnecessary view redraws or performance issues

## Pain Points This Skill Solves

Models without this skill commonly make these mistakes:

| Pain Point | What Goes Wrong | Impact |
| ---------- | --------------- | ------ |
| `@StateObject` + `@Observable` mixing | Uses `@StateObject` for `@Observable` classes | Crashes, undefined behavior |
| `onAppear { Task { } }` | Unmanaged tasks, no cancellation on disappear | Memory leaks, duplicate requests |
| `wait(for:)` in tests | Deadlocks on `@MainActor` test classes | Tests hang forever |
| Separate `isLoading`/`error` booleans | Allows impossible states (loading AND error) | UI bugs, race conditions |

## Benchmark Results

Tested on **23 scenarios** with **63 discriminating assertions**.

### Results Summary

| Model | With Skill | Without Skill | Delta | A/B Quality |
| --- | --- | --- | --- | --- |
| **Sonnet 4.6** | 54/63 (85.7%) | 45/63 (71.4%) | **+14.3%** | **9W 15T 0L** (avg 9.2 vs 8.8) |
| **GPT-5.4** | 62/63 (98.4%) | 57/63 (90.5%) | **+7.9%** | 5W 17T 1L |
| **Gemini 3.1 Pro** | 33/55 (60.0%)* | 19/55 (34.5%)* | **+25.5%** | **21W** 0T 0L (avg 9.1 vs 6.2) |

> A/B Quality: blind judge scores each response 0–10 and picks the better one without knowing which used the skill. Position (A/B) is randomized across evals to prevent bias.
> \* 21/23 evals graded (55 assertions); task-lifecycle-complex and navigation-simple had no responses in the outputs file.

### Results (Sonnet 4.6)

| Metric | Value |
| --- | --- |
| With Skill | 54/63 (85.7%) |
| Without Skill | 45/63 (71.4%) |
| Delta | **+14.3%** |
| A/B Quality | **9W 15T 0L** (avg 9.2 vs 8.8) |

**Interpretation:** Sonnet 4.6 without the skill misses 18 of 63 discriminating assertions — concentrated on `@Bindable` usage, `.task(id:)` for reactive reloads, Observation-native environment injection, navigation state ownership, and focused `@Observable` model splitting. A/B confirms with 9 wins, 15 ties, and zero losses.

### Results (GPT-5.4)

| Metric | Value |
| --- | --- |
| With Skill | 62/63 (98.4%) |
| Without Skill | 57/63 (90.5%) |
| Delta | **+7.9%** |
| A/B | 5W 17T 1L |

**Interpretation:** GPT-5.4 is a strong SwiftUI baseline (90.5%). Skill adds `@Entry` EnvironmentValues registration, `Sendable` on protocol types, migration mapping tables, and `Self._printChanges()` verification workflow. One loss: with-skill misclassified UIViewController severity in anti-patterns-complex. (Graded: Claude Sonnet 4.6, strict, iteration-5)

### Key Discriminating Assertions — GPT-5.4

| Topic | Assertion | Why It Matters |
| --- | --- | --- |
| observable-viewmodel | `@Bindable` is the correct wrapper for `$` bindings | Distinguishes read-only model passing from true two-way binding |
| observable-viewmodel | ViewModels should import `Foundation`, not `SwiftUI`, and must be `@MainActor` | Preserves testability and keeps state mutation on the correct actor |
| task-lifecycle | `.task(id:)` is required for reactive reloads | Keeps data loading tied to changing inputs like filters |
| task-lifecycle | `CancellationError` must be handled silently in ViewModel tasks | Prevents user-facing "Cancelled" error states during normal view lifecycle changes |
| navigation | Navigation booleans belong in the View layer, not the ViewModel | Keeps presentation state out of business logic and improves testability |
| dependency-injection | `@EnvironmentObject` is wrong for `@Observable` | Avoids mixing Combine DI with Observation-native environment APIs |
| dependency-injection | `@Entry` enables environment-backed protocol injection | Makes shared services testable without changing ViewModel code |
| performance | Split large `@Observable` types into focused ViewModels | Reduces redraw scope and keeps observation granular |
| performance | Separate `@State` app-level models are not shared state | Catches a subtle but severe architecture bug in large SwiftUI apps |

> Raw data:
> `swiftui-mvvm-architecture-workspace/iteration-1/benchmark-gpt-5-4.json`

### Results (Gemini 3.1 Pro)

| Metric | Value |
| --- | --- |
| With Skill | 33/55 (60.0%) |
| Without Skill | 19/55 (34.5%) |
| Delta | **+25.5%** |
| Evals Graded | 21/23 |

**Interpretation:** Gemini 3.1 Pro's outputs show significant prompt routing issues — responses for viewstate, dependency-injection (medium/complex), testing-simple, and all anti-patterns evals appear to answer UIKit MVVM prompts rather than the SwiftUI prompts. Among correctly answered evals, the skill adds substantial value: navigation-complex (0→3/3), performance (1→4/4 on PE2.1-2.4), and OV-complex completeness (2→5/5 for final+private(set)+CancellationError+injection). The 34.5% without-skill baseline reflects both genuine SwiftUI gaps and prompt routing failures. (Graded: Claude Sonnet 4.6, strict, iteration-1)

### Key Discriminating Assertions — Gemini 3.1 Pro

| Topic | Assertion | Why It Matters |
| --- | --- | --- |
| observable-viewmodel | Corrected declaration requires `final` modifier | Without-skill omits `final` in the corrected class declaration |
| observable-viewmodel | `private(set)` on state + `CancellationError` handling in corrected code | Without-skill leaves state mutable and skips cancellation guard |
| observable-viewmodel | Constructor injection for undeclared `repository` dependency | Without-skill leaves `repository` as an undeclared implicit dependency |
| navigation | `TabRouter @Observable` with typed per-tab route arrays | Without-skill only removes the outer stack without providing a Router architecture |
| navigation | Navigation state belongs in View layer; ViewModel signals via closures | Without-skill reinforces the anti-pattern by suggesting `@Bindable` on ViewModel booleans |
| testing | `addTeardownBlock` memory leak detection | Without-skill omits this in both medium and complex test setups |
| performance | `@Observable` tracks only properties read by the view body | Without-skill does not explain granular tracking mechanism |
| performance | `Self._printChanges()` verification workflow after splitting | Without-skill does not prescribe a structured post-fix verification |

> Raw data:
> `workspaces/ios/swiftui-mvvm-architecture/iteration-1/benchmark-gemini-3-1-pro.json`

## Author

[Ruslan Popesku](https://github.com/rusel95)
