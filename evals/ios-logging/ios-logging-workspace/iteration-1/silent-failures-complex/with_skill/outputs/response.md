# Silent Failure Audit: OrderViewModel

## Summary of Issues Found

This ViewModel contains **6 distinct silent failure patterns** across its 3 methods. Every single method has at least one critical observability gap. In production, errors from order loading, placement, and deletion would all vanish without a trace.

---

## Issue-by-Issue Breakdown

### 1. `loadOrders()` -- `try?` erases diagnostics on a network call

```swift
let result = try? await OrderService.shared.fetchOrders()
```

`try?` converts any thrown error to `nil`, destroying the error type, message, and stack context. Was it a 401 unauthorized? A timeout? A server 500? All information is lost. The user sees an empty order list with no indication of what went wrong. This is a network/user-facing operation -- `try?` is not acceptable here.

### 2. `loadOrders()` -- no error state exposed to the UI

When `fetchOrders()` fails, `orders` silently defaults to `[]` via the nil-coalescing operator. The view has no way to distinguish "zero orders" from "network failure." The user sees an empty screen with no error message and no retry option.

### 3. `placeOrder(_:)` -- `try?` on two sequential critical operations

```swift
try? await OrderService.shared.submitOrder(order)
try? await OrderService.shared.sendConfirmationEmail(order)
```

Both operations use `try?`, which means:
- If `submitOrder` fails, the code proceeds to send a confirmation email for an order that was never placed.
- If `sendConfirmationEmail` fails, nobody knows the customer did not receive confirmation.
- The `print("Order placed successfully")` executes regardless of whether anything actually succeeded -- it is a lie in the logs.

These are payment/transactional operations. `try?` must never be used here.

### 4. `placeOrder(_:)` -- `print()` instead of structured logging

```swift
print("Order placed successfully")
```

`print()` writes to stdout, which is invisible on production devices (no debugger attached), has no log levels, no privacy controls, no persistence, and cannot be searched remotely. It must be replaced with `os.Logger`.

### 5. `placeOrder(_:)` -- no error reporting to crash/analytics SDK

Even if errors were caught, there is no call to any remote error reporting service. In production, you cannot attach a debugger. Without remote reporting (Sentry, Crashlytics, etc.), order placement failures are invisible to the engineering team.

### 6. `deleteOrder(_:)` -- `Task.detached` swallows errors with no handling

```swift
Task.detached {
    try await OrderService.shared.deleteOrder(id)
}
```

`Task.init` (and `Task.detached`) is `@discardableResult`. If `deleteOrder` throws, the error is silently discarded -- no crash, no log, nothing. Additionally, `Task.detached` strips priority inheritance, task-locals, and cancellation propagation. There is no reason to use `Task.detached` here; a regular `Task` with proper error handling is correct.

---

## Fixed ViewModel

```swift
import os

extension Logger {
    static let orders = Logger(subsystem: Bundle.main.bundleIdentifier ?? "com.app", category: "orders")
}

class OrderViewModel: ObservableObject {
    @Published var orders: [Order] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    func loadOrders() {
        isLoading = true
        errorMessage = nil
        Task {
            do {
                let fetched = try await OrderService.shared.fetchOrders()
                await MainActor.run {
                    self.orders = fetched
                    self.isLoading = false
                }
            } catch is CancellationError {
                // Task cancelled -- expected lifecycle behavior, not a failure
            } catch {
                Logger.orders.error("Failed to load orders: \(error.localizedDescription, privacy: .public)")
                ErrorReporter.shared.recordNonFatal(error, context: ["operation": "loadOrders"])
                await MainActor.run {
                    self.errorMessage = "Unable to load orders. Please try again."
                    self.isLoading = false
                }
            }
        }
    }

    func placeOrder(_ order: Order) {
        Task {
            do {
                try await OrderService.shared.submitOrder(order)
                Logger.orders.notice("Order submitted: \(order.id, privacy: .public)")
            } catch {
                Logger.orders.error("Order submission failed: \(error.localizedDescription, privacy: .public)")
                ErrorReporter.shared.recordNonFatal(error, context: [
                    "operation": "submitOrder",
                    "orderId": order.id
                ])
                await MainActor.run {
                    self.errorMessage = "Failed to place order. Please try again."
                }
                return // Do not send confirmation if order was not placed
            }

            do {
                try await OrderService.shared.sendConfirmationEmail(order)
                Logger.orders.notice("Confirmation email sent: \(order.id, privacy: .public)")
            } catch {
                // Order was placed but email failed -- non-blocking, but must be tracked
                Logger.orders.error("Confirmation email failed for order \(order.id, privacy: .public): \(error.localizedDescription, privacy: .public)")
                ErrorReporter.shared.recordNonFatal(error, context: [
                    "operation": "sendConfirmationEmail",
                    "orderId": order.id
                ])
            }
        }
    }

    func deleteOrder(_ id: String) {
        Task {
            do {
                try await OrderService.shared.deleteOrder(id)
                Logger.orders.notice("Order deleted: \(id, privacy: .public)")
            } catch is CancellationError {
                // Task cancelled -- normal lifecycle
            } catch {
                Logger.orders.error("Delete order failed for \(id, privacy: .public): \(error.localizedDescription, privacy: .public)")
                ErrorReporter.shared.recordNonFatal(error, context: [
                    "operation": "deleteOrder",
                    "orderId": id
                ])
                await MainActor.run {
                    self.errorMessage = "Failed to delete order."
                }
            }
        }
    }
}
```

---

## What Changed and Why

| # | Change | Rationale |
|---|--------|-----------|
| 1 | `try?` replaced with `do/catch` in `loadOrders()` | Network calls must never use `try?` -- the error type, HTTP status, and failure reason are critical for diagnosis |
| 2 | Added `@Published var errorMessage` | The UI needs an error state to distinguish "no orders" from "load failed" and show the user a retry path |
| 3 | `try?` replaced with `do/catch` in `placeOrder()` | Order submission and email are transactional operations; `try?` hides payment and delivery failures |
| 4 | Sequential operations get separate `do/catch` blocks | If `submitOrder` fails, we `return` early so `sendConfirmationEmail` never runs for an unplaced order. If only the email fails, the order still stands but the failure is tracked |
| 5 | `print()` replaced with `Logger.orders.notice()` / `.error()` | `os.Logger` is persisted, filterable, privacy-annotated, and visible in production via log collection; `print()` is none of these |
| 6 | `ErrorReporter.shared.recordNonFatal()` added to every catch | Remote crash reporting (Sentry, Crashlytics, etc.) is the only way to see errors from production devices you cannot attach a debugger to |
| 7 | `Task.detached` replaced with regular `Task` | `Task.detached` strips priority inheritance and task-locals for no benefit here. A regular `Task` inherits the actor context correctly |
| 8 | `CancellationError` handled separately | Cancellation is normal Swift concurrency lifecycle (e.g., a view disappearing), not an error. Reporting it as a failure creates noise in crash dashboards |
| 9 | Privacy annotations on all dynamic log values | `privacy: .public` on order IDs so they are readable in production logs; default is `.private` which redacts values, making logs useless for debugging |

---

## The Three Rules Applied

1. **No `print()` in production code** -- all `print()` replaced with `Logger` using privacy annotations.
2. **No catch block without observability** -- every `catch` has both `Logger.error()` and `ErrorReporter.shared.recordNonFatal()`.
3. **No `try?` on operations where failure matters** -- all three methods dealt with network/persistence/transactional operations; all `try?` converted to `do/catch`.
