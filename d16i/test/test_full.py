from d16i.cpu import D16Cpu
import glob
import subprocess


def test_full():
    def run_test(code, test_data):
        cpu = D16Cpu(bytearray(code.read()))
        for line in test_data:
            regs_str = line.split()
            regs = [int(i) for i in regs_str]
            cpu.execute(steps=1, debug=True)
            assert cpu.reg == regs

    sources = glob.glob("data/*.s")
    for source in sources:
        print(source)
        name = source[:-2]
        subprocess.call(["d16", source, name + ".bin"])
        with open(name + ".bin") as code:
            with open(name + ".test") as test_data:
                run_test(code, test_data)
