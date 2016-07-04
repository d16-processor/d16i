from d16i.cpu import D16Cpu
import pytest


def test_update_flags():
    cpu = D16Cpu([])
    cpu._update_flags(-1)
    assert cpu.flags == {
        "negative": True,
        "zero": False,
        "carry": True,
        "overflow": False
    }

    cpu._update_flags(0)
    assert cpu.flags == {
        "negative": False,
        "zero": True,
        "carry": False,
        "overflow": False
    }

    cpu._update_flags(-0x7fff)
    assert cpu.flags == {
        "negative": True,
        "zero": False,
        "carry": True,
        "overflow": False
    }

    cpu._update_flags(-0xffff)
    assert cpu.flags == {
        "negative": False,
        "zero": False,
        "carry": True,
        "overflow": False
    }

    cpu._update_flags(0x7fff)
    assert cpu.flags == {
        "negative": False,
        "zero": False,
        "carry": False,
        "overflow": False
    }

    cpu._update_flags(0x10000)
    assert cpu.flags == {
        "negative": False,
        "zero": True,
        "carry": True,
        "overflow": False
    }


def test_signed_flags():
    cpu = D16Cpu([])
    cpu._update_flags(0x8000)
    cpu._update_signed_flags(0x7FFF, 1)
    assert cpu.flags == {
        "negative": True,
        "zero": False,
        "carry": False,
        "overflow": True
    }
    cpu._update_flags(0)
    cpu._update_signed_flags(0xFFFF, 1)
    assert cpu.flags == {
        "negative": False,
        "zero": True,
        "carry": False,
        "overflow": False
    }
    cpu._update_flags(4)
    cpu._update_signed_flags(3, 1)
    assert cpu.flags == {
        "negative": False,
        "zero": False,
        "carry": False,
        "overflow": False
    }
    cpu._update_flags(-1)
    cpu._update_signed_flags(0, -1)
    assert cpu.flags == {
        "negative": True,
        "zero": False,
        "carry": True,
        "overflow": False
    }
