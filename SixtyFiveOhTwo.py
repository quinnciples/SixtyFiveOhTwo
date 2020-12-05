# 6502 machine code processor


class CPU6502:

    """

    All single-byte instructions waste a cycle reading and ignoring the byte that comes immediately after the instruction (this means no instruction can take less than two cycles).
    Zero page,X, zero page,Y, and (zero page,X) addressing modes spend an extra cycle reading the unindexed zero page address.
    Absolute,X, absolute,Y, and (zero page),Y addressing modes need an extra cycle if the indexing crosses a page boundary, or if the instruction writes to memory.
    The conditional branch instructions require an extra cycle if the branch actually happens, and a second extra cycle if the branch happens and crosses a page boundary.
    Read-modify-write instructions (ASL, DEC, INC, LSR, ROL, ROR) need a cycle for the modify stage (except in accumulator mode, which doesn't access memory).
    Instructions that pull data off the stack (PLA, PLP, RTI, RTS) need an extra cycle to increment the stack pointer (because the stack pointer points to the first empty address on the stack, not the last used address).
    RTS needs an extra cycle (in addition to the single-byte penalty and the pull-from-stack penalty) to increment the return address.
    JSR spends an extra cycle juggling the return address internally.
    Hardware interrupts take the same number of cycles as a BRK instruction (even in the case of RESET, which goes through the motions of pushing the return address and status on the stack, but doesn't actually alter the stack).

    """

    """

            ORA 	AND 	EOR 	ADC 	STA 	LDA 	CMP 	SBC
    (zp,X) 	01 	    21 	    41 	    61 	    81 	    A1 	    C1 	    E1
    zp 	    05 	    25 	    45 	    65 	    85 	    A5 	    C5 	    E5
    # 	    09 	    29 	    49 	    69 	  	A9 	    C9 	    E9
    abs 	0D 	    2D 	    4D 	    6D 	    8D 	    AD 	    CD 	    ED
    (zp),Y 	11 	    31 	    51 	    71 	    91 	    B1 	    D1 	    F1
    zp,X 	15 	    35 	    55 	    75 	    95 	    B5 	    D5 	    F5
    abs,Y 	19 	    39 	    59 	    79 	    99 	    B9 	    D9 	    F9
    abs,X 	1D 	    3D 	    5D 	    7D 	    9D 	    BD 	    DD 	    FD

    """

    version = '0.01'
    MAX_MEMORY_SIZE = 1024 * 64  # 64k memory size
    opcodes = {0xA9: 'LDA_IM',
               0xA5: 'LDA_ZP',
               0xB5: 'LDA_ZP_X',
               0xAD: 'LDA_ABS',
               0xBD: 'LDA_ABS_X',
               0xB9: 'LDA_ABS_Y',
               0xA1: 'LDA_IND_X',
               0xB1: 'LDA_IND_Y',
               0x20: 'JSR',
               0xEA: 'NOP'}

    def __init__(self, cycle_limit=30):

        self.program_counter = 0xFF10
        self.stack_pointer = 0x0100
        self.cycle_limit = cycle_limit

        self.INS = None

        self.registers = {
            'A': 0,
            'X': 0,
            'Y': 0,
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
        self.log = []

        self.initializeLog()

    def memoryDump(self, startingAddress=0x0000, endingAddress=0x0000):
        print('\nMemory Dump:\n')
        while startingAddress <= endingAddress and startingAddress <= CPU6502.MAX_MEMORY_SIZE:
            header = '0x{0:0{1}X}'.format(startingAddress, 4) + '\t'
            row = '\t'.join('0x{0:0{1}X}'.format(self.memory[v], 2) for v in range(startingAddress, min(startingAddress + 8, CPU6502.MAX_MEMORY_SIZE)))
            line = header + row
            print(line)
            startingAddress += 8

    def cycleInc(self):
        self.logState()
        self.cycles += 1

    def programCounterInc(self):
        self.program_counter += 1
        if self.program_counter >= CPU6502.MAX_MEMORY_SIZE:
            self.program_counter = 0

    def reset(self, program_counter=0xFF10):
        self.program_counter = program_counter
        self.stack_pointer = 0x0100
        self.cycles = 0

        # Reset all registers to zero
        self.registers = dict.fromkeys(self.registers.keys(), 0)

        self.memory = [0] * CPU6502.MAX_MEMORY_SIZE

    def readMemory(self, increment_pc=True, address=None) -> int:
        if not address:
            data = self.memory[self.program_counter]
        else:
            data = self.memory[address]

        if increment_pc:
            self.programCounterInc()

        self.cycleInc()
        return data

    def setFlags(self, register, flags=[]):
        if 'Z' in flags:
            if self.registers[register] == 0:
                self.registers['Z'] = 1
            else:
                self.registers['Z'] = 0
        if 'N' in flags:
            if self.registers[register] & 0b10000000 > 0:
                self.registers['N'] = 1
            else:
                self.registers['N'] = 0

    def execute(self):
        data = self.readMemory()
        self.INS = CPU6502.opcodes.get(data, None)
        while self.cycles <= self.cycle_limit and self.INS is not None:
            opcode = CPU6502.opcodes.get(data, None)  # Use the NOP code as a safe default?
            self.INS = opcode

            if self.INS == 'LDA_IM':
                # Load memory into accumulator
                data = self.readMemory()
                self.registers['A'] = data
                self.setFlags(register='A', flags=['Z', 'N'])

            elif self.INS == 'LDA_ZP':
                zp_address = self.readMemory()
                data = self.readMemory(address=zp_address, increment_pc=False)
                self.registers['A'] = data
                self.setFlags(register='A', flags=['Z', 'N'])

            elif self.INS == 'LDA_ZP_X':
                zp_address = self.readMemory()
                zp_address += self.registers['X']
                # Zero Page address wraps around if the value exceeds 0xFF
                while zp_address > 0xFF:
                    zp_address -= 0x100
                self.cycleInc()
                data = self.readMemory(address=zp_address, increment_pc=False)
                self.registers['A'] = data
                self.setFlags(register='A', flags=['Z', 'N'])

            elif self.INS == 'LDA_ABS':
                address = self.readMemory()
                address += (self.readMemory() * 0x100)
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['A'] = data
                self.setFlags(register='A', flags=['Z', 'N'])

            elif self.INS == 'LDA_ABS_X':
                address = self.readMemory()
                address += (self.readMemory() * 0x100)
                address += self.registers['X']
                if int(address / 0x100) != int((address - self.registers['X']) / 0x100):
                    self.cycleInc()  # Only if PAGE crossed
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['A'] = data
                self.setFlags(register='A', flags=['Z', 'N'])

            elif self.INS == 'LDA_ABS_Y':
                address = self.readMemory()
                address += (self.readMemory() * 0x100)
                address += self.registers['Y']
                if int(address / 0x100) != int((address - self.registers['Y']) / 0x100):
                    self.cycleInc()  # Only if PAGE crossed
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['A'] = data
                self.setFlags(register='A', flags=['Z', 'N'])

            elif self.INS == 'LDA_IND_X':
                zp_address = self.readMemory()
                zp_address += self.registers['X']
                # Zero Page address wraps around if the value exceeds 0xFF
                while zp_address > 0xFF:
                    zp_address -= 0x100
                self.cycleInc()
                data = self.readMemory(address=zp_address, increment_pc=False)
                data += (self.readMemory(address=zp_address + 1, increment_pc=False) * 0x100)
                self.registers['A'] = self.readMemory(address=data, increment_pc=False)
                self.setFlags(register='A', flags=['Z', 'N'])

            elif self.INS == 'LDA_IND_Y':
                zp_address = self.readMemory()
                address = self.readMemory(address=zp_address, increment_pc=False)
                address += (self.readMemory(address=zp_address + 1, increment_pc=False) * 0x100)
                address += self.registers['Y']
                if int(address / 0x100) != int((address - self.registers['Y']) / 0x100):
                    self.cycleInc()  # Only if PAGE crossed
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['A'] = data
                self.setFlags(register='A', flags=['Z', 'N'])

            elif opcode == 'NOP':
                self.cycleInc()

            data = self.readMemory()
            self.INS = CPU6502.opcodes.get(data, None)

    def printState(self):
        combined = {**{'Cycle': self.cycles, '%-10s' % 'INS': '%-10s' % self.INS}, **self.registers, **{'SP': '0x{0:0{1}X}'.format(self.stack_pointer, 4), 'PC': '0x{0:0{1}X}'.format(self.program_counter, 4), 'MEM': '0x{0:0{1}X}'.format(self.memory[self.program_counter], 2)}}
        headerString = '\t'.join(combined)
        valueString = '\t'.join(str(v) for v in combined.values())
        print(headerString)
        print(valueString)

    def initializeLog(self):
        combined = {**{'Cycle': self.cycles, '%-10s' % 'INS': '%-10s' % self.INS}, **self.registers, **{'SP': '0x{0:0{1}X}'.format(self.stack_pointer, 4), 'PC': '0x{0:0{1}X}'.format(self.program_counter, 4), 'MEM': '0x{0:0{1}X}'.format(self.memory[self.program_counter], 2)}}
        headerString = '\t'.join(combined)
        self.log.append(headerString)

    def logState(self):
        combined = {**{'Cycle': self.cycles, '%-10s' % 'INS': '%-10s' % self.INS}, **self.registers, **{'SP': '0x{0:0{1}X}'.format(self.stack_pointer, 4), 'PC': '0x{0:0{1}X}'.format(self.program_counter, 4), 'MEM': '0x{0:0{1}X}'.format(self.memory[self.program_counter], 2)}}
        valueString = '\t'.join(str(v) for v in combined.values())
        self.log.append(valueString)

    def printLog(self):
        for line in self.log:
            print(line)

    def loadProgram(self, instructions=[], memoryAddress=0x0000):
        for ins in instructions:
            self.memory[memoryAddress] = ins
            memoryAddress += 1
            if memoryAddress >= CPU6502.MAX_MEMORY_SIZE:
                memoryAddress = 0


def run():
    cpu = CPU6502()
    cpu.reset()
    cpu.memory[0x00CC] = 0x02  # Used for LDA_ZP

    cpu.memory[0x0080] = 0x03  # Used for LDA_ZP_X

    cpu.memory[0x00AA] = 0x03  # Used for LDA_IND_X
    cpu.memory[0x00AB] = 0xFF  # Used for LDA_IND_X

    cpu.memory[0x00AC] = 0x01  # Used for LDA_IND_Y
    cpu.memory[0x00AD] = 0xFF  # Used for LDA_IND_Y

    cpu.memory[0xFF00] = 0x04
    cpu.memory[0xFF01] = 0x05
    cpu.memory[0xFF02] = 0x06
    cpu.memory[0xFF03] = 0x07
    cpu.memory[0xFF04] = 0x08

    cpu.loadProgram(instructions=[0xA9, 0x01, 0xA5, 0xCC, 0xB5, 0x80, 0xAD, 0x00, 0xFF, 0xBD, 0x01, 0xFF, 0xB9, 0xFF, 0xFE, 0xA1, 0xAA, 0xB1, 0xAC], memoryAddress=0xFF10)
    cpu.registers['Y'] = 0x03

    cpu.execute()
    cpu.printLog()
    cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF27)


if __name__ == '__main__':
    run()
