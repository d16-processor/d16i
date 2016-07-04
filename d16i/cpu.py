instructions = 256 * [None]  # type: list[dict[str, Any]]


def register_instruction(value, name, **kwargs):
    assert instructions[value] is None,\
        "attempted to insert duplicate instruction"
    kwargs.update({"name": name})
    instructions[value] = kwargs


register_instruction(0x00, "NOP", custom="noop")
register_instruction(0x01, "ADD", signed_flags=lambda s, d: (s, d),
                     regsel=lambda s, d: (s + d))
register_instruction(0x02, "SUB", signed_flags=lambda s, d: (-s, d),
                     regsel=lambda s, d: (d - s))
register_instruction(0x03, "PUSH")
register_instruction(0x04, "POP")
register_instruction(0x05, "MOVB_R0", reg_store=0)
register_instruction(0x06, "MOVB_R1", reg_store=1)
register_instruction(0x07, "MOVB_R2", reg_store=2)
register_instruction(0x08, "MOVB_R3", reg_store=3)
register_instruction(0x09, "MOVB_R4", reg_store=4)
register_instruction(0x0A, "MOVB_R5", reg_store=5)
register_instruction(0x0B, "MOVB_R6", reg_store=6)
register_instruction(0x0C, "MOVB_R7", reg_store=7)
register_instruction(0x0D, "MOV", regsel=lambda s, d: s)
register_instruction(0x0E, "AND", regsel=lambda s, d: (s & d))
register_instruction(0x0F, "OR", regsel=lambda s, d: (s | d))
register_instruction(0x10, "XOR", regsel=lambda s, d: (s ^ d))
register_instruction(0x11, "NOT", regsel=lambda s, d: (~d))
register_instruction(0x12, "NEG", regsel=lambda s, d: (-s) & 0xFFFF)
register_instruction(0x13, "LD", custom="ld")
register_instruction(0x14, "ST", custom="st")
register_instruction(0x15, "CMP", signed_flags=lambda s, d: (-s, d))
register_instruction(0x16, "JMP", custom="jmp")
register_instruction(0x17, "CALL")
register_instruction(0x18, "SPEC")
register_instruction(0x19, "SHL", regsel=lambda s, d: (d << s))
register_instruction(0x1A, "SHR", regsel=lambda s, d: (d >> s))
register_instruction(0x1B, "ROL", regsel=lambda s, d: (d >> s & 0xFFFF) |
                                                      (d << (16 - s) & 0xFFFF))
register_instruction(0x1C, "RCL")
register_instruction(0x1D, "LDCP")
register_instruction(0x1E, "STCP")
register_instruction(0x1F, "ADC")
register_instruction(0x20, "SBB")

register_instruction(0x81, "ADDI", immediate=True,
                     signed_flags_imm=lambda imm, s: (imm, s),
                     regsel_imm=lambda imm, s: (s + imm))
register_instruction(0x82, "SUBI", immediate=True,
                     signed_flags_imm=lambda imm, s: (-imm, s),
                     regsel_imm=lambda imm, s: (s - imm))
register_instruction(0x83, "PUSHI", immediate=True)
register_instruction(0x8D, "MOVI", immediate=True,
                     regsel_imm=lambda imm, s: imm)
register_instruction(0x8E, "ANDI", immediate=True,
                     regsel_imm=lambda imm, s: (imm & s))
register_instruction(0x8F, "ORI", immediate=True,
                     regsel_imm=lambda imm, s: (imm | s))
register_instruction(0x90, "XORI", immediate=True,
                     regsel_imm=lambda imm, s: (imm ^ s))
register_instruction(0x93, "LDI", immediate=True,
                     custom="ldi")
register_instruction(0x94, "STI", immediate=True,
                     custom="sti")
register_instruction(0x95, "CMPI", immediate=True,
                     signed_flags_imm=lambda imm, s: (-imm, s))
register_instruction(0x96, "JMPI", immediate=True,
                     custom="jmpi")
register_instruction(0x97, "CALLI", immediate=True)
register_instruction(0x99, "SHLI", immediate=True,
                     regsel_imm=lambda imm, s: (s << s))
register_instruction(0x9A, "SHRI", immediate=True,
                     regsel_imm=lambda imm, s: (s >> s))
register_instruction(0x9B, "ROLI", immediate=True,
                     regsel_imm=lambda imm, s: (s >> s & 0xFFFF) |
                                               (s << (16 - s) & 0xFFFF))
register_instruction(0x9C, "RCLI", immediate=True)
register_instruction(0x9F, "ADC", immediate=True)
register_instruction(0xA0, "SBB", immediate=True)

register_instruction(0xFF, "STOP", custom="stop")


def _test_cc(flags, cc):
    if cc == 0x0:
        return False
    elif cc == 0x1:  # EQ
        return flags["zero"]
    elif cc == 0x2:  # NE
        return not flags["zero"]
    elif cc == 0x3:  # OS
        return flags["overflow"]
    elif cc == 0x4:  # OC
        return not flags["overflow"]
    elif cc == 0x5:  # HI
        return flags["carry"] and not flags["zero"]
    elif cc == 0x6:  # LS
        return not flags["carry"] or flags["zero"]
    elif cc == 0x7:  # P
        return not flags["negative"]
    elif cc == 0x8:  # N
        return flags["negative"]
    elif cc == 0x9:  # CS
        return flags["carry"]
    elif cc == 0xA:  # CC
        return not flags["carry"]
    elif cc == 0xB:  # GE
        return flags["negative"] == flags["overflow"]
    elif cc == 0xC:  # G
        return not flags["zero"] and flags["negative"] == flags["overflow"]
    elif cc == 0xD:  # LE
        return flags["zero"] and flags["negative"] != flags["overflow"]
    elif cc == 0xE:  # L
        return flags["negative"] != flags["overflow"]
    elif cc == 0xF:  # AL
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

        self._update_flags(result)
        self.flags["overflow"] = (s_sign == d_sign) and result_sign != s_sign


    # Memory access {{{
    def load_word(self, addr):
        return self.mem[addr + 1] << 8 | self.mem[addr + 0]

    def store_word(self, addr, value):
        self.mem[addr + 1] = (value >> 8) & 0xFF
        self.mem[addr + 0] = (value >> 0) & 0xFF

    def load_half(self, addr):
        return self.mem[addr]

    def store_half(self, addr, value):
        self.mem[addr] = value & 0xFF
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

        self._reset_flags()
        self._increment_ip()
        instruction_type = self._current_instruction()
        if "regsel" in instruction_type or\
           "regsel_imm" in instruction_type or\
           "reg_store" in instruction_type:
            regsel, regsel_imm, reg_store =\
                instruction_type.get("regsel"),\
                instruction_type.get("regsel_imm"),\
                instruction_type.get("reg_store")
            if regsel is not None:
                rS, rD = self._decode_reg_sel()
                result = regsel(self.regs[rS], self.regs[rD])

            elif regsel_imm is not None:
                rS, rD, imm = self._decode_imm()
                result = regsel_imm(imm, self.regs[rS])

            elif reg_store is not None:
                rD = reg_store
                result = self._next_half()

            else:
                assert False, "one of regsel, regsel_imm, or reg_store is "\
                              "assigned, but is `None`"

            self._update_flags(result)
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

                is_byte = self._decode_byte_sel()

                if custom in {"sti", "st"}:
                    value = self.regs[rS]
                    if is_byte:
                        self.store_half(addr, value)
                    else:
                        self.store_word(addr, value)
                elif custom in {"ldi", "ld"}:
                    value = self.load_half(addr) if is_byte\
                        else self.load_word(addr)
                    self.store_reg(rD, value)

            elif custom in {"jmp", "jmpi"}:
                if custom == "jmp":
                    rD, cc = self._decode_jmpsel()
                    addr = rD
                elif custom == "jmpi":
                    _, cc = self._decode_jmpsel()
                    _, _, imm = self._decode_imm()
                    addr = imm
                else:
                    assert False

                if _test_cc(self.flags, cc):
                    self._jump_to(addr)

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
