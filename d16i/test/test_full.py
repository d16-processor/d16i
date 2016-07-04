import os
import sys
import inspect
from d16i.cpu import D16Cpu
import glob
import subprocess
import pytest
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(
    inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(parentdir)
sys.path.insert(0, parentdir)



def run_test(code, test_data):
    cpu = D16Cpu(bytearray(code.read()))
    for line in test_data:
        regs_str = line.split()
        regs = [int(i) for i in regs_str]
        cpu.execute(steps=1, debug=True)
        for i in range(0, 8):
            assert cpu.regs[i] == regs[i], "Register r{0:1d} \
            was {1:4x}, expected {2:4x}".format(
                i, cpu.regs[i], regs[i])
            pass


def full_test():
    sources = glob.glob("data/*.s")
    for source in sources:
        print(source)
        name = source[:-2]
        subprocess.call(["d16", source, name + ".bin"])
        with open(name + ".bin") as code:
            with open(name + ".test") as test_data:
                run_test(code, test_data)


if __name__ == "__main__":
    full_test()
