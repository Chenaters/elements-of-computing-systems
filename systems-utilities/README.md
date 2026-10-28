# Small systems exercises

`stack-machine.py` executes push/pop/add/sub/mul/div instructions from a text
file and prints the final top-of-stack value:

```sh
python stack-machine.py instructions.txt
```

`elfinfo.c` is a historical ELF-header inspection exercise. It opens a file
named `wc` in the working directory. It assumes a compatible ELF64 file/host
layout and lacks robust length/magic/file-open validation. It is source coursework,
not a general-purpose binary parser. The original executable/input binaries
are excluded. With a C compiler, build in a separate output directory:

```sh
gcc -std=c99 -Wall -Wextra elfinfo.c -o elfinfo
```
