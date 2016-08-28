from abc import ABCMeta, abstractmethod
from collections import namedtuple


CpuStatistics = namedtuple("CpuStatistics", ["instructions_dispatched"])


class BaseCpu(metaclass=ABCMeta):
    """
    Base CPU class. This contains some of the base specification
    for the CPU class.
    """

    def __init__(self, code):
        self.regs = [0] * 8
        self.mem = (bytearray(code) +
                    bytearray([0xff, 0xff]) +
                    bytearray(0x10000 - (len(code) + 2)))
        self.stats = CpuStatistics(instructions_dispatched=0)

    @abstractmethod
    def execute_instruction(self):
        pass

    @abstractmethod
    def execute(self, steps, debug):
        """
        :type steps: int | None
        :param steps: Number of instructions to execute or None to run
                    indefinitely
        """
        pass

    @staticmethod
    @abstractmethod
    def trace_header_str():
        pass

    @abstractmethod
    def trace_str(self):
        pass
