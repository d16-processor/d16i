from d16i.cpu import D16Cpu
import glob
import subprocess
import pytest
import os


@pytest.mark.parametrize("name", [
    ("add"),
    ("logic"),
    ("jmp"),
    ("mem"),
])
def test_cpu(name):
    print(os.getcwd())
    name = "d16i/test/data/" + name
    subprocess.call(["d16", name + ".s", name + ".bin"])
    print(name + ".bin")
    code = open(name + ".bin", "rb").read()
    data = open(name + ".test")

    cpu = D16Cpu(bytearray(code))
    for line in data:
        regs_str = line.split()
        regs = [int(i, 16) for i in regs_str]
        cpu.execute(steps=1, debug=True)
        assert cpu.regs == regs
