# Handling Errors in SwiftUI Views

Setting an error string and showing an alert is a common starting point, but it has significant gaps: those errors are invisible in production. You cannot attach a debugger to a user's device, so when something fails you need structured logging and remote reporting to actually diagnose it. Here is how to upgrade your approach.

## The Problem with Bare Error Strings

A typical pattern looks like this:

```swift
@State private var errorMessage: String?

.task {
    do {
        data = try await fetchItems()
    } catch {
        errorMessage = error.localizedDescription // This is all that happens
    }
}
.alert("Error", isPresented: .constant(errorMessage != nil)) {
    Button("OK") { errorMessage = nil }
} message: {
    Text(errorMessage ?? "")
}
```

This has three problems:
1. The error is not logged with `os.Logger`, so it will not appear in Console.app or device logs.
2. The error is not reported to a crash reporting service (Sentry, Crashlytics), so you will never know it happened in production.
3. Every view repeats the same error handling boilerplate with no consistency in how errors are categorized or presented.

## Step 1: Add Structured Logging and Remote Reporting to Every Catch Block

Every catch block should follow this template:

```swift
catch {
    // 1. ALWAYS: Structured log with privacy annotations
    Logger.networking.error("Failed to fetch items: \(error.localizedDescription, privacy: .public)")

    // 2. ALWAYS: Report to crash/analytics SDK
    ErrorReporter.shared.recordNonFatal(error, context: ["operation": "fetchItems"])

    // 3. CONDITIONALLY: Surface to the user (if user-facing)
    errorMessage = error.localizedDescription
}
```

The `os.Logger` call ensures the error is captured in the unified logging system with appropriate privacy annotations. The `ErrorReporter` call sends it to your remote crash SDK so you can see it in a dashboard. The user-facing message is still there, but it is now the third concern, not the only one.

## Step 2: Build a Centralized Error Handler

Instead of scattering error state across every view, create a single `ErrorHandler` that every view delegates to:

```swift
@MainActor
final class ErrorHandler: ObservableObject {
    @Published var currentAlert: AlertInfo?

    func handle(_ error: Error, context: String) {
        // 1. Always log
        Logger.ui.error("\(context, privacy: .public): \(error.localizedDescription, privacy: .public)")

        // 2. Always report
        ErrorReporter.shared.recordNonFatal(error, context: ["context": context])

        // 3. Route based on error category
        if let categorized = error as? CategorizedError {
            switch categorized.category {
            case .retryable:
                currentAlert = AlertInfo(
                    title: "Temporary Issue",
                    message: "Please try again in a moment.",
                    retryAction: { /* caller provides */ }
                )
            case .nonRetryable:
                currentAlert = AlertInfo(
                    title: "Something Went Wrong",
                    message: error.localizedDescription
                )
            case .requiresLogout:
                AuthManager.shared.logout()
                currentAlert = AlertInfo(
                    title: "Session Expired",
                    message: "Please sign in again."
                )
            }
        } else {
            currentAlert = AlertInfo(
                title: "Error",
                message: error.localizedDescription
            )
        }
    }
}
```

This uses a `CategorizedError` protocol so different error types drive different behavior -- retryable errors offer a retry action, auth failures trigger logout, and non-retryable errors show a plain message:

```swift
enum ErrorCategory {
    case retryable
    case nonRetryable
    case requiresLogout
}

protocol CategorizedError: Error {
    var category: ErrorCategory { get }
}
```

## Step 3: Wire It Into SwiftUI with a View Modifier

Create a modifier that attaches the alert presentation to any view:

```swift
struct ErrorHandlingModifier: ViewModifier {
    @EnvironmentObject var errorHandler: ErrorHandler

    func body(content: Content) -> some View {
        content.alert(item: $errorHandler.currentAlert) { alert in
            Alert(
                title: Text(alert.title),
                message: Text(alert.message),
                dismissButton: .default(Text("OK"))
            )
        }
    }
}

extension View {
    func withErrorHandling() -> some View {
        modifier(ErrorHandlingModifier())
    }
}
```

Inject the handler at the app root:

```swift
@main
struct MyApp: App {
    @StateObject private var errorHandler = ErrorHandler()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(errorHandler)
                .withErrorHandling()
        }
    }
}
```

Now any view can use it:

```swift
struct ItemListView: View {
    @EnvironmentObject var errorHandler: ErrorHandler

    var body: some View {
        List { /* ... */ }
            .task {
                do {
                    items = try await fetchItems()
                } catch {
                    errorHandler.handle(error, context: "ItemListView.fetchItems")
                }
            }
    }
}
```

## Step 4: Handle CancellationError in .task {} Modifiers

SwiftUI's `.task {}` modifier cancels its task when the view disappears. This is normal behavior, not an error. You must distinguish it from real failures:

```swift
.task {
    do {
        items = try await fetchItems()
    } catch is CancellationError {
        // Normal -- view disappeared, do nothing
    } catch {
        errorHandler.handle(error, context: "ItemListView.fetchItems")
    }
}
```

If you do not handle `CancellationError` separately, you will get false error reports every time a user navigates away from a screen before a network call finishes.

## Step 5: Replace print() with os.Logger

If any of your catch blocks use `print()`, replace them with `os.Logger`. Use the appropriate log level:

- `.debug` -- tracing during development (not persisted in production)
- `.info` -- contextual details (memory-only, captured on faults)
- `.notice` -- operational events (persisted to disk)
- `.error` -- recoverable errors (always persisted)
- `.fault` -- bugs or unrecoverable states (persisted with process chain info)

Always include privacy annotations on dynamic strings:

```swift
// Bad
print("Failed to load user: \(error)")

// Good
Logger.networking.error("Failed to load user: \(error.localizedDescription, privacy: .public)")
```

## Summary

The key shift is: an alert shown to the user is not observability. Production error handling requires three layers working together:

1. **os.Logger** with privacy annotations for structured device logs
2. **Remote crash SDK** (Sentry, Crashlytics) for production visibility via `ErrorReporter`
3. **Centralized ErrorHandler** injected via SwiftUI environment for consistent user-facing alerts

This turns your catch blocks from dead ends into observable events that you can query and debug remotely.
