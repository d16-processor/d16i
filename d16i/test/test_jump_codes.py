from d16i.cpu import D16Cpu, _test_cc
from d16i.definitions import CC
import d16i
import pytest
import unittest


class ConditionCodeTest(unittest.TestCase):
    def setUp(self):
        self.cpu = D16Cpu([])
        self.cpu._reset_flags()

    def test_always_code(self):
        assert _test_cc(self.cpu.flags, CC.AL) is True
        assert not _test_cc(self.cpu.flags, CC.NV)

    def test_carry(self):
        self.cpu._update_flags(0x1ffff)  # set carry
        assert _test_cc(self.cpu.flags, CC.CS)
        assert not _test_cc(self.cpu.flags, CC.CC)

        self.cpu._update_flags(0x00ff)
        assert not _test_cc(self.cpu.flags, CC.CS)
        assert _test_cc(self.cpu.flags, CC.CC)

    def test_zero(self):
        self.cpu._update_flags(0)
        assert _test_cc(self.cpu.flags, CC.EQ)
        assert not _test_cc(self.cpu.flags, CC.NE)
        self.cpu._update_flags(1)
        assert not _test_cc(self.cpu.flags, CC.EQ)
        assert _test_cc(self.cpu.flags, CC.NE)

    def test_overflow(self):
        self.cpu._update_signed_flags(0x7fff, 1)
        assert _test_cc(self.cpu.flags, CC.OS)
        assert not _test_cc(self.cpu.flags, CC.OC)
        self.cpu._update_signed_flags(0x7f, 1)
        assert not _test_cc(self.cpu.flags, CC.OS)
        assert _test_cc(self.cpu.flags, CC.OC)

    def test_sign(self):
        self.cpu._update_flags(-1)
        assert _test_cc(self.cpu.flags, CC.N)
        assert not _test_cc(self.cpu.flags, CC.P)
        self.cpu._update_flags(1)
        assert not _test_cc(self.cpu.flags, CC.N)
        assert _test_cc(self.cpu.flags, CC.P)

    def test_unsigned_cmp(self):
        self.cpu._update_flags(1 - 5)
        assert _test_cc(self.cpu.flags, CC.HI)
        assert not _test_cc(self.cpu.flags, CC.LS)
        self.cpu._update_flags(5 - 1)
        assert not _test_cc(self.cpu.flags, CC.HI)
        assert _test_cc(self.cpu.flags, CC.LS)

    def test_signed_cmp(self):
        self.cpu._update_flags(5 - 3)
        self.cpu._update_signed_flags(-3, 5)
        assert _test_cc(self.cpu.flags, CC.G)
        assert _test_cc(self.cpu.flags, CC.GE)
        assert not _test_cc(self.cpu.flags, CC.L)
        assert not _test_cc(self.cpu.flags, CC.LE)

        self.cpu._update_flags(10 - 10)
        self.cpu._update_signed_flags(10, -10)
        print(self.cpu.flags)
        assert not _test_cc(self.cpu.flags, CC.G)
        assert _test_cc(self.cpu.flags, CC.GE)
        assert not _test_cc(self.cpu.flags, CC.L)
        assert _test_cc(self.cpu.flags, CC.LE)

        self.cpu._update_flags(10 - 11)
        self.cpu._update_signed_flags(-11, 10)
        assert not _test_cc(self.cpu.flags, CC.G)
        assert not _test_cc(self.cpu.flags, CC.GE)
        assert _test_cc(self.cpu.flags, CC.L)
        assert _test_cc(self.cpu.flags, CC.LE)
