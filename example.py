#!/usr/bin/env python3
import sys
from macroassembler import instructions

# Generate a simple "Hello, World" program that writes to the QEMU Virt
# machine's UART device
def gen_hello_world():
    # Put the UART address (0x10000000) into R1
    yield 'addi', dict(imm=0x1, rs1=0x0, rd=0x1)                # R1 ← R0 + 1
    yield 'slli', dict(imm=0x0, shamt=0x1C, src=0x1, dest=0x1)  # R1 ← R1 << 28

    # Generate an unrolled loop of instructions which put each char value in R2
    # and then write it to the UART address.
    for c in "Hello, World!\n":
        yield 'addi', dict(imm=ord(c), rs1=0x0, rd=0x2)       # R2 ← R0 + ord(c)
        yield 'store', dict(offset=0, src=2, base=1, width=0) # M[R0 + 0] ← R2

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('usage: {} <output_file>'.format(sys.argv[0]))
        sys.exit(1)

    out_file_name = sys.argv[1]

    with open(out_file_name, 'w') as f:
        for name, args in gen_hello_world():
            instruction = instructions[name]
            f.buffer.write(instruction.encode(**args).value.to_bytes(4, 'little'))
