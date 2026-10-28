import os
import sys
from CompilationEngine import CompilationEngine
from SymbolTable import SymbolTable
from VMWriter import VMWriter


def compileFile(input_file, output_file):
    output_path = input_file.replace('.jack', '')
    compiler_engine = CompilationEngine(input_file, output_path)
    compiler_engine.compileClass()

def main():
    if len(sys.argv) != 2:
        print("Usage: python JackCompiler.py <input_file_or_directory>")
        return

    input_path = sys.argv[1]

    if os.path.isdir(input_path):
        jack_files = sorted(
            file_name
            for file_name in os.listdir(input_path)
            if file_name.lower().endswith('.jack')
        )

        if not jack_files:
            print("No .jack files found in directory.")
            return

        for file_name in jack_files:
            full_path = os.path.join(input_path, file_name)
            compileFile(full_path, full_path.replace('.jack', ''))
            print(full_path)
        return

    if input_path.lower().endswith('.jack') and os.path.isfile(input_path):
        compileFile(input_path, input_path.replace('.jack', ''))
        print(input_path)
        return

    print("Input must be a .jack file or a directory containing .jack files.")


if __name__ == "__main__":
    main()
