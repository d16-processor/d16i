# D16 interpreter/emulator
This project is a mostly-complete emulator for the [D16 cpu](https://github.com/c-elegans/d16).
It requires a working and up to date version of the d16 assembler found at the link above.
##Running
To run, you must first have built a d16 binary from the d16 assembler above. Afterwards, simply run `python d16i.py [binary]`.

For each instruction executed, the emulator will output the address, instruction type, flags, and the state of every register.
For example:
```
addr instr  : NZCV  r0   r1   r2   r3   r4   r5   r6   r7
0002 NOP    : 0000  0000 0000 0000 0000 0000 0000 0000 0000
0006 MOVI   : 1001  fffe 0000 0000 0000 0000 0000 0000 0000
0008 MOVB_R1: 0000  fffe 0001 0000 0000 0000 0000 0000 0000
0010 ADD    : 1001  ffff 0001 0000 0000 0000 0000 0000 0000
```