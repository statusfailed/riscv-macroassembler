set architecture riscv:rv64
target remote :1234
layout asm
layout reg
break *0x80000000
continue
