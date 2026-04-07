# VIPER UIKit Architecture Skill

Enterprise-grade UIKit VIPER architecture skill for production iOS codebases (iOS 13+).

## What This Skill Does

Guides AI coding assistants through VIPER (View-Interactor-Presenter-Entity-Router) architecture for UIKit applications, preventing the most common AI-generated mistakes: retain cycles from incorrect reference directions, UIKit imports in Presenters, business logic in Presenters instead of Interactors, and strong references where weak ones are required.

**Covers:**
- Building new VIPER modules with correct ownership chains and protocol contracts
- Refactoring legacy MVC/MVVM codebases to VIPER through phased, reviewable PRs
- Decomposing god ViewControllers into properly separated VIPER layers
- Implementing Router/Wireframe navigation with weak reference safety
- Testing Presenters and Interactors in isolation with mock protocols
- Debugging and fixing retain cycles in VIPER module wiring
- Integrating Coordinators for multi-flow navigation in large apps
- Migrating VIPER Views to SwiftUI via UIHostingController adapter pattern
- Module assembly with dependency injection (enum-based Builders)
- Enterprise concerns: error propagation chains, ViewState management, thread dispatching

## When to Use

- Creating new VIPER modules for UIKit apps
- Refactoring MVC or MVVM screens to VIPER architecture
- Reviewing VIPER code for anti-patterns (especially retain cycles and layer violations)
- Fixing memory leaks in VIPER module wiring
- Setting up module Builders/Factories with dependency injection
- Implementing Router navigation patterns
- Testing VIPER Presenters and Interactors
- Migrating VIPER Views to SwiftUI incrementally
- Adding Coordinator pattern on top of VIPER Routers

## Structure

```
viper-uikit-architecture/
├── SKILL.md                              # Main skill: architecture layers, decision trees, workflows, rules
├── README.md                             # This file
└── references/
    ├── rules.md                          # Do's and Don'ts quick reference
    ├── module-contracts.md               # 6 protocols per module, naming conventions, AnyObject constraints
    ├── view-patterns.md                  # Passive View rules, lifecycle forwarding, UITableView data flow
    ├── presenter-patterns.md             # UIKit-free Presenter, ViewState mapping, Entity→ViewModel translation
    ├── interactor-patterns.md            # Single use case, service injection, Entity boundaries, async patterns
    ├── router-navigation.md              # Weak VC reference, push/present/dismiss, deep linking
    ├── module-assembly.md                # Builder/Factory patterns, DI, wiring order
    ├── memory-management.md              # Ownership chain, retain cycle debugging, deallocation verification
    ├── testing.md                        # Interactor/Presenter/Router testing, mock patterns, leak assertions
    ├── anti-patterns.md                  # AI-specific mistakes, severity-ranked violations, detection checklist
    ├── coordinator-integration.md        # When Routers aren't enough, Coordinator hierarchy, wiring
    ├── migration-patterns.md             # MVC→VIPER extraction, VIPER→SwiftUI via UIHostingController
    ├── enterprise-patterns.md            # Error propagation, ViewState, analytics decoration, thread safety
    └── refactoring-workflow.md           # refactoring/ directory protocol, per-feature plans, PR sizing
```

## Benchmark Results

Tested on **16 scenarios** with **149 assertions**. All grading by **Claude Sonnet 4.6** (strict, independent grader).

### Results Summary

| Model | With Skill | Without Skill | Delta | A/B Quality |
| --- | --- | --- | --- | --- |
| **Sonnet 4.6** | 148/149 (99.3%) | 144/149 (96.6%) | **+2.7%** | **15W** 1T 0L (avg 9.5 vs 9.4) |
| **GPT-5.4** | 148/149 (99.3%) | 129/149 (86.6%) | **+12.8%** | **16W** 0T 0L (avg 9.0 vs 7.3) |
| **Gemini 3.1 Pro** | 149/149 (100.0%) | 29/149 (19.5%) | **+80.5%** | **16W** 0T 0L (avg 7.3 vs 1.7) |

> A/B Quality: blind judge scores each response 0–10 and picks the better one without knowing which used the skill. Format: wins/ties/losses (avg with_skill score vs avg without_skill score).

> **Note on Sonnet 4.6:** Sonnet 4.6 has a very strong VIPER baseline (96.6%) — it already knows most VIPER patterns without the skill. The skill adds the remaining 5 assertions it misses.
>
> **Note on GPT-5.4 grading:** Initial self-grading by GPT-5.4 reported 149/149 (100%) with-skill and 141/149 (94.6%) without-skill (+5.4% delta). Independent regrading found significant charity bias — 14 phantom passes on the without-skill side and 2 on the with-skill side. The numbers above reflect the strict regrading.

### GPT-5.4 Per-Scenario Breakdown (Claude-regraded)

| # | Scenario | With Skill | Without Skill | Delta |
| --- | --- | --- | --- | --- |
| 1 | Greenfield product-list module | 17/17 | 14/17 | **+3** |
| 2 | Profile MVC→VIPER refactor | 13/13 | 10/13 | **+3** |
| 3 | Presenter unit tests (checkout) | 12/12 | 9/12 | **+3** |
| 4 | Complex navigation | 9/9 | 6/9 | **+3** |
| 5 | Inter-module communication | 9/9 | 7/9 | +2 |
| 6 | async/await integration | 9/9 | 7/9 | +2 |
| 7 | Interactor unit tests (cart) | 12/12 | 11/12 | +1 |
| 8 | SwiftUI migration (UIHostingController) | 11/11 | 10/11 | +1 |
| 9 | Builder assembly + UITabBarController timing | 6/6 | 5/6 | +1 |
| 10 | Thread-safety dispatching boundary | 5/5 | 4/5 | +1 |
| 11 | God Interactor decomposition | 7/7 | 6/7 | +1 |
| 12 | Entities domain layer design | 6/6 | 5/6 | +1 |
| 13 | Code review anti-patterns | 11/11 | 11/11 | 0 |
| 14 | Retain cycle detection & fix | 10/10 | 10/10 | 0 |
| 15 | Error propagation chain | 5/6 | 6/6 | **-1** |
| 16 | ViewState enum design | 5/6 | 6/6 | **-1** |

### GPT-5.4 Discriminating Assertions (22 total)

GPT-5.4's baseline missed 22 assertions across 12 evals (Claude-regraded):

| Scenario | Missing Assertion |
| --- | --- |
| Product-list module | Presenter maps domain data to ViewModels before passing to View |
| Product-list module | Product entities defined OUTSIDE the module folder |
| Product-list module | Builder is enum-based (not a class) |
| Profile refactor | Presenter does NOT import UIKit |
| Profile refactor | Presenter maps User entity to a display-ready ViewModel |
| Profile refactor | User and Post entities defined outside the module folder |
| Presenter tests | Full communication chain test (Presenter→Interactor→Output→View) |
| Presenter tests | Memory leak detection via `addTeardownBlock` |
| Presenter tests | Router test keeps strong ViewController reference |
| Complex navigation | Modal dismissal by presenting Router, not composer itself |
| Complex navigation | Comment posting delegate reaches both FeedDetail and FeedList |
| Complex navigation | FeedDetail Router dismisses after delegate callback |
| Module communication | OrderDetail delegate wired through Router→Builder |
| Module communication | ItemPicker dismissal by presenting module's Router |
| async/await integration | Error handling covers both initial fetch and stream failure separately |
| async/await integration | AsyncStream continuation onTermination handler for cleanup |
| Interactor tests | Presenter mock held weakly with leak detection via `addTeardownBlock` |
| SwiftUI migration | SwiftUI View does NOT use NavigationLink or NavigationStack |
| Builder + TabBar | Builder calls initial setup before returning VC |
| Thread dispatching | Explains why Presenter dispatch is wrong (thread-safety hazard) |
| God Interactor | Presenter conforms to ALL interactor output protocols |
| Entities | Interactors map to intermediate response types, not raw entities |

### GPT-5.4 Skill Regressions (2 assertions)

In 2 evals the skill-guided response scored lower than baseline:

| Scenario | Failed Assertion | Cause |
| --- | --- | --- |
| Error propagation chain | A6: No wildcard catch-all in error handling | Skill's error mapping pattern caused overly generic `default:` fallback |
| ViewState enum design | A6: View renders each enum case distinctly | Skill's focus on ViewState design caused response to omit View layer code |

### Gemini 3.1 Pro Per-Scenario Breakdown (Claude-regraded)

| # | Scenario | With Skill | Without Skill | Delta |
| --- | --- | --- | --- | --- |
| 1 | Greenfield product-list module | 17/17 | 5/17 | **+12** |
| 2 | Profile MVC→VIPER refactor | 13/13 | 4/13 | **+9** |
| 3 | Presenter unit tests (checkout) | 12/12 | 5/12 | **+7** |
| 4 | Inter-module communication | 9/9 | 5/9 | **+4** |
| 5 | Code review anti-patterns | 11/11 | 5/11 | **+6** |
| 6 | async/await integration | 9/9 | 0/9 | **+9** |
| 7 | Retain cycle detection & fix | 10/10 | 2/10 | **+8** |
| 8 | SwiftUI migration (UIHostingController) | 11/11 | 0/11 | **+11** |
| 9 | Complex navigation | 9/9 | 0/9 | **+9** |
| 10 | Interactor unit tests (cart) | 12/12 | 0/12 | **+12** |
| 11 | Builder assembly + UITabBarController timing | 6/6 | 0/6 | **+6** |
| 12 | Thread-safety dispatching boundary | 5/5 | 0/5 | **+5** |
| 13 | ViewState enum design | 6/6 | 0/6 | **+6** |
| 14 | God Interactor decomposition | 7/7 | 0/7 | **+7** |
| 15 | Entities domain layer design | 6/6 | 0/6 | **+6** |
| 16 | Error propagation chain | 6/6 | 3/6 | **+3** |

### Gemini 3.1 Pro Key Findings

Gemini 3.1 Pro without the skill demonstrates severe VIPER knowledge gaps — a 19.5% baseline is the lowest across all tested models. Nine of sixteen scenarios scored 0/N without skill context. The skill raises Gemini to 100.0% (+80.5% delta), the largest improvement of any model tested.

Key patterns Gemini fails without skill guidance:
- **Architecture fundamentals**: Entities passed directly from Interactor to Presenter (should map to response structs), async/await still uses callback InteractorOutput protocol, SwiftUI migration not understood (11/11 assertions failed), ViewState modeled as boolean flags instead of enum
- **Memory safety**: Only 2/10 retain cycle assertions passed — Gemini identifies one Presenter↔Interactor cycle but misses Presenter→View, Router→VC, and AnyObject constraint as root cause
- **Advanced patterns**: Complex navigation (0/9), God Interactor decomposition using extensions instead of separate use-case Interactors (0/7), TabBar timing issue misdiagnosed (0/6)
- **Thread safety**: Dispatches on main thread inside Presenter (the anti-pattern), not at Interactor output boundary (0/5)
- **Testing**: Completely absent without skill — both interactor-tests (0/12) and async-await-integration (0/9) scored zero

### Cross-Model Analysis

GPT-5.4 achieves a strong 99.3% with-skill result and 86.6% without — a solid +12.8% delta showing consistent VIPER knowledge gaps regardless of model family (Router-coordinated dismissal, shared domain entities, test leak detection, AsyncStream cleanup).

Gemini 3.1 Pro shows the steepest skill improvement at +80.5%. Its without-skill baseline (19.5%) is dramatically lower than GPT-5.4 (86.6%) or Sonnet 4.6 (96.6%), indicating that Gemini has significantly less VIPER training data and relies almost entirely on the skill for correct output. With the skill, Gemini reaches 100.0% — meaning the skill fully compensates for the knowledge gap.

GPT-5.4 self-grading masked its baseline weakness, inflating the without-skill score from 86.6% to 94.6%. Independent grading reveals the actual 22-assertion gap. Sonnet 4.6 data was removed as corrupted.

## Source Material

- objc.io "Architecting iOS Apps with VIPER" (original Mutual Mobile article)
- Rambler&Co VIPER guidelines and Typhoon DI patterns
- TheSwiftDev VIPER ownership chain analysis
- CheesecakeLabs VIPER implementation guides
- ZIKViper Router/Wireframe distinction
- Infinum iOS templates (GitHub issue #31 — UIKit in Presenter fix)
- Vadim Bulavin's DI patterns for VIPER
- mutualmobile/VIPER-TODO GitHub issues
- Point-Free swift-snapshot-testing for View layer
- Multiple production post-mortems on VIPER retain cycles
