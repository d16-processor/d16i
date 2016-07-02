from d16i.cpu import D16Cpu


def test_init_flags():
    cpu = D16Cpu(code=[])
    assert len(cpu.regs) == 8
    for reg in cpu.regs:
        assert reg == 0


def test_init_flags():
    cpu = D16Cpu(code=[])
    assert cpu.flags["negative"] is False
    assert cpu.flags["zero"] is False
    assert cpu.flags["carry"] is False
    assert cpu.flags["overflow"] is False


def test_init_mem():
    code = 75 * [0xBEEF]
    cpu = D16Cpu(code=code)
    assert len(cpu.mem) == 0xFFFF
    for i in range(0, 75):
        assert cpu.mem[i] == 0xBEEF
    for i in range(75, 0xFFFF):
        assert cpu.mem[i] == 0x0
