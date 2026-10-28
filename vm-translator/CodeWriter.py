import sys
from AssemblyHelper import AssemblyHelper


class CodeWriter:
    """CodeWriter class to handle writing assembly code to output file"""
    SEGMENTS = {
        "local": "LCL",
        "argument": "ARG",
        "this": "THIS",
        "that": "THAT"}

    def __init__(self, outputFile=None):
        self.outputFileName = outputFile
        self.file = open(self.outputFileName, 'w')
        self.original_stdout = sys.stdout
        sys.stdout = self.file
        self.counter = 0  # TODO: Ensure this doesn't 
        # need to be reset for each function

    def setFileName(self, fileName):
        self.curTranslate = fileName
        self.directFileName = fileName.split("\\")[-1].replace(".asm", "")

    def writeArithmetic(self, command):
        if command == "add":
            AssemblyHelper.add()
        elif command == "sub":
            AssemblyHelper.sub()
        elif command == "neg":
            AssemblyHelper.neg()
        elif command == "eq":
            AssemblyHelper.eq()
        elif command == "lt":
            AssemblyHelper.lt()
        elif command == "gt":
            AssemblyHelper.gt()
        elif command == "not":
            AssemblyHelper.nots()
        elif command == "and":
            AssemblyHelper.ands()
        elif command == "or":
            AssemblyHelper.ors()
        else:
            print("Unknown command:", command, file=sys.stderr)

    def writePushPop(self, command, segment, index):
        if command == "C_PUSH":
            if segment == "constant":
                AssemblyHelper.push(index)
            elif segment in {"local", "argument", "this", "that"}:
                AssemblyHelper.memoryPush(self.SEGMENTS[segment], index)
            elif segment in {"temp", "pointer"}:
                AssemblyHelper.tpPush(segment, index)
            elif segment == "static":
                AssemblyHelper.staticPush(self.directFileName, index)
            else:
                print("Unknown segment:", segment, file=sys.stderr)
        elif command == "C_POP":
            if segment in {"local", "argument", "this", "that"}:
                AssemblyHelper.memoryPop(self.SEGMENTS[segment], index)
            elif segment in {"temp", "pointer"}:
                AssemblyHelper.tpPop(segment, index)
            elif segment == "static":
                AssemblyHelper.staticPop(self.directFileName, index)
            else:
                print("Unknown segment:", segment, file=sys.stderr)
        else:
            print("Unknown command:", command, file=sys.stderr)

    # TODO: Fix labelling naming
    def writeLabel(self, label):
        AssemblyHelper.writeLabel(self.directFileName, label=label)

    # TODO: Fix labelling naming
    def writeGoto(self, label):
        AssemblyHelper.writeGoto(self.directFileName, label=label)

    # TODO: Fix labelling naming
    def writeIf(self, label):
        AssemblyHelper.writeIf(self.directFileName, label=label)

    def writeFunction(self, functionName, nVars):
        AssemblyHelper.writeFunction(functionName, int(nVars))

    def writeCall(self, functionName, nArgs):
        self.counter += 1
        AssemblyHelper.writeCall(functionName, int(nArgs), self.counter)

    def writeReturn(self):
        AssemblyHelper.writeReturn()

    def initializeSegments(self, SP, LCL, ARG, THIS, THAT):
        AssemblyHelper.initializeSegments(SP, LCL, ARG, THIS, THAT)

    def initialSysCall(self):
        self.writeCall("Sys.init", 0)

    def close(self):
        sys.stdout = self.original_stdout
        self.file.close()
