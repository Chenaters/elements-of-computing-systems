class AssemblyHelper:
    """Helper class for generating Hack assembly code for VM commands."""
    @staticmethod
    def incSP():
        print("@SP")
        print("M=M+1")

    @staticmethod
    def decSP():
        print("@SP")
        print("M=M-1")

    # Pop instructions
    @staticmethod
    def pop():
        AssemblyHelper.decSP()
        print("A=M")
        print("D=M")

    # Push instructions
    @staticmethod
    def push(val):
        print(f"@{val}")
        print("D=A")
        print("@SP")
        print("A=M")
        print("M=D")
        AssemblyHelper.incSP()

    # Nine arithmetic operations

    @staticmethod
    def add():
        AssemblyHelper.pop()
        AssemblyHelper.decSP()
        print("A=M")
        print("M=D+M")
        AssemblyHelper.incSP()

    @staticmethod
    def sub():
        AssemblyHelper.pop()
        AssemblyHelper.decSP()
        print("A=M")
        print("M=M-D")
        AssemblyHelper.incSP()

    eq_label_counter = 0
    lt_label_counter = 0
    gt_label_counter = 0

    @staticmethod
    def eq():
        AssemblyHelper.pop()
        AssemblyHelper.decSP()
        print("A=M")
        print("D=M-D")
        print(f"@EQ_TRUE{AssemblyHelper.eq_label_counter}")
        print("D;JEQ")
        print("@SP")
        print("A=M")
        print("M=0")
        print(f"@EQ_END{AssemblyHelper.eq_label_counter}")
        print("0;JMP")
        print(f"(EQ_TRUE{AssemblyHelper.eq_label_counter})")
        print("@SP")
        print("A=M")
        print("M=-1")
        print(f"@EQ_END{AssemblyHelper.eq_label_counter}")
        print("0;JMP")
        print(f"(EQ_END{AssemblyHelper.eq_label_counter})")
        AssemblyHelper.incSP()
        AssemblyHelper.eq_label_counter += 1

    @staticmethod
    def lt():
        AssemblyHelper.pop()
        AssemblyHelper.decSP()
        print("A=M")
        print("D=M-D")
        print(f"@LT_TRUE{AssemblyHelper.lt_label_counter}")
        print("D;JLT")
        print("@SP")
        print("A=M")
        print("M=0")
        print(f"@LT_END{AssemblyHelper.lt_label_counter}")
        print("0;JMP")
        print(f"(LT_TRUE{AssemblyHelper.lt_label_counter})")
        print("@SP")
        print("A=M")
        print("M=-1")
        print(f"@LT_END{AssemblyHelper.lt_label_counter}")
        print("0;JMP")
        print(f"(LT_END{AssemblyHelper.lt_label_counter})")
        AssemblyHelper.incSP()
        AssemblyHelper.lt_label_counter += 1

    @staticmethod
    def gt():
        AssemblyHelper.pop()
        AssemblyHelper.decSP()
        print("A=M")
        print("D=M-D")
        print(f"@GT_TRUE{AssemblyHelper.gt_label_counter}")
        print("D;JGT")
        print("@SP")
        print("A=M")
        print("M=0")
        print(f"@GT_END{AssemblyHelper.gt_label_counter}")
        print("0;JMP")
        print(f"(GT_TRUE{AssemblyHelper.gt_label_counter})")
        print("@SP")
        print("A=M")
        print("M=-1")
        print(f"@GT_END{AssemblyHelper.gt_label_counter}")
        print("0;JMP")
        print(f"(GT_END{AssemblyHelper.gt_label_counter})")
        AssemblyHelper.incSP()
        AssemblyHelper.gt_label_counter += 1

    @staticmethod
    def neg():
        AssemblyHelper.pop()
        print("M=-D")
        AssemblyHelper.incSP()

    @staticmethod
    def nots():
        AssemblyHelper.pop()
        print("M=!D")
        AssemblyHelper.incSP()

    @staticmethod
    def ands():
        AssemblyHelper.pop()
        AssemblyHelper.decSP()
        print("A=M")
        print("M=D&M")
        AssemblyHelper.incSP()

    @staticmethod
    def ors():
        AssemblyHelper.pop()
        AssemblyHelper.decSP()
        print("A=M")
        print("M=D|M")
        AssemblyHelper.incSP()

    # Push for local, argument, this, that
    @staticmethod
    def memoryPush(seg, index):
        print(f"@{seg}")
        print("D=M")
        print(f"@{index}")
        print("A=D+A")
        print("D=M")
        print("@SP")
        print("A=M")
        print("M=D")
        AssemblyHelper.incSP()

    # Pop for local, argument, this, that
    @staticmethod
    def memoryPop(seg, index):
        print(f"@{seg}")
        print("D=M")
        print(f"@{index}")
        print("D=D+A")
        print("@R13")
        print("M=D")  # R13 holds the target address
        AssemblyHelper.decSP()
        print("A=M")
        print("D=M")
        print("@R13")
        print("A=M")
        print("M=D")

    # Push for temp and pointer
    @staticmethod
    def tpPush(tp, index):
        print(f"@{index}")
        print("D=A")
        if tp == "pointer":
            print("@3")
        else:  # temp
            print("@5")
        print("A=D+A")
        print("D=M")
        print("@SP")
        print("A=M")
        print("M=D")
        AssemblyHelper.incSP()

    # Pop for temp and pointer
    @staticmethod
    def tpPop(tp, index):
        print(f"@{index}")
        print("D=A")
        if tp == "pointer":
            print("@3")
        else:  # temp
            print("@5")
        print("D=D+A")
        print("@R13")
        print("M=D")  # R13 holds the target address
        AssemblyHelper.decSP()
        print("A=M")
        print("D=M")
        print("@R13")
        print("A=M")
        print("M=D")

    @staticmethod
    def staticPush(fileName, index):
        print(f"@{fileName}.{index}")
        print("D=M")
        print("@SP")
        print("A=M")
        print("M=D")
        AssemblyHelper.incSP()

    @staticmethod
    def staticPop(fileName, index):
        print(f"@{fileName}.{index}")
        print("D=A")
        print("@R13")
        print("M=D")  # R13 holds the target address
        AssemblyHelper.decSP()
        print("A=M")
        print("D=M")
        print("@R13")
        print("A=M")
        print("M=D")

    @staticmethod
    def writeLabel(fileName, label, command=""):
        print(f"({fileName}.{command}${label})")

    @staticmethod
    def writeGoto(fileName, label, command=""):
        print(f"@{fileName}.{command}${label}")
        print("0;JMP")

    @staticmethod
    def writeIf(fileName, label, command=""):
        print("@SP")
        print("AM=M-1")
        print("D=M")
        print(f"@{fileName}.{command}${label}")
        print("D;JNE")

    @staticmethod
    def writeFunction(functionName, nVars):
        print(f"({functionName})")
        for _ in range(nVars):
            AssemblyHelper.push(0)

    @staticmethod
    def writeCall(functionName, nArgs, counter):
        # Push return address
        print(f"@{functionName}$ret.{counter}")
        print("D=A")
        print("@SP")
        print("A=M")
        print("M=D")
        AssemblyHelper.incSP()
        # Push LCL, ARG, THIS, THAT
        for seg in ["LCL", "ARG", "THIS", "THAT"]:
            print(f"@{seg}")
            print("D=M")
            print("@SP")
            print("A=M")
            print("M=D")
            AssemblyHelper.incSP()
        # Reposition ARG
        print("@SP")
        print("D=M")
        print("@5")
        print("D=D-A")
        print(f"@{nArgs}")
        print("D=D-A")
        print("@ARG")
        print("M=D")
        # Reposition LCL
        print("@SP")
        print("D=M")
        print("@LCL")
        print("M=D")
        # Goto function
        print(f"@{functionName}")
        print("0;JMP")
        print(f"({functionName}$ret.{counter})")

    @staticmethod
    def writeReturn():
        # FRAME = LCL
        print("@LCL")
        print("D=M")
        print("@R14")
        print("M=D")  # R14 = FRAME
        # RET = *(FRAME-5)
        print("@5")
        print("A=D-A")
        print("D=M")
        print("@R15")
        print("M=D")  # R15 = RET
        # *ARG = pop()
        AssemblyHelper.pop()
        print("@ARG")
        print("A=M")
        print("M=D")
        # SP = ARG + 1
        print("@ARG")
        print("D=M+1")
        print("@SP")
        print("M=D")
        # THAT = *(FRAME-1)
        print("@R14")
        print("AM=M-1")
        print("D=M")
        print("@THAT")
        print("M=D")
        # THIS = *(FRAME-2)
        print("@R14")
        print("AM=M-1")
        print("D=M")
        print("@THIS")
        print("M=D")
        # ARG = *(FRAME-3)
        print("@R14")
        print("AM=M-1")
        print("D=M")
        print("@ARG")
        print("M=D")
        # LCL = *(FRAME-4)
        print("@R14")
        print("AM=M-1")
        print("D=M")
        print("@LCL")
        print("M=D")
        # goto RET
        print("@R15")
        print("A=M")
        print("0;JMP")

    @staticmethod
    def initializeSegments(SP, LCL, ARG, THIS, THAT):
        print(f"@{SP}")
        print("D=A")
        print("@SP")
        print("M=D")
        print(f"@{LCL}")
        print("D=A")
        print("@LCL")
        print("M=D")
        print(f"@{ARG}")
        print("D=A")
        print("@ARG")
        print("M=D")
        print(f"@{THIS}")
        print("D=A")
        print("@THIS")
        print("M=D")
        print(f"@{THAT}")
        print("D=A")
        print("@THAT")
        print("M=D")
