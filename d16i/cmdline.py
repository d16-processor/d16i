import sys
import getopt

from d16i.cpu import D16Cpu


def cmdline_main():
    opts, args = getopt.getopt(sys.argv[1:], "q")
    debug = True
    for o, a in opts:
        if o == "-q":
            debug = False
    if len(args) < 1:
        print("Usage: run_d16i.py [-q] <binary>")
        sys.exit(1)
    filename = args[0]
    with open(filename, "rb") as code:
        cpu = D16Cpu(bytearray(code.read()))
        cpu.execute(steps=None, debug=debug)
        cpu.end()
