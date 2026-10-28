import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from vm_runner import VM

ROOT = Path(__file__).resolve().parents[1]


class CourseworkTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.work = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, script, *args):
        result = subprocess.run([sys.executable, str(ROOT/script), *map(str, args)],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def compile(self, path=None, source=None, compiler='jack-coroutines'):
        folder = self.work/'input'
        folder.mkdir(exist_ok=True)
        if source is not None:
            (folder/'Counter.jack').write_text(source)
        else:
            for p in (ROOT/path).glob('*.jack'):
                shutil.copyfile(p, folder/p.name)
        self.run_script(Path(compiler)/'JackCompiler.py', folder)
        return folder

    def test_original_single_coroutine_demo(self):
        folder = self.compile('jack-coroutines/testFolders/TestA_SimpleCoroutine')
        vm = VM(folder.glob('*.vm'))
        vm.invoke('Main.main')
        output = ''.join(vm.output)
        self.assertEqual(output, 'Test A: Simple Coroutine\nCalling step() iteration 1\n'
                         'Starting counter...\nCalling step() iteration 2\nCounting: 0\n'
                         'Calling step() iteration 3\nCounter finished!\n1\nTest A Complete\n')
        for p in folder.glob('*.xml'):
            ET.parse(p)

    def test_original_producer_consumer_demo(self):
        folder = self.compile('jack-coroutines/testFolders/TestB_MultiCoroutine')
        vm = VM(folder.glob('*.vm'))
        vm.invoke('Main.main')
        output = ''.join(vm.output)
        events = [line.strip() for line in output.splitlines()
                  if 'Producer:' in line or 'Consumer:' in line]
        self.assertEqual(events, [line for value in (10, 20, 30)
                                 for line in (f'Producer: Generated {value}',
                                              f'Consumer: Received {value}')])
        self.assertIn('Test B Complete - Processed 3 items', output)
        self.assertEqual(output.count('Consumer: Received'), 3)

    def test_instances_resume_independently_and_finish_is_idempotent(self):
        folder = self.compile(source='''coroutine class Counter {
            field int value;
            constructor Counter new() { let value = 0; return this; }
            task step() {
                let value = value + 1; yield;
                let value = value + 1; finish;
            }
            method int get() { return value; }
        }''')
        vm = VM(folder.glob('*.vm'))
        a, b = vm.invoke('Counter.new'), vm.invoke('Counter.new')
        vm.invoke('Counter.step', [a])
        self.assertEqual(vm.invoke('Counter.get', [a]), 1)
        self.assertEqual(vm.invoke('Counter.get', [b]), 0)
        vm.invoke('Counter.step', [a])
        vm.invoke('Counter.step', [a])
        vm.invoke('Counter.step', [b])
        self.assertEqual(vm.invoke('Counter.get', [a]), 2)
        self.assertEqual(vm.invoke('Counter.get', [b]), 1)

    def test_field_counter_survives_yielding_loop(self):
        folder = self.compile(source='''coroutine class Counter {
            field int value;
            constructor Counter new() { let value = 0; return this; }
            task step() {
                while (value < 3) { let value = value + 1; yield; }
                finish;
            }
            method int get() { return value; }
        }''')
        vm = VM(folder.glob('*.vm'))
        obj = vm.invoke('Counter.new')
        observed = []
        for _ in range(6):
            vm.invoke('Counter.step', [obj])
            observed.append(vm.invoke('Counter.get', [obj]))
        self.assertEqual(observed, [1, 2, 3, 3, 3, 3])

    @unittest.expectedFailure
    def test_known_limit_locals_do_not_survive_yield(self):
        """Records the existing missing local-state lifting; not a passing guarantee."""
        folder = self.compile(source='''coroutine class Counter {
            field int value;
            constructor Counter new() { let value = 0; return this; }
            task step() { var int saved; let saved = 7; yield;
                let value = saved; finish; }
            method int get() { return value; }
        }''')
        vm = VM(folder.glob('*.vm'))
        obj = vm.invoke('Counter.new')
        vm.invoke('Counter.step', [obj])
        vm.invoke('Counter.step', [obj])
        self.assertEqual(vm.invoke('Counter.get', [obj]), 7)

    def test_standard_square_still_compiles(self):
        folder = self.compile('jack-coroutines/testFolders/Square')
        self.assertEqual(len(list(folder.glob('*.vm'))), 3)
        for p in folder.glob('*.xml'):
            ET.parse(p)

    def test_original_tetris_and_os_sources_compile(self):
        folder = self.compile('jack-tetris')
        self.assertEqual(len(list(folder.glob('*.vm'))), 5)
        for p in folder.glob('*'):
            if p.is_file():
                p.unlink()
        folder = self.compile('jack-os')
        self.assertEqual(len(list(folder.glob('*.vm'))), 8)

    def test_standard_compiler_entry_point(self):
        folder = self.compile(source='class Counter { function int run() { return 2 + 3; } }',
                              compiler='jack-compiler')
        vm = VM(folder.glob('*.vm'))
        self.assertEqual(vm.invoke('Counter.run'), 5)

    def test_hack_assembler_two_pass_symbol_resolution(self):
        p = self.work/'Program.asm'
        p.write_text('@2\nD=A\n@3\nD=D+A\n@result\nM=D\n(END)\n@END\n0;JMP\n')
        self.run_script(Path('hack-assembler/hackAssembler.py'), p)
        words = (self.work/'LouisProgram.hack').read_text().splitlines()
        self.assertEqual(words, ['0000000000000010', '1110110000010000',
                                '0000000000000011', '1110000010010000',
                                '0000000000010000', '1110001100001000',
                                '0000000000000110', '1110101010000111'])

    def test_stack_machine_executes_arithmetic(self):
        p = self.work/'instructions.txt'
        p.write_text('push 7\npush 8\nadd\npush 3\nmul\n')
        result = self.run_script(Path('systems-utilities/stack-machine.py'), p)
        self.assertEqual(result.stdout.strip(), '45')


if __name__ == '__main__':
    unittest.main()
