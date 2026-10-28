class VMWriter:

    def __init__(self, outputFile):
        self.outputFile = open(outputFile, "w", newline="\n")
        self._buffers = []

    def _write_line(self, line):
        if self._buffers:
            self._buffers[-1].append(line)
        else:
            self.outputFile.write(line + "\n")

    def beginBuffer(self):
        self._buffers.append([])

    def endBuffer(self):
        if not self._buffers:
            return []
        return self._buffers.pop()

    def writeBuffered(self, lines):
        for line in lines:
            self._write_line(line)

    def writePush(self, segment, index):
        """Writes a VM push command.
        Args:
            segment: constant, argument, local, static, this, that, pointer, or temp.
            index: The index within the segment to push.
        """
        self._write_line(f"    push {segment} {index}")

    def writePop(self, segment, index):
        """Writes a VM pop command.
        Args:
            segment: argument, local, static, this, that, pointer, or temp.
            index: The index within the segment to pop.
        """
        self._write_line(f"    pop {segment} {index}")

    def writeArithmetic(self, command):
        self._write_line(f"    {command}")

    def writeLabel(self, label):
        self._write_line(f"label {label}")

    def writeGoto(self, label):
        self._write_line(f"    goto {label}")

    def writeIf(self, label):
        self._write_line(f"    if-goto {label}")

    def writeCall(self, name, nArgs):
        self._write_line(f"    call {name} {nArgs}")

    def writeFunction(self, name, nVars):
        self._write_line(f"function {name} {nVars}")

    def writeReturn(self):
        self._write_line("    return")

    def close(self):
        # Match the reference VM files, which do not end with a trailing newline.
        self.outputFile.flush()
        current_pos = self.outputFile.tell()
        if current_pos > 0:
            self.outputFile.seek(current_pos - 1)
            self.outputFile.truncate()
        self.outputFile.close()
