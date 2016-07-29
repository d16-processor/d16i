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
    ("stack"),
    ("call"),
])
def test_cpu(name):
    print(os.getcwd())
    name = "d16i/test/data/" + name
    subprocess.call(["d16", "-b", "-o", name + ".bin", name + ".s"])
    print(name + ".bin")
    with open(name + ".bin", "rb") as code_file, open(name + ".test") as data:
        cpu = D16Cpu(code_file.read())
        for line in data:
            regs_str = line.split()
            regs = [int(i, 16) for i in regs_str]
            cpu.execute(steps=1, debug=True)
            assert cpu.regs == regs
