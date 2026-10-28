# JackCompiler

This project uses the VMWriter, SymbolTable, JackTokenizer, and CompilationEngine to give a vm file output.

## Run

Can be run on a single jack file or a folder.

The output is written in the same folder as the input `.jack` file.

For each input file `FileName.jack`, the compiler creates:

- `FileNameMy.xml`
- `FileNameMy.vm`

Examples:

- `Main.jack` -> `MainMy.xml` + `MainMy.vm`

### Compile one Jack file

```powershell
py .\JackCompiler.py .\11\Square\Main.jack
```

### Compile all Jack files in a folder

```powershell
py .\JackCompiler.py .\11\Square\
```


# Jack Analyzer

This project implements a jack code tokenizer and parser. 
The analyzer uses both these tools to output a parsed XML file from jack code input.

## Run

Can be run on a single jack file or a folder.

The output is written in the same folder as the input `.jack` file.

For each input file `FileName.jack`, the analyzer creates:

- `FileNameMy.xml`

Examples:

- `Main.jack` -> `MainMy.xml`
- `SquareGame.jack` -> `SquareGameMy.xml`

### Analyze one Jack file

```powershell
py .\JackAnalyzer.py .\10\Square\Main.jack
```

### Analyze all Jack files in a folder

```powershell
py .\JackAnalyzer.py .\10\Square\
```


