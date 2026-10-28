# Standard Jack compiler and XML analyzer

Coursework implementing Jack tokenization, parsing, symbol tables and VM code generation. This is the standard-language precursor to the coroutine capstone.

From the collection root:

```sh
python jack-compiler/JackCompiler.py jack-coroutines/testFolders/Square
python jack-compiler/JackAnalyzer.py jack-coroutines/testFolders/Square
```

The compiler writes NameMy.vm and NameMy.xml next to each input; the analyzer writes NameMy.xml. Accepts one .jack file or a directory. The coroutine keywords require the extended compiler in jack-coroutines/, not this standard compiler.

The [original course-project guide](docs/ORIGINAL_README.md) references supplied test distributions that are excluded from this publication. Those tests and the official tools can be obtained separately. The supplied Square example is included only as a compatibility fixture.
