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

    version = '0.10'
    MAX_MEMORY_SIZE = 1024 * 64  # 64k memory size
    opcodes = {0xA9: 'LDA_IM',
               0xA5: 'LDA_ZP',
               0xB5: 'LDA_ZP_X',
               0xAD: 'LDA_ABS',
               0xBD: 'LDA_ABS_X',
               0xB9: 'LDA_ABS_Y',
               0xA1: 'LDA_IND_X',
               0xB1: 'LDA_IND_Y',

               0xA2: 'LDX_IM',
               0xA6: 'LDX_ZP',
               0xB6: 'LDX_ZP_Y',
               0xAE: 'LDX_ABS',
               0xBE: 'LDX_ABS_Y',

               0xA0: 'LDY_IM',
               0xA4: 'LDY_ZP',
               0xB4: 'LDY_ZP_X',
               0xAC: 'LDY_ABS',
               0xBC: 'LDY_ABS_X',

               0x85: 'STA_ZP',
               0x95: 'STA_ZP_X',
               0x8D: 'STA_ABS',
               0x9D: 'STA_ABS_X',
               0x99: 'STA_ABS_Y',
               0x81: 'STA_IND_X',
               0x91: 'STA_IND_Y',

               0x86: 'STX_ZP',
               0x96: 'STX_ZP_Y',
               0x8E: 'STX_ABS',

               0x84: 'STY_ZP',
               0x94: 'STY_ZP_X',
               0x8c: 'STY_ABS',

               0x4C: 'JMP',
               0x6C: 'JMP_IND',
               0x20: 'JSR',
               0x60: 'RTS',

               0x38: 'SEC',
               0xF8: 'SED',
               0x78: 'SEI',

               0x18: 'CLC',
               0x58: 'CLI',
               0xB8: 'CLV',
               0xD8: 'CLD',

               0xEA: 'NOP',

               0xE6: 'INC_ZP',
               0xF6: 'INC_ZP_X',
               0xEE: 'INC_ABS',
               0xFE: 'INC_ABS_X',
               0xC8: 'INY',
               0xE8: 'INX'}

    def __init__(self, cycle_limit=2):

        self.program_counter = 0xFF10
        self.stack_pointer = 0x01FF
        self.cycle_limit = cycle_limit

        self.INS = None

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

    def stackPointerDec(self):
        self.stack_pointer -= 1
        if self.stack_pointer < 0x0100:
            self.stack_pointer = 0x01FF

    def reset(self, program_counter=0xFF10):
        self.program_counter = program_counter
        self.stack_pointer = 0x01FF
        self.cycles = 0

        # Reset all registers to zero
        self.registers = dict.fromkeys(self.registers.keys(), 0)
        # Reset all flags to zero
        self.flags = dict.fromkeys(self.flags.keys(), 0)

        self.memory = [0] * CPU6502.MAX_MEMORY_SIZE

    def readMemory(self, increment_pc=True, address=None, bytes=1) -> int:
        data = 0
        for byte in range(bytes):
            self.cycleInc()
            if not address:
                data += (self.memory[self.program_counter] * (0x100 ** byte))
            else:
                data += (self.memory[address + byte] * (0x100 ** byte))

            if increment_pc:
                self.programCounterInc()
        return data

    def writeMemory(self, data, address, bytes=1):
        for byte in range(bytes):
            self.cycleInc()
            self.memory[address + byte] = data

    def setFlags(self, check=None, flags=[], value=None):
        if 'Z' in flags:
            if check == 0:
                self.flags['Z'] = 1
            else:
                self.flags['Z'] = 0

        if 'N' in flags:
            if check & 0b10000000 > 0:
                self.flags['N'] = 1
            else:
                self.flags['N'] = 0

        if 'C' in flags and value is not None:
            self.flags['C'] = value

        if 'D' in flags and value is not None:
            self.flags['D'] = value

        if 'I' in flags and value is not None:
            self.flags['I'] = value

        if 'V' in flags and value is not None:
            self.flags['V'] = value

    def determineAddress(self, mode):
        address = 0
        if mode == 'ZP':
            address = self.readMemory()
        elif mode == 'ZP_X':
            address = self.readMemory()
            address += self.registers['X']
            # Zero Page address wraps around if the value exceeds 0xFF
            address = address % 0x100
            self.cycleInc()
        elif mode == 'ZP_Y':
            address = self.readMemory()
            address += self.registers['Y']
            # Zero Page address wraps around if the value exceeds 0xFF
            address = address % 0x100
            self.cycleInc()
        elif mode == 'ABS':
            address = self.readMemory(bytes=2)
        elif mode == 'ABS_X':
            address = self.readMemory(bytes=2)
            address += self.registers['X']
            if int(address / 0x100) != int((address - self.registers['X']) / 0x100):
                self.cycleInc()  # Only if PAGE crossed
        elif mode == 'ABS_Y':
            address = self.readMemory(bytes=2)
            address += self.registers['Y']
            if int(address / 0x100) != int((address - self.registers['Y']) / 0x100):
                self.cycleInc()  # Only if PAGE crossed
        elif mode == 'IND':  # Indirect
            address = self.readMemory(bytes=2)
        elif mode == 'IND_X':
            address = self.readMemory()
            address += self.registers['X']
            # Zero Page address wraps around if the value exceeds 0xFF
            address = address % 0x100
            self.cycleInc()
            address = self.readMemory(address=address, increment_pc=False, bytes=2)
        elif mode == 'IND_Y':
            address = self.readMemory()
            address = self.readMemory(address=address, increment_pc=False, bytes=2)
            address += self.registers['Y']
            if int(address / 0x100) != int((address - self.registers['Y']) / 0x100):
                self.cycleInc()  # Only if PAGE crossed

        return address

    def execute(self):
        data = self.readMemory()
        self.INS = CPU6502.opcodes.get(data, None)
        while self.INS is not None:  # self.cycles <= self.cycle_limit:  # This was changed from <= to <

            if self.INS in ['INC_ZP', 'INC_ZP_X', 'INC_ABS', 'INC_ABS_X']:
                ins_set = self.INS.split('_')
                address_mode = '_'.join(_ for _ in ins_set[1:])
                address = self.determineAddress(mode=address_mode)
                value = self.readMemory(address=address, increment_pc=False, bytes=1)
                value += 1
                value = value % 0x10000
                self.cycleInc()  # Is this really necessary?
                self.writeMemory(data=value, address=address, bytes=1)
                self.setFlags(check=value, flags=['N', 'Z'])

            if self.INS in ['INX', 'INY']:
                value = self.registers[self.INS[2]]
                value += 1
                value = value % 0x100
                self.cycleInc()  # Is this really necessary?
                self.registers[self.INS[2]] = value
                self.setFlags(check=self.registers[self.INS[2]], flags=['N', 'Z'])

            if self.INS.startswith('STA'):
                ins_set = self.INS.split('_')
                target = ins_set[0][2]
                address_mode = '_'.join(_ for _ in ins_set[1:])
                address = self.determineAddress(mode=address_mode)
                self.writeMemory(data=self.registers[target], address=address, bytes=1)

            if self.INS.startswith('STX'):
                ins_set = self.INS.split('_')
                target = ins_set[0][2]
                address_mode = '_'.join(_ for _ in ins_set[1:])
                address = self.determineAddress(mode=address_mode)
                self.writeMemory(data=self.registers[target], address=address, bytes=1)

            if self.INS.startswith('STY'):
                ins_set = self.INS.split('_')
                target = ins_set[0][2]
                address_mode = '_'.join(_ for _ in ins_set[1:])
                address = self.determineAddress(mode=address_mode)
                self.writeMemory(data=self.registers[target], address=address, bytes=1)

            if self.INS in ['CLC', 'CLI', 'CLD', 'CLV', 'SEC', 'SED', 'SEI']:
                if self.INS in ['CLC', 'CLI', 'CLD', 'CLV']:
                    self.setFlags(flags=[self.INS[2]], value=0)
                else:
                    self.setFlags(flags=[self.INS[2]], value=1)
                self.cycleInc()

            if self.INS == 'LDA_IM':
                data = self.readMemory()
                self.registers['A'] = data
                self.setFlags(check=self.registers['A'], flags=['Z', 'N'])

            elif self.INS == 'LDX_IM':
                data = self.readMemory()
                self.registers['X'] = data
                self.setFlags(check=self.registers['X'], flags=['Z', 'N'])

            elif self.INS == 'LDY_IM':
                data = self.readMemory()
                self.registers['Y'] = data
                self.setFlags(check=self.registers['Y'], flags=['Z', 'N'])

            elif self.INS == 'LDA_ZP':
                address = self.determineAddress(mode='ZP')
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['A'] = data
                self.setFlags(check=self.registers['A'], flags=['Z', 'N'])

            elif self.INS == 'LDX_ZP':
                address = self.determineAddress(mode='ZP')
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['X'] = data
                self.setFlags(check=self.registers['X'], flags=['Z', 'N'])

            elif self.INS == 'LDY_ZP':
                address = self.determineAddress(mode='ZP')
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['Y'] = data
                self.setFlags(check=self.registers['Y'], flags=['Z', 'N'])

            elif self.INS == 'LDA_ZP_X':
                address = self.determineAddress(mode='ZP_X')
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['A'] = data
                self.setFlags(check=self.registers['A'], flags=['Z', 'N'])

            elif self.INS == 'LDX_ZP_Y':
                address = self.determineAddress(mode='ZP_Y')
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['X'] = data
                self.setFlags(check=self.registers['X'], flags=['Z', 'N'])

            elif self.INS == 'LDY_ZP_X':
                address = self.determineAddress(mode='ZP_X')
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['Y'] = data
                self.setFlags(check=self.registers['Y'], flags=['Z', 'N'])

            elif self.INS == 'LDA_ABS':
                address = self.determineAddress(mode='ABS')
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['A'] = data
                self.setFlags(check=self.registers['A'], flags=['Z', 'N'])

            elif self.INS == 'LDX_ABS':
                address = self.determineAddress(mode='ABS')
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['X'] = data
                self.setFlags(check=self.registers['X'], flags=['Z', 'N'])

            elif self.INS == 'LDY_ABS':
                address = self.determineAddress(mode='ABS')
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['Y'] = data
                self.setFlags(check=self.registers['Y'], flags=['Z', 'N'])

            elif self.INS == 'LDA_ABS_X':
                address = self.determineAddress(mode='ABS_X')
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['A'] = data
                self.setFlags(check=self.registers['A'], flags=['Z', 'N'])

            elif self.INS == 'LDA_ABS_Y':
                address = self.determineAddress(mode='ABS_Y')
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['A'] = data
                self.setFlags(check=self.registers['A'], flags=['Z', 'N'])

            elif self.INS == 'LDY_ABS_X':
                address = self.determineAddress(mode='ABS_X')
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['Y'] = data
                self.setFlags(check=self.registers['Y'], flags=['Z', 'N'])

            elif self.INS == 'LDX_ABS_Y':
                address = self.determineAddress(mode='ABS_Y')
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['X'] = data
                self.setFlags(check=self.registers['X'], flags=['Z', 'N'])

            elif self.INS == 'LDA_IND_X':
                address = self.determineAddress(mode='IND_X')
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['A'] = data
                self.setFlags(check=self.registers['A'], flags=['Z', 'N'])

            elif self.INS == 'LDA_IND_Y':
                address = self.determineAddress(mode='IND_Y')
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['A'] = data
                self.setFlags(check=self.registers['A'], flags=['Z', 'N'])

            elif self.INS == 'JMP':
                address = self.determineAddress(mode='ABS')
                self.program_counter = address
                pass

            elif self.INS == 'JMP_IND':
                address = self.determineAddress(mode='IND')
                address = self.readMemory(address=address, increment_pc=False, bytes=2)
                self.program_counter = address
                pass

            elif self.INS == 'NOP':
                self.cycleInc()

            data = self.readMemory()
            self.INS = CPU6502.opcodes.get(data, None)

    def printState(self):
        combined = {**{'Cycle': self.cycles, '%-10s' % 'INS': '%-10s' % self.INS}, **self.registers, **self.flags, **{'SP': '0x{0:0{1}X}'.format(self.stack_pointer, 4), 'PC': '0x{0:0{1}X}'.format(self.program_counter, 4), 'MEM': '0x{0:0{1}X}'.format(self.memory[self.program_counter], 2)}}
        headerString = '\t'.join(combined)
        valueString = '\t'.join(str(v) for v in combined.values())
        print(headerString)
        print(valueString)

    def initializeLog(self):
        combined = {**{'Cycle': self.cycles, '%-10s' % 'INS': '%-10s' % self.INS}, **self.registers, **self.flags, **{'SP': '0x{0:0{1}X}'.format(self.stack_pointer, 4), 'PC': '0x{0:0{1}X}'.format(self.program_counter, 4), 'MEM': '0x{0:0{1}X}'.format(self.memory[self.program_counter], 2)}}
        headerString = '\t'.join(combined)
        self.log.append(headerString)

    def logState(self):
        combined = {**{'Cycle': self.cycles, '%-10s' % 'INS': '%-10s' % self.INS}, **self.registers, **self.flags, **{'SP': '0x{0:0{1}X}'.format(self.stack_pointer, 4), 'PC': '0x{0:0{1}X}'.format(self.program_counter, 4), 'MEM': '0x{0:0{1}X}'.format(self.memory[self.program_counter], 2)}}
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

    cpu.loadProgram(instructions=[0xA9, 0x01, 0xA5, 0xCC, 0xB5, 0x80, 0xAD, 0x00, 0xFF, 0xBD, 0x01, 0xFF, 0xB9, 0xFF, 0xFE, 0xA1, 0xAA, 0xB1, 0xAC, 0x4C, 0x28, 0xFF], memoryAddress=0xFF10)
    cpu.loadProgram(instructions=[0xA9, 0x09, 0x6C, 0x30, 0xFF], memoryAddress=0xFF28)
    cpu.loadProgram(instructions=[0x38, 0xFF], memoryAddress=0xFF30)
    cpu.loadProgram(instructions=[0xA9, 0x0A, 0x85, 0xB0, 0xA2, 0x01, 0xA9, 0x0B, 0x95, 0xB0], memoryAddress=0xFF38)

    cpu.registers['Y'] = 0x03

    cpu.execute()
    cpu.printLog()
    cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF3F)
    cpu.memoryDump(startingAddress=0x0000, endingAddress=0xFF)


if __name__ == '__main__':
    run()
