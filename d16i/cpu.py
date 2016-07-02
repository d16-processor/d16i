from operator import setitem
import sys

instructions = 255 * [None]

def register_instruction(value, name, **kwargs):
    assert instructions[value] is None, "attempted to insert duplicate instruction"
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
register_instruction(0x0F, "OR",  regsel=lambda s, d: (s | d))
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
register_instruction(0x1B, "ROL", regsel=lambda s, d: (d >> s & 0xFFFF) | (d << (16 - s) & 0xFFFF))
register_instruction(0x1C, "RCL")
register_instruction(0x1D, "LDCP")
register_instruction(0x1E, "STCP")
register_instruction(0x1F, "ADC")
register_instruction(0x20, "SBB")


register_instruction(0x81, "ADDI",  immediate=True,
                                    signed_flags_imm=lambda imm, s: (imm, s),
                                    regsel_imm=lambda imm, s: (s + imm))
register_instruction(0x82, "SUBI",  immediate=True,
                                    signed_flags_imm=lambda imm, s: (-imm, s),
                                    regsel_imm=lambda imm, s: (s - imm))
register_instruction(0x83, "PUSHI", immediate=True)
register_instruction(0x8D, "MOVI",  immediate=True,
                                    regsel_imm=lambda imm, s: imm)
register_instruction(0x8E, "ANDI",  immediate=True,
                                    regsel_imm=lambda imm, s: (imm & s))
register_instruction(0x8F, "ORI",   immediate=True,
                                    regsel_imm=lambda imm, s: (imm | s))
register_instruction(0x90, "XORI",  immediate=True,
                                    regsel_imm=lambda imm, s: (imm ^ s))
register_instruction(0x93, "LDI",   immediate=True,
                                    custom="ldi")
register_instruction(0x94, "STI",   immediate=True,
                                    custom="sti")
register_instruction(0x95, "CMPI",  immediate=True,
                                    signed_flags_imm=lambda imm, s: (-imm, s))
register_instruction(0x96, "JMPI",  immediate=True,
                                    custom="jmpi")
register_instruction(0x97, "CALLI", immediate=True)
register_instruction(0x99, "SHLI",  immediate=True,
                                    regsel_imm=lambda imm, s: (s << s))
register_instruction(0x9A, "SHRI",  immediate=True,
                                    regsel_imm=lambda imm, s: (s >> s))
register_instruction(0x9B, "ROLI",  immediate=True,
                                    regsel_imm=lambda imm, s: (s >> s & 0xFFFF) | (s << (16 - s) & 0xFFFF))
register_instruction(0x9C, "RCLI",  immediate=True)
register_instruction(0x9F, "ADC",   immediate=True)
register_instruction(0xA0, "SBB",   immediate=True)



def test_cc(flags, cc):
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




class D16Cpu():
    def __init__(self, code):
        self.ip = {"has_branched": False,
                   "i": 0}
        self.regs = [0] * 8
        self.flags = {}
        self._reset_flags()
        self.mem = code + (0xFFFF - len(code)) * [0]

    def _reset_flags(self):
        self.flags.update({
            "negative": False,
            "zero": False,
            "carry": False,
            "overflow": False
        })

    def _current_instruction(self):
        return instructions[mem[i]]


    def _update_flags(self, value):
        self.flags["overflow"] = False
        self.flags["negative"] = (value & 0xFFFF) >> 15 == 1
        self.flags["zero"] = (value & 0xFFFF) == 0
        self.flags["carry"] = (value >> 16) & 0x1 == 1

    def _update_signed_flags(flags, s, d):
        s_sign = s >> 15
        d_sign = d >> 15
        result = (s + d) & 0xFFFF
        result_sign = result >> 15

        self._update_flags(result)
        self.flags["overflow"] = (s_sign == d_sign) and result_sign != s_sign


    def _current_word(self):
        return self.mem[i + 0] << 8 | self.mem[i + 1]
    def _next_word(self):
        return self.mem[i + 2] << 8 | self.mem[i + 3]
    def _current_half(self):
        return self.mem[i + 0]
    def _next_half(self):
        return self.mem[i + 1]


    # Instruction decoding helpers {{{
    def decode_reg_sel(self):
        rD = (self._next_half() & 0b00000111)
        rS = (self._next_half() & 0b00111000) >> 3
        return rS, rD

    def decode_imm(self):
        rS, rD = decode_reg_sel(self.mem, i)
        return rS, rD, self._next_word()

    def decode_reg_sel_disp(self):
        return self._next_half() & 0b01000000 > 0
    def decode_byte_sel(self):
        return self._next_half() & 0b10000000 > 0
    def decode_reg_store(self):
        return self._next_half()

    def decode_jmpsel(self):
        rD = (self._next_half() & 0b00000111)
        cc = (self._next_half() & 0b01111000) >> 3
        return rD, cc
    # }}}


    # Debug printing {{{
    def regs_to_str(self):
        return " ".join(["{:04x}".format(v) for v in self.regs])

    def flags_to_str(self):
        return "{:b}{:b}{:b}{:b}".format(
            self.flags["negative"],
            self.flags["zero"],
            self.flags["carry"],
            self.flags["overflow"])
    # }}}


def main(code):
    print("addr instr  : NZCV  r0   r1   r2   r3   r4   r5   r6   r7")
    while i < len(code):
        i_start = i
        instruction_type = instructions[mem[i]]
        if "regsel" in instruction_type:
            rS, rD = decode_reg_sel(mem, i)
            regs[rD] = instruction_type["regsel"](regs[rS], regs[rD])
            update_flags(flags, regs[rD])
            regs[rD] &= 0xFFFF
        elif "regsel_manual" in instruction_type:
            rS, rD = decode_reg_sel(mem, i)
            instruction_type["regsel_manual"](rS, rD, regs, mem, flags)
        elif "regsel_imm" in instruction_type:
            rS, rD, imm = decode_imm(mem, i)
            regs[rD] = instruction_type["regsel_imm"](imm, regs[rS])
            update_flags(flags, regs[rD])
            regs[rD] &= 0xFFFF
        elif "reg_store" in instruction_type:
            rD = instruction_type["reg_store"]
            data = decode_reg_store(mem, i)
            regs[rD] = data
            update_flags(flags, regs[rD])
            regs[rD] &= 0xFFFF
        elif "regsel_manual_imm" in instruction_type:
            rS, rD, imm = decode_imm(mem, i)
            instruction_type["regsel_manual_imm"](imm,regs[rD],regs,mem,flags)

        if "custom" in instruction_type:
            custom = instruction_type["custom"]
            if custom == "noop":
                pass
            elif custom == "ldi":
                disp = decode_reg_sel_disp(mem, i)
                byte = decode_byte_sel(mem,i)
                rS, rD, imm = decode_imm(mem, i)
                if disp:
                    if byte:
                        regs[rD] = mem[imm+regs[rS]]
                    else:
                        regs[rD] = (mem[imm+regs[rS]+1]<<8) | mem[imm+regs[rS]]
                else:
                    if byte:
                       regs[rD] = mem[imm]
                    else:
                        regs[rD] = (mem[imm+1]<<8) | mem[imm]
            elif custom == "ld":
                byte = decode_byte_sel(mem, i)
                if byte:
                    regs[rD] = mem[regs[rS]]
                else:
                    regs[rD] = (mem[regs[rS]+1]<<8) | mem[regs[rS]]
            elif custom == "sti":
                disp = decode_reg_sel_disp(mem, i)
                byte = decode_byte_sel(mem,i)
                rS,rD,imm = decode_imm(mem,i)
                if disp:
                    mem[regs[rD] + imm] = regs[rS]&0xff
                    if not byte:
                        mem[regs[rD] + imm + 1] = (regs[rS]>>8) & 0xff
                else:
                    mem[imm] = regs[rS]&0xff
                    if not byte:
                        mem[imm+1] = (regs[rS]>>8) & 0xff
            elif custom == "st":
                rS, rD = decode_reg_sel(mem,i)
                byte = decode_byte_sel(mem,i)
                mem[regs[rD]] = regs[rS]&0xff
                if not byte:
                    mem[regs[rD]+1] = (regs[rS]>>8)&0xff
            elif custom == "jmp":
                rD, cc = decode_jmpsel(mem, i)
                if test_cc(flags,cc):
                    i = regs[rD]
                else:
                    pass
            elif custom == "jmpi":
                _, cc = decode_jmpsel(mem, i)
                _, _, imm = decode_imm(mem, i)
                if test_cc(flags,cc):
                    i = imm
                else:
                    pass
            else:
                assert False

        if "signed_flags" in instruction_type:
            rS, rD = decode_reg_sel(mem, i)
            update_signed_flags(flags, *instruction_type["signed_flags"](regs[rS], regs[rD]))
        elif "signed_flags_imm" in instruction_type:
            rS, rD, imm = decode_imm(mem, i)
            update_signed_flags(flags, *instruction_type["signed_flags_imm"](imm, regs[rS]))

        if i == i_start:  # none of the instructions jumped
                          # TODO this is actually wrong, what if it jumps to the same instruction
            if "immediate" in instruction_type and instruction_type["immediate"]:
                i += 4
            else:
                i += 2

        print("{:04x} {:7}: {}  {}".format(i, instruction_type["name"],
                                           flags_to_str(flags), regs_to_str(regs)))



def little_to_big_endian_16(data):
    assert len(data) % 2 == 0
    result = len(data) * [0]
    for i in range(0, int(len(data) / 2)):
        result[2*i] = data[2*i+1]
        result[2*i+1] = data[2*i]
    return result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: d16i [binary]")
        sys.exit(1)
    with open(sys.argv[1], "rb") as code:
        main(little_to_big_endian_16(bytearray(code.read())))
