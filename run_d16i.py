#!/usr/bin/env python3

import sys

from d16i.cpu import D16Cpu


def main(code):
    cpu = D16Cpu(code)
    cpu.execute(steps=16, debug=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: run_d16i.py [binary]")
        sys.exit(1)
    with open(sys.argv[1], "rb") as code:
        main(bytearray(code.read()))
