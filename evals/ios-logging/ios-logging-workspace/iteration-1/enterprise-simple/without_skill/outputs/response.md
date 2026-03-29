# Handling Errors in SwiftUI Views

Setting an error string and showing an alert is a common starting point, but it has limitations -- you lose error context, can't distinguish error severity, and have no visibility into errors happening in production. Here's a more robust approach.

## 1. Use Typed Errors Instead of Raw Strings

Define domain-specific error types rather than passing around strings:

```swift
enum DataError: LocalizedError {
    case networkUnavailable
    case unauthorized
    case serverError(statusCode: Int)
    case decodingFailed(underlying: Error)
    case unknown(Error)

    var errorDescription: String? {
        switch self {
        case .networkUnavailable:
            return "No network connection available."
        case .unauthorized:
            return "Your session has expired. Please sign in again."
        case .serverError(let code):
            return "Server returned an error (code \(code))."
        case .decodingFailed:
            return "Failed to process the server response."
        case .unknown(let error):
            return error.localizedDescription
        }
    }

    var recoverySuggestion: String? {
        switch self {
        case .networkUnavailable:
            return "Check your internet connection and try again."
        case .unauthorized:
            return "Tap Sign In to re-authenticate."
        default:
            return "Please try again later."
        }
    }
}
```

## 2. Add Structured Logging with OSLog

Apple's `os.Logger` is the recommended way to log errors. It is performant, supports structured metadata, and integrates with Console.app and Instruments:

```swift
import OSLog

extension Logger {
    private static let subsystem = Bundle.main.bundleIdentifier ?? "com.myapp"

    static let ui = Logger(subsystem: subsystem, category: "UI")
    static let network = Logger(subsystem: subsystem, category: "Network")
    static let data = Logger(subsystem: subsystem, category: "Data")
}
```

Use appropriate log levels:

```swift
do {
    try await viewModel.loadData()
} catch let error as DataError {
    switch error {
    case .networkUnavailable:
        Logger.network.warning("Network unavailable when loading data")
    case .unauthorized:
        Logger.network.error("Unauthorized access - token may be expired")
    case .serverError(let code):
        Logger.network.error("Server error with status code: \(code)")
    case .decodingFailed(let underlying):
        Logger.data.fault("Decoding failed: \(underlying.localizedDescription)")
    case .unknown(let underlying):
        Logger.data.error("Unknown error: \(underlying.localizedDescription)")
    }
    self.currentError = error
    self.showErrorAlert = true
} catch {
    Logger.data.error("Unexpected error: \(error.localizedDescription)")
    self.currentError = DataError.unknown(error)
    self.showErrorAlert = true
}
```

Key log levels and when to use them:
- **`debug`** -- verbose info useful only during development
- **`info`** -- informational messages for normal operations
- **`notice`** (default) -- notable events worth persisting
- **`warning`** -- recoverable issues (e.g., network retry)
- **`error`** -- failures that affect functionality
- **`fault`** -- programming errors or corrupted state

## 3. Centralize Error Presentation

Create a reusable error-handling view modifier:

```swift
struct ErrorAlertModifier: ViewModifier {
    @Binding var error: DataError?

    var isPresented: Binding<Bool> {
        Binding(
            get: { error != nil },
            set: { if !$0 { error = nil } }
        )
    }

    func body(content: Content) -> some View {
        content
            .alert(
                "Something Went Wrong",
                isPresented: isPresented,
                presenting: error
            ) { error in
                Button("OK", role: .cancel) { }
                if case .unauthorized = error {
                    Button("Sign In") {
                        // handle re-auth
                    }
                }
            } message: { error in
                Text(error.localizedDescription)
            }
    }
}

extension View {
    func errorAlert(_ error: Binding<DataError?>) -> some View {
        modifier(ErrorAlertModifier(error: error))
    }
}
```

Usage becomes clean:

```swift
struct ContentView: View {
    @State private var error: DataError?

    var body: some View {
        MyContentView()
            .errorAlert($error)
            .task {
                do {
                    try await loadData()
                } catch let dataError as DataError {
                    Logger.data.error("Load failed: \(dataError.localizedDescription)")
                    error = dataError
                } catch {
                    Logger.data.error("Unexpected: \(error.localizedDescription)")
                    self.error = .unknown(error)
                }
            }
    }
}
```

## 4. Move Error-Prone Logic to the ViewModel

Keep your views thin. The view model handles errors, logs them, and exposes state for the view to react to:

```swift
@Observable
class ContentViewModel {
    var items: [Item] = []
    var error: DataError?
    var isLoading = false

    func loadItems() async {
        isLoading = true
        defer { isLoading = false }

        do {
            items = try await repository.fetchItems()
            Logger.data.info("Loaded \(self.items.count) items")
        } catch let error as DataError {
            Logger.data.error("Failed to load items: \(error.localizedDescription)")
            self.error = error
        } catch {
            Logger.data.error("Unexpected error loading items: \(error.localizedDescription)")
            self.error = .unknown(error)
        }
    }
}
```

## 5. Consider a Lightweight Error Reporting Layer

For production visibility, wrap your logger so you can funnel errors to a crash/error reporting service without changing call sites:

```swift
enum ErrorReporter {
    static func report(_ error: Error, context: String, file: String = #file, line: Int = #line) {
        let fileName = (file as NSString).lastPathComponent
        Logger.data.error("[\(fileName):\(line)] \(context): \(error.localizedDescription)")

        // Send to your analytics/crash reporting service in production
        #if !DEBUG
        CrashReportingService.shared.recordError(error, metadata: ["context": context])
        #endif
    }
}
```

## Summary

| Practice | Why |
|---|---|
| Use typed errors (`LocalizedError`) | Enables pattern matching, recovery suggestions, and clear user messaging |
| Log with `os.Logger` | Structured, performant, and visible in Console.app and Instruments |
| Use appropriate log levels | Lets you filter noise in production while keeping detail in development |
| Centralize error presentation | Avoids duplicated alert logic across views |
| Keep error handling in view models | Keeps views declarative and testable |
| Add a reporting layer | Gives production visibility without changing every call site |

The key shift is moving from "catch and show a string" to "catch, classify, log with context, and present appropriately." This gives you debuggability during development and observability in production.
