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
npx skills add git@git.epam.com:epm-ease/research/agent-skills.git --skill mvvm-uikit-architecture
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
| **Sonnet 4.6** | 51/51 (100%) | 42/51 (82.3%) | **+17.6%** | **20W 2T 2L** (avg 9.1 vs 8.2) |
| **GPT-5.4** | 50/51 (98.0%) | 44/51 (86.3%) | **+11.8%** | **24W 0T 0L** (avg 9.0 vs 7.4) |
| **Gemini 3.1 Pro** | 50/51 (98.0%) | 11/51 (21.6%) | **+76.5%** | **24W** 0T 0L (avg 9.2 vs 5.7) |

> A/B Quality: blind judge scores each response 0–10 and picks the better one without knowing which used the skill. Position (A/B) is randomized across evals to prevent bias.

### Results (Sonnet 4.6)

| Metric | Value |
| --- | --- |
| With Skill | 51/51 (100%) |
| Without Skill | 42/51 (82.3%) |
| Delta | **+17.6%** |
| A/B Quality | **20W 2T 2L** (avg 9.1 vs 8.2) |

**Interpretation:** Sonnet 4.6 without the skill misses 9 of 51 discriminating assertions — concentrated on `ViewState<T>` enum usage, Combine lifecycle mistakes, coordinator cleanup and back-button handling, Storyboard DI with `instantiateViewController(creator:)`, and phased refactoring discipline. A/B confirms with 20 wins — the strongest A/B result across all skills for this model. (Graded: Claude Sonnet 4.6, strict, iteration-6)

### Results (GPT-5.4)

| Metric | Value |
| --- | --- |
| With Skill | 50/51 (98.0%) |
| Without Skill | 44/51 (86.3%) |
| Delta | **+11.8%** |
| A/B | **24W 0T 0L** (avg 9.0 vs 7.4) |

**Interpretation:** GPT-5.4 is already a solid UIKit MVVM baseline at 86.3% without the skill and rises to 98.0% with it — a +11.8% delta. The recovered gaps cluster around MVVM boundary enforcement: GPT-5.4 without the skill consistently misses `private(set)` on `@Published` properties, the concrete cost of `import UIKit` in a ViewModel (simulator-only unit tests), intermediate-state race conditions between separate publisher emissions, the `@Published` immediate-replay mechanism (causing nil-outlet crashes), `.receive(on: DispatchQueue.main)` as a separate combine-bindings violation, and the hide-all-then-show pattern with DiffableDataSource. One with-skill regression: `testing-simple` still uses `wait(for:)` instead of `await fulfillment(of:)`. Blind A/B strongly favors the skill at 24W 0T 0L — no losses — with average quality 9.0 vs 7.4.

### Key Discriminating Assertions — GPT-5.4

| Topic | Assertion | Why It Matters |
| --- | --- | --- |
| viewmodel | `UIKit` import is the core violation | Keeps the ViewModel platform-neutral and testable. |
| viewmodel | UIKit dependency breaks unit testability because UIKit requires a simulator | Explains the concrete cost of the architecture violation. |
| viewmodel | Missing `private(set)` on `@Published` properties | Enforces unidirectional data flow — only the ViewModel writes its own state. |
| viewmodel | Warns about race conditions between separate publisher emissions | `ViewState<T>` enum eliminates intermediate inconsistent states. |
| combine-bindings | `@Published` fires immediately on subscription — explains nil-outlet crash | Drives correct `viewDidLoad` timing for all Combine subscriptions. |
| combine-bindings | Missing `.receive(on: DispatchQueue.main)` — UI updates from wrong thread | Prevents intermittent layout crashes on background queue. |
| viewstate | Hide-all-then-show reset pattern before `switch` over `ViewState` | Prevents stale loading/error views overlapping new content. |
| viewstate | `DiffableDataSource` `applySnapshot` for `.loaded` — warns against `reloadData()` | Crash-free, animatable table updates with no index-path arithmetic. |

### Results (Gemini 3.1 Pro)

| Metric | Value |
| --- | --- |
| With Skill | 50/51 (98.0%) |
| Without Skill | 11/51 (21.6%) |
| Delta | **+76.5%** |

**Interpretation:** Gemini 3.1 Pro without the skill is the weakest baseline of the three models at 21.6% — it passes only the most obvious surface-level assertions. Without the skill, it completely misses all 9 refactoring assertions (phased PRs, discovered.md, severity scanning), all 6 dependency injection assertions (protocol-based injection, `instantiateViewController(creator:)`, ScreenFactory), all 6 testing assertions (`addTeardownBlock`, `await fulfillment(of:)`, cooperative-thread deadlock), and nearly all ViewState and anti-pattern assertions. With the skill, it rises to 98.0% (matching GPT-5.4), demonstrating that skill injection recovers nearly all gaps. The single with-skill failure is `testing-simple` (TE1.3) — the code example uses `wait(for:)` while the prose simultaneously warns against it, a self-contradictory response. The 76.5% delta is the largest of all models tested on this skill. (Graded: Claude Sonnet 4.6, strict, iteration-6)

### Key Discriminating Assertions — Gemini 3.1 Pro

| Topic | Assertion | Without | With |
| --- | --- | --- | --- |
| viewmodel | `private(set)` on `@Published` — unidirectional data flow | FAIL | PASS |
| viewmodel | `UITableView` ref in ViewModel = Critical (retain cycle) | FAIL | PASS |
| viewmodel | Race conditions between separate publisher emissions | FAIL | PASS |
| dependency-injection | Protocol-based constructor injection (`NetworkServiceProtocol`) | FAIL | PASS |
| dependency-injection | `instantiateViewController(creator:)` for Storyboard DI | FAIL | PASS |
| dependency-injection | `ScreenFactory` protocol injected into Coordinator | FAIL | PASS |
| viewstate | Hide-all-then-show reset pattern before `switch` | FAIL | PASS |
| viewstate | `reconfigureItems` (iOS 15+) vs `reloadItems` for single-item updates | FAIL | PASS |
| testing | `addTeardownBlock { [weak sut] in XCTAssertNil(sut) }` | FAIL | PASS |
| testing | `await fulfillment(of:)` vs `wait(for:)` deadlock | FAIL | PASS |
| refactoring | `refactoring/` directory + per-feature plan files | FAIL | PASS |
| refactoring | Phase 1 = safety fixes only, ≤200 lines | FAIL | PASS |
| refactoring | New discoveries → `refactoring/discovered.md` | FAIL | PASS |

> Raw data:
> `workspaces/ios/mvvm-uikit-architecture/iteration-6/benchmark-gpt-5-4.json`
> `workspaces/ios/mvvm-uikit-architecture/iteration-6/benchmark-gemini-3-1-pro.json`

## Author

[Ruslan Popesku](https://git.epam.com/Ruslan_Popesku)
