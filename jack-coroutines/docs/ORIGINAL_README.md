# JackCompiler

Jack compiler for the Nand2Tetris Jack language, with XML parse output and VM code generation.

The compiler supports standard Jack plus these coroutine extensions:
- `coroutine` (class modifier)
- `task` (subroutine kind)
- `yield` (pause and resume point)
- `finish` (mark coroutine instance complete)

## Repository Layout

Top-level source files:
- `JackCompiler.py`
- `CompilationEngine.py`
- `JackTokenizer.py`
- `SymbolTable.py`
- `VMWriter.py`

Test content:
- `testFolders/Square/`
- `testFolders/TestA_SimpleCoroutine/`
- `testFolders/TestB_MultiCoroutine/`
- `testFolders/README.md`
- `testFolders/TEST_REFERENCE.md`

## How To Run

You can compile either one `.jack` file or an entire directory.

For each input file `FileName.jack`, the compiler writes:
- `FileName.xml`
- `FileName.vm`

### Compile one Jack file

```powershell
py .\JackCompiler.py .\testFolders\Square\Main.jack
```

### Compile all Jack files in a folder

```powershell
py .\JackCompiler.py .\testFolders\Square\
```

## Coroutine Feature Notes

- A `coroutine class` is declared as `coroutine class Name { ... }`.
- `task` subroutines are compiled as resumable step functions using internal state.
- `yield;` saves the next resume state and returns immediately.
- `finish;` marks the coroutine as finished and returns.

Internal fields automatically added to coroutine classes:
- `__state` (resume point tracking)
- `__finished` (completion flag)

## Current Limitation: `yield` in loops

`yield` inside `while` loops may not behave as expected in all programs.

Reason:
- Task methods currently resume by jumping to saved labels, but local variable lifetime across yields is not fully lifted into persistent object state.
- If a loop depends on locals that should survive across yields (for example loop counters or temporary control values), the resumed execution can observe incorrect state.

Practical guidance:
- Prefer fields for values that must persist across `yield` boundaries.
- Be cautious with `yield` inside loops, especially when loop progress depends on local variables.

