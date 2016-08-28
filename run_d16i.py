#!/usr/bin/env python3

import sys
import getopt

from d16i.cpu import D16Cpu
import d16i.cmdline as cmdline


def main(code):
    cpu = D16Cpu(code)
    cpu.execute(steps=None, debug=None)


if __name__ == "__main__":
    cmdline.cmdline_main()
