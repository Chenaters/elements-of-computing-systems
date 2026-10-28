# Jack Coroutine Compiler: yield and resume

A capstone extension to the Jack compiler. It adds cooperative, resumable
tasks while continuing to emit ordinary Hack VM code and an XML parse tree.

## Added syntax

- `coroutine class Name { ... }` enables hidden state fields.
- `task step(...) { ... }` declares a method-like step routine. There is **no
  return-type token** after `task` in this implementation.
- `yield;` records a resume label and returns to the caller.
- `finish;` marks the object finished and returns; later task calls do no work.

The caller supplies the scheduler by alternating task calls. The extension does
not create threads, preempt tasks, or provide automatic scheduling.

## Run

From this folder:

```sh
python JackCompiler.py testFolders/TestA_SimpleCoroutine
python JackCompiler.py testFolders/TestB_MultiCoroutine
python JackCompiler.py testFolders/Square
```

Or compile one `.jack` file. Each input produces matching `.vm` and `.xml`
files. Load the generated directory in the Nand2Tetris VM emulator to run a
graphical/text demonstration. The standard Jack compiler cannot compile the
new coroutine keywords; use this extended compiler.

The [single-coroutine demo](testFolders/TestA_SimpleCoroutine/) advances through
three segments. The [producer/consumer demo](testFolders/TestB_MultiCoroutine/)
alternates two coroutine objects and checks their field state. Square is the
supplied standard-language compatibility example, not an original game here.

## How it works

The compiler injects `__state` and `__finished` fields into each coroutine
instance. A task's generated entry checks completion, then dispatches on
`__state`. At a yield, generated code stores the next state and returns zero.
The next call enters a fresh VM frame and jumps to the matching resume label.

See [DESIGN.md](docs/DESIGN.md), the [original proposal](docs/PROJECT_PROPOSAL.md),
and the [original project guide](docs/ORIGINAL_README.md).

## Current limits

Persistent values must be fields: local variables are fresh on each task call.
Yielding loops that depend on locals are therefore unreliable. Arguments must
be supplied again by the caller. All tasks in one coroutine object share one
state/completion pair, so use one resumable task per object. Use explicit
`finish;` to end a task: falling off the body does not set the finished flag.
`yield` outside a coroutine task currently returns immediately rather than
reporting a syntax error. These behaviors are documented, not silently fixed
for publication. Compilation and selected execution tests do not establish
complete Jack-language conformance.
