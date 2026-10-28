import sys


class Parser:
    """Parses commands from a .vm file and accesses components of command."""

    ARITHMETIC_COMMANDS = {
        "add",
        "sub",
        "neg",
        "eq",
        "lt",
        "gt",
        "and",
        "or",
        "not"}

    def __init__(self, fileName):
        self.fileName = fileName
        self.outputFileName = self.fileName.replace(".vm", ".asm")
        self.curInstruction = 0
        self.currentCommand = []
        # Read instructions from file
        try:
            with open(fileName, 'r') as f:
                content = f.read()
                instructs = content.splitlines()
                self.instructions = [
                    instr.strip() for instr in instructs
                    if instr.strip() and not instr.strip().startswith("//")
                ]
        except FileNotFoundError:
            print(f"Error: File '{fileName}' not found", file=sys.stderr)
            sys.exit(1)

    def hasMoreCommands(self):
        return self.curInstruction < len(self.instructions)

    def advance(self):
        if self.hasMoreCommands():
            instr = self.instructions[self.curInstruction]
            self.currentCommand = instr
            self.curInstruction += 1
            return instr
        else:
            return None

    def commandType(self):
        if self.currentCommand.startswith("push"):
            return "C_PUSH"
        elif self.currentCommand.startswith("pop"):
            return "C_POP"
        elif self.currentCommand.split()[0] in self.ARITHMETIC_COMMANDS:
            return "C_ARITHMETIC"
        elif self.currentCommand.startswith("label"):
            return "C_LABEL"
        elif self.currentCommand.startswith("goto"):
            return "C_GOTO"
        elif self.currentCommand.startswith("if-goto"):
            return "C_IF"
        elif self.currentCommand.startswith("function"):
            return "C_FUNCTION"
        elif self.currentCommand.startswith("call"):
            return "C_CALL"
        elif self.currentCommand.startswith("return"):
            return "C_RETURN"
        else:
            print(
                "Unknown command type for:",
                self.currentCommand,
                file=sys.stderr)
            return "INVALID"

    def arg1(self):
        if self.commandType() == "C_ARITHMETIC":
            return self.currentCommand.split()[0]
        elif self.commandType() in {"C_PUSH", "C_POP", "C_LABEL", "C_GOTO",
                                    "C_IF", "C_FUNCTION", "C_CALL"}:
            return self.currentCommand.split()[1]
        else:
            print(
                "arg1 called on invalid command type:",
                self.currentCommand,
                file=sys.stderr)
            return None

    def arg2(self):
        if self.commandType() in {"C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"}:
            return self.currentCommand.split()[2]
        else:
            print(
                "arg2 called on invalid command type:",
                self.currentCommand,
                file=sys.stderr)
            return None
