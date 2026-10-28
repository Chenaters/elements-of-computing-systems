# Hack assembler

Two-pass assembler coursework. `hackAssembler.py` resolves labels and variables
and translates A/C instructions into 16-bit words.

```sh
python hackAssembler.py path/to/Program.asm
```

The output is `LouisProgram.hack` next to the input. The implementation is
educational: invalid computations can fall back to zero bits, and out-of-range
addresses are wrapped rather than rejected. Do not treat it as a strict validator.
`alternatives/hackAssemblerAI.py` preserves a separately AI-named variant;
that filename/provenance is retained rather than presenting it as the primary
independently authored implementation. Supplied assembly examples are not copied.
