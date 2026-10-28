# Test Suite Reference Guide

## Quick Test Summary

| Test Category | Files | Purpose | Features Tested |
|---|---|---|---|
| Backward Compatibility | `Square/` | Verify existing programs still work | Traditional Jack behavior |
| Coroutine: Simple | `TestA_SimpleCoroutine/Main.jack`, `TestA_SimpleCoroutine/SimpleCounter.jack` | Single coroutine progression | `coroutine`, `task`, `yield`, `finish` |
| Coroutine: Multiple | `TestB_MultiCoroutine/Main.jack`, `TestB_MultiCoroutine/Producer.jack`, `TestB_MultiCoroutine/Consumer.jack` | Cooperative scheduling across multiple coroutines | Independent state tracking and resume behavior |

## Test Execution Commands

```powershell
py .\JackCompiler.py .\testFolders\Square\
py .\JackCompiler.py .\testFolders\TestA_SimpleCoroutine\
py .\JackCompiler.py .\testFolders\TestB_MultiCoroutine\
```

## Coroutine Notes

- `task` functions run as resumable coroutine steps.
- `yield;` pauses and returns control to the caller.
- `finish;` marks the coroutine complete and returns.

## Important Limitation: `yield` in loops

`yield` inside `while` loops may not always behave correctly.

Cause:
- Current implementation does not fully persist local variables across `yield` boundaries.
- Loop variables stored as locals can be reset or become inconsistent after resume.

Guidance:
- Store loop-critical state in fields if it must persist across yields.
- Keep `yield` usage in loops simple and validate generated behavior.