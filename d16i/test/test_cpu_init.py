from d16i.cpu import D16Cpu
import pytest


def test_init_regs():
    cpu = D16Cpu([])
    assert len(cpu.regs) == 8
    for reg in cpu.regs:
        assert reg == 0


def test_init_flags():
    cpu = D16Cpu([])
    assert cpu.flags["negative"] is False
    assert cpu.flags["zero"] is False
    assert cpu.flags["carry"] is False
    assert cpu.flags["overflow"] is False

    cpu.flags = {}
    cpu._reset_flags()
    assert cpu.flags["negative"] is False
    assert cpu.flags["zero"] is False
    assert cpu.flags["carry"] is False
    assert cpu.flags["overflow"] is False


def test_init_mem():
    code = 75 * [0xBE]
    cpu = D16Cpu(code)
    for i in range(0, 75):
        assert cpu.mem[i] == 0xBE
    for i in range(0x7F, 0x10000):
        assert cpu.mem[i] == 0x0

    with pytest.raises(IndexError):
        # noinspection PyStatementEffect
        cpu.mem[0x10000]


def test_store_mem():
    cpu = D16Cpu([])
    cpu.store_word(0x0000, 0xBEEF)
    assert cpu.load_word(0x0000) == 0xBEEF
    assert cpu.mem[0x0000] == 0xEF
    assert cpu.mem[0x0001] == 0xBE
