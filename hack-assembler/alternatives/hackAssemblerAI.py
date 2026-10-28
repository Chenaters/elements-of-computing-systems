#!/usr/bin/env python3
"""
Hack Assembler - Converts Hack assembly language (.asm) to binary machine code (.hack)
Part of the Nand2Tetris course
"""

import sys
import os
import re


class Parser:
    """Handles the parsing of a single .asm file"""
    
    def __init__(self, filename):
        """Opens the input file and gets ready to parse it"""
        with open(filename, 'r') as f:
            self.lines = f.readlines()
        self.current_line = 0
        self.current_command = ""
        
    def has_more_commands(self):
        """Are there more commands in the input?"""
        return self.current_line < len(self.lines)
    
    def advance(self):
        """Reads the next command from the input and makes it the current command"""
        if self.has_more_commands():
            line = self.lines[self.current_line]
            self.current_line += 1
            
            # Remove comments and whitespace
            line = line.split('//')[0].strip()
            self.current_command = line
            
            # Skip empty lines
            if not line:
                if self.has_more_commands():
                    self.advance()
    
    def command_type(self):
        """Returns the type of the current command"""
        if not self.current_command:
            return None
        
        if self.current_command.startswith('@'):
            return 'A_COMMAND'
        elif self.current_command.startswith('('):
            return 'L_COMMAND'
        else:
            return 'C_COMMAND'
    
    def symbol(self):
        """Returns the symbol or decimal of the current command (A or L command)"""
        if self.command_type() == 'A_COMMAND':
            return self.current_command[1:]
        elif self.command_type() == 'L_COMMAND':
            return self.current_command[1:-1]
        return None
    
    def dest(self):
        """Returns the dest mnemonic in the current C-command"""
        if self.command_type() == 'C_COMMAND':
            if '=' in self.current_command:
                return self.current_command.split('=')[0]
        return None
    
    def comp(self):
        """Returns the comp mnemonic in the current C-command"""
        if self.command_type() == 'C_COMMAND':
            command = self.current_command
            
            # Remove dest part if present
            if '=' in command:
                command = command.split('=')[1]
            
            # Remove jump part if present
            if ';' in command:
                command = command.split(';')[0]
            
            return command
        return None
    
    def jump(self):
        """Returns the jump mnemonic in the current C-command"""
        if self.command_type() == 'C_COMMAND':
            if ';' in self.current_command:
                return self.current_command.split(';')[1]
        return None


class Code:
    """Translates Hack assembly language mnemonics into binary codes"""
    
    # Computation lookup tables
    COMP_TABLE = {
        '0':   '0101010',
        '1':   '0111111',
        '-1':  '0111010',
        'D':   '0001100',
        'A':   '0110000',
        '!D':  '0001101',
        '!A':  '0110001',
        '-D':  '0001111',
        '-A':  '0110011',
        'D+1': '0011111',
        'A+1': '0110111',
        'D-1': '0001110',
        'A-1': '0110010',
        'D+A': '0000010',
        'D-A': '0010011',
        'A-D': '0000111',
        'D&A': '0000000',
        'D|A': '0010101',
        'M':   '1110000',
        '!M':  '1110001',
        '-M':  '1110011',
        'M+1': '1110111',
        'M-1': '1110010',
        'D+M': '1000010',
        'D-M': '1010011',
        'M-D': '1000111',
        'D&M': '1000000',
        'D|M': '1010101',
    }
    
    DEST_TABLE = {
        None:  '000',
        'M':   '001',
        'D':   '010',
        'MD':  '011',
        'A':   '100',
        'AM':  '101',
        'AD':  '110',
        'AMD': '111',
    }
    
    JUMP_TABLE = {
        None:  '000',
        'JGT': '001',
        'JEQ': '010',
        'JGE': '011',
        'JLT': '100',
        'JNE': '101',
        'JLE': '110',
        'JMP': '111',
    }
    
    @staticmethod
    def dest(mnemonic):
        """Returns the binary code of the dest mnemonic"""
        return Code.DEST_TABLE.get(mnemonic, '000')
    
    @staticmethod
    def comp(mnemonic):
        """Returns the binary code of the comp mnemonic"""
        return Code.COMP_TABLE.get(mnemonic, '0000000')
    
    @staticmethod
    def jump(mnemonic):
        """Returns the binary code of the jump mnemonic"""
        return Code.JUMP_TABLE.get(mnemonic, '000')


class SymbolTable:
    """Keeps a correspondence between symbolic labels and numeric addresses"""
    
    def __init__(self):
        """Creates a new empty symbol table with predefined symbols"""
        self.table = {
            'SP':     0,
            'LCL':    1,
            'ARG':    2,
            'THIS':   3,
            'THAT':   4,
            'R0':     0,
            'R1':     1,
            'R2':     2,
            'R3':     3,
            'R4':     4,
            'R5':     5,
            'R6':     6,
            'R7':     7,
            'R8':     8,
            'R9':     9,
            'R10':    10,
            'R11':    11,
            'R12':    12,
            'R13':    13,
            'R14':    14,
            'R15':    15,
            'SCREEN': 16384,
            'KBD':    24576,
        }
        self.next_variable_address = 16
    
    def add_entry(self, symbol, address):
        """Adds the pair (symbol, address) to the table"""
        self.table[symbol] = address
    
    def contains(self, symbol):
        """Does the symbol table contain the given symbol?"""
        return symbol in self.table
    
    def get_address(self, symbol):
        """Returns the address associated with the symbol"""
        return self.table.get(symbol)
    
    def add_variable(self, symbol):
        """Adds a variable to the symbol table at the next available address"""
        if not self.contains(symbol):
            self.add_entry(symbol, self.next_variable_address)
            self.next_variable_address += 1
        return self.get_address(symbol)


def assemble(input_filename):
    """
    Main assembler function that performs two-pass assembly
    """
    # First pass: Build symbol table with labels
    parser = Parser(input_filename)
    symbol_table = SymbolTable()
    rom_address = 0
    
    while parser.has_more_commands():
        parser.advance()
        command_type = parser.command_type()
        
        if command_type == 'L_COMMAND':
            # Label declaration - add to symbol table with current ROM address
            symbol = parser.symbol()
            symbol_table.add_entry(symbol, rom_address)
        elif command_type in ['A_COMMAND', 'C_COMMAND']:
            # Actual instruction - increment ROM address
            rom_address += 1
    
    # Second pass: Generate machine code
    parser = Parser(input_filename)
    output_lines = []
    
    while parser.has_more_commands():
        parser.advance()
        command_type = parser.command_type()
        
        if command_type == 'A_COMMAND':
            symbol = parser.symbol()
            
            # Check if it's a number or a symbol
            if symbol.isdigit():
                address = int(symbol)
            else:
                # Look up or create variable
                if symbol_table.contains(symbol):
                    address = symbol_table.get_address(symbol)
                else:
                    address = symbol_table.add_variable(symbol)
            
            # Convert to 16-bit binary (A-instruction starts with 0)
            binary = format(address, '016b')
            output_lines.append(binary)
            
        elif command_type == 'C_COMMAND':
            # C-instruction: 111accccccdddjjj
            dest_bits = Code.dest(parser.dest())
            comp_bits = Code.comp(parser.comp())
            jump_bits = Code.jump(parser.jump())
            
            binary = '111' + comp_bits + dest_bits + jump_bits
            output_lines.append(binary)
    
    # Write output file
    output_filename = input_filename.replace('.asm', '.hack')
    with open(output_filename, 'w') as f:
        f.write('\n'.join(output_lines) + '\n')
    
    print(f"Assembly complete: {output_filename}")
    return output_filename


def main():
    """Main entry point for the assembler"""
    if len(sys.argv) < 2:
        print("Usage: python hackAssembler.py <file.asm>")
        print("\nExample: python hackAssembler.py Add.asm")
        print("\nAvailable .asm files in current directory:")
        for file in os.listdir('.'):
            if file.endswith('.asm'):
                print(f"  - {file}")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    
    if not input_file.endswith('.asm'):
        print("Error: Input file must have .asm extension")
        sys.exit(1)
    
    assemble(input_file)


if __name__ == '__main__':
    main()
