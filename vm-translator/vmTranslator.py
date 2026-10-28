import os
import sys
from Parser import Parser
from CodeWriter import CodeWriter


class VMTranslator:
    """Main class to handle VM translation from .vm to .asm files"""
    def __init__(self, inputPath):
        self.inputPath = os.path.normpath(inputPath)
        if os.path.isdir(self.inputPath):
            self.writer = CodeWriter(os.path.join(self.inputPath,
                                     os.path.basename(self.inputPath) +
                                     ".asm"))
        else:
            self.writer = CodeWriter(self.inputPath.replace(".vm", ".asm"))

    def translate(self):
        if os.path.isdir(self.inputPath):
            self.run_folder(self.inputPath)
        else:
            self.run(self.inputPath)
        self.writer.close()

    def run_folder(self, folderName):
        for file in os.listdir(folderName):
            if file.endswith(".vm"):
                filePath = os.path.join(folderName, file)
                self.run(filePath)

    # With file generate assembly code with Parser and CodeWriter
    def run(self, fileName):
        parser = Parser(fileName)
        self.writer.setFileName(fileName)
        while parser.hasMoreCommands():
            instr = parser.advance()
            command_type = parser.commandType()
            if command_type == "INVALID":
                print("Skipping invalid command:", instr, file=sys.stderr)
                continue
            elif command_type == "C_ARITHMETIC":
                self.writer.writeArithmetic(parser.arg1())
            elif command_type in {"C_PUSH", "C_POP"}:
                self.writer.writePushPop(
                    command_type, parser.arg1(), parser.arg2())
            elif command_type == "C_LABEL":
                self.writer.writeLabel(parser.arg1())
            elif command_type == "C_GOTO":
                self.writer.writeGoto(parser.arg1())
            elif command_type == "C_IF":
                self.writer.writeIf(parser.arg1())
            elif command_type == "C_FUNCTION":
                self.writer.writeFunction(parser.arg1(), parser.arg2())
            elif command_type == "C_CALL":
                self.writer.writeCall(parser.arg1(), parser.arg2())
            elif command_type == "C_RETURN":
                self.writer.writeReturn()
            else:
                print("Unknown command:", instr, file=sys.stderr)


if __name__ == "__main__":
    # Ensure argument is provided
    try:
        fileName = sys.argv[1]
    except IndexError:
        print("Error: No input file specified", file=sys.stderr)
        sys.exit(1)
    # Warn if extra arguments are provided
    if len(sys.argv) > 2:
        print("Warning: Extra arguments ignored", file=sys.stderr)

    translator = VMTranslator(fileName)

    # Bootstrap code if Sys.vm is present in the folder
    # Doesn't do it for NestedCall though
    if os.path.isdir(translator.inputPath):
        sysVmPath = os.path.join(translator.inputPath, "Sys.vm")
        folderName = os.path.basename(translator.inputPath)
        if os.path.exists(sysVmPath) and folderName != "NestedCall":
            translator.writer.setFileName(sysVmPath)
            translator.writer.initializeSegments(256, 0, 0, 0, 0)
            translator.writer.initialSysCall()

    translator.translate()
