# Elements of Computing Systems

Computer systems coursework and projects by Louis Chen, built while studying
Elements of Computing Systems. The lead project extends the Jack
language with cooperative coroutines and a `yield` statement.

## Featured: adding yield to Jack

[Jack coroutine compiler](jack-coroutines/README.md) extends the tokenizer,
parser and VM-code generator with `coroutine`, `task`, `yield` and `finish`.
Tasks compile into resumable state machines using object fields and VM labels.
The calling Jack program schedules tasks by invoking them cooperatively.

```jack
coroutine class Counter {
    field int value;
    constructor Counter new() {
        let value = 0;
        return this;
    }
    task step() {
        let value = value + 1;
        yield;
        let value = value + 1;
        finish;
    }
}
```

This is a course compiler extension, not a production coroutine runtime.
Locals do not persist across yields, and one state/finished pair is shared by
all tasks on an object. See the [design and limitations](jack-coroutines/docs/DESIGN.md).

## Project collection

| Folder | Work included |
| --- | --- |
| [jack-coroutines](jack-coroutines/) | Custom yield/coroutine compiler extension, original single/multiple coroutine demos, design notes |
| [jack-compiler](jack-compiler/) | Standard Jack tokenizer, XML analyzer, symbol tables and VM compiler |
| [hack-assembler](hack-assembler/) | Two-pass Hack assembler; separately labeled alternate AI-named source |
| [vm-translator](vm-translator/) | Hack VM arithmetic, memory segments, branching and function-call translation |
| [jack-tetris](jack-tetris/) | Tetris implementation in Jack: board, blocks, shapes and game loop |
| [jack-os](jack-os/) | Coursework implementations in the supplied Jack OS class interfaces |
| [fpga](fpga/) | VGA graphics/snake, shift register, switch logic, board constraints and source testbenches |
| [systems-utilities](systems-utilities/) | Small stack-machine interpreter and ELF-header inspection exercise |

## Run the coroutine examples

Python 3.10+ is sufficient for the compiler and automated Python checks; no
third-party Python dependencies are needed.

```sh
python jack-coroutines/JackCompiler.py jack-coroutines/testFolders/TestA_SimpleCoroutine
python jack-coroutines/JackCompiler.py jack-coroutines/testFolders/TestB_MultiCoroutine
python -m unittest discover -s tests -v
```

Compilation writes `.vm` and `.xml` next to the Jack input. For the original
graphical demos, obtain the Nand2Tetris VM emulator separately and load the
generated VM files. Automated tests use a small, explicitly limited VM execution
harness for the coroutine output; they are not a replacement for that emulator.

## Credits and validation

These are educational implementations built around the Nand2Tetris course
interfaces and supplied examples. Original upstream headers are retained;
provided examples are labeled in [SOURCE_NOTES.md](SOURCE_NOTES.md). The custom
coroutine extension is the capstone focus. No blanket license is assigned to
course or third-party material by this collection.

See [VALIDATION.md](VALIDATION.md) for what was exercised and what remains
unverified. Original coursework folders remain unchanged. Tools, archives,
compiled binaries, generated VM/XML, build caches and private paths are excluded.
