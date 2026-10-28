# Publication validation — October 28, 2026

The original student compiler/program sources were preserved without behavior
changes. Documentation and automated publication checks were added.

## Automated Python suite

`python -m unittest discover -s tests -v` ran 10 tests: **9 passed and 1 was an
expected failure documenting the known nonpersistent-local limitation**.

- Original single-coroutine demo: generated VM executed with the expected text.
- Original producer/consumer demo: generated VM alternated 10/20/30 correctly;
  calls after completion did not create extra consumer work.
- Separate objects retained independent fields and resume states.
- Repeated task calls after finish left the result unchanged.
- A yielding loop with a field counter progressed through 1, 2, 3 and finished.
- A local value written before yield was lost on the next call. The expected
  failure records this existing limitation, not successful local-state support.
- Standard Square compiled into VM and parseable XML.
- All five Tetris classes and eight OS classes compiled.
- The standard compiler entry point produced an executable arithmetic function.
- The assembler resolved a label and a variable to exact expected machine words.
- The small stack-machine exercise executed an arithmetic input correctly.

The coroutine execution tests use `tests/vm_runner.py`, a limited independent
Hack-VM instruction/function interpreter with tiny Memory/String/Output stubs.
It is not the official VM emulator, a graphical runtime, a full Jack OS, or proof
of complete compiler conformance. The suite was run with the available Python
3.14 runtime. Temporary artifacts were directed outside the published folder.

## Other checks

- A VM arithmetic/memory sample translated into 37 Hack assembly instructions;
  every computation mnemonic was recognized by the assembler, and all emitted
  machine words were 16-bit binary. This is a translation smoke check, not a full
  function-call or CPU execution validation.
- `gcc -std=c99 -Wall -Wextra -fsyntax-only systems-utilities/elfinfo.c` passed
  syntax checking with 64-bit printf format warnings on Windows. The historical
  parser assumes a compatible ELF64 layout and a local input named `wc` and lacks
  robust input validation; it was not executed on an external binary.
- Python syntax, relative Markdown links, prepared source credential patterns,
  private absolute paths and source hashes were checked before upload.

Java, Icarus Verilog and Verilator were not available on PATH. No official
Nand2Tetris emulator run, interactive Tetris gameplay, complete OS runtime suite,
HDL simulation, FPGA synthesis or board programming was performed.
