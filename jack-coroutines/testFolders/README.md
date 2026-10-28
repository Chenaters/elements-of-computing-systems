# Jack Compiler Test Suite

This folder contains baseline Jack tests and coroutine-extension tests used by this capstone compiler.

## Actual Test Folders

### `Square/` (baseline compatibility)
- `Main.jack`
- `Square.jack`
- `SquareGame.jack`

Purpose:
- Confirms standard Jack programs still compile correctly.

### `TestA_SimpleCoroutine/` (single coroutine)
- `Main.jack`
- `SimpleCounter.jack`

Purpose:
- Verifies `coroutine class`, `task`, `yield`, and `finish` in a simple flow.

### `TestB_MultiCoroutine/` (multiple coroutines)
- `Main.jack`
- `Producer.jack`
- `Consumer.jack`

Purpose:
- Verifies multiple coroutine instances can be stepped cooperatively.

## Running Tests

From the repository root:

```powershell
py .\JackCompiler.py .\testFolders\Square\
py .\JackCompiler.py .\testFolders\TestA_SimpleCoroutine\
py .\JackCompiler.py .\testFolders\TestB_MultiCoroutine\
```

Each run generates `.xml` and `.vm` files next to each `.jack` input file.

## Coroutine Feature Coverage

- `coroutine` keyword: marks a class as coroutine-enabled.
- `task` keyword: defines a resumable method-like routine.
- `yield;`: pauses execution and returns to caller.
- `finish;`: marks coroutine completed and returns.

## Known Limitation

`yield` may not work correctly in some `while`-loop patterns.

Why:
- Resume points are label-based, but local variables are not fully persisted across yields.
- Loop counters or temporary locals can lose intended state across task resumptions.

Recommendation:
- Use fields (object state) for values that must survive `yield` boundaries.