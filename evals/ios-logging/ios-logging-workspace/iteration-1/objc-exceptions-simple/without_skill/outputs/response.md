# Will Swift's do/catch Handle All Errors in My iOS App?

**Short answer: No.** Swift's `do/catch` only handles Swift errors (types conforming to the `Error` protocol) that are explicitly thrown from functions marked with `throws`. There are several categories of failures it will **not** catch.

---

## What `do/catch` Does Handle

Swift's error handling system catches errors thrown by functions declared with `throws`:

```swift
enum NetworkError: Error {
    case timeout
    case noConnection
}

func fetchData() throws -> Data {
    throw NetworkError.timeout
}

do {
    let data = try fetchData()
} catch NetworkError.timeout {
    print("Request timed out")
} catch {
    print("Other error: \(error)")
}
```

This works reliably for any Swift `Error`-conforming type that is explicitly thrown.

---

## What `do/catch` Will NOT Catch

### 1. Objective-C Exceptions (`NSException`)

This is the most common surprise for iOS developers. Objective-C exceptions (thrown via `@throw` or `NSException raise`) are **not** caught by Swift's `do/catch`. They use a completely different runtime mechanism.

Common sources of `NSException` in iOS:
- **Array/Dictionary out-of-bounds access** in `NSArray`, `NSDictionary`
- **Invalid `NSKeyValueCoding` keys** (e.g., `setValue:forKey:` with an unknown key)
- **Core Data faults** that fail to fulfill
- **Invalid `NSCoder` operations** (e.g., decoding a key that does not exist with a non-optional type)
- **UIKit threading violations** (accessing UI from a background thread can raise)
- **`NSInvalidArgumentException`** from passing `nil` where Objective-C expects non-nil
- **Storyboard/XIB issues** (missing outlets, unrecognized selectors)

Example that will crash despite `do/catch`:

```swift
do {
    let array = NSArray(array: [1, 2, 3])
    let _ = array.object(at: 10) // NSRangeException - NOT caught
} catch {
    print("This will never execute")
}
```

To catch Objective-C exceptions, you need an Objective-C wrapper:

```objc
// ObjCExceptionCatcher.h
@interface ObjCExceptionCatcher : NSObject
+ (BOOL)catchException:(void (^)(void))tryBlock error:(NSError **)error;
@end

// ObjCExceptionCatcher.m
@implementation ObjCExceptionCatcher
+ (BOOL)catchException:(void (^)(void))tryBlock error:(NSError **)error {
    @try {
        tryBlock();
        return YES;
    } @catch (NSException *exception) {
        if (error) {
            *error = [NSError errorWithDomain:exception.name
                                         code:0
                                     userInfo:exception.userInfo];
        }
        return NO;
    }
}
@end
```

### 2. Fatal Runtime Errors (Traps)

Swift deliberately makes certain programming errors unrecoverable. These call `fatalError` or trigger a trap and cannot be caught:

- **Force-unwrapping a nil optional**: `let x: String? = nil; print(x!)`
- **`fatalError()`, `preconditionFailure()`, `assertionFailure()`** (in non-debug builds for assert)
- **Array index out of bounds** on Swift `Array`: `let a = [1,2,3]; a[10]`
- **Forced cast failure**: `let x = someString as! Int`
- **Arithmetic overflow**: `Int.max + 1` (in non-optimized builds)
- **Stack overflow** from infinite recursion
- **Implicitly unwrapped optional** access when nil

These are treated as programmer errors and intentionally crash the process.

### 3. POSIX Signals

Low-level signals from the operating system are not caught by Swift error handling:

- **SIGSEGV** (segmentation fault / bad memory access)
- **SIGBUS** (bus error)
- **SIGABRT** (abort, often sent after an unhandled exception)
- **SIGKILL** (process killed by the OS, e.g., memory pressure / watchdog)
- **SIGPIPE** (broken pipe)
- **EXC_BAD_ACCESS** (accessing deallocated memory)

You can install signal handlers for some of these, but recovery is generally not possible or advisable.

### 4. Memory Issues

- **Out-of-memory (OOM)** conditions: iOS will terminate your app if it uses too much memory. There is no way to catch this.
- **EXC_BAD_ACCESS / zombie objects**: Accessing deallocated memory crashes immediately.

### 5. Watchdog Terminations

iOS enforces time limits for certain operations:
- App launch must complete within ~20 seconds
- Background tasks have strict time limits
- Extensions have memory and time limits

Exceeding these causes the system to kill your app with no opportunity to catch an error.

---

## Summary Table

| Error Type | Caught by `do/catch`? | Recovery Possible? |
|---|---|---|
| Swift `throws` errors | Yes | Yes |
| Objective-C `NSException` | **No** | Possible with ObjC wrapper |
| Force-unwrap nil (`!`) | **No** | No (fatal trap) |
| Swift array out-of-bounds | **No** | No (fatal trap) |
| `fatalError()` / `preconditionFailure()` | **No** | No |
| POSIX signals (SIGSEGV, etc.) | **No** | Generally no |
| OOM termination | **No** | No |
| Watchdog kill | **No** | No |

---

## Best Practices

1. **Prefer safe unwrapping** (`if let`, `guard let`, `??`) over force-unwrapping.
2. **Bounds-check arrays** before accessing by index, or use `.first`, `.last`, or safe subscript extensions.
3. **Use crash reporting tools** (e.g., Firebase Crashlytics, Sentry) to capture and diagnose unrecoverable crashes.
4. **Wrap Objective-C exception-prone code** with an ObjC try/catch bridge if you must call APIs known to throw `NSException`.
5. **Validate inputs** before passing them to Objective-C APIs.
6. **Monitor memory usage** and respond to `didReceiveMemoryWarning` to avoid OOM kills.
7. **Keep app launch fast** and background work within time limits to avoid watchdog terminations.

In summary, Swift's `do/catch` is designed only for recoverable, explicitly-thrown Swift errors. A significant portion of iOS app crashes come from Objective-C exceptions, fatal traps, and system-level terminations that require entirely different strategies to handle or prevent.
