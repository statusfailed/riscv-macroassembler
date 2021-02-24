# Design

Instructions are modeled as a collection of named arguments, each of which is
assigned a list of non-contiguous bit-ranges.

Consider for example the "SB" (store byte) instruction from the
[RISC-V specification][riscv-spec]:

     31           25 24   20 19     15 14   12 11            7 6             0
    [   imm[11:5]   |  rs2  |   rs1   |  000  |   imm[4:0]    |    0100011    ]
       offset[11:5]    src     base             offset[4:0]

[riscv-spec]: https://riscv.org/risc-v-isa/

This instruction denotes the operation

    Memory[base + offset] ← src

It has three arguments:

- `base` (aka `rs1`): the address register
- `offset` (aka `imm`): a 12-bit immediate added to the base register
- `src` (aka `rs2`): the register containing the value to store

Note that the "offset" immediate is stored in two non-contiguous bit ranges.

We specify an instruction by defining how to encode each of its
arguments. We can write `sb` as follows:

    sb = NormalizedInstruction(32
      offset=bits[31:25, 11:7], # offset is a 12-bit value stored in two places
      src=bits[24:20],
      base=bits[19:15],
      width=bits[14:12],
      opcode=bits[6:0:0b0100011] # the 'step' part of the slice is a constant
      )

For more examples of instruction definitions, see
[`macroassembler.py`](./macroassembler.py)
