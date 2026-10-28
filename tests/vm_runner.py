"""Limited Hack VM execution harness for coroutine regression tests.

Implements instruction/function semantics and tiny Memory/String/Output stubs.
It is not the Nand2Tetris emulator, a hardware model, or a complete Jack OS.
Unknown operations/builtins fail instead of silently succeeding.
"""
from collections import defaultdict


def word(value):
    value &= 0xffff
    return value - 0x10000 if value & 0x8000 else value


class VM:
    def __init__(self, paths):
        self.functions = {}
        self.ram = defaultdict(int)
        self.static = defaultdict(int)
        self.temp = [0] * 8
        self.strings = {}
        self.heap = 2048
        self.output = []
        self.steps = 0
        for path in paths:
            current = None
            for line in path.read_text().splitlines():
                tokens = line.split('//', 1)[0].split()
                if not tokens:
                    continue
                if tokens[0] == 'function':
                    current = {'file': path.stem, 'locals': int(tokens[2]),
                               'code': [], 'labels': {}}
                    if tokens[1] in self.functions:
                        raise ValueError('Duplicate VM function: ' + tokens[1])
                    self.functions[tokens[1]] = current
                else:
                    if current is None:
                        raise ValueError('Instruction outside a VM function')
                    if tokens[0] == 'label':
                        current['labels'][tokens[1]] = len(current['code'])
                    current['code'].append(tokens)

    def allocate(self, size):
        address = self.heap
        self.heap += max(1, size)
        for offset in range(max(1, size)):
            self.ram[address + offset] = 0
        return address

    def builtin(self, name, args):
        if name in ('Memory.alloc', 'Array.new'):
            return self.allocate(args[0])
        if name in ('Memory.deAlloc', 'Array.dispose'):
            return 0
        if name == 'String.new':
            address = self.allocate(args[0] + 2)
            self.strings[address] = ''
            return address
        if name == 'String.appendChar':
            self.strings[args[0]] += chr(args[1])
            return args[0]
        if name == 'Output.printString':
            self.output.append(self.strings[args[0]])
            return 0
        if name == 'Output.printInt':
            self.output.append(str(args[0]))
            return 0
        if name == 'Output.println':
            self.output.append('\n')
            return 0
        if name == 'Math.multiply':
            return word(args[0] * args[1])
        if name == 'Math.divide':
            return word(int(args[0] / args[1]))
        raise NotImplementedError('Unsupported VM builtin: ' + name)

    def invoke(self, name, args=()):
        if name not in self.functions:
            return self.builtin(name, args)
        fn = self.functions[name]
        local, argument = [0] * fn['locals'], list(args)
        pointer = [0, 0]
        stack = []
        pc = 0
        while pc < len(fn['code']):
            self.steps += 1
            if self.steps > 200_000:
                raise RuntimeError('VM execution step limit exceeded')
            op, *operands = fn['code'][pc]
            pc += 1
            if op in ('push', 'pop'):
                segment, index = operands[0], int(operands[1])
                if segment == 'constant':
                    if op != 'push':
                        raise ValueError('Cannot pop to constant')
                    stack.append(word(index))
                    continue
                if segment in ('local', 'argument', 'pointer', 'temp'):
                    storage = {'local': local, 'argument': argument,
                               'pointer': pointer, 'temp': self.temp}[segment]
                    key = index
                elif segment in ('this', 'that'):
                    storage = self.ram
                    key = pointer[segment == 'that'] + index
                elif segment == 'static':
                    storage, key = self.static, (fn['file'], index)
                else:
                    raise NotImplementedError(segment)
                if op == 'push':
                    stack.append(storage[key])
                else:
                    storage[key] = word(stack.pop())
            elif op in ('add', 'sub', 'eq', 'lt', 'gt', 'and', 'or'):
                b, a = stack.pop(), stack.pop()
                result = {'add': lambda: a+b, 'sub': lambda: a-b,
                          'eq': lambda: -int(a == b), 'lt': lambda: -int(a < b),
                          'gt': lambda: -int(a > b), 'and': lambda: a & b,
                          'or': lambda: a | b}[op]()
                stack.append(word(result))
            elif op in ('neg', 'not'):
                a = stack.pop()
                stack.append(word(-a if op == 'neg' else ~a))
            elif op == 'label':
                pass
            elif op == 'goto':
                pc = fn['labels'][operands[0]]
            elif op == 'if-goto':
                if stack.pop():
                    pc = fn['labels'][operands[0]]
            elif op == 'call':
                nargs = int(operands[1])
                call_args = [stack.pop() for _ in range(nargs)][::-1]
                stack.append(word(self.invoke(operands[0], call_args)))
            elif op == 'return':
                return stack.pop()
            else:
                raise NotImplementedError(op)
        raise RuntimeError('VM function fell through without return: ' + name)
