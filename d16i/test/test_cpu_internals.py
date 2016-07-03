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
