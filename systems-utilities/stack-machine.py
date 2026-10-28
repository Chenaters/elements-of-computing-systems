import sys

class Stack:
    
    def __init__(self, length):
        """Stack implementation with fixed size."""
        self.length = length
        self.values = [0 for _ in range(length)]
        self.curSpot = 0
    def push(self, value):
        """Pushes a value onto the stack."""
        if self.curSpot >= self.length:
            print("Error: Stack overflow", file=sys.stderr)
            sys.exit(1)
        self.values[self.curSpot] = value
        self.curSpot += 1
    def pop(self):
        """Pops a value off the stack and returns it."""
        if self.curSpot == 0:
            print("Error: Attempt to pop from empty stack", file=sys.stderr)
            sys.exit(1)
        self.curSpot -= 1
        return self.values[self.curSpot]

# Ensure extra argument is provided
try:
    fileName = sys.argv[1]
except IndexError:
    print("Error: No input file specified", file=sys.stderr)
    sys.exit(1)

# Read instructions from file
try:
    with open(fileName, 'r') as f:
        content = f.read()
        instructions = content.splitlines()
except FileNotFoundError:
    print(f"Error: File '{fileName}' not found", file=sys.stderr)
    sys.exit(1)

stack = Stack(len(instructions))
# Go through instructions
for i, instr in enumerate(instructions):
    vals = instr.split(" ")
    if vals[0] == "push" and len(vals) == 2:
        stack.push(int(vals[1]))
    elif vals[0] == "pop" and len(vals) == 1:
        stack.pop()
    elif vals[0] == "sub" and len(vals) == 1:
        b = stack.pop()
        a = stack.pop()
        stack.push(a - b)
    elif vals[0] == "add" and len(vals) == 1:
        b = stack.pop()
        a = stack.pop()
        stack.push(a + b)
    elif vals[0] == "mul" and len(vals) == 1:
        b = stack.pop()
        a = stack.pop()
        stack.push(a * b)
    elif vals[0] == "div" and len(vals) == 1:
        b = stack.pop()
        a = stack.pop()
        stack.push(a // b)
    else:
        print(f"Error: Unknown instruction '{instr}' at position {i}", file=sys.stderr)
        sys.exit(1)



print(stack.pop())

sys.exit(0)