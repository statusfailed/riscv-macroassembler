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

    $ riscv64-linux-gnu-objdump -b binary --architecture=riscv -D test.bin
      0000000000000000 <.data>:
     0:   00100093                li      ra,1
     4:   01c09093                slli    ra,ra,0x1c
     8:   04800113                li      sp,72
     c:   00208023                sb      sp,0(ra)
    10:   06500113                li      sp,101
    14:   00208023                sb      sp,0(ra)
    18:   06c00113                li      sp,108
    (...snip...)

# Running on `sifive_u`

Running on `sifive_u` is a little different: the UART address is at
`0x10010000`, and we have to write in word-sized chunks. Run like this:

    $ ./sifive_example.py out.bin
    $ qemu-system-riscv64 -nographic -M sifive_u -bios out.bin
    HHeelllloo,,  WWoorrlldd!
    !

Note the repeated output. I think this is because out.bin writes
a full word `[0x0, 0x0, 0x0, c]` for each character `c`. **TODO!**

If you try to write in byte-sized chunks to the UART address, you get no output.
To see an error, run this:

    qemu-system-riscv64 -nographic -M sifive_u -bios out.bin -d guest_errors,unimp,pcall -D qemu.log

Exit using `C-a c quit` and then `head -n 1 qemu.log`:

    Invalid write at addr 0x0, size 1, region 'riscv.sifive.uart', reason: invalid size (min:4 max:4)

# Debugging

Install a RISC-V-compatible gdb, e.g. on arch:

    pacman -S riscv64-linux-gnu-gdb

Run QEMU in debug mode:

    qemu-system-riscv64 -nographic -M sifive_u -bios out.bin -s -S

Connect to gdb:

    riscv64-linux-gnu-gdb

Run this in gdb:

    target remote :1234
    layout asm

If you want to skip the bootloader(?) and go straight to your code from
`out.bin`, you can also run

    b *0x80000000
    c

Instead of typing this all out, you can also just do this:

    riscv64-linux-gnu-gdb -x start.gdb

# Bugs

- [ ] Fix `sifive_u` output - write 4 chars at a time? Find some driver docs!

Probably loads more.

# TODO

- [ ] `Instruction.where`
- [ ] `make_instruction` helper
- [ ] Generate instruction encodings using [riscv-opcodes](https://github.com/riscv/riscv-opcodes)

# References

- [Risc-V ISA Reference](https://github.com/riscv/riscv-isa-manual/releases/download/Ratified-IMAFDQC/riscv-spec-20191213.pdf)
    - See Chapter 24 for a table of instruction encodings
