# Accessibility Review: Reduce Motion for Spring Animation

## Issue Found

### [HIGH] Spring animation ignores Reduce Motion preference

**WCAG:** 2.3.3 Animation from Interactions (Level AAA) | **HIG:** Accessibility > Motion
**Issue:** The `withAnimation(.spring(...))` call runs unconditionally, ignoring the user's "Reduce Motion" system preference. Bouncing spring animations are explicitly classified as motion that requires an accessible alternative.
**Impact:** Users with vestibular disorders, motion sensitivity, or epilepsy who enable "Reduce Motion" in Settings will still experience the full bouncing spring animation. This can cause discomfort, disorientation, or nausea.

**Fix:**

```swift
// ❌ Current — ignores user preference
withAnimation(.spring(response: 0.5, dampingFraction: 0.3)) {
    showDetail.toggle()
}

// ✅ Corrected — reads the environment and substitutes a safe transition
@Environment(\.accessibilityReduceMotion) var reduceMotion

withAnimation(reduceMotion ? .easeInOut(duration: 0.2) : .spring(response: 0.5, dampingFraction: 0.3)) {
    showDetail.toggle()
}
```

---

## Why a Spring Counts as Motion

Bouncing springs involve spatial oscillation — the view overshoots its destination and snaps back. This is listed in the "Needs reduce-motion alternative" category alongside parallax effects, sliding transitions, and scaling animations. It is not a safe crossfade or color change.

---

## Key Principle: Replace, Don't Remove

Do **not** pass `.none` (no animation at all) when reduce motion is enabled. A completely instantaneous state change feels broken and jarring in its own way. Instead, substitute a gentle crossfade or a short `easeInOut` — these communicate the state change without spatial movement.

| Reduce Motion OFF | Reduce Motion ON |
|---|---|
| `.spring(response: 0.5, dampingFraction: 0.3)` | `.easeInOut(duration: 0.2)` |
| `.slide` transition | `.opacity` transition |

---

## Alternative: Reusable Helper

If this pattern appears in multiple places across the codebase, extract a helper to keep the logic DRY:

```swift
func withOptionalAnimation<Result>(
    _ animation: Animation? = .default,
    _ body: () throws -> Result
) rethrows -> Result {
    if UIAccessibility.isReduceMotionEnabled {
        return try body()
    } else {
        return try withAnimation(animation, body)
    }
}

// Usage
withOptionalAnimation(.spring(response: 0.5, dampingFraction: 0.3)) {
    showDetail.toggle()
}
```

This helper uses `UIAccessibility.isReduceMotionEnabled` directly (imperative check) which is equivalent to the `@Environment(\.accessibilityReduceMotion)` property wrapper. Use the `@Environment` approach in SwiftUI views; use the helper when the call site is outside a view body.

---

## If the View Also Uses Transitions

If `showDetail` drives a conditional view insertion/removal (e.g., `if showDetail { DetailView() }`), also update the transition:

```swift
DetailView()
    .transition(reduceMotion ? .opacity : .slide)
```

---

## Confidence Check

- [x] Animation checks `@Environment(\.accessibilityReduceMotion)` before applying spring
- [x] Motion replaced with crossfade/easeInOut — not removed entirely
- [x] No hardcoded font sizes or colors introduced
- [x] No `onTapGesture` used
- [x] No deprecated API used

---

## Severity

**🟡 HIGH** — Breaks under an accessibility setting (`reduceMotion`). Not a blocking release issue in most contexts, but violates Apple HIG motion guidance and should be fixed before shipping to users with vestibular sensitivities.
