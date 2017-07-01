#!/usr/bin/env python

# code pulled from py65, which has the license:
#
# Copyright (c) 2008-2014, Mike Naberezny and contributors.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Mike Naberezny nor the names of the contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


instruct = [""] * 256
cycletime = [0] * 256
extracycles = [0] * 256
disassemble = [('???', 'imp')] * 256

def make_instruction_decorator(instruct, disasm, allcycles, allextras):
    def instruction(name, mode, cycles, extracycles=0):
        def decorate(f):
            opcode = int(f.__name__.split('_')[-1], 16)
            instruct[opcode] = f
            disasm[opcode] = (name, mode)
            allcycles[opcode] = cycles
            allextras[opcode] = extracycles
            return f  # Return the original function
        return decorate
    return instruction

instruction = make_instruction_decorator(instruct, disassemble,
                                         cycletime, extracycles)

@instruction(name="BRK", mode="imp", cycles=7)
def inst_0x00(self):
    # pc has already been increased one
    pc = (self.pc + 1) & self.addrMask
    self.stPushWord(pc)

    self.p |= self.BREAK
    self.stPush(self.p | self.BREAK | self.UNUSED)

    self.p |= self.INTERRUPT
    self.pc = self.WordAt(self.IRQ)

@instruction(name="ORA", mode="inx", cycles=6)
def inst_0x01(self):
    self.opORA(self.IndirectXAddr)
    self.pc += 1

@instruction(name="ORA", mode="zpg", cycles=3)
def inst_0x05(self):
    self.opORA(self.ZeroPageAddr)
    self.pc += 1

@instruction(name="ASL", mode="zpg", cycles=5)
def inst_0x06(self):
    self.opASL(self.ZeroPageAddr)
    self.pc += 1

@instruction(name="PHP", mode="imp", cycles=3)
def inst_0x08(self):
    self.stPush(self.p | self.BREAK | self.UNUSED)

@instruction(name="ORA", mode="imm", cycles=2)
def inst_0x09(self):
    self.opORA(self.ProgramCounter)
    self.pc += 1

@instruction(name="ASL", mode="acc", cycles=2)
def inst_0x0a(self):
    self.opASL(None)

@instruction(name="ORA", mode="abs", cycles=4)
def inst_0x0d(self):
    self.opORA(self.AbsoluteAddr)
    self.pc += 2

@instruction(name="ASL", mode="abs", cycles=6)
def inst_0x0e(self):
    self.opASL(self.AbsoluteAddr)
    self.pc += 2

@instruction(name="BPL", mode="rel", cycles=2, extracycles=2)
def inst_0x10(self):
    self.opBCL(self.NEGATIVE)

@instruction(name="ORA", mode="iny", cycles=5, extracycles=1)
def inst_0x11(self):
    self.opORA(self.IndirectYAddr)
    self.pc += 1

@instruction(name="ORA", mode="zpx", cycles=4)
def inst_0x15(self):
    self.opORA(self.ZeroPageXAddr)
    self.pc += 1

@instruction(name="ASL", mode="zpx", cycles=6)
def inst_0x16(self):
    self.opASL(self.ZeroPageXAddr)
    self.pc += 1

@instruction(name="CLC", mode="imp", cycles=2)
def inst_0x18(self):
    self.opCLR(self.CARRY)

@instruction(name="ORA", mode="aby", cycles=4, extracycles=1)
def inst_0x19(self):
    self.opORA(self.AbsoluteYAddr)
    self.pc += 2

@instruction(name="ORA", mode="abx", cycles=4, extracycles=1)
def inst_0x1d(self):
    self.opORA(self.AbsoluteXAddr)
    self.pc += 2

@instruction(name="ASL", mode="abx", cycles=7)
def inst_0x1e(self):
    self.opASL(self.AbsoluteXAddr)
    self.pc += 2

@instruction(name="JSR", mode="abs", cycles=6)
def inst_0x20(self):
    self.stPushWord((self.pc + 1) & self.addrMask)
    self.pc = self.WordAt(self.pc)

@instruction(name="AND", mode="inx", cycles=6)
def inst_0x21(self):
    self.opAND(self.IndirectXAddr)
    self.pc += 1

@instruction(name="BIT", mode="zpg", cycles=3)
def inst_0x24(self):
    self.opBIT(self.ZeroPageAddr)
    self.pc += 1

@instruction(name="AND", mode="zpg", cycles=3)
def inst_0x25(self):
    self.opAND(self.ZeroPageAddr)
    self.pc += 1

@instruction(name="ROL", mode="zpg", cycles=5)
def inst_0x26(self):
    self.opROL(self.ZeroPageAddr)
    self.pc += 1

@instruction(name="PLP", mode="imp", cycles=4)
def inst_0x28(self):
    self.p = (self.stPop() | self.BREAK | self.UNUSED)

@instruction(name="AND", mode="imm", cycles=2)
def inst_0x29(self):
    self.opAND(self.ProgramCounter)
    self.pc += 1

@instruction(name="ROL", mode="acc", cycles=2)
def inst_0x2a(self):
    self.opROL(None)

@instruction(name="BIT", mode="abs", cycles=4)
def inst_0x2c(self):
    self.opBIT(self.AbsoluteAddr)
    self.pc += 2

@instruction(name="AND", mode="abs", cycles=4)
def inst_0x2d(self):
    self.opAND(self.AbsoluteAddr)
    self.pc += 2

@instruction(name="ROL", mode="abs", cycles=6)
def inst_0x2e(self):
    self.opROL(self.AbsoluteAddr)
    self.pc += 2

@instruction(name="BMI", mode="rel", cycles=2, extracycles=2)
def inst_0x30(self):
    self.opBST(self.NEGATIVE)

@instruction(name="AND", mode="iny", cycles=5, extracycles=1)
def inst_0x31(self):
    self.opAND(self.IndirectYAddr)
    self.pc += 1

@instruction(name="AND", mode="zpx", cycles=4)
def inst_0x35(self):
    self.opAND(self.ZeroPageXAddr)
    self.pc += 1

@instruction(name="ROL", mode="zpx", cycles=6)
def inst_0x36(self):
    self.opROL(self.ZeroPageXAddr)
    self.pc += 1

@instruction(name="SEC", mode="imp", cycles=2)
def inst_0x38(self):
    self.opSET(self.CARRY)

@instruction(name="AND", mode="aby", cycles=4, extracycles=1)
def inst_0x39(self):
    self.opAND(self.AbsoluteYAddr)
    self.pc += 2

@instruction(name="AND", mode="abx", cycles=4, extracycles=1)
def inst_0x3d(self):
    self.opAND(self.AbsoluteXAddr)
    self.pc += 2

@instruction(name="ROL", mode="abx", cycles=7)
def inst_0x3e(self):
    self.opROL(self.AbsoluteXAddr)
    self.pc += 2

@instruction(name="RTI", mode="imp", cycles=6)
def inst_0x40(self):
    self.p = (self.stPop() | self.BREAK | self.UNUSED)
    self.pc = self.stPopWord()

@instruction(name="EOR", mode="inx", cycles=6)
def inst_0x41(self):
    self.opEOR(self.IndirectXAddr)
    self.pc += 1

@instruction(name="EOR", mode="zpg", cycles=3)
def inst_0x45(self):
    self.opEOR(self.ZeroPageAddr)
    self.pc += 1

@instruction(name="LSR", mode="zpg", cycles=5)
def inst_0x46(self):
    self.opLSR(self.ZeroPageAddr)
    self.pc += 1

@instruction(name="PHA", mode="imp", cycles=3)
def inst_0x48(self):
    self.stPush(self.a)

@instruction(name="EOR", mode="imm", cycles=2)
def inst_0x49(self):
    self.opEOR(self.ProgramCounter)
    self.pc += 1

@instruction(name="LSR", mode="acc", cycles=2)
def inst_0x4a(self):
    self.opLSR(None)

@instruction(name="JMP", mode="abs", cycles=3)
def inst_0x4c(self):
    self.pc = self.WordAt(self.pc)

@instruction(name="EOR", mode="abs", cycles=4)
def inst_0x4d(self):
    self.opEOR(self.AbsoluteAddr)
    self.pc += 2

@instruction(name="LSR", mode="abs", cycles=6)
def inst_0x4e(self):
    self.opLSR(self.AbsoluteAddr)
    self.pc += 2

@instruction(name="BVC", mode="rel", cycles=2, extracycles=2)
def inst_0x50(self):
    self.opBCL(self.OVERFLOW)

@instruction(name="EOR", mode="iny", cycles=5, extracycles=1)
def inst_0x51(self):
    self.opEOR(self.IndirectYAddr)
    self.pc += 1

@instruction(name="EOR", mode="zpx", cycles=4)
def inst_0x55(self):
    self.opEOR(self.ZeroPageXAddr)
    self.pc += 1

@instruction(name="LSR", mode="zpx", cycles=6)
def inst_0x56(self):
    self.opLSR(self.ZeroPageXAddr)
    self.pc += 1

@instruction(name="CLI", mode="imp", cycles=2)
def inst_0x58(self):
    self.opCLR(self.INTERRUPT)

@instruction(name="EOR", mode="aby", cycles=4, extracycles=1)
def inst_0x59(self):
    self.opEOR(self.AbsoluteYAddr)
    self.pc += 2

@instruction(name="EOR", mode="abx", cycles=4, extracycles=1)
def inst_0x5d(self):
    self.opEOR(self.AbsoluteXAddr)
    self.pc += 2

@instruction(name="LSR", mode="abx", cycles=7)
def inst_0x5e(self):
    self.opLSR(self.AbsoluteXAddr)
    self.pc += 2

@instruction(name="RTS", mode="imp", cycles=6)
def inst_0x60(self):
    self.pc = self.stPopWord()
    self.pc += 1

@instruction(name="ADC", mode="inx", cycles=6)
def inst_0x61(self):
    self.opADC(self.IndirectXAddr)
    self.pc += 1

@instruction(name="ADC", mode="zpg", cycles=3)
def inst_0x65(self):
    self.opADC(self.ZeroPageAddr)
    self.pc += 1

@instruction(name="ROR", mode="zpg", cycles=5)
def inst_0x66(self):
    self.opROR(self.ZeroPageAddr)
    self.pc += 1

@instruction(name="PLA", mode="imp", cycles=4)
def inst_0x68(self):
    self.a = self.stPop()
    self.FlagsNZ(self.a)

@instruction(name="ADC", mode="imm", cycles=2)
def inst_0x69(self):
    self.opADC(self.ProgramCounter)
    self.pc += 1

@instruction(name="ROR", mode="acc", cycles=2)
def inst_0x6a(self):
    self.opROR(None)

@instruction(name="JMP", mode="ind", cycles=5)
def inst_0x6c(self):
    ta = self.WordAt(self.pc)
    self.pc = self.WrapAt(ta)

@instruction(name="ADC", mode="abs", cycles=4)
def inst_0x6d(self):
    self.opADC(self.AbsoluteAddr)
    self.pc += 2

@instruction(name="ROR", mode="abs", cycles=6)
def inst_0x6e(self):
    self.opROR(self.AbsoluteAddr)
    self.pc += 2

@instruction(name="BVS", mode="rel", cycles=2, extracycles=2)
def inst_0x70(self):
    self.opBST(self.OVERFLOW)

@instruction(name="ADC", mode="iny", cycles=5, extracycles=1)
def inst_0x71(self):
    self.opADC(self.IndirectYAddr)
    self.pc += 1

@instruction(name="ADC", mode="zpx", cycles=4)
def inst_0x75(self):
    self.opADC(self.ZeroPageXAddr)
    self.pc += 1

@instruction(name="ROR", mode="zpx", cycles=6)
def inst_0x76(self):
    self.opROR(self.ZeroPageXAddr)
    self.pc += 1

@instruction(name="SEI", mode="imp", cycles=2)
def inst_0x78(self):
    self.opSET(self.INTERRUPT)

@instruction(name="ADC", mode="aby", cycles=4, extracycles=1)
def inst_0x79(self):
    self.opADC(self.AbsoluteYAddr)
    self.pc += 2

@instruction(name="ADC", mode="abx", cycles=4, extracycles=1)
def inst_0x7d(self):
    self.opADC(self.AbsoluteXAddr)
    self.pc += 2

@instruction(name="ROR", mode="abx", cycles=7)
def inst_0x7e(self):
    self.opROR(self.AbsoluteXAddr)
    self.pc += 2

@instruction(name="STA", mode="inx", cycles=6)
def inst_0x81(self):
    self.opSTA(self.IndirectXAddr)
    self.pc += 1

@instruction(name="STY", mode="zpg", cycles=3)
def inst_0x84(self):
    self.opSTY(self.ZeroPageAddr)
    self.pc += 1

@instruction(name="STA", mode="zpg", cycles=3)
def inst_0x85(self):
    self.opSTA(self.ZeroPageAddr)
    self.pc += 1

@instruction(name="STX", mode="zpg", cycles=3)
def inst_0x86(self):
    self.opSTX(self.ZeroPageAddr)
    self.pc += 1

@instruction(name="DEY", mode="imp", cycles=2)
def inst_0x88(self):
    self.y -= 1
    self.y &= self.byteMask
    self.FlagsNZ(self.y)

@instruction(name="TXA", mode="imp", cycles=2)
def inst_0x8a(self):
    self.a = self.x
    self.FlagsNZ(self.a)

@instruction(name="STY", mode="abs", cycles=4)
def inst_0x8c(self):
    self.opSTY(self.AbsoluteAddr)
    self.pc += 2

@instruction(name="STA", mode="abs", cycles=4)
def inst_0x8d(self):
    self.opSTA(self.AbsoluteAddr)
    self.pc += 2

@instruction(name="STX", mode="abs", cycles=4)
def inst_0x8e(self):
    self.opSTX(self.AbsoluteAddr)
    self.pc += 2

@instruction(name="BCC", mode="rel", cycles=2, extracycles=2)
def inst_0x90(self):
    self.opBCL(self.CARRY)

@instruction(name="STA", mode="iny", cycles=6)
def inst_0x91(self):
    self.opSTA(self.IndirectYAddr)
    self.pc += 1

@instruction(name="STY", mode="zpx", cycles=4)
def inst_0x94(self):
    self.opSTY(self.ZeroPageXAddr)
    self.pc += 1

@instruction(name="STA", mode="zpx", cycles=4)
def inst_0x95(self):
    self.opSTA(self.ZeroPageXAddr)
    self.pc += 1

@instruction(name="STX", mode="zpy", cycles=4)
def inst_0x96(self):
    self.opSTX(self.ZeroPageYAddr)
    self.pc += 1

@instruction(name="TYA", mode="imp", cycles=2)
def inst_0x98(self):
    self.a = self.y
    self.FlagsNZ(self.a)

@instruction(name="STA", mode="aby", cycles=5)
def inst_0x99(self):
    self.opSTA(self.AbsoluteYAddr)
    self.pc += 2

@instruction(name="TXS", mode="imp", cycles=2)
def inst_0x9a(self):
    self.sp = self.x

@instruction(name="STA", mode="abx", cycles=5)
def inst_0x9d(self):
    self.opSTA(self.AbsoluteXAddr)
    self.pc += 2

@instruction(name="LDY", mode="imm", cycles=2)
def inst_0xa0(self):
    self.opLDY(self.ProgramCounter)
    self.pc += 1

@instruction(name="LDA", mode="inx", cycles=6)
def inst_0xa1(self):
    self.opLDA(self.IndirectXAddr)
    self.pc += 1

@instruction(name="LDX", mode="imm", cycles=2)
def inst_0xa2(self):
    self.opLDX(self.ProgramCounter)
    self.pc += 1

@instruction(name="LDY", mode="zpg", cycles=3)
def inst_0xa4(self):
    self.opLDY(self.ZeroPageAddr)
    self.pc += 1

@instruction(name="LDA", mode="zpg", cycles=3)
def inst_0xa5(self):
    self.opLDA(self.ZeroPageAddr)
    self.pc += 1

@instruction(name="LDX", mode="zpg", cycles=3)
def inst_0xa6(self):
    self.opLDX(self.ZeroPageAddr)
    self.pc += 1

@instruction(name="TAY", mode="imp", cycles=2)
def inst_0xa8(self):
    self.y = self.a
    self.FlagsNZ(self.y)

@instruction(name="LDA", mode="imm", cycles=2)
def inst_0xa9(self):
    self.opLDA(self.ProgramCounter)
    self.pc += 1

@instruction(name="TAX", mode="imp", cycles=2)
def inst_0xaa(self):
    self.x = self.a
    self.FlagsNZ(self.x)

@instruction(name="LDY", mode="abs", cycles=4)
def inst_0xac(self):
    self.opLDY(self.AbsoluteAddr)
    self.pc += 2

@instruction(name="LDA", mode="abs", cycles=4)
def inst_0xad(self):
    self.opLDA(self.AbsoluteAddr)
    self.pc += 2

@instruction(name="LDX", mode="abs", cycles=4)
def inst_0xae(self):
    self.opLDX(self.AbsoluteAddr)
    self.pc += 2

@instruction(name="BCS", mode="rel", cycles=2, extracycles=2)
def inst_0xb0(self):
    self.opBST(self.CARRY)

@instruction(name="LDA", mode="iny", cycles=5, extracycles=1)
def inst_0xb1(self):
    self.opLDA(self.IndirectYAddr)
    self.pc += 1

@instruction(name="LDY", mode="zpx", cycles=4)
def inst_0xb4(self):
    self.opLDY(self.ZeroPageXAddr)
    self.pc += 1

@instruction(name="LDA", mode="zpx", cycles=4)
def inst_0xb5(self):
    self.opLDA(self.ZeroPageXAddr)
    self.pc += 1

@instruction(name="LDX", mode="zpy", cycles=4)
def inst_0xb6(self):
    self.opLDX(self.ZeroPageYAddr)
    self.pc += 1

@instruction(name="CLV", mode="imp", cycles=2)
def inst_0xb8(self):
    self.opCLR(self.OVERFLOW)

@instruction(name="LDA", mode="aby", cycles=4, extracycles=1)
def inst_0xb9(self):
    self.opLDA(self.AbsoluteYAddr)
    self.pc += 2

@instruction(name="TSX", mode="imp", cycles=2)
def inst_0xba(self):
    self.x = self.sp
    self.FlagsNZ(self.x)

@instruction(name="LDY", mode="abx", cycles=4, extracycles=1)
def inst_0xbc(self):
    self.opLDY(self.AbsoluteXAddr)
    self.pc += 2

@instruction(name="LDA", mode="abx", cycles=4, extracycles=1)
def inst_0xbd(self):
    self.opLDA(self.AbsoluteXAddr)
    self.pc += 2

@instruction(name="LDX", mode="aby", cycles=4, extracycles=1)
def inst_0xbe(self):
    self.opLDX(self.AbsoluteYAddr)
    self.pc += 2

@instruction(name="CPY", mode="imm", cycles=2)
def inst_0xc0(self):
    self.opCMPR(self.ProgramCounter, self.y)
    self.pc += 1

@instruction(name="CMP", mode="inx", cycles=6)
def inst_0xc1(self):
    self.opCMPR(self.IndirectXAddr, self.a)
    self.pc += 1

@instruction(name="CPY", mode="zpg", cycles=3)
def inst_0xc4(self):
    self.opCMPR(self.ZeroPageAddr, self.y)
    self.pc += 1

@instruction(name="CMP", mode="zpg", cycles=3)
def inst_0xc5(self):
    self.opCMPR(self.ZeroPageAddr, self.a)
    self.pc += 1

@instruction(name="DEC", mode="zpg", cycles=5)
def inst_0xc6(self):
    self.opDECR(self.ZeroPageAddr)
    self.pc += 1

@instruction(name="INY", mode="imp", cycles=2)
def inst_0xc8(self):
    self.y += 1
    self.y &= self.byteMask
    self.FlagsNZ(self.y)

@instruction(name="CMP", mode="imm", cycles=2)
def inst_0xc9(self):
    self.opCMPR(self.ProgramCounter, self.a)
    self.pc += 1

@instruction(name="DEX", mode="imp", cycles=2)
def inst_0xca(self):
    self.x -= 1
    self.x &= self.byteMask
    self.FlagsNZ(self.x)

@instruction(name="CPY", mode="abs", cycles=4)
def inst_0xcc(self):
    self.opCMPR(self.AbsoluteAddr, self.y)
    self.pc += 2

@instruction(name="CMP", mode="abs", cycles=4)
def inst_0xcd(self):
    self.opCMPR(self.AbsoluteAddr, self.a)
    self.pc += 2

@instruction(name="DEC", mode="abs", cycles=3)
def inst_0xce(self):
    self.opDECR(self.AbsoluteAddr)
    self.pc += 2

@instruction(name="BNE", mode="rel", cycles=2, extracycles=2)
def inst_0xd0(self):
    self.opBCL(self.ZERO)

@instruction(name="CMP", mode="iny", cycles=5, extracycles=1)
def inst_0xd1(self):
    self.opCMPR(self.IndirectYAddr, self.a)
    self.pc += 1

@instruction(name="CMP", mode="zpx", cycles=4)
def inst_0xd5(self):
    self.opCMPR(self.ZeroPageXAddr, self.a)
    self.pc += 1

@instruction(name="DEC", mode="zpx", cycles=6)
def inst_0xd6(self):
    self.opDECR(self.ZeroPageXAddr)
    self.pc += 1

@instruction(name="CLD", mode="imp", cycles=2)
def inst_0xd8(self):
    self.opCLR(self.DECIMAL)

@instruction(name="CMP", mode="aby", cycles=4, extracycles=1)
def inst_0xd9(self):
    self.opCMPR(self.AbsoluteYAddr, self.a)
    self.pc += 2

@instruction(name="CMP", mode="abx", cycles=4, extracycles=1)
def inst_0xdd(self):
    self.opCMPR(self.AbsoluteXAddr, self.a)
    self.pc += 2

@instruction(name="DEC", mode="abx", cycles=7)
def inst_0xde(self):
    self.opDECR(self.AbsoluteXAddr)
    self.pc += 2

@instruction(name="CPX", mode="imm", cycles=2)
def inst_0xe0(self):
    self.opCMPR(self.ProgramCounter, self.x)
    self.pc += 1

@instruction(name="SBC", mode="inx", cycles=6)
def inst_0xe1(self):
    self.opSBC(self.IndirectXAddr)
    self.pc += 1

@instruction(name="CPX", mode="zpg", cycles=3)
def inst_0xe4(self):
    self.opCMPR(self.ZeroPageAddr, self.x)
    self.pc += 1

@instruction(name="SBC", mode="zpg", cycles=3)
def inst_0xe5(self):
    self.opSBC(self.ZeroPageAddr)
    self.pc += 1

@instruction(name="INC", mode="zpg", cycles=5)
def inst_0xe6(self):
    self.opINCR(self.ZeroPageAddr)
    self.pc += 1

@instruction(name="INX", mode="imp", cycles=2)
def inst_0xe8(self):
    self.x += 1
    self.x &= self.byteMask
    self.FlagsNZ(self.x)

@instruction(name="SBC", mode="imm", cycles=2)
def inst_0xe9(self):
    self.opSBC(self.ProgramCounter)
    self.pc += 1

@instruction(name="NOP", mode="imp", cycles=2)
def inst_0xea(self):
    pass

@instruction(name="CPX", mode="abs", cycles=4)
def inst_0xec(self):
    self.opCMPR(self.AbsoluteAddr, self.x)
    self.pc += 2

@instruction(name="SBC", mode="abs", cycles=4)
def inst_0xed(self):
    self.opSBC(self.AbsoluteAddr)
    self.pc += 2

@instruction(name="INC", mode="abs", cycles=6)
def inst_0xee(self):
    self.opINCR(self.AbsoluteAddr)
    self.pc += 2

@instruction(name="BEQ", mode="rel", cycles=2, extracycles=2)
def inst_0xf0(self):
    self.opBST(self.ZERO)

@instruction(name="SBC", mode="iny", cycles=5, extracycles=1)
def inst_0xf1(self):
    self.opSBC(self.IndirectYAddr)
    self.pc += 1

@instruction(name="SBC", mode="zpx", cycles=4)
def inst_0xf5(self):
    self.opSBC(self.ZeroPageXAddr)
    self.pc += 1

@instruction(name="INC", mode="zpx", cycles=6)
def inst_0xf6(self):
    self.opINCR(self.ZeroPageXAddr)
    self.pc += 1

@instruction(name="SED", mode="imp", cycles=2)
def inst_0xf8(self):
    self.opSET(self.DECIMAL)

@instruction(name="SBC", mode="aby", cycles=4, extracycles=1)
def inst_0xf9(self):
    self.opSBC(self.AbsoluteYAddr)
    self.pc += 2

@instruction(name="SBC", mode="abx", cycles=4, extracycles=1)
def inst_0xfd(self):
    self.opSBC(self.AbsoluteXAddr)
    self.pc += 2

@instruction(name="INC", mode="abx", cycles=7)
def inst_0xfe(self):
    self.opINCR(self.AbsoluteXAddr)
    self.pc += 2


print cycletime
print extracycles