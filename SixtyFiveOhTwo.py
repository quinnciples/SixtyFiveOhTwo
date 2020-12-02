# 6502 machine code processor
from enum import Enum


class OPCODE(Enum):
    LDA_IM = 0xA9


class CPU6502:

    version = '0.01'
    MAX_MEMORY_SIZE = 1024 * 64  # 64k memory size

    def __init__(self):

        self.program_counter = 0xFFFC
        self.stack_pointer = 0x0100

        self.registers = {
            'A': 0,
            'X': 0,
            'Y': 0
        }

        self.flags = {
            'C': 0,
            'Z': 0,
            'I': 0,
            'D': 0,
            'B': 0,
            'V': 0,
            'N': 0
        }

        self.memory = [0] * CPU6502.MAX_MEMORY_SIZE

        self.cycles = 0

    def reset(self):
        self.program_counter = 0xFFFC
        self.stack_pointer = 0x0100

        # Reset all registers to zero
        self.registers = dict.fromkeys(self.registers.keys(), 0)

        # Reset all flags to zero
        self.flags = dict.fromkeys(self.flags.keys(), 0)

        self.memory = [0] * CPU6502.MAX_MEMORY_SIZE

    def printState(self):
        combined = {**self.registers, **self.flags, **{'PC': '0x{0:0{1}X}'.format(self.program_counter,4), 'SP': '0x{0:0{1}X}'.format(self.stack_pointer,4)}}
        headerString = '\t'.join(combined)
        valueString = '\t'.join(str(v) for v in combined.values())
        print(headerString)
        print(valueString)


cpu = CPU6502()
cpu.printState()
cpu.reset()
cpu.printState()
