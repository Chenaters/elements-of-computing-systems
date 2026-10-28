import re

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

    SYMBOL_TABLE = {
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
        'R10':   10,
        'R11':   11,
        'R12':   12,
        'R13':   13,
        'R14':   14,
        'R15':   15,
        'SCREEN':16384,
        'KBD':   24576,
        'SP':    0,
        'LCL':   1,
        'ARG':   2,
        'THIS':  3,
        'THAT':  4
    }

def main():
    # Read input file and remove comments/whitespace
    import sys
    if len(sys.argv) != 2:
        print("Usage: python hackAssembler.py <inputfile.asm>")
        return
    input_file = sys.argv[1]
    print("=" * 50)
    lines = []
    with open(input_file, 'r') as f:
        for line_number, line in enumerate(f, 1):
            # Remove comments and whitespace
            line = line.split('//')[0].strip()
            if line:  # Only add non-empty lines
                lines.append(line)
                    
    
    # Pass for A instruction labels
    lines_nolabels = []
    variables = []
    label_lines = {}
    label_pattern = re.compile(r'^\(([^)]+)\)$')
    unincr = 0
    for line_number, line in enumerate(lines): # Find labels, they don't take up a line
        if label_pattern.match(line):
            label = label_pattern.match(line).group(1)
            label_lines[label] = line_number - unincr
            unincr += 1
        else:
            lines_nolabels.append(line)
            # Convert integer to binary or use memory
    Code.SYMBOL_TABLE.update(label_lines)

    # Second pass to generate binary code
    output_lines = [0 for _ in range(len(lines_nolabels))]
    variable_address = 16
    for line_number, line in enumerate(lines_nolabels):
        if line.startswith('@'): # A-instruction
            symbol = line[1:]
            address = None
            try: # Use integer address directly
                address = int(symbol)            
            except ValueError: # Look for symbols
                if symbol in Code.SYMBOL_TABLE:
                    address = Code.SYMBOL_TABLE[symbol]
                else: # New variable
                    Code.SYMBOL_TABLE[symbol] = variable_address
                    address = variable_address
                    variable_address += 1
            address = address % (1 << 16) # For overflow and negatives
            binary_code = format(address, '016b')
            output_lines[line_number] = binary_code
        else: # Handle C-instructions here 
            # Either ; or =
            dest = None
            comp = line
            jump = None
            # Parse dest=comp;jump format
            if '=' in line:
                dest, comp = line.split('=', 1)
            if ';' in comp:
                comp, jump = comp.split(';', 1)
            # Look up binary codes
            dest_bits = Code.DEST_TABLE.get(dest, '000')
            comp_bits = Code.COMP_TABLE.get(comp, '0000000')
            jump_bits = Code.JUMP_TABLE.get(jump, '000')
            # C-instruction format: 111accccccdddjjj
            binary_code = '111' + comp_bits + dest_bits + jump_bits
            output_lines[line_number] = binary_code
    
    # Write output to .hack file
    import os
    input_dir = os.path.dirname(input_file)
    base_name = os.path.basename(input_file).replace('.asm', '')
    output_file = os.path.join(input_dir, f'Louis{base_name}.hack') 
    with open(output_file, 'w') as f:
        valid_lines = [line for line in output_lines if line]
        for i, line in enumerate(valid_lines):
            f.write(line)
            if i < len(valid_lines) - 1:  # Don't add newline after last line
                f.write('\n')
    print(f"Generated: {output_file}")
    print(f"Total instructions: {len(output_lines)}")
    
if __name__ == '__main__':
    main()

