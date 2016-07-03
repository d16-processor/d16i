# D16 interpreter

This project is a mostly-complete emulator for the [D16 cpu][d16-cpu].
Generating code to execute requires a working and up to date version of the
[d16 assembler][d16-cpu].

[d16-cpu]: https://github.com/c-elegans/d16


# Usage

Run `./run_d16i.py <assembler_output.bin>`

For each instruction executed, the emulator will output the address,
instruction type, flags, and the state of every register.

For example:

```
addr instr  : NZCV  r0   r1   r2   r3   r4   r5   r6   r7
0000 NOP    : 0000  0000 0000 0000 0000 0000 0000 0000 0000
0002 MOVB_R0: 0000  0000 0000 0000 0000 0000 0000 0000 0000
0004 ADDI   : 0100  0000 0000 0000 0000 0000 0000 0000 0000
0008 STI    : 0000  2000 0000 0000 0000 0000 0000 0000 0000
000c JMPI   : 0000  2000 0000 0000 0000 0000 0000 0000 0000
0010 AND    : 0000  2000 0000 0000 0000 0000 0000 0000 0000
0012 STOP   : 0100  2000 0000 0000 0000 0000 0000 0000 0000
```

## Requirements

1. Ensure you have [Python 3.5][python-35] and [Tox][tox] installed and on your
   PATH.
2. Run `tox` to initialize the virtualenv and ensure that tests successfully
   complete.
3. Run `source .tox/py35/bin/activate` to make sure that python can find all
   dependencies.

[python-35]: https://www.python.org/downloads/release/python-352/
[tox]: https://testrun.org/tox/latest/
