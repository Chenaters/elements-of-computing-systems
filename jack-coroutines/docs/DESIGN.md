# Coroutine implementation notes

The extension is split across existing compiler components:

| Component | Extension |
| --- | --- |
| JackTokenizer.py | Recognizes coroutine, task, yield and finish as keywords |
| CompilationEngine.compileClass | Accepts the coroutine modifier and injects __state and __finished fields |
| CompilationEngine.compileSubroutineDec | Accepts task name(args), with an implicit receiver argument |
| CompilationEngine.compileSubroutineBody | Buffers task VM output so dispatch can be emitted after collecting resume labels |
| CompilationEngine._emit_task_dispatch | Checks the finished flag and branches to the initial or saved resume point |
| CompilationEngine.compileYield | Saves the next state, emits return, then emits the resume label |
| CompilationEngine.compileFinish | Sets completion, resets the state field, and returns |
| VMWriter.py | Buffers and flushes generated task instructions |

## State transition example

For a task with two yields, the first call runs state 0 to yield 1. The second
call dispatches to state 1 and runs to yield 2. The third dispatches to state 2
and reaches finish. Later calls see the completed flag and return immediately.
Each constructor initializes its object's hidden fields independently.

The task call frame is not suspended: it returns. Its locals and previous
arguments are not retained. The object is the persistent continuation state.
This makes fields appropriate for counters/accumulators that cross yields.
There is one state/completion pair per object rather than one pair per task.

## Preservation and scope

The original compiler source is copied without behavior changes. The publication
adds documentation and automated checks. The proposal's illustrative `task void
run()` differs from the implemented grammar; runnable examples use `task run()`.
Tests explicitly record the known local-variable persistence limitation.
The provided producer/consumer demonstrates cooperative execution; it does not
provide a queue or a separate scheduler runtime.
