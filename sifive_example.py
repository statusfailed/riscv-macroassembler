#!/usr/bin/env python3
import sys
from macroassembler import instructions

# Generate a "hello world" program that writes to the sifive_u board's UART0.
def gen_hello_world():
    # yield 'lui', dict(imm=0x10010, rd=0x1)
    # yield 'beq', dict(imm12=0b1, imm10_5=0b111111, imm4_1=0b1110, imm11=0b1, rs2=0x0, rs1=0x3) # jump back 2*2 bytes
    # return

    # read 0xF14 CSR - Hart ID - into R1
    yield 'csrrs', dict(csr=0xF14, rs1=0x0, rd=0x1)
    # loop forever if hart ID is not 0.
    yield 'bne', dict(imm12=0b1, imm10_5=0b111111, imm4_1=0b1110, imm11=0b1, rs2=0x0, rs1=0x1)

    # R1 ← 0x10010000
    yield 'lui', dict(imm=0x10010, rd=0x1)

    # Generate an unrolled loop of instructions which put each char value in R2
    # and then write it to the UART address.
    # NOTE: the sifive_u UART0 requires we write 4 bytes at a time, so we have
    # to set width=0b10 or it doesn't work.
    # However this causes some slightly weird output :^)
    # for c in "Hello, World!\n":
    for c in "Hello!\n":
        yield 'addi', dict(imm=ord(c), rs1=0x0, rd=0x2)       # R2 ← R0 + ord(c)
        yield 'store', dict(offset=0, src=2, base=1, width=0b10) # M[R0 + 0] ← R2

        # read the tx register to see the status of the 'full' flag
        yield 'lw', dict(imm=0x0, base=0x1, dest=0x3) # R3 ← M[R1]

        # branch
        # yield 'beq', dict(imm12=0b1, imm10_5=0b111111, imm4_1=0b1110, imm11=0b1, rs2=0x0, rs1=0x3) # jump back 2*2 bytes
        # jump back 2*2 bytes if txdata != 0
        yield 'bne', dict(imm12=0b1, imm10_5=0b111111, imm4_1=0b1110, imm11=0b1, rs2=0x0, rs1=0x3)

        # branch if lw equals 0

        # Read the tx field into R4
        # yield 'lw', dict(offset=0x4, base=0x1, dest=0x4) # R4 ← M[R1]   (word)

    # infinite loop at the end
    yield 'auipc', dict(imm=0x0, rd=0x5) # R5 ← pc + 0
    yield 'jalr', dict(imm=0x0, rs1=0x5, rd=0x0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('usage: {} <output_file>'.format(sys.argv[0]))
        sys.exit(1)

    out_file_name = sys.argv[1]

    with open(out_file_name, 'w') as f:
        for name, args in gen_hello_world():
            instruction = instructions[name]
            f.buffer.write(instruction.encode(**args).value.to_bytes(4, 'little'))
