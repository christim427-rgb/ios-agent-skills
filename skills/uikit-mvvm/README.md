# UIKit MVVM Architecture

Enterprise-grade UIKit MVVM architecture skill for iOS 13+. Ensures consistency across teams: every new screen follows the same ViewModel + Coordinator + DI structure, and existing code evolves through safe, reviewable PRs.

## What This Skill Changes

| Without Skill | With Skill |
| --- | --- |
| AI moves all logic to ViewModel but keeps `import UIKit` | ViewModel imports only `Foundation` + `Combine` — testable on any platform |
| AI uses `var isLoading = false` + `var error: Error?` + `var data: [T]` | `ViewState<T>` enum — impossible states eliminated at compile time |
| AI generates `assign(to:on:)` as "cleaner" syntax (retain cycle) | `sink` with `[weak self]` + `.receive(on: DispatchQueue.main)` — no leaks |
| AI calls `tableView.reloadData()` after mutations | `DiffableDataSource` with `applySnapshot` — crash-free, animatable updates |
| AI has VC instantiate and push other VCs directly | Coordinator pattern — ViewModel signals via closures, never imports UIKit |
| AI uses `NetworkManager.shared` or force-unwrapped `var service: NetworkService!` | Constructor injection via protocol types, Coordinator-owned factories |
| AI skips tests because ViewModel has UIKit deps | Mock pattern + Combine publisher testing + memory leak detection in `tearDown` |
| AI forgets `translatesAutoresizingMaskIntoConstraints = false`, mixes layout approaches | Consistent programmatic Auto Layout with lazy view properties, `NSLayoutConstraint.activate` |
| AI refactors entire file in one pass with no plan | Phased `refactoring/` directory with ≤200-line PRs, one concern per PR |

## Install

```bash
npx skills add rusel95/ios-agent-skills --skill uikit-mvvm
```

Verify installation by asking your AI agent to refactor a UIKit ViewController — it should follow Coordinator + ViewModel + Combine patterns and reference the `refactoring/` directory.

## When to Use

- Modernizing existing UIKit code — extracting ViewModels, adopting Combine, introducing Coordinators
- Implementing Combine bindings (@Published + sink)
- Adopting DiffableDataSource for collection/table views
- Writing ViewModel unit tests

## Pain Points This Skill Solves

Models without this skill commonly make these mistakes:

| Pain Point | What Goes Wrong | Impact |
| ---------- | --------------- | ------ |
| Combine `.sink` retain cycles | Uses `assign(to:on:)` or forgets `[weak self]` | Memory leaks |
| Missing Coordinator pattern | ViewController creates and pushes other VCs directly | Tight coupling, untestable navigation |
| `reloadData()` during mutations | Calls `tableView.reloadData()` while data is changing | Crashes, no animations |
| `import UIKit` in ViewModel | ViewModel depends on UIKit types | Cannot unit test |

## Benchmark Results

Tested on **24 scenarios** (8 topics × 3 difficulty tiers) with **51 discriminating assertions**.

### Results Summary

| Model | With Skill | Without Skill | Delta | A/B Quality |
| --- | --- | --- | --- | --- |
| **Sonnet 4.6** | 51/51 (100%) | 44/51 (86.3%) | **+13.7%** | **20W 2T 2L** (avg 9.1 vs 8.2) |
| **GPT-5.4** | 100% | 59.2% | **+40.8%** | **23/24 wins**, 1 tie (avg 8.5 vs 7.1) |
| **Gemini 3.1 Pro** | 93.0% | 38.0% | **+54.9%** | **24/24 wins** (avg 8.5 vs 6.7) |

> A/B Quality: blind judge scores each response 0–10 and picks the better one without knowing which used the skill. Position (A/B) is randomized across evals to prevent bias.

### Results (Sonnet 4.6)

| Metric | Value |
| --- | --- |
| With Skill | 51/51 (100%) |
| Without Skill | 44/51 (86.3%) |
| Delta | **+13.7%** |
| A/B Quality | **20W 2T 2L** (avg 9.1 vs 8.2) |

**Interpretation:** Sonnet 4.6 without the skill misses 7 of 51 discriminating assertions — concentrated on `ViewState<T>` enum usage, Combine lifecycle mistakes, coordinator cleanup and back-button handling, Storyboard DI with `instantiateViewController(creator:)`, and phased refactoring discipline. A/B confirms with 20 wins — the strongest A/B result across all skills for this model.

### Results (GPT-5.4)

| Difficulty | With Skill | Without Skill | Delta | A/B Quality |
| --- | --- | --- | --- | --- |
| Simple | 22/22 (100%) | 22/22 (100%) | **0%** | **7/8 wins**, 1 tie (avg 8.2 vs 7.1) |
| Medium | 23/23 (100%) | 9/23 (39.1%) | **+60.9%** | **8/8 wins** (avg 8.6 vs 7.2) |
| Complex | 26/26 (100%) | 11/26 (42.3%) | **+57.7%** | **8/8 wins** (avg 8.8 vs 7.1) |
| **Total** | **71/71 (100%)** | **42/71 (59.2%)** | **+40.8%** | **23/24 wins**, 1 tie (avg 8.5 vs 7.1) |

### Results (Gemini 3.1 Pro)

| Difficulty | With Skill | Without Skill | Delta | A/B Quality |
| --- | --- | --- | --- | --- |
| Simple | 20/22 (90.9%) | 13/22 (59.1%) | **+31.8%** | **8/8 wins** (avg 8.2 vs 6.9) |
| Medium | 22/23 (95.7%) | 8/23 (34.8%) | **+60.9%** | **8/8 wins** (avg 8.8 vs 6.6) |
| Complex | 24/26 (92.3%) | 6/26 (23.1%) | **+69.2%** | **8/8 wins** (avg 8.6 vs 6.6) |
| **Total** | **66/71 (93.0%)** | **27/71 (38.0%)** | **+54.9%** | **24/24 wins** (avg 8.5 vs 6.7) |

### Key Discriminating Assertions — GPT-5.4

| Topic | Assertion | Why It Matters |
| --- | --- | --- |
| viewmodel | `ViewState<T>` replaces impossible flag combinations | Prevents contradictory UI state and simplifies rendering |
| viewmodel | UITableView references in a ViewModel are a critical retain-cycle and UIKit-coupling violation | Prevents VM↔VC retention bugs and broken MVVM boundaries |
| combine-bindings | `sink` must be stored in `cancellables` | Explains why subscriptions silently stop receiving values |
| combine-bindings | Bind in `viewDidLoad`, not `init` | Avoids nil outlets and duplicate lifecycle bugs |
| combine-bindings | `.receive(on: DispatchQueue.main)` before UI writes | Prevents off-main-thread UI mutation from service callbacks |
| coordinator | Coordinators must clean up children and observe back-button pops | Prevents child-flow leaks in real navigation stacks |
| dependency-injection | `instantiateViewController(creator:)` enables non-optional storyboard DI | Removes fragile property injection on iOS 13+ |
| dependency-injection | ScreenFactory + MockScreenFactory isolate construction from navigation | Keeps coordinators testable and wiring centralized |
| viewstate | `reconfigureItems` / `reloadItems` instead of `reloadData()` with DiffableDataSource | Preserves diffing integrity and avoids UIKit assertion failures |
| refactoring | Existing tests stay green during MVVM extraction | Enforces the skill’s production-first migration discipline |

### Key Discriminating Assertions — Gemini 3.1 Pro (39 total)

Gemini 3.1 Pro without-skill baseline is only 38% — the lowest of all tested models for this skill. Key gaps span refactoring discipline, coordinator lifecycle, ViewState, and testing patterns:

| Topic | ID | Assertion | Why It Matters |
| --- | --- | --- | --- |
| refactoring | RF1.1–1.3 | `refactoring/` directory, Phase 1 = critical-only (≤200 lines), new discoveries → `discovered.md` | Enforces production-safe migration without scope creep |
| refactoring | RF2.2 | Phase 1 PR must contain only critical safety fixes | Prevents mixing safe fixes with architectural changes |
| coordinator | CO3.1–3.3 | Strong VC reference prevents dealloc; missing `didFinish`; missing `UINavigationControllerDelegate` | Coordinator memory leaks and invisible back-button taps |
| coordinator | CO2.2–2.3 | `didFinish` closure pattern; `removeAll { $0 === coord }` | Required cleanup for child coordinator lifecycle |
| anti-patterns | AP3.1, AP3.3 | `static shared` ViewController is Critical; rank 3 Critical before High/Medium | Global state + correct severity ordering |
| viewmodel | VM3.1, VM3.3, VM3.4 | `UITableView` in ViewModel is Critical; `private(set)` for VM properties; `ViewState<T>` for multiple booleans | Prevents retain cycles, state exposure, and impossible states |
| dependency-injection | DI3.2–3.3 | `ScreenFactory` protocol + `MockScreenFactory` injected into Coordinator | Keeps Coordinator independently testable |
| testing | TE3.1–3.3 | `wait(for:)` deadlocks in async test; `await fulfillment(of:)` fix; explains suspends vs blocks | Critical async testing correctness |
| testing | TE2.2–2.3 | `addTeardownBlock { [weak sut] in XCTAssertNil(sut) }` in `setUp` | Catches silent retain cycles not caught by tearDown |

> Raw data:
> `mvvm-uikit-architecture-workspace/iteration-1/benchmark-gpt-5-4-tiered.json`
>
> `mvvm-uikit-architecture-workspace/iteration-1/benchmark-gemini-3-1-pro-tiered.json`

## Author

[Ruslan Popesku](https://github.com/rusel95)
