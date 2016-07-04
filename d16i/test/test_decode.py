from d16i.cpu import D16Cpu
from d16i.definitions import Opcode
import pytest
import unittest


def test_reg_decode():
    cpu = D16Cpu([0b00101010, Opcode.ADD])
    rS, rD = cpu._decode_reg_sel()
    assert rS == 5
    assert rD == 2


def test_imm_decode():
    cpu = D16Cpu([0b00110011, Opcode.ADD, 0x45, 0x00])
    rS, rD, imm = cpu._decode_imm()
    assert rS == 6
    assert rD == 3
    assert imm == 0x45


def test_mem_sel():
    cpu = D16Cpu([0b11001000, Opcode.STI, 0x00, 0x00])
    assert cpu._decode_reg_sel_disp()
    assert cpu._decode_byte_sel()
