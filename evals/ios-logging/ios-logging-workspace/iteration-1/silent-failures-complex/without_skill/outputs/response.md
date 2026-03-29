# Audit: Silent Failure Patterns in OrderViewModel

## Issues Found

### 1. `loadOrders()` -- `try?` silently swallows fetch errors

```swift
let result = try? await OrderService.shared.fetchOrders()
```

**Problem:** `try?` converts any thrown error into `nil`, which then falls through to the `?? []` coalescing. The user sees an empty list with no indication that a network error, auth failure, or server error occurred. The `isLoading` spinner disappears and the screen looks as though there are simply no orders.

### 2. `placeOrder(_:)` -- Two independent `try?` calls with no error state

```swift
try? await OrderService.shared.submitOrder(order)
try? await OrderService.shared.sendConfirmationEmail(order)
print("Order placed successfully")
```

**Problems:**
- If `submitOrder` fails, the code still attempts `sendConfirmationEmail` on an order that was never persisted. Both failures are silently discarded.
- `"Order placed successfully"` prints unconditionally regardless of whether anything actually succeeded.
- There is no `@Published` error property, so the UI has no way to show a failure state to the user.

### 3. `deleteOrder(_:)` -- `Task.detached` with unhandled throw

```swift
Task.detached {
    try await OrderService.shared.deleteOrder(id)
}
```

**Problems:**
- `Task.detached` does not inherit the actor context, so `self` cannot be referenced to update UI state on failure.
- The `try` will throw, but there is no `catch`; the error is silently absorbed by the detached task. The user taps "delete," nothing happens, and there is no feedback.
- No optimistic UI update or post-deletion refresh of the `orders` array.

### 4. General ViewModel problems

- No `@Published var errorMessage: String?` or equivalent error state for the UI to observe.
- No structured logging anywhere -- only a misleading `print` statement.
- No `@MainActor` annotation on the class, despite publishing to `@Published` properties (potential data-race warnings under strict concurrency).

---

## Fixed Implementation

```swift
import os.log

private let logger = Logger(subsystem: Bundle.main.bundleIdentifier ?? "com.app", category: "OrderViewModel")

@MainActor
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
                self.orders = fetched
                logger.info("Loaded \(fetched.count) orders")
            } catch {
                logger.error("Failed to load orders: \(error.localizedDescription)")
                self.errorMessage = "Unable to load orders. Please try again."
            }
            self.isLoading = false
        }
    }

    func placeOrder(_ order: Order) {
        isLoading = true
        errorMessage = nil

        Task {
            do {
                try await OrderService.shared.submitOrder(order)
                logger.info("Order \(order.id) submitted successfully")
            } catch {
                logger.error("Failed to submit order \(order.id): \(error.localizedDescription)")
                self.errorMessage = "Failed to place order. Please try again."
                self.isLoading = false
                return
            }

            do {
                try await OrderService.shared.sendConfirmationEmail(order)
                logger.info("Confirmation email sent for order \(order.id)")
            } catch {
                // Email failure is non-critical -- log but do not block the user
                logger.warning("Confirmation email failed for order \(order.id): \(error.localizedDescription)")
            }

            // Refresh the list so the new order appears
            await refreshOrders()
            self.isLoading = false
        }
    }

    func deleteOrder(_ id: String) {
        // Optimistic removal
        let previousOrders = orders
        orders.removeAll { $0.id == id }

        Task {
            do {
                try await OrderService.shared.deleteOrder(id)
                logger.info("Deleted order \(id)")
            } catch {
                logger.error("Failed to delete order \(id): \(error.localizedDescription)")
                // Roll back the optimistic removal
                self.orders = previousOrders
                self.errorMessage = "Failed to delete order. Please try again."
            }
        }
    }

    private func refreshOrders() async {
        do {
            self.orders = try await OrderService.shared.fetchOrders()
        } catch {
            logger.error("Failed to refresh orders: \(error.localizedDescription)")
        }
    }
}
```

---

## Summary of Changes

| Original Pattern | Problem | Fix |
|---|---|---|
| `try?` in `loadOrders` | Network errors silently produce an empty list | `do/catch` with `@Published errorMessage` |
| `try?` in `placeOrder` | Submit and email failures both swallowed; misleading `print` | Separate `do/catch` blocks; short-circuit on submit failure; treat email as non-critical warning |
| `Task.detached` in `deleteOrder` | Error thrown into the void; no UI update | Regular `Task` on `@MainActor`; optimistic delete with rollback on failure |
| No error state | UI cannot display any failure | Added `@Published var errorMessage: String?` |
| No logging | `print` only; no severity levels; misleading message | `os.log` `Logger` with `info`, `warning`, and `error` levels |
| Missing `@MainActor` | Potential data races when updating `@Published` properties from tasks | `@MainActor` annotation on the class |
