class VMWriter:

    def __init__(self, outputFile):
        self.outputFile = open(outputFile, "w", newline="\n")

    def writePush(self, segment, index):
        """Writes a VM push command.
        Args:
            segment: constant, argument, local, static, this, that, pointer, or temp.
            index: The index within the segment to push.
        """
        self.outputFile.write(f"    push {segment} {index}\n")

    def writePop(self, segment, index):
        """Writes a VM pop command.
        Args:
            segment: argument, local, static, this, that, pointer, or temp.
            index: The index within the segment to pop.
        """
        self.outputFile.write(f"    pop {segment} {index}\n")

    def writeArithmetic(self, command):
        self.outputFile.write(f"    {command}\n")

    def writeLabel(self, label):
        self.outputFile.write(f"label {label}\n")

    def writeGoto(self, label):
        self.outputFile.write(f"    goto {label}\n")

    def writeIf(self, label):
        self.outputFile.write(f"    if-goto {label}\n")

    def writeCall(self, name, nArgs):
        self.outputFile.write(f"    call {name} {nArgs}\n")

    def writeFunction(self, name, nVars):
        self.outputFile.write(f"function {name} {nVars}\n")

    def writeReturn(self):
        self.outputFile.write("    return\n")

    def close(self):
        # Match the reference VM files, which do not end with a trailing newline.
        self.outputFile.flush()
        current_pos = self.outputFile.tell()
        if current_pos > 0:
            self.outputFile.seek(current_pos - 1)
            self.outputFile.truncate()
        self.outputFile.close()
