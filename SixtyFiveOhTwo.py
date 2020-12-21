# 6502 machine code processor


class CPU6502:

    """
    ADC - Done
    AND - Done
    ASL - Done
    BCC - Done
    BCS - Done
    BEQ - Done
    BIT - Done
    BMI - Done
    BNE - Done
    BPL - Done
    BRK
    BVC - Done
    BVS - Done
    CLC - Done
    CLD - Done
    CLI - Done
    CLV - Done
    CMP - Need to test
    CPX - Need to test
    CPY - Need to test
    DEC - Done
    DEX - Done
    DEY - Done
    EOR - Done
    INC - Done
    INX - Done
    INY - Done
    JMP - Done
    JSR - Done
    LDA - Done
    LDX - Done
    LDY - Done
    LSR - Done
    NOP - Done
    ORA - Done
    PHA - Done
    PHP - Done
    PLA - Done
    PLP - Done
    ROL - Need to complete tests
    ROR - Need to complete tests
    RTI
    RTS - Done
    SBC
    SEC - Done
    SED - Done
    SEI - Done
    STA - Done
    STX - Done
    STY - Done
    TAX - Done
    TAY - Done
    TSX - Done
    TXA - Done
    TXS - Done
    TYA - Done
    """

    """

    All single-byte instructions waste a cycle reading and ignoring the byte that comes immediately after the instruction (this means no instruction can take less than two cycles).
    Zero page,X, zero page,Y, and (zero page,X) addressing modes spend an extra cycle reading the unindexed zero page address.
    Absolute,X, absolute,Y, and (zero page),Y addressing modes need an extra cycle if the indexing crosses a page boundary, ********** or if the instruction writes to memory **********.
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

    version = '0.50'
    MAX_MEMORY_SIZE = 1024 * 64  # 64k memory size
    OPCODES_WRITE_TO_MEMORY = ['STA', 'STX', 'STY', 'ROL', 'ROR']
    opcodes = {0x29: 'AND_IM',
               0x25: 'AND_ZP',
               0x35: 'AND_ZP_X',
               0x2D: 'AND_ABS',
               0x3D: 'AND_ABS_X',
               0x39: 'AND_ABS_Y',
               0x21: 'AND_IND_X',
               0x31: 'AND_IND_Y',

               0x0A: 'ASL_ACC',
               0x06: 'ASL_ZP',
               0x16: 'ASL_ZP_X',
               0x0E: 'ASL_ABS',
               0x1E: 'ASL_ABS_X',

               0x24: 'BIT_ZP',
               0x2C: 'BIT_ABS',

               0xFA: 'BRK',

               0x90: 'BCC',
               0xB0: 'BCS',
               0xF0: 'BEQ',
               0xD0: 'BNE',
               0x50: 'BVC',
               0x70: 'BVS',
               0x10: 'BPL',
               0x30: 'BMI',

               0xC9: 'CMP_IM',
               0xC5: 'CMP_ZP',
               0xD5: 'CMP_ZP_X',
               0xCD: 'CMP_ABS',
               0xDD: 'CMP_ABS_X',
               0xD9: 'CMP_ABS_Y',
               0xC1: 'CMP_IND_X',
               0xD1: 'CMP_IND_Y',

               0xE0: 'CMX_IM',
               0xE4: 'CPX_ZP',
               0xEC: 'CPX_ABS',

               0xC0: 'CPY_IM',
               0xC4: 'CPY_ZP',
               0xCC: 'CPY_ABS',

               0x49: 'EOR_IM',
               0x45: 'EOR_ZP',
               0x55: 'EOR_ZP_X',
               0x4D: 'EOR_ABS',
               0x5D: 'EOR_ABS_X',
               0x59: 'EOR_ABS_Y',
               0x41: 'EOR_IND_X',
               0x51: 'EOR_IND_Y',

               0x4A: 'LSR_ACC',
               0x46: 'LSR_ZP',
               0x56: 'LSR_ZP_X',
               0x4E: 'LSR_ABS',
               0x5E: 'LSR_ABS_X',

               0xA9: 'LDA_IM',
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

               0x48: 'PHA_IMP',
               0x68: 'PLA_IMP',

               0x08: 'PHP_IMP',
               0x28: 'PLP_IMP',

               0x2A: 'ROL_ACC',
               0X26: 'ROL_ZP',
               0X36: 'ROL_ZP_X',
               0X2E: 'ROL_ABS',
               0X3E: 'ROL_ABS_X',

               0x6A: 'ROR_ACC',
               0X66: 'ROR_ZP',
               0X76: 'ROR_ZP_X',
               0X6E: 'ROR_ABS',
               0X7E: 'ROR_ABS_X',

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

               0xAA: 'TAX',
               0x8A: 'TXA',
               0xA8: 'TAY',
               0x98: 'TYA',
               0x9A: 'TXS',
               0xBA: 'TSX',

               0x4C: 'JMP',
               0x6C: 'JMP_IND',
               0x20: 'JSR_ABS',
               0x60: 'RTS',

               0x38: 'SEC_IMP',
               0xF8: 'SED_IMP',
               0x78: 'SEI_IMP',

               0x18: 'CLC_IMP',
               0x58: 'CLI_IMP',
               0xB8: 'CLV_IMP',
               0xD8: 'CLD_IMP',

               0xEA: 'NOP',

               0xE6: 'INC_ZP',
               0xF6: 'INC_ZP_X',
               0xEE: 'INC_ABS',
               0xFE: 'INC_ABS_X',
               0xC8: 'INY_IMP',
               0xE8: 'INX_IMP',

               0x69: 'ADC_IM',
               0x65: 'ADC_ZP',
               0x75: 'ADC_ZP_X',
               0x6D: 'ADC_ABS',
               0x7D: 'ADC_ABS_X',
               0x79: 'ADC_ABS_Y',
               0x61: 'ADC_IND_X',
               0x71: 'ADC_IND_Y',

               0x09: 'ORA_IM',
               0x05: 'ORA_ZP',
               0x15: 'ORA_ZP_X',
               0x0D: 'ORA_ABS',
               0x1D: 'ORA_ABS_X',
               0x19: 'ORA_ABS_Y',
               0x01: 'ORA_IND_X',
               0x11: 'ORA_IND_Y',
               }

    def __init__(self, cycle_limit=100):

        self.program_counter = 0xFFFE
        self.stack_pointer = 0xFF  # This is technically 0x01FF since the stack pointer lives on page 01.
        self.cycle_limit = cycle_limit

        self.INS = None

        self.registers = {
            'A': 0,
            'X': 0,
            'Y': 0
        }

        self.flags = {
            'C': 0,  # Carry flag
            'Z': 0,  # Zero flag
            'I': 0,  # Interrupt flag
            'D': 0,  # Decimal mode flag
            'B': 0,  # Break flag
            'V': 0,  # Overflow flag
            'N': 0   # Negative flag
        }

        self.initializeMemory()
        self.cycles = 0
        self.log = []

        self.initializeLog()

    def initializeMemory(self):
        self.memory = [0x00] * CPU6502.MAX_MEMORY_SIZE

    def memoryDump(self, startingAddress=0x0000, endingAddress=0x0000, display_format='Hex'):
        print('\nMemory Dump:\n')
        line = ''  # to clear issues with pylance
        header = ''
        row = ''
        while startingAddress <= endingAddress and startingAddress <= CPU6502.MAX_MEMORY_SIZE:
            if display_format == 'Hex':
                header = '0x{0:0{1}X}'.format(startingAddress, 4) + '\t'
                row = '\t'.join('0x{0:0{1}X}'.format(self.memory[v], 2) for v in range(startingAddress, min(startingAddress + 8, CPU6502.MAX_MEMORY_SIZE)))
            elif display_format == 'Dec':
                header = '0x{0:0{1}X}'.format(startingAddress, 4) + '\t'
                row = '\t'.join('%-5s' % str(self.memory[v]) for v in range(startingAddress, min(startingAddress + 8, CPU6502.MAX_MEMORY_SIZE)))
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
        if self.stack_pointer < 0x00:
            self.stack_pointer = 0xFF

    def stackPointerInc(self):
        self.cycleInc()
        self.stack_pointer += 1
        if self.stack_pointer > 0xFF:
            self.stack_pointer = 0x00

    def getStackPointerAddress(self):
        return self.stack_pointer | 0x0100

    def savePCAtStackPointer(self):
        hi_byte = ((self.program_counter - 1) & 0b1111111100000000) >> 8
        lo_byte = (self.program_counter - 1) & 0b0000000011111111
        self.writeMemory(data=hi_byte, address=self.getStackPointerAddress(), bytes=1)
        self.stackPointerDec()
        self.writeMemory(data=lo_byte, address=self.getStackPointerAddress(), bytes=1)
        self.stackPointerDec()

    def saveByteAtStackPointer(self, data=None):
        # Enforce 1 byte size
        assert(data <= 0xFF)
        assert(data is not None)
        self.writeMemory(data=data, address=self.getStackPointerAddress(), bytes=1)
        self.stackPointerDec()

    def loadPCFromStackPointer(self):
        self.stackPointerInc()
        lo_byte = self.readMemory(increment_pc=False, address=self.getStackPointerAddress(), bytes=1)
        self.stackPointerInc()
        hi_byte = self.readMemory(increment_pc=False, address=self.getStackPointerAddress(), bytes=1)
        # address = lo_byte + (hi_byte << 8)
        self.program_counter = lo_byte
        # self.cycleInc()
        self.program_counter += (hi_byte << 8)
        # self.cycleInc()

    def loadByteFromStackPointer(self):
        self.stackPointerInc()
        byte = self.readMemory(increment_pc=False, address=self.getStackPointerAddress(), bytes=1)
        return byte

    def reset(self, program_counter=0xFFFE):
        self.program_counter = program_counter
        self.stack_pointer = 0xFF
        self.cycles = 0

        # Reset all registers to zero
        self.registers = dict.fromkeys(self.registers.keys(), 0)
        # Reset all flags to zero
        self.flags = dict.fromkeys(self.flags.keys(), 0)

        self.initializeMemory()

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

    def setFlagsByRegister(self, register=None, flags=[]):
        # Carry flag must be checked first, because it can alter the register value which can then be tested against other criteria in this same subroutine
        # if 'C' in flags:
            # if self.registers[register] & 0b100000000 > 0:
                # self.flags['C'] = 1
                # self.registers[register] = self.registers[register] % 0x0100
            # else:
                # self.flags['C'] = 0

        if 'Z' in flags:
            if self.registers[register] == 0:
                self.flags['Z'] = 1
            else:
                self.flags['Z'] = 0

        if 'N' in flags:
            self.flags['N'] = self.registers[register] >> 7 & 1

    def setFlagsByValue(self, value=None, flags=[]):
        if value is None or len(flags) == 0:
            return

        if 'Z' in flags:
            if value == 0:
                self.flags['Z'] = 1
            else:
                self.flags['Z'] = 0

        if 'N' in flags:
            if value & 0b10000000 > 0:
                self.flags['N'] = 1
            else:
                self.flags['N'] = 0

    def setFlagsManually(self, flags=[], value=None):
        if value is None or value < 0 or value > 1:
            return
        for flag in flags:
            self.flags[flag] = value

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
            if int(address / 0x100) != int((address - self.registers['X']) / 0x100) or (self.INS[0:3] in CPU6502.OPCODES_WRITE_TO_MEMORY):
                self.cycleInc()  # Only if PAGE crossed or instruction writes to memory
        elif mode == 'ABS_Y':
            address = self.readMemory(bytes=2)
            address += self.registers['Y']
            if (int(address / 0x100) != int((address - self.registers['Y']) / 0x100)) or (self.INS[0:3] in CPU6502.OPCODES_WRITE_TO_MEMORY):
                self.cycleInc()  # Only if PAGE crossed or instruction writes to memory
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
            if int(address / 0x100) != int((address - self.registers['Y']) / 0x100) or (self.INS[0:3] in CPU6502.OPCODES_WRITE_TO_MEMORY):
                self.cycleInc()  # Only if PAGE crossed or instruction writes to memory

        return address

    def getProcessorStatus(self) -> int:
        order = ['C', 'Z', 'I', 'D', 'B', 'X', 'V', 'N']
        state = 0
        for shift, flag in enumerate(order):
            if flag == 'X':
                continue
            state += (self.flags[flag] << shift)
        return state

    def setProcessorStatus(self, flags: int):
        order = ['C', 'Z', 'I', 'D', 'B', 'X', 'V', 'N']
        for shift, flag in enumerate(order):
            if flag == 'X':
                continue
            flag_value = (flags >> shift) & 0b00000001
            self.setFlagsManually(flags=[flag], value=flag_value)

    def handleBRK(self):
        address = self.memory[0xFFFF] << 8
        address += self.memory[0xFFFE]
        self.program_counter = address

    def execute(self):
        # Set starting position based on 0xFFFE/F
        self.handleBRK()

        data = self.readMemory()
        self.INS = CPU6502.opcodes.get(data, None)
        while self.INS is not None and self.cycles <= max(self.cycle_limit, 100):

            if self.INS == 'BRK':
                # Save program counter to stack
                self.savePCAtStackPointer()
                # Save flags to stack
                value = self.getProcessorStatus()
                self.saveByteAtStackPointer(data=value)
                # Set B flag
                self.setFlagsManually(['B'], 1)
                # Manually change PC to 0xFFFE
                self.handleBRK()

            if self.INS in ['PHP_IMP', 'PLP_IMP']:
                # Push
                if self.INS == 'PHP_IMP':
                    value = self.getProcessorStatus()
                    self.saveByteAtStackPointer(data=value)
                    self.readMemory()  # single byte instruction
                elif self.INS == 'PLP_IMP':
                    # Pull
                    flags = self.loadByteFromStackPointer()
                    self.setProcessorStatus(flags=flags)
                    self.readMemory()  # single byte instruction

            if self.INS in ['BIT_ZP', 'BIT_ABS']:
                ins_set = self.INS.split('_')
                address_mode = '_'.join(_ for _ in ins_set[1:])
                address = self.determineAddress(mode=address_mode)
                value = self.readMemory(address=address, increment_pc=False, bytes=1)

                zero_flag = 1 if (self.registers['A'] & value) == 0 else 0
                self.setFlagsManually(flags=['Z'], value=zero_flag)

                self.setFlagsByValue(value=value, flags=['N'])

                overflow_flag = (value & 0b01000000) >> 6
                self.setFlagsManually(flags=['V'], value=overflow_flag)

            if self.INS == 'PHA_IMP':
                value = self.registers['A']
                self.saveByteAtStackPointer(data=value)
                self.readMemory()  # single byte instruction

            if self.INS == 'PLA_IMP':
                value = self.loadByteFromStackPointer()
                self.registers['A'] = value
                self.setFlagsByRegister(register='A', flags=['N', 'Z'])
                self.readMemory()  # single byte instruction

            if self.INS in ['ROL_ACC', 'ROL_ZP', 'ROL_ZP_X', 'ROL_ABS', 'ROL_ABS_X', 'ROR_ACC', 'ROR_ZP', 'ROR_ZP_X', 'ROR_ABS', 'ROR_ABS_X']:
                ins_set = self.INS.split('_')
                address_mode = '_'.join(_ for _ in ins_set[1:])
                if address_mode == 'ACC':
                    value = self.registers['A']
                    self.readMemory()  # one byte instruction
                else:
                    address = self.determineAddress(mode=address_mode)
                    value = self.readMemory(address=address, increment_pc=False, bytes=1)

                # Carry flag
                if self.INS in ['ROL_ACC', 'ROL_ZP', 'ROL_ZP_X', 'ROL_ABS', 'ROL_ABS_X']:
                    determine_carry_flag = (value & 0b10000000) >> 7
                    current_carry_flag = self.flags['C']
                    value = value << 1
                    value = value & 0b0000000011111111  # 8 bit mask
                    value = value | 0b00000001 if current_carry_flag == 1 else value & 0b11111110
                    if self.INS != 'ROL_ACC':
                        self.cycleInc()  # Necessary according to notes above
                elif self.INS in ['ROR_ACC', 'ROR_ZP', 'ROR_ZP_X', 'ROR_ABS', 'ROR_ABS_X']:
                    determine_carry_flag = value & 0b00000001
                    current_carry_flag = self.flags['C']
                    value = value >> 1
                    value = value & 0b0000000011111111  # 8 bit mask
                    value = value | 0b10000000 if current_carry_flag == 1 else value & 0b01111111
                    if self.INS != 'ROR_ACC':
                        self.cycleInc()  # Necessary according to notes above
                self.setFlagsManually(value=determine_carry_flag, flags=['C'])

                # Negative flag and Zero flag
                self.setFlagsByValue(value=value, flags=['N', 'Z'])

                if address_mode == 'ACC':
                    self.registers['A'] = value
                else:
                    self.writeMemory(data=value, address=address, bytes=1)

            if self.INS in ['CMP_IM', 'CMP_ZP', 'CMP_ZP_X', 'CMP_ABS', 'CMP_ABS_X', 'CMP_ABS_Y', 'CMP_IND_X', 'CMP_IND_Y',
                            'CPX_IM', 'CPX_ZP', 'CPX_ABS'
                            'CPY_IM', 'CPY_ZP', 'CPY_ABS']:
                target = 'A' if self.INS[2] == 'P' else self.INS[2]
                if self.INS in ['CMP_IM', 'CPX_IM', 'CPY_IM']:
                    value = self.readMemory()
                else:
                    ins_set = self.INS.split('_')
                    address_mode = '_'.join(_ for _ in ins_set[1:])
                    address = self.determineAddress(mode=address_mode)
                    value = self.readMemory(address=address, increment_pc=False, bytes=1)

                compare = self.registers[target]
                if compare > value:
                    self.setFlagsManually(['C'], 1)
                    self.setFlagsManually(['Z'], 0)
                elif compare == value:
                    self.setFlagsManually(['C'], 0)
                    self.setFlagsManually(['Z'], 1)
                elif compare < value:
                    self.setFlagsManually(['C'], 0)
                    self.setFlagsManually(['Z'], 0)
                self.setFlagsByValue(value=(compare - value), flags=['N'])

            if self.INS in ['BEQ', 'BNE',
                            'BCC', 'BCS',
                            'BMI', 'BPL',
                            'BVC', 'BVS']:

                # Instruction: [Flag, Value to Test]
                comparisons = {'BEQ': ['Z', 1],
                               'BNE': ['Z', 0],
                               'BCC': ['C', 0],
                               'BCS': ['C', 1],
                               'BMI': ['N', 1],
                               'BPL': ['N', 0],
                               'BVS': ['V', 1],
                               'BVC': ['V', 0],
                               }
                offset = self.readMemory()
                flag = comparisons[self.INS][0]
                test_value = comparisons[self.INS][1]
                if self.flags[flag] == test_value:
                    self.program_counter += offset
                    self.cycleInc()
                    # Check if page was crossed
                    if ((self.program_counter & 0b1111111100000000) != ((self.program_counter - offset) & 0b1111111100000000)):
                        self.cycleInc()

            if self.INS in ['TAX', 'TXA', 'TAY', 'TYA']:
                source = self.INS[1]
                dest = self.INS[2]
                self.registers[dest] = self.registers[source]
                self.setFlagsByRegister(register=dest, flags=['N', 'Z'])
                self.readMemory()  # 1 byte instruction -- read next byte and ignore

            if self.INS in ['TXS', 'TSX']:
                source = self.INS[1]
                dest = self.INS[2]
                if dest == 'X':
                    self.registers[dest] = self.stack_pointer
                    self.setFlagsByRegister(register=dest, flags=['N', 'Z'])
                elif dest == 'S':
                    self.stack_pointer = self.registers[source]

                self.readMemory()  # 1 byte instruction -- read next byte and ignore

            if self.INS in ['ASL_ACC', 'ASL_ZP', 'ASL_ZP_X', 'ASL_ABS', 'ASL_ABS_X']:
                if self.INS == 'ASL_ACC':
                    value = self.registers['A']
                    carry_flag = 1 if (value & 0b10000000) > 0 else 0
                    value = value << 1
                    value = value & 0b0000000011111110
                    self.registers['A'] = value
                    self.setFlagsByRegister(register='A', flags=['Z', 'N'])
                    self.setFlagsManually(flags=['C'], value=carry_flag)
                    self.readMemory()  # 1 byte instruction -- read next byte and ignore
                else:
                    ins_set = self.INS.split('_')
                    address_mode = '_'.join(_ for _ in ins_set[1:])
                    address = self.determineAddress(mode=address_mode)
                    value = self.readMemory(address=address, increment_pc=False, bytes=1)
                    carry_flag = 1 if (value & 0b10000000) > 0 else 0
                    value = value << 1
                    value = value & 0b0000000011111110
                    self.cycleInc()  # Extra cycle for modify stage in RMW instruction per note at top.
                    self.writeMemory(data=value, address=address, bytes=1)
                    self.setFlagsByValue(value=value, flags=['Z', 'N'])
                    self.setFlagsManually(flags=['C'], value=carry_flag)

            if self.INS in ['LSR_ACC', 'LSR_ZP', 'LSR_ZP_X', 'LSR_ABS', 'LSR_ABS_X']:
                if self.INS == 'LSR_ACC':
                    value = self.registers['A']
                    carry_flag = 1 if (value & 0b00000001) > 0 else 0
                    value = value >> 1
                    value = value & 0b0000000001111111
                    self.registers['A'] = value
                    self.setFlagsByRegister(register='A', flags=['Z', 'N'])
                    self.setFlagsManually(flags=['C'], value=carry_flag)
                    self.readMemory()  # 1 byte instruction -- read next byte and ignore
                else:
                    ins_set = self.INS.split('_')
                    address_mode = '_'.join(_ for _ in ins_set[1:])
                    address = self.determineAddress(mode=address_mode)
                    value = self.readMemory(address=address, increment_pc=False, bytes=1)
                    carry_flag = 1 if (value & 0b00000001) > 0 else 0
                    value = value >> 1
                    value = value & 0b0000000001111111
                    self.cycleInc()  # Extra cycle for modify stage in RMW instruction per note at top.
                    self.writeMemory(data=value, address=address, bytes=1)
                    self.setFlagsByValue(value=value, flags=['Z', 'N'])
                    self.setFlagsManually(flags=['C'], value=carry_flag)

            if self.INS == 'ORA_IM':
                value = self.readMemory()
                result = self.registers['A'] | value
                self.registers['A'] = result
                self.setFlagsByRegister(register='A', flags=['Z', 'N'])

            if self.INS in ['ORA_ZP', 'ORA_ZP_X', 'ORA_ABS', 'ORA_ABS_X', 'ORA_ABS_Y', 'ORA_IND_X', 'ORA_IND_Y']:
                ins_set = self.INS.split('_')
                address_mode = '_'.join(_ for _ in ins_set[1:])
                address = self.determineAddress(mode=address_mode)
                value = self.readMemory(address=address, increment_pc=False, bytes=1)
                result = self.registers['A'] | value
                self.registers['A'] = result
                self.setFlagsByRegister(register='A', flags=['Z', 'N'])

            if self.INS == 'EOR_IM':
                value = self.readMemory()
                result = self.registers['A'] ^ value
                self.registers['A'] = result
                self.setFlagsByRegister(register='A', flags=['Z', 'N'])

            if self.INS in ['EOR_ZP', 'EOR_ZP_X', 'EOR_ABS', 'EOR_ABS_X', 'EOR_ABS_Y', 'EOR_IND_X', 'EOR_IND_Y']:
                ins_set = self.INS.split('_')
                address_mode = '_'.join(_ for _ in ins_set[1:])
                address = self.determineAddress(mode=address_mode)
                value = self.readMemory(address=address, increment_pc=False, bytes=1)
                result = self.registers['A'] ^ value
                self.registers['A'] = result
                self.setFlagsByRegister(register='A', flags=['Z', 'N'])

            if self.INS == 'AND_IM':
                value = self.readMemory()
                result = self.registers['A'] & value
                self.registers['A'] = result
                self.setFlagsByRegister(register='A', flags=['Z', 'N'])

            if self.INS in ['AND_ZP', 'AND_ZP_X', 'AND_ABS', 'AND_ABS_X', 'AND_ABS_Y', 'AND_IND_X', 'AND_IND_Y']:
                ins_set = self.INS.split('_')
                address_mode = '_'.join(_ for _ in ins_set[1:])
                address = self.determineAddress(mode=address_mode)
                value = self.readMemory(address=address, increment_pc=False, bytes=1)
                result = self.registers['A'] & value
                self.registers['A'] = result
                self.setFlagsByRegister(register='A', flags=['Z', 'N'])

            if self.INS == 'ADC_IM':
                value = self.readMemory()
                value += self.registers['A']
                self.registers['A'] = value & 0b0000000011111111
                self.setFlagsByRegister(register='A', flags=['Z', 'V', 'N'])
                carry_flag = 1 if (value & 0b1111111100000000) > 0 else 0
                self.setFlagsManually(flags=['C'], value=carry_flag)

            if self.INS in ['ADC_ZP', 'ADC_ZP_X', 'ADC_ABS', 'ADC_ABS_X', 'ADC_ABS_Y', 'ADC_IND_X', 'ADC_IND_Y']:
                ins_set = self.INS.split('_')
                address_mode = '_'.join(_ for _ in ins_set[1:])
                address = self.determineAddress(mode=address_mode)
                value = self.readMemory(address=address, increment_pc=False, bytes=1)
                value += self.registers['A']
                self.registers['A'] = value & 0b0000000011111111
                self.setFlagsByRegister(register='A', flags=['C', 'Z', 'V', 'N'])
                carry_flag = 1 if (value & 0b1111111100000000) > 0 else 0
                self.setFlagsManually(flags=['C'], value=carry_flag)

            if self.INS == 'JSR_ABS':
                ins_set = self.INS.split('_')
                address_mode = '_'.join(_ for _ in ins_set[1:])
                address = self.determineAddress(mode=address_mode)
                self.savePCAtStackPointer()
                self.program_counter = address
                self.cycleInc()

            if self.INS == 'RTS':
                self.loadPCFromStackPointer()
                self.programCounterInc()
                self.cycleInc()

            if self.INS in ['INC_ZP', 'INC_ZP_X', 'INC_ABS', 'INC_ABS_X']:
                ins_set = self.INS.split('_')
                address_mode = '_'.join(_ for _ in ins_set[1:])
                address = self.determineAddress(mode=address_mode)
                value = self.readMemory(address=address, increment_pc=False, bytes=1)
                value += 1
                value = value % 0x100
                self.cycleInc()  # Is this really necessary? -- apparently, yes
                if self.INS == 'INC_ABS_X':
                    self.cycleInc()  # Also necessary according to comments above
                self.writeMemory(data=value, address=address, bytes=1)
                self.setFlagsByValue(value=value, flags=['N', 'Z'])

            if self.INS in ['INX_IMP', 'INY_IMP']:
                value = self.registers[self.INS[2]]
                value += 1
                value = value % 0x100
                self.cycleInc()  # Is this really necessary?
                self.registers[self.INS[2]] = value
                self.setFlagsByRegister(register=self.INS[2], flags=['N', 'Z'])

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

            if self.INS in ['CLC_IMP', 'CLI_IMP', 'CLD_IMP', 'CLV_IMP', 'SEC_IMP', 'SED_IMP', 'SEI_IMP']:
                if self.INS in ['CLC_IMP', 'CLI_IMP', 'CLD_IMP', 'CLV_IMP']:
                    self.setFlagsManually(flags=[self.INS[2]], value=0)
                else:
                    self.setFlagsManually(flags=[self.INS[2]], value=1)
                self.readMemory()  # Single byte opcode

            elif self.INS in ['LDA_IM', 'LDA_ZP', 'LDA_ZP_X', 'LDA_ABS', 'LDA_ABS_X', 'LDA_ABS_Y', 'LDA_IND_X', 'LDA_IND_Y',
                              'LDX_IM', 'LDX_ZP', 'LDX_ZP_Y', 'LDX_ABS', 'LDX_ABS_Y',
                              'LDY_IM', 'LDY_ZP', 'LDY_ZP_X', 'LDY_ABS', 'LDY_ABS_X']:
                ins_set = self.INS.split('_')
                register = ins_set[0][2]
                address_mode = '_'.join(_ for _ in ins_set[1:])
                if address_mode == 'IM':
                    data = self.readMemory()
                else:
                    address = self.determineAddress(mode=address_mode)
                    data = self.readMemory(address=address, increment_pc=False)
                self.registers[register] = data
                self.setFlagsByRegister(register=register, flags=['Z', 'N'])

            elif self.INS == 'JMP':
                address = self.determineAddress(mode='ABS')
                self.program_counter = address

            elif self.INS == 'JMP_IND':
                address = self.determineAddress(mode='IND')
                address = self.readMemory(address=address, increment_pc=False, bytes=2)
                self.program_counter = address

            elif self.INS == 'NOP':
                self.readMemory() # single byte instruction

            data = self.readMemory()
            self.INS = CPU6502.opcodes.get(data, None)

    def printState(self):
        combined = {**{'Cycle': self.cycles, '%-10s' % 'INS': '%-10s' % self.INS}, **self.registers, **self.flags, **{'SP': '0x{0:0{1}X}'.format(self.getStackPointerAddress(), 4), 'PC': '0x{0:0{1}X}'.format(self.program_counter, 4), 'MEM': '0x{0:0{1}X}'.format(self.memory[self.program_counter], 2)}}
        headerString = '\t'.join(combined)
        valueString = '\t'.join(str(v) for v in combined.values())
        print(headerString)
        print(valueString)

    def initializeLog(self):
        combined = {**{'Cycle': self.cycles, '%-10s' % 'INS': '%-10s' % self.INS}, **self.registers, **self.flags, **{'SP': '0x{0:0{1}X}'.format(self.getStackPointerAddress(), 4), 'PC': '0x{0:0{1}X}'.format(self.program_counter, 4), 'MEM': '0x{0:0{1}X}'.format(self.memory[self.program_counter], 2)}}
        headerString = '\t'.join(combined)
        self.log.append(headerString)

    def logState(self):
        combined = {**{'Cycle': self.cycles, '%-10s' % 'INS': '%-10s' % self.INS}, **self.registers, **self.flags, **{'SP': '0x{0:0{1}X}'.format(self.getStackPointerAddress(), 4), 'PC': '0x{0:0{1}X}'.format(self.program_counter, 4), 'MEM': '0x{0:0{1}X}'.format(self.memory[self.program_counter], 2)}}
        valueString = '\t'.join(str(v) for v in combined.values())
        self.log.append(valueString)

    def printLog(self):
        for line in self.log:
            print(line)

    def loadProgram(self, instructions=[], memoryAddress=0x0000, mainProgram=True):
        if mainProgram:
            self.memory[0xFFFE] = memoryAddress & 0b0000000011111111
            self.memory[0xFFFF] = (memoryAddress >> 8) & 0b0000000011111111
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

    cpu.loadProgram(instructions=[0xA9, 0x09, 0x6C, 0x30, 0xFF], memoryAddress=0xFF28)
    cpu.loadProgram(instructions=[0x38, 0xFF], memoryAddress=0xFF30)
    cpu.loadProgram(instructions=[0xA9, 0x0A, 0x85, 0xB0, 0xA2, 0x01, 0xA9, 0x0B, 0x95, 0xB0], memoryAddress=0xFF38)

    cpu.loadProgram(instructions=[0xA9, 0x01, 0xA5, 0xCC, 0xB5, 0x80, 0xAD, 0x00, 0xFF, 0xBD, 0x01, 0xFF, 0xB9, 0xFF, 0xFE, 0xA1, 0xAA, 0xB1, 0xAC, 0x4C, 0x28, 0xFF], memoryAddress=0xFF10)

    cpu.registers['Y'] = 0x03

    cpu.execute()
    cpu.printLog()
    cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF3F)
    cpu.memoryDump(startingAddress=0x0000, endingAddress=0x00FF)
    cpu.memoryDump(startingAddress=0x00, endingAddress=0x0F)


def fibonacci_test():
    cpu = CPU6502(cycle_limit=5000)
    cpu.reset(program_counter=0x0000)

    program = [0xA9, 0x01,  # LDA_IM 1
               0xA2, 0x00,  # LDX_IM 0
               0x85, 0x21,  # STA_ZP [0x21]
               0xA9, 0x00,  # LDA_IM 0
               0x65, 0x21,  # ADC [0x21]  -- This is the main loop; the jump ins below should point to the address of this line
               0xB0, 0x11,  # BCS 0x11  ; Jump to end of program if value exceeds 0xFF
               0x95, 0x30,  # STA_ZP_X [0x30]
               0xE8,        # INX
               0x85, 0x22,  # STA_ZP [0x22]
               0xA5, 0x21,  # LDA_ZP [0x21]
               0x85, 0x20,  # STA_ZP [0x20]
               0xA5, 0x22,  # LDA_ZP [0x22]
               0x85, 0x21,  # STA_ZP [0x21]
               0xA5, 0x20,  # LDA_ZP [0x20]
               0x4C, 0x08, 0x00  # JMP 0x0008
               ]
    cpu.loadProgram(instructions=program, memoryAddress=0x0000)
    cpu.execute()
    cpu.printLog()
    cpu.memoryDump(startingAddress=0x0000, endingAddress=0x001F)
    cpu.memoryDump(startingAddress=0x0020, endingAddress=0x0022, display_format='Dec')
    cpu.memoryDump(startingAddress=0x0030, endingAddress=0x003F, display_format='Dec')


def fast_multiply_10():
    cpu = CPU6502(cycle_limit=100)
    cpu.reset(program_counter=0x2000)

    program = [0xA9, 0x19,  # LDA_IM 25 ; Load initial value
               0x0A, 0x00,  # ASL ACC ; Double accumulator value
               0x8D, 0x00, 0x30,  # STA [0x3000] ; Store doubled value in memory
               0x0A, 0x00,  # ASL ACC ; Double accumulator again (x4 total)
               0x0A, 0x00,  # ASL ACC ; Double accumulator again (x8 total)
               0x18, 0x00,  # CLC ; Clear carry flag for some reason
               0x6D, 0x00, 0x30,  # ADC [0x3000] ; Add memory to accumulator (effectively value x 8 + value x 2 = value x 10)
               0x8D, 0x01, 0x30,  # STA [0x3000] ; Store accumulator value in memory
               ]
    cpu.loadProgram(instructions=program, memoryAddress=0x2000)
    cpu.execute()
    cpu.printLog()
    cpu.memoryDump(startingAddress=0x2000, endingAddress=0x200F)
    cpu.memoryDump(startingAddress=0x3000, endingAddress=0x3001, display_format='Dec')


def square_root_test():
    """
    ; Calculates the 8 bit root and 9 bit remainder of a 16 bit unsigned integer in
    ; Numberl/Numberh. The result is always in the range 0 to 255 and is held in
    ; Root, the remainder is in the range 0 to 511 and is held in Reml/Remh
    ;
    ; partial results are held in templ/temph
    ;
    ; This routine is the complement to the integer square program.
    ;
    ; Destroys A, X registers.

    ; variables - must be in RAM

    Numberl		= $F0		; number to find square root of low byte
    Numberh		= Numberl+1	; number to find square root of high byte
    Reml		= $F2		; remainder low byte
    Remh		= Reml+1	; remainder high byte
    templ		= $F4		; temp partial low byte
    temph		= templ+1	; temp partial high byte
    Root		= $F6		; square root

        *= $8000		; can be anywhere, ROM or RAM

    SqRoot
        LDA	#$00		; clear A
        STA	Reml		; clear remainder low byte
        STA	Remh		; clear remainder high byte
        STA	Root		; clear Root
        LDX	#$08		; 8 pairs of bits to do
    Loop
        ASL	Root		; Root = Root * 2

        ASL	Numberl		; shift highest bit of number ..
        ROL	Numberh		;
        ROL	Reml		; .. into remainder
        ROL	Remh		;

        ASL	Numberl		; shift highest bit of number ..
        ROL	Numberh		;
        ROL	Reml		; .. into remainder
        ROL	Remh		;

        LDA	Root		; copy Root ..
        STA	templ		; .. to templ
        LDA	#$00		; clear byte
        STA	temph		; clear temp high byte

        SEC			; +1
        ROL	templ		; temp = temp * 2 + 1
        ROL	temph		;

        LDA	Remh		; get remainder high byte
        CMP	temph		; comapre with partial high byte
        BCC	Next		; skip sub if remainder high byte smaller

        BNE	Subtr		; do sub if <> (must be remainder>partial !)

        LDA	Reml		; get remainder low byte
        CMP	templ		; comapre with partial low byte
        BCC	Next		; skip sub if remainder low byte smaller

                    ; else remainder>=partial so subtract then
                    ; and add 1 to root. carry is always set here
    Subtr
        LDA	Reml		; get remainder low byte
        SBC	templ		; subtract partial low byte
        STA	Reml		; save remainder low byte
        LDA	Remh		; get remainder high byte
        SBC	temph		; subtract partial high byte
        STA	Remh		; save remainder high byte

        INC	Root		; increment Root
    Next
        DEX			; decrement bit pair count
        BNE	Loop		; loop if not all done

        RTS
    """


def flags_test():
    cpu = CPU6502(cycle_limit=10)
    cpu.setFlagsManually(['C', 'Z', 'I', 'D', 'B', 'V', 'N'], 0)
    cpu.getProcessorStatus()
    cpu.setFlagsManually(['C', 'Z', 'I', 'D', 'B', 'V', 'N'], 1)
    cpu.getProcessorStatus()
    cpu.setFlagsManually(['C', 'Z', 'I', 'D', 'B', 'V', 'N'], 0)
    flags = ['N', 'V', 'B', 'D', 'I', 'Z', 'C']
    for flag in flags:
        print(f'Flag: {flag}')
        cpu.setFlagsManually([flag], 1)
        cpu.printState()
        value = cpu.getProcessorStatus()
        cpu.setFlagsManually([flag], 0)
        cpu.printState()
        cpu.setProcessorStatus(value)
        cpu.printState()
        print('*' * 50)


if __name__ == '__main__':
    # run()
    fibonacci_test()
    # print()
    # fast_multiply_10()
    # print()
    # flags_test()
