#!/usr/bin/env python

# See accompanying README for usage.
# You probably want `decode()` and `disassemble()`.

# The decoding structure is based on http://www.z80.info/decoding.htm
# with modifications to match libopcodes or z80ex.

# The functionality for Z80-opcodes that do not exist on the LR35902
# has been stripped, and the additional opcodes added and decoded.

import sys
import struct
from enum import Enum, auto, unique

#------------------------------------------------------------------------------
# ENUMERATIONS
#------------------------------------------------------------------------------

@unique
class DECODE_STATUS(Enum):
    OK = 0
    INVALID_INSTRUCTION = auto()
    ERROR = auto()

@unique
class INSTRTYPE(Enum):
    NOP = 0
    LOAD_EXCHANGE = auto()
    ARITHMETIC_LOGICAL = auto()
    ROTATE_SHIFT = auto()
    BIT_MANIPULATION = auto()
    JUMP_CALL_RETURN = auto()
    CPU_CONTROL = auto()

@unique
class OPER_TYPE(Enum):
    NONE = 0
    REG = auto()
    REG_DEREF = auto()
    REG_DEREF_FF00 = auto()
    REG_DEREF_INC = auto()
    REG_DEREF_DEC = auto()
    ADDR = auto()
    ADDR_DEREF = auto()
    ADDR_DEREF_FF00 = auto()
    IMM = auto()
    COND = auto()
    SP_OFFSET = auto()

@unique
class REG(Enum):
    NONE = 0
    # main register set
    # 8 bit registers individually
    A = auto()
    F = auto()
    B = auto()
    C = auto()
    D = auto()
    E = auto()
    H = auto()
    L = auto()
    # 8 bit registers in 16-bit groups
    AF = auto()
    BC = auto()
    DE = auto()
    HL = auto()
    # alternate register set
    A_ = auto()
    F_ = auto()
    B_ = auto()
    C_ = auto()
    D_ = auto()
    E_ = auto()
    H_ = auto()
    L_ = auto()
    # 8 bit registers in 16-bit groups
    AF_ = auto()
    BC_ = auto()
    DE_ = auto()
    HL_ = auto()
    # special purpose registers
    SP = auto()
    PC = auto()

@unique
class OP(Enum):
    NOP = 0
    NONI = auto() # no operation (4 T-states), no interrupts
    # LOAD_EXCHANGE
    LD = auto()
    POP = auto()
    PUSH = auto()
    MARKER_END_LOAD_EXCHANGE = auto()
    # ARITHMETIC_LOGICAL
    ADD = auto()
    ADC = auto()
    SUB = auto()
    SBC = auto()
    AND = auto()
    XOR = auto()
    OR = auto()
    CP = auto()
    RLC = auto()
    RRC = auto()
    RL = auto()
    RR = auto()
    SLA = auto()
    SRA = auto()
    SLL = auto()
    SRL = auto()
    INC = auto()
    DEC = auto()
    NEG = auto()

    DAA = auto()               # decimal adjust A
    CPL = auto()               # complement A
    SCF = auto()               # set carry flag
    CCF = auto()               # clear carry flag
    MARKER_END_ARITHMETIC_LOGICAL = auto()
    # ROTATE_SHIFT
    RLCA = auto()              # rotate left *TO* carry A
    RRCA = auto()              # right
    RLA = auto()               # rotate left *THRU* carry A
    RRA = auto()               # right
    RRD = auto()
    RLD = auto()
    MARKER_END_ROTATE_SHIFT = auto()
    # BIT_MANIPULATION
    BIT = auto()               # bit test
    RES = auto()               # bit reset
    SET = auto()               # bit set
    SWAP = auto()              # swap nibbles
    MARKER_END_BIT_MANIPULATION = auto()
    # JUMP_CALL_RETURN
    CALL = auto()
    RET = auto()
    JP = auto()                # jump
    JR = auto()                # jump relative
    RETI = auto()              # return from interrupt
    MARKER_END_JUMP_CALL_RETURN = auto()
    # CPU_CONTROL
    HALT = auto()
    STOP = auto()
    DI = auto()                # disable interrupts
    EI = auto()                # enable interrupts
    RST = auto()               # reset
    MARKER_END_CPU_CONTROL = auto()

@unique
class FLAGS(Enum):
    FLAG_C = 1 << 4            # carry flag (add/adc, sub/sbb, rla/rra/rls/rrs, rlca/rlc,sla, AND,OR,XOR resets)!
    FLAG_H = 1 << 5            # half-carry flag (if carry from bit 3 to 4)
    FLAG_N = 1 << 6            # cleared after ADD, set after SUB (used by DAA)
    FLAG_Z = 1 << 7            # zero flag

@unique
class CC(Enum):
    ALWAYS = 0
    C = auto()                 # carry
    NOT_C = auto()
    Z = auto()                 # zero
    NOT_Z = auto()

@unique
class PREFIX(Enum):
    NONE = 0
    CB = auto()

# ------------------------------------------------------------
# structs
# ------------------------------------------------------------
class Decoded():
    def __init__(self):
        self.status = DECODE_STATUS.ERROR

        self.len = 0
        # instruction type
        self.typ = None        # Z80_INSTRTYPE
        self.op = None         # Z80_OP
        # list of (OPER_TYPE, VALUE)
        self.operands = []
        # whether the entire instruction's result gets written to a reg
        # (special case for DDCB, FDCB)
        self.metaLoad = None

    def __str__(self):
        result = ''

        result += '%s\n' % str(self.op)
        for i in range(len(self.operands)):
            result += '.operands[%d] = %s' % (i, self.operands[i])
            if i < len(self.operands)-1:
                result += '\n'

        return result

#------------------------------------------------------------------------------
# DECODING
#------------------------------------------------------------------------------

# tables
# (from http:#z80.info/decoding.htm)

TABLE_R = [
    (OPER_TYPE.REG, REG.B),
    (OPER_TYPE.REG, REG.C),
    (OPER_TYPE.REG, REG.D),
    (OPER_TYPE.REG, REG.E),
    (OPER_TYPE.REG, REG.H),
    (OPER_TYPE.REG, REG.L),
    (OPER_TYPE.REG_DEREF, REG.HL),
    (OPER_TYPE.REG, REG.A)
]

# register pairs featuring SP
TABLE_RP = [
    (OPER_TYPE.REG, REG.BC),
    (OPER_TYPE.REG, REG.DE),
    (OPER_TYPE.REG, REG.HL),
    (OPER_TYPE.REG, REG.SP)
]

# register pairs featuring AF
TABLE_RP2 = [
    (OPER_TYPE.REG, REG.BC),
    (OPER_TYPE.REG, REG.DE),
    (OPER_TYPE.REG, REG.HL),
    (OPER_TYPE.REG, REG.AF)
]

# condition codes
# see cc table in ZiLOG manual for RET cc
TABLE_CC = [
    CC.NOT_Z,            # NZ
    CC.Z,                # Z
    CC.NOT_C,            # NC
    CC.C,                # C
]
# arithm/logic
TABLE_ALU_OP = [
    OP.ADD, OP.ADC, OP.SUB, OP.SBC, OP.AND, OP.XOR, OP.OR, OP.CP
]
# rotate
TABLE_ROT = [
    OP.RLC, OP.RRC, OP.RL, OP.RR, OP.SLA, OP.SRA, OP.SWAP, OP.SRL
]
TABLE_ASSORTED = [
    OP.RLCA, OP.RRCA, OP.RLA, OP.RRA, OP.DAA, OP.CPL, OP.SCF, OP.CCF
]

#------------------------------------------------------------------------------
# DECODING
#------------------------------------------------------------------------------

def int8(b):
    if b & 0x80:
        return -((b ^ 255) + 1)
    else:
        return b

def uint16(b0,b1):
    return (b1<<8)|b0

def reorder(dc):
    if len(dc.operands) == 2:
        (dc.operands[0], dc.operands[1]) = (dc.operands[1], dc.operands[0])

def xyz(byte):
    x = byte >> 6       # bits 7:6
    y = (byte >> 3) & 7 # bits 5:3
    z = byte & 7        # bits 2:0
    p = y >> 1          # bits 5:4
    q = y & 1           # bits 3:3
    return (x,y,z,p,q)

def will_deref_hl(opc):
    (x,y,z,p,q) = xyz(opc)
    # INC r[y], DEC r[y], LD r[y],n and TABLE_R[6] == '(HL)'
    if x == 0 and (z in [4,5,6]) and y == 6:
        return True
    # LD r[y],r[z] and TABLE_R[6] == '(HL)'
    if x == 1 and not (z == 6 and y == 6) and (y == 6 or z == 6):
        return True
    # alu[y] r[z] and TABLE_R[6] == '(HL)'
    if x == 2 and z == 6:
        return True
    # jp (HL)
    if x == 3 and z == 1 and q == 1 and p == 2:
        return True
    # else
    return False

def decode_unprefixed(data, addr, result):
    (x,y,z,p,q) = xyz(data[0])
    result.len += 1
    if x == 0:
        # relative jumps and assorted ops
        if z == 0:
            if y == 0:
                result.op = OP.NOP
            elif y == 1:
                result.op = OP.LD
                result.operands.append((OPER_TYPE.ADDR_DEREF, uint16(data[1], data[2])))
                result.operands.append((OPER_TYPE.REG, REG.SP))
                result.len += 2
            elif y == 2:
                result.op = OP.STOP
                result.operands.append((OPER_TYPE.IMM, 0))
                result.len += 1
            else: # 3,4,5,6,7
                result.op = OP.JR
                result.operands.append((OPER_TYPE.COND, TABLE_CC[y-4]))
                result.operands.append((OPER_TYPE.ADDR, addr + 2 + int8(data[1])))
                result.len += 1
                if y == 3:
                    result.operands = [result.operands[1]]

        elif z == 1:
            # 16-bit load immediate
            if q == 0:
                result.op = OP.LD
                result.operands.append(TABLE_RP[p])
                result.operands.append((OPER_TYPE.IMM, uint16(data[1], data[2])))
                result.len += 2
            elif q == 1:
                result.op = OP.ADD
                result.operands.append((OPER_TYPE.REG, REG.HL))
                result.operands.append(TABLE_RP[p])

        elif z == 2:
            result.op = OP.LD
            if p == 0:
                result.operands.append((OPER_TYPE.REG_DEREF, REG.BC))
                result.operands.append((OPER_TYPE.REG, REG.A))
            elif p == 1:
                result.operands.append((OPER_TYPE.REG_DEREF, REG.DE))
                result.operands.append((OPER_TYPE.REG, REG.A))
            elif p == 2:
                result.operands.append((OPER_TYPE.REG_DEREF_INC, REG.HL))
                result.operands.append((OPER_TYPE.REG, REG.A))
            elif p == 3:
                result.operands.append((OPER_TYPE.REG_DEREF_DEC, REG.HL))
                result.operands.append((OPER_TYPE.REG, REG.A))
            if q:
                reorder(result)

        elif z == 3:
            if q:
                result.op = OP.DEC
            else:
                result.op = OP.INC
            result.operands.append(TABLE_RP[p])

        elif z == 4:
            result.op = OP.INC
            result.operands.append(TABLE_R[y])

        elif z == 5:
            result.op = OP.DEC
            result.operands.append(TABLE_R[y])

        elif z == 6:
            result.op = OP.LD
            result.operands.append(TABLE_R[y])
            result.operands.append((OPER_TYPE.IMM, data[1]))
            result.len += 1

        elif z == 7:
            result.op = TABLE_ASSORTED[y]

    elif x == 1:
        # exception! not a load!
        if z == 6 and y == 6:
            result.op = OP.HALT
        # 8-bit loading
        else:
            result.op = OP.LD
            result.operands.append(TABLE_R[y])
            result.operands.append(TABLE_R[z])

    elif x == 2:
        result.op = TABLE_ALU_OP[y]
        result.operands.append((OPER_TYPE.REG, REG.A))
        result.operands.append(TABLE_R[z])
        if result.op in [OP.SUB, OP.AND, OP.XOR, OP.OR, OP.CP]:
            result.operands = [result.operands[1]]

    elif x == 3:
        # conditional return
        # no prefix, x==3, z==0
        if z == 0:
            if y < 4:
                result.op = OP.RET
                result.operands.append((OPER_TYPE.COND, TABLE_CC[y]))
            elif y == 4 or y == 6:
                result.op = OP.LD
                result.operands.append((OPER_TYPE.ADDR_DEREF_FF00, data[1]))
                result.operands.append((OPER_TYPE.REG, REG.A))
                result.len += 1
                if y == 6:
                    reorder(result)
            elif y == 5:
                result.op = OP.ADD
                result.operands.append((OPER_TYPE.REG, REG.SP))
                result.operands.append((OPER_TYPE.IMM, int8(data[1])))
                result.len += 1
            elif y == 7:
                result.op = OP.LD
                result.operands.append((OPER_TYPE.REG, REG.HL))
                result.operands.append((OPER_TYPE.SP_OFFSET, int8(data[1])))
                result.len += 1

        # pop and various ops
        # no prefix, x==3, z==1
        elif z == 1:
            if q:
                if p == 0:
                    result.op = OP.RET
                elif p == 1:
                    result.op = OP.RETI
                elif p == 2:
                    result.op = OP.JP
                    result.operands.append((OPER_TYPE.REG, REG.HL))
                elif p == 3:
                    result.op = OP.LD
                    result.operands.append((OPER_TYPE.REG, REG.SP))
                    result.operands.append((OPER_TYPE.REG, REG.HL))

            else:
                result.op = OP.POP
                result.operands.append(TABLE_RP2[p])

        # no prefix, x==3, z==2
        elif z == 2:
            if y < 4:
                result.op = OP.JP
                result.operands.append((OPER_TYPE.COND, TABLE_CC[y]))
                result.operands.append((OPER_TYPE.ADDR, uint16(data[1], data[2])))
                result.len += 2
            else:
                result.op = OP.LD
                if y == 4 or y == 6:
                    result.operands.append((OPER_TYPE.REG_DEREF_FF00, REG.C))
                    result.operands.append((OPER_TYPE.REG, REG.A))
                else:
                    result.operands.append((OPER_TYPE.ADDR_DEREF, uint16(data[1], data[2])))
                    result.operands.append((OPER_TYPE.REG, REG.A))
                    result.len += 2
                if y >= 6:
                    reorder(result)

        # no prefix, x==3, z==3
        elif z == 3:
            if y == 0:
                result.op = OP.JP
                result.operands.append((OPER_TYPE.ADDR, uint16(data[1], data[2])))
                result.len += 2
            elif y == 1:
                pass
            elif 2 <= y < 6:
                # fuckup! (D3, DB, E3, EB) are not instructions!
                result.op = OP.NONI
            elif y == 6:
                result.op = OP.DI
            elif y == 7:
                result.op = OP.EI

        elif z == 4:
            if y < 4:
                result.op = OP.CALL
                result.operands.append((OPER_TYPE.COND, TABLE_CC[y]))
                result.operands.append((OPER_TYPE.ADDR, uint16(data[1], data[2])))
                result.len += 2
            else:
                # fuckup! (E4, EC, F4, FC) are not instructions!
                result.op = OP.NONI
        elif z == 5:
            if q:
                if p:
                    # fuckup! DD, ED, and FD are invalid!!
                    result.op = OP.NONI
                else:
                    result.op = OP.CALL
                    result.operands.append((OPER_TYPE.ADDR, uint16(data[1], data[2])))
                    result.len += 2

            else:
                result.op = OP.PUSH
                result.operands.append(TABLE_RP2[p])

        elif z == 6:
            # accumulator and immediate
            result.op = TABLE_ALU_OP[y]
            result.operands.append((OPER_TYPE.REG, REG.A))
            result.operands.append((OPER_TYPE.IMM, data[1]))
            result.len += 1
            if result.op in [OP.SUB, OP.AND, OP.XOR, OP.OR, OP.CP]:
                result.operands = [result.operands[1]]

        elif z == 7:
            result.op = OP.RST
            result.operands.append((OPER_TYPE.IMM, 8*y))

def decode_cb(data, addr, result):
    (x,y,z,p,q) = xyz(data[0])
    result.len += 1
    if x:
        if x == 1:
            result.op = OP.BIT
        elif x == 2:
            result.op = OP.RES
        elif x == 3:
            result.op = OP.SET

        result.operands.append((OPER_TYPE.IMM, y))
        result.operands.append(TABLE_R[z])
    else:
        result.op = TABLE_ROT[y]
        result.operands.append(TABLE_R[z])

def decode(data, addr):
    result = Decoded()
    if not data:
        return result

    try:
        # prefix determination
        prefix = PREFIX.NONE
        if data[0] == 0xCB:
            prefix = PREFIX.CB
            data = data[1:]
            result.len = 1

        if not data:
            return result

        # 2. UNPREFIXED OPCODES
        if prefix == PREFIX.NONE:
            decode_unprefixed(data, addr, result)

        # 3. CB-PREFIXED OPCODES
        elif prefix == PREFIX.CB:
            decode_cb(data, addr, result)

    except IndexError:
        # if a decode path had insufficient bytes
        result.op = OP.NONI

    # done, recap
    if result.op == OP.NONI:
        result.status = DECODE_STATUS.INVALID_INSTRUCTION
    else:
        result.status = DECODE_STATUS.OK

        if result.op.value < OP.MARKER_END_LOAD_EXCHANGE.value:
            result.typ = INSTRTYPE.LOAD_EXCHANGE
        elif result.op.value < OP.MARKER_END_ARITHMETIC_LOGICAL.value:
            result.typ = INSTRTYPE.ARITHMETIC_LOGICAL
        elif result.op.value < OP.MARKER_END_ROTATE_SHIFT.value:
            result.typ = INSTRTYPE.ROTATE_SHIFT
        elif result.op.value < OP.MARKER_END_BIT_MANIPULATION.value:
            result.typ = INSTRTYPE.BIT_MANIPULATION
        elif result.op.value < OP.MARKER_END_JUMP_CALL_RETURN.value:
            result.typ = INSTRTYPE.JUMP_CALL_RETURN
        elif result.op.value < OP.MARKER_END_CPU_CONTROL.value:
            result.typ = INSTRTYPE.CPU_CONTROL

    return result

#------------------------------------------------------------------------------
# STRING MAKING
#------------------------------------------------------------------------------

CC_TO_STR = {
    CC.ALWAYS:"1", CC.NOT_Z:"nz", CC.Z:"z", CC.NOT_C:"nc", CC.C:"c",
}

def uint2str(d):
    if d == 0:
        return '0'
    if d >= 16:
        return '0x%x' % d
    return '%d' % d

def displ2str(d):
    if d == 0:
        return ''
    if d >= 16:
        return '+0x%x' % d
    if d > 0:
        return '+%d' % d
    if d <= -16:
        return '-0x%x' % (-d)
    return '%d' % d

def reg2str(r):
    # enum AF_ should be returned as AF'
    reg_name = r.name
    return reg_name if reg_name[-1] != '_' else reg_name[:-1]+"'"

def oper2str(oper_type, val):
    if oper_type == OPER_TYPE.REG:
        return reg2str(val)

    elif oper_type == OPER_TYPE.REG_DEREF:
        return '(%s)' % reg2str(val)

    elif oper_type == OPER_TYPE.REG_DEREF_INC:
        assert val == REG.HL
        return '(HL+)'

    elif oper_type == OPER_TYPE.REG_DEREF_DEC:
        assert val == REG.HL
        return '(HL-)'

    elif oper_type == OPER_TYPE.REG_DEREF_FF00:
        return '(0xFF00+%s)' % reg2str(val)

    elif oper_type == OPER_TYPE.ADDR:
        if val < 0:
            val = val & 0xFFFF
        return '0x%04x' % val

    elif oper_type == OPER_TYPE.ADDR_DEREF:
        return '(0x%04x)' % val

    elif oper_type == OPER_TYPE.ADDR_DEREF_FF00:
        assert 0 <= val <= 0xff
        return '(0xFF00+0x%02x)' % val

    elif oper_type == OPER_TYPE.SP_OFFSET:
        return 'SP' + ('-' if val < 0 else '+') + '0x{:02x}'.format(abs(val))

    elif oper_type == OPER_TYPE.IMM:
        return uint2str(val)

    elif oper_type == OPER_TYPE.COND:
        return CC_TO_STR[val]

    else:
        raise Exception('unknown oper_type: %s' % oper_type)

def decoded2str(decoded):
    if decoded.status != DECODE_STATUS.OK:
        return ''

    result = decoded.op.name

    if decoded.operands:
        result += ' '

    result += ','.join([oper2str(*oper) for oper in decoded.operands])

    if decoded.metaLoad:
        (oper_type, oper_val) = decoded.metaLoad
        assert oper_type == OPER_TYPE.REG
        result = 'ld %s,%s' % (reg2str(oper_val), result)

    return result

def disasm(data, pc = 0):
    if type(data) == bytes:
        decoded = decode(data, pc)
    else:
        decoded = data

    return decoded2str(decoded)
