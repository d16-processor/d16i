from d16i.definitions import CC, Opcode
from d16i.io import isIo, write_io_8
instructions = 256 * [None]  # type: list[dict[str, Any]]


def register_instruction(value, name, **kwargs):
    assert instructions[value] is None, \
        "attempted to insert duplicate instruction"
    kwargs.update({"name": name})
    instructions[value] = kwargs


register_instruction(Opcode.NOP, "NOP", custom="noop")
register_instruction(Opcode.ADD, "ADD", signed_flags=lambda s, d: (s, d),
                     regsel=lambda s, d: (s + d))
register_instruction(Opcode.SUB, "SUB", signed_flags=lambda s, d: (-s, d),
                     regsel=lambda s, d: (d - s))
register_instruction(Opcode.PUSH, "PUSH", custom="push")
register_instruction(Opcode.POP, "POP", custom="pop")
register_instruction(Opcode.MOVB_R0, "MOVB_R0", reg_store=0)
register_instruction(Opcode.MOVB_R1, "MOVB_R1", reg_store=1)
register_instruction(Opcode.MOVB_R2, "MOVB_R2", reg_store=2)
register_instruction(Opcode.MOVB_R3, "MOVB_R3", reg_store=3)
register_instruction(Opcode.MOVB_R4, "MOVB_R4", reg_store=4)
register_instruction(Opcode.MOVB_R5, "MOVB_R5", reg_store=5)
register_instruction(Opcode.MOVB_R6, "MOVB_R6", reg_store=6)
register_instruction(Opcode.MOVB_R7, "MOVB_R7", reg_store=7)
register_instruction(Opcode.MOV, "MOV", regsel=lambda s, d: s)
register_instruction(Opcode.AND, "AND", regsel=lambda s, d: (s & d))
register_instruction(Opcode.OR, "OR", regsel=lambda s, d: (s | d))
register_instruction(Opcode.XOR, "XOR", regsel=lambda s, d: (s ^ d))
register_instruction(Opcode.NOT, "NOT", regsel=lambda s, d: (~d))
register_instruction(Opcode.NEG, "NEG", regsel=lambda s, d: (-s) & 0xFFFF)
register_instruction(0x13, "LD", custom="ld")
register_instruction(0x14, "ST", custom="st")
register_instruction(0x15, "CMP", signed_flags=lambda s, d: (-s, d),
                     no_update_dest=True, regsel=lambda s, d: (d - s))
register_instruction(0x16, "JMP", custom="jmp")
register_instruction(Opcode.CALL, "CALL", custom="call")
register_instruction(Opcode.SPEC, "SPEC", custom="ret")
register_instruction(Opcode.SHL, "SHL", regsel=lambda s, d: (d << s))
register_instruction(Opcode.SHR, "SHR", regsel=lambda s, d: (d >> s))
register_instruction(Opcode.ROL, "ROL", regsel=lambda s, d:
                     (d >> s & 0xFFFF) | (d << (16 - s) & 0xFFFF))
register_instruction(Opcode.RCL, "RCL")
register_instruction(Opcode.LDCP, "LDCP")
register_instruction(Opcode.STCP, "STCP")
register_instruction(Opcode.ADC, "ADC")
register_instruction(Opcode.SBB, "SBB")
register_instruction(Opcode.SET, "SET", custom="set")

register_instruction(Opcode.ADDI, "ADDI", immediate=True,
                     signed_flags_imm=lambda imm, s: (imm, s),
                     regsel_imm=lambda imm, s: (s + imm))
register_instruction(Opcode.SUBI, "SUBI", immediate=True,
                     signed_flags_imm=lambda imm, s: (-imm, s),
                     regsel_imm=lambda imm, s: (s - imm))
register_instruction(Opcode.PUSHI, "PUSHI", immediate=True, custom="pushi")
register_instruction(Opcode.MOVI, "MOVI", immediate=True,
                     regsel_imm=lambda imm, s: imm)
register_instruction(Opcode.ANDI, "ANDI", immediate=True,
                     regsel_imm=lambda imm, s: (imm & s))
register_instruction(Opcode.ORI, "ORI", immediate=True,
                     regsel_imm=lambda imm, s: (imm | s))
register_instruction(Opcode.XORI, "XORI", immediate=True,
                     regsel_imm=lambda imm, s: (imm ^ s))
register_instruction(Opcode.LDI, "LDI", immediate=True,
                     custom="ldi")
register_instruction(Opcode.STI, "STI", immediate=True,
                     custom="sti")
register_instruction(Opcode.CMPI, "CMPI", immediate=True,
                     signed_flags_imm=lambda imm, s: (-imm, s),
                     no_update_dest=True, regsel_imm=lambda imm, s: (s - imm))
register_instruction(Opcode.JMPI, "JMPI", immediate=True,
                     custom="jmpi")
register_instruction(Opcode.CALLI, "CALLI", immediate=True, custom="calli")
register_instruction(Opcode.SHLI, "SHLI", immediate=True,
                     regsel_imm=lambda imm, s: (s << imm))
register_instruction(Opcode.SHRI, "SHRI", immediate=True,
                     regsel_imm=lambda imm, s: (s >> imm))
register_instruction(Opcode.ROLI, "ROLI", immediate=True,
                     regsel_imm=lambda imm, s: ((s >> imm) & 0xFFFF) |
                                               (s << (16 - imm) & 0xFFFF))
register_instruction(Opcode.RCLI, "RCLI", immediate=True)
register_instruction(Opcode.ADCI, "ADCI", immediate=True)
register_instruction(Opcode.SBBI, "SBBI", immediate=True)

register_instruction(0xFF, "STOP", custom="stop")


def _test_cc(flags, cc):
    if cc == CC.NV:
        return False
    elif cc == CC.EQ:  # EQ
        return flags["zero"]
    elif cc == CC.NE:  # NE
        return not flags["zero"]
    elif cc == CC.OS:  # OS
        return flags["overflow"]
    elif cc == CC.OC:  # OC
        return not flags["overflow"]
    elif cc == CC.HI:  # HI
        return flags["carry"] and not flags["zero"]
    elif cc == CC.LS:  # LS
        return not flags["carry"] or flags["zero"]
    elif cc == CC.P:  # P
        return not flags["negative"]
    elif cc == CC.N:  # N
        return flags["negative"]
    elif cc == CC.CS:  # CS
        return flags["carry"]
    elif cc == CC.CC:  # CC
        return not flags["carry"]
    elif cc == CC.GE:  # GE
        return flags["negative"] == flags["overflow"]
    elif cc == CC.G:  # G
        return not flags["zero"] and flags["negative"] == flags["overflow"]
    elif cc == CC.LE:  # LE
        return flags["zero"] or (flags["negative"] != flags["overflow"])
    elif cc == CC.L:  # L
        return flags["negative"] != flags["overflow"]
    elif cc == CC.AL:  # AL
        return True


class _StopException(Exception):
    """Thrown to halt execution of the program"""
    pass


class D16Cpu():

    def __init__(self, code):
        self.ip = {"has_jumped": True,
                   "i": 0}
        self.regs = [0] * 8
        self.flags = {}
        self._reset_flags()
        self.mem = (bytearray(code) +
                    bytearray([0xff, 0xff]) +
                    bytearray(0x10000 - (len(code) + 2)))

    def _reset_flags(self):
        self.flags.update({
            "negative": False,
            "zero": False,
            "carry": False,
            "overflow": False
        })

    def _current_instruction(self):
        return instructions[self._current_half()]

    def _jump_to(self, addr):
        assert addr < 0xFFFF
        self.ip["i"] = addr
        self.ip["has_jumped"] = True

    def _increment_ip(self):
        if self.ip["has_jumped"]:
            self.ip["has_jumped"] = False
        else:
            is_immediate = self._current_instruction().get("immediate")
            self.ip["i"] += 4 if is_immediate else 2

    def _update_flags(self, value):
        self.flags["overflow"] = False
        self.flags["negative"] = (value & 0xFFFF) >> 15 == 1
        self.flags["zero"] = (value & 0xFFFF) == 0
        self.flags["carry"] = (value >> 16) & 0x1 == 1

    def _update_signed_flags(self, s, d):
        s_sign = s >> 15
        d_sign = d >> 15
        result = (s + d) & 0xFFFF
        result_sign = result >> 15

        self.flags["overflow"] = (s_sign == d_sign) and result_sign != s_sign

    # Memory access {{{
    def load_word(self, addr):
        return self.mem[addr + 1] << 8 | self.mem[addr + 0]

    def store_word(self, addr, value):
        if isIo(addr):
            write_io_8(addr + 1, value >> 8)
            write_io_8(addr, value & 0xff)
        else:
            self.mem[addr + 1] = (value >> 8) & 0xFF
            self.mem[addr + 0] = (value >> 0) & 0xFF

    def load_half(self, addr):
        return self.mem[addr]

    def store_half(self, addr, value):
        if isIo(addr):
            write_io_8(addr, value & 0xff)
        else:
            self.mem[addr] = value & 0xFF

    def push(self, value):
        self.regs[7] -= 2
        self.store_word(self.regs[7], value)

    def pop(self):
        data = self.load_word(self.regs[7])
        self.regs[7] += 2
        return data
    # }}}

    # Instruction access {{{
    def _current_word(self):
        return self.load_word(self.ip["i"])

    def _next_word(self):
        return self.load_word(self.ip["i"] + 2)

    def _current_half(self):
        return self.load_half(self.ip["i"] + 1)

    def _next_half(self):
        return self.load_half(self.ip["i"] + 0)

    # }}}

    def store_reg(self, i, value):
        self.regs[i] = value & 0xFFFF

    # Instruction decoding helpers {{{
    def _decode_reg_sel(self):
        rD = (self._next_half() & 0b00000111)
        rS = (self._next_half() & 0b00111000) >> 3
        return rS, rD

    def _decode_imm(self):
        rS, rD = self._decode_reg_sel()
        return rS, rD, self._next_word()

    def _decode_reg_sel_disp(self):
        return self._next_half() & 0b01000000 > 0

    def _decode_byte_sel(self):
        return self._next_half() & 0b10000000 > 0

    def _decode_jmpsel(self):
        rD = (self._next_half() & 0b00000111)
        cc = (self._next_half() & 0b01111000) >> 3
        return rD, cc

    # }}}

    def execute_instruction(self):

        self._increment_ip()
        instruction_type = self._current_instruction()
        if "regsel" in instruction_type or \
            "regsel_imm" in instruction_type or \
                "reg_store" in instruction_type:
            regsel, regsel_imm, reg_store = \
                instruction_type.get("regsel"), \
                instruction_type.get("regsel_imm"), \
                instruction_type.get("reg_store")
            if regsel is not None:
                rS, rD = self._decode_reg_sel()
                result = regsel(self.regs[rS], self.regs[rD])

            elif regsel_imm is not None:
                rS, rD, imm = self._decode_imm()
                result = regsel_imm(imm, self.regs[rD])

            elif reg_store is not None:
                rD = reg_store
                result = self._next_half()

            else:
                assert False, "one of regsel, regsel_imm, or reg_store is " \
                              "assigned, but is `None`"

            self._update_flags(result)
            if "no_update_dest" in instruction_type:
                pass
            else:
                self.store_reg(rD, result)

        if "custom" in instruction_type:
            custom = instruction_type["custom"]
            if custom == "noop":
                pass

            elif custom in {"ldi", "ld", "sti", "st"}:
                if custom in {"ldi", "sti"}:
                    is_displacement = self._decode_reg_sel_disp()
                    rS, rD, imm = self._decode_imm()
                    addr = imm + (self.regs[rS] if is_displacement else 0)
                elif custom in {"ld", "st"}:
                    rS, rD = self._decode_reg_sel()
                    addr = self.regs[rS]
                else:
                    assert False
                addr = addr & 0xFFFF
                is_byte = self._decode_byte_sel()

                if custom in {"sti", "st"}:
                    value = self.regs[rD]
                    if is_byte:
                        self.store_half(addr, value)
                    else:
                        self.store_word(addr, value)
                elif custom in {"ldi", "ld"}:
                    value = self.load_half(addr) if is_byte \
                        else self.load_word(addr)
                    self.store_reg(rD, value)

            elif custom in {"jmp", "jmpi"}:
                if custom == "jmp":
                    rD, cc = self._decode_jmpsel()
                    addr = self.regs[rD]
                elif custom == "jmpi":
                    _, cc = self._decode_jmpsel()
                    _, _, imm = self._decode_imm()
                    addr = imm
                else:
                    assert False

                if _test_cc(self.flags, cc):
                    self._jump_to(addr)
            elif custom == "set":
                rD, cc = self._decode_jmpsel()
                self.regs[rD] = _test_cc(self.flags, cc)
            elif custom in {"push", "pushi"}:
                if custom == "push":
                    _, rd = self._decode_reg_sel()
                    data = self.regs[rd]
                else:
                    _, _, imm = self._decode_imm()
                    data = imm
                self.push(data)
            elif custom == "pop":
                _, rD = self._decode_reg_sel()
                self.store_reg(rD, self.pop())
            elif custom in {"call", "calli"}:
                ip = self.ip["i"]
                if custom == "call":
                    rD, cc = self._decode_jmpsel()
                    addr = self.regs[rD]
                    ip += 2
                elif custom == "calli":
                    _, cc = self._decode_jmpsel()
                    _, _, imm = self._decode_imm()
                    addr = imm
                    ip += 4
                else:
                    assert False

                self.push(ip)
                self._jump_to(addr)
            elif custom == "ret":
                ip = self.pop()
                self._jump_to(ip)
            elif custom == "stop":
                raise _StopException()

            else:
                assert False

        if "signed_flags" in instruction_type:
            rS, rD = self._decode_reg_sel()
            self._update_signed_flags(
                *instruction_type["signed_flags"](self.regs[rS], self.regs[rD]))
        elif "signed_flags_imm" in instruction_type:
            rS, rD, imm = self._decode_imm()
            self._update_signed_flags(
                *instruction_type["signed_flags_imm"](imm, self.regs[rS]))

    def execute(self, steps=None, debug=False):
        """
        :type steps: int | None
        :param steps: Number of instructions to execute or None to run
                    indefinitely
        """

        def do_step(i):
            self.execute_instruction()
            if debug:
                if i % 16 == 0:
                    print(D16Cpu.trace_header_str())
                print(self.trace_str())

        try:
            if steps:
                for i in range(steps):
                    do_step(i)
            else:
                i = 0
                while True:
                    do_step(i)
                    i += 1
        except _StopException:
            pass

    # Debug printing {{{
    def regs_str(self):
        return " ".join(["{:04x}".format(v) for v in self.regs])

    def flags_str(self):
        return "{:b}{:b}{:b}{:b}".format(
            self.flags["negative"],
            self.flags["zero"],
            self.flags["carry"],
            self.flags["overflow"])

    @staticmethod
    def trace_header_str():
        return "addr instr  : NZCV  r0   r1   r2   r3   r4   r5   r6   r7"

    def trace_str(self):
        return "{:04x} {:7}: {}  {}".format(
            self.ip["i"],
            self._current_instruction()["name"],
            self.flags_str(),
            self.regs_str())
        # }}}
