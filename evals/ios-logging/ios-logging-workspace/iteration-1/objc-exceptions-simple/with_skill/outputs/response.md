# Will Swift's do/catch Handle All Errors in My iOS App?

No. Swift's `do/catch` only catches Swift `Error` types (i.e., values thrown with `throw` that conform to the `Error` protocol). There are several categories of failures in an iOS app that `do/catch` will never intercept.

## What do/catch Catches

Swift's `do/catch` handles any value thrown via `throw` that conforms to the `Error` protocol. This covers the vast majority of errors you write yourself and errors from Swift-native APIs (network failures from URLSession when using async/await, JSON decoding errors, file system errors, etc.).

## What do/catch Does NOT Catch

### 1. Objective-C NSExceptions

This is the most common surprise. Many Foundation and UIKit APIs are backed by Objective-C and raise `NSException` instead of throwing a Swift `Error`. **Swift's `do/catch` will never execute its catch block for an NSException.** The app simply crashes.

Common NSException triggers include:

- **NSArray/NSDictionary** out-of-bounds access or nil key insertion
- **Invalid KVO key paths** (typos in key path strings, unregistered observers)
- **Unrecognized selectors** (calling a method that does not exist on an object)
- **Core Data threading violations** (accessing managed objects from the wrong thread)
- **NSInvalidArgumentException** (wrong argument types passed to Objective-C methods)
- **Storyboard/Nib loading failures** (missing outlet connections, wrong class names)

Example of code that looks safe but is not:

```swift
// This catch block will NEVER execute for an NSRangeException
do {
    let item = nsArray.object(at: 999) // raises NSRangeException -> crash
} catch {
    // Never reached
}
```

The fix is to validate inputs before calling into Objective-C APIs:

```swift
guard index < nsArray.count else {
    Logger.database.error("Index \(index, privacy: .public) out of bounds for array of \(nsArray.count, privacy: .public)")
    return nil
}
let item = nsArray.object(at: index)
```

### 2. Swift Runtime Traps

Force-unwrapping a nil optional (`myOptional!`), out-of-bounds access on a Swift `Array`, failed forced casts (`as!`), and `fatalError()` / `preconditionFailure()` all trigger a SIGTRAP signal. These are not Swift `Error` types and cannot be caught with `do/catch`.

### 3. Memory Access Violations (EXC_BAD_ACCESS)

Accessing deallocated memory or invalid pointers results in a SIGSEGV or EXC_BAD_ACCESS. These are low-level signals, not Swift errors.

### 4. Swift-ObjC Bridge Edge Case

When a Swift `throws` function is exposed to Objective-C via `@objc`, ObjC determines success or failure based on the return value (nil means failure), not on whether an `NSError` was set. If an Objective-C caller receives a non-nil return AND an NSError was set, Swift's catch block is never invoked and the error is silently lost.

## Coverage Summary

| Error Type                     | Caught by do/catch? | What Catches It Instead        |
|--------------------------------|:-------------------:|--------------------------------|
| Swift `Error` (throw)          | Yes                 | --                             |
| Objective-C `NSException`      | **No**              | `NSSetUncaughtExceptionHandler` |
| Swift trap (force unwrap nil)  | **No**              | Signal handler (SIGTRAP)       |
| EXC_BAD_ACCESS (bad memory)    | **No**              | Signal handler (SIGSEGV)       |

## What To Do About It

1. **Validate inputs defensively** before calling Objective-C APIs rather than relying on catch blocks.
2. **Use a crash reporting SDK** (Sentry or Firebase Crashlytics). These SDKs install three layers of protection that cover all the gaps above:
   - `NSSetUncaughtExceptionHandler` for Objective-C exceptions
   - UNIX signal handlers (`sigaction`) for Swift traps and memory violations
   - Mach exception handlers for low-level machine exceptions
3. **Add MetricKit** to detect out-of-memory kills, watchdog terminations, and hangs that no in-process handler can catch.
4. **Do not install your own `NSSetUncaughtExceptionHandler`** if you are using a crash SDK -- a second call replaces the first and will interfere with the SDK's crash capture.

In short, `do/catch` is the right tool for Swift-native error handling, but it covers only one of the four major failure categories in an iOS app. Defensive validation and a crash reporting SDK are essential for the rest.
