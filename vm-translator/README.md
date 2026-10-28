# Hack VM translator

Coursework translating Hack VM stack operations, memory segments, control flow,
function calls and returns to Hack assembly.

```sh
python vmTranslator.py path/to/Program.vm
python vmTranslator.py path/to/ProgramFolder
```

File output replaces `.vm` with `.asm`; folder output uses the folder name.
The existing driver adds bootstrap code for a folder containing Sys.vm, except
for its special-cased NestedCall fixture. File naming and label scoping are
historical implementation details; the limited smoke test does not establish
full VM specification conformance. See docs/ORIGINAL_README.md.
