from operator import setitem
import sys

instructions = 255 * [None]

def register_instruction(value, name, **kwargs):
    kwargs.update({"name": name})
    instructions[value] = kwargs


register_instruction(0x00, "NOP", custom="noop")
register_instruction(0x01, "ADD", regsel=lambda s, d: (s + d))
register_instruction(0x02, "SUB",  regsel=lambda s, d: (d - s))
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
register_instruction(0x15, "CMP", regsel_manual=lambda s, d, regs, mem, flags: update_flags(flags, regs[d] - regs[s]))
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


register_instruction(0x81, "ADDI", regsel_imm=lambda imm, d: (d + imm))
register_instruction(0x82, "SUBI", regsel_imm=lambda imm, d: (d - imm))
register_instruction(0x83, "PUSHI")
register_instruction(0x8D, "MOVI", regsel_imm=lambda imm, d: imm)
register_instruction(0x8E, "ANDI", regsel_imm=lambda imm, d: (imm & d))
register_instruction(0x8F, "ORI",  regsel_imm=lambda imm, d: (imm | d))
register_instruction(0x90, "XORI", regsel_imm=lambda imm, d: (imm ^ d))
register_instruction(0x93, "LDI", custom="ldi")
register_instruction(0x94, "STI", custom="sti")
register_instruction(0x95, "CMPI", regsel_manual_imm=lambda imm, d, regs, mem, flags: update_flags(flags, d - imm))
register_instruction(0x96, "JMPI", custom="jmpi")
register_instruction(0x97, "CALLI")
register_instruction(0x99, "SHLI", regsel_imm=lambda imm, d: (d << s))
register_instruction(0x9A, "SHRI", regsel_imm=lambda imm, d: (d >> s))
register_instruction(0x9B, "ROLI", regsel_imm=lambda imm, d: (d >> s & 0xFFFF) | (d << (16 - s) & 0xFFFF))
register_instruction(0x9C, "RCLI")
register_instruction(0x9F, "ADC")
register_instruction(0xA0, "SBB")


def decode_reg_sel(code, i):
    byte = code[i + 1]
    rD = byte & 0b111
    rS = (byte >> 3) & 0b111
    return rS, rD

def decode_imm(code, i):
    rS, rD = decode_reg_sel(code, i)
    imm = code[i + 2] << 8 | code[i + 3]
    return rS, rD, imm

def decode_reg_sel_disp(code, i):
    isDisp = code[i + 1] >> 7 & 0x1
    if isDisp:
        return decode_imm(code, i)
    else:
        rS, rD = decode_reg_sel(code, i)
        return rS, rD, None

def decode_reg_store(code, i):
    return code[i+1]

def decode_jmpsel(code, i):
    cc = (code[i + 1] >> 3) & 0xf
    rD = code[i + 1] & 0x7
    return rD, cc

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


def update_flags(flags, value):
    flags["overflow"] = value > 0xFFFF
    flags["negative"] = (value & 0xFFFF) >> 7 == 1
    flags["zero"] = (value & 0xFFFF) == 0
    flags["carry"] = (value >> 8) & 0x1 == 1

def regs_to_str(regs):
    result = ""
    for v in regs:
        result += "{:02x} ".format(v)
    return result

def flags_to_str(flags):
    return "{:b}{:b}{:b}{:b}".format(flags["negative"], flags["zero"],
            flags["carry"], flags["overflow"])

def main(code):
    i = 0
    regs = [0] * 8
    flags = {"negative": 0, "zero": 0, "carry": 0, "overflow": 0}
    mem = code + (0xFFFF - len(code)) * [0]
    print("addr instr  : NZCV r0 r1 r2 r3 r4 r5 r6 r7")
    while i < len(code):
        instruction_type = instructions[mem[i]]
        print("{:04} {:7}: {}  {}".format(i, instruction_type["name"],
            flags_to_str(flags), regs_to_str(regs)))
        if "regsel" in instruction_type:
            rS, rD = decode_regsel(mem, i)
            regs[rD] = instruction_type["regsel"](regs[rS], regs[rD])
            update_flags(flags, regs[rD])
            regs[rD] &= 0xFFFF
            i += 2
        elif "regsel_manual" in instruction_type:
            rS, rD = decode_regsel(mem, i)
            instruction_type["regsel_manual"](rS, rD, regs, mem, flags)
            i += 2
        elif "regsel_imm" in instruction_type:
            rS, rD, imm = decode_imm(mem, i)
            regs[rD] = instruction_type["regsel_imm"](imm, regs[rS])
            update_flags(flags, regs[rD])
            regs[rD] &= 0xFFFF
            i += 4
        elif "reg_store" in instruction_type:
            rD = instruction_type["reg_store"]
            data = decode_reg_store(mem, i)
            regs[rD] = data
            update_flags(flags, regs[rD])
            regs[rD] &= 0xFFFF
            i += 2
        elif "regsel_manual_imm" in instruction_type:
            rS, rD, imm = decode_imm(mem, i)
            instruction_type["regsel_manual_imm"](imm,regs[rD],regs,mem,flags)
            i += 4
        elif "custom" in instruction_type:
            custom = instruction_type["custom"]
            if custom == "noop":
                i += 2
            elif custom == "ldi" or custom == "ld":
                rS, rD, disp = decode_reg_sel_disp(mem, i)
                if disp:
                    regs[rD] = mem[regs[rS] + disp]
                    i += 4
                else:
                    regs[rD] = mem[regs[rS]]
                    i += 2
            elif custom == "sti" or custom == "st":
                rS, rD, disp = decode_reg_sel_disp(mem, i)
                if disp:
                    mem[regs[rD] + disp] = regs[rS]
                    i += 4
                else:
                    mem[regs[rD]] = regs[rS]
                    i += 2
            elif custom == "jmp":
                rD, cc = decode_jmpsel(mem, i)
                if test_cc(flags,cc):
                    i = regs[rD]
                else:
                    i += 2
            elif custom == "jmpi":
                _, cc = decode_jmpsel(mem, i)
                _, _, imm = decode_imm(mem, i)
                if test_cc(flags,cc):
                    i = imm
                else:
                    i += 4
            else:
                assert False
        else:
            assert False, "Unknown operation 0x{:x} at {}".format(mem[i], i)



def little_to_big_endian_16(data):
    assert len(data) % 2 == 0
    result = len(data) * [0]
    for i in range(0, int(len(data) / 2)):
        result[2*i] = data[2*i+1]
        result[2*i+1] = data[2*i]
    return result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: d16i [binary]"
        sys.exit(1)
    with open(sys.argv[1], "rb") as code:
        main(little_to_big_endian_16(bytearray(code.read())))
