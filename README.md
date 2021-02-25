# RISC-V Macroassembler

This toy project is an assembler for RISC-V that requires only a Python 3
interpreter, and doesn't have any external dependencies like gcc.

It can produce a binary file of RISC-V instructions, but doesn't wrap them in a
format like ELF.

Note that this code is not finished, and currently supports very few instructions.
See [`DESIGN.md`](./DESIGN.md) for implementation details.

# Usage

See [`example.py`](./example.py) for example usage.
This file generates a "Hello, World" program which can run in
[QEMU](https://www.qemu.org/) under the `virt` RISC-V machine.
You can run it as follows.

First, encode some instructions and write them to `test.bin`:

    $ python3 example.py test.bin

Run `test.bin` on a QEMU `virt` machine using the following command:

    $ qemu-system-riscv64 -nographic -machine virt -bios test.bin
    Hello, World!

At this point the QEMU machine will appear to hang; you can bring up a QEMU
prompt and quit using `C-a c`:

    QEMU 5.2.0 monitor - type 'help' for more information
    (qemu) quit

Finally, if you have a RISC-V-aware objdump, you can disassemble the contents of
`test.bin`:

    $ objdump -b binary --architecture=riscv -D test.bin
      0000000000000000 <.data>:
     0:   00100093                li      ra,1
     4:   01c09093                slli    ra,ra,0x1c
     8:   04800113                li      sp,72
     c:   00208023                sb      sp,0(ra)
    10:   06500113                li      sp,101
    14:   00208023                sb      sp,0(ra)
    18:   06c00113                li      sp,108
    (...snip...)

# Bugs

Probably loads

# TODO

- [ ] `Instruction.where`
- [ ] `make_instruction` helper
- [ ] Generate instruction encodings using [riscv-opcodes](https://github.com/riscv/riscv-opcodes)
