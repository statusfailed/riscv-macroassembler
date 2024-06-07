#!/usr/bin/env python3
import sys
from macroassembler import instructions

# Generate a "hello world" program that writes to the sifive_u board's UART0.
def gen_hello_world():
    # R1 ← 0x10010000
    yield 'lui', dict(imm=0x10010, rd=0x1)

    # Generate an unrolled loop of instructions which put each char value in R2
    # and then write it to the UART address.
    # NOTE: the sifive_u UART0 requires we write 4 bytes at a time, so we have
    # to set width=0b10 or it doesn't work.
    # However this causes some slightly weird output :^) 
    for c in "Hello, World!\n":
        yield 'addi', dict(imm=ord(c), rs1=0x0, rd=0x2)       # R2 ← R0 + ord(c)
        yield 'store', dict(offset=0, src=2, base=1, width=0b10) # M[R0 + 0] ← R2

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('usage: {} <output_file>'.format(sys.argv[0]))
        sys.exit(1)

    out_file_name = sys.argv[1]

    with open(out_file_name, 'w') as f:
        for name, args in gen_hello_world():
            instruction = instructions[name]
            f.buffer.write(instruction.encode(**args).value.to_bytes(4, 'little'))
