# 6502 machine code processor
import datetime
import time
# from bcolors import bcolors as bcolors
import msvcrt
import traceback

global tabcount
tabcount = 0

monitoring = False
if monitoring:
    global log
    log = open('time.txt', 'w')


def timetrack(func):
    if not monitoring:
        return func

    def timing(*args, **kwargs):
        global tabcount
        start_time = time.time()
        func_name = func.__name__
        spacer = ''.join(['\t' * i for i in range(tabcount)])
        arg = [f'{k}: {v}' for k, v in kwargs.items()]
        log.write(' '.join([spacer, func_name, 'STARTED', *arg, '\n']))
        tabcount += 1
        result = func(*args, **kwargs)
        tabcount -= 1
        end_time = time.time()
        ex_time = str(end_time - start_time)
        spacer = ''.join(['\t' * i for i in range(tabcount)])
        log.write(' '.join([spacer, func_name, 'FINISHED', ex_time, '\n']))
        return result
    return timing


class CPU6502:

    """
    Notes:
    0000-00FF  - RAM for Zero-Page & Indirect-Memory Addressing
    0100-01FF  - RAM for Stack Space & Absolute Addressing
    0200-3FFF  - RAM for programmer use
    4000-7FFF  - Memory mapped I/O
    8000-FFF9  - ROM for programmer useage
    FFFA       - Vector address for NMI (low byte)
    FFFB       - Vector address for NMI (high byte)
    FFFC       - Vector address for RESET (low byte)
    FFFD       - Vector address for RESET (high byte)
    FFFE       - Vector address for IRQ & BRK (low byte)
    FFFF       - Vector address for IRQ & BRK  (high byte)
    """
    VECTORS = {
        'NMI': 0xFFFA,
        'RESET': 0xFFFC,
        'IRQ': 0xFFFE,
        'BRK': 0xFFFE
    }
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

    VERSION = '0.95'
    MAX_MEMORY_SIZE = 1024 * 64  # 64k memory size
    OPCODES_WRITE_TO_MEMORY = ('STA', 'STX', 'STY', 'ROL', 'ROR', 'ASL', 'LSR', 'INC', 'DEC')
    OPCODES = {
        0x29: 'AND_IM',
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

        0xE0: 'CPX_IM',
        0xE4: 'CPX_ZP',
        0xEC: 'CPX_ABS',

        0xC0: 'CPY_IM',
        0xC4: 'CPY_ZP',
        0xCC: 'CPY_ABS',

        0xC6: 'DEC_ZP',
        0xD6: 'DEC_ZP_X',
        0xCE: 'DEC_ABS',
        0xDE: 'DEC_ABS_X',
        0xCA: 'DEX_IMP',
        0x88: 'DEY_IMP',

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

        0xE9: 'SBC_IM',
        0xE5: 'SBC_ZP',
        0xF5: 'SBC_ZP_X',
        0xED: 'SBC_ABS',
        0xFD: 'SBC_ABS_X',
        0xF9: 'SBC_ABS_Y',
        0xE1: 'SBC_IND_X',
        0xF1: 'SBC_IND_Y',

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

        0xAA: 'TAX_IMP',
        0x8A: 'TXA_IMP',
        0xA8: 'TAY_IMP',
        0x98: 'TYA_IMP',
        0x9A: 'TXS_IMP',
        0xBA: 'TSX_IMP',

        0x4C: 'JMP_ABS',
        0x6C: 'JMP_IND',
        0x20: 'JSR_ABS',
        0x60: 'RTS_IMP',

        0x40: 'RTI',

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

    def __init__(self, cycle_limit=10_000, logging=False, printActivity=False, logFile=None, enableBRK=False):

        self.program_counter = 0xFFFE
        self.stack_pointer = 0xFF  # This is technically 0x01FF since the stack pointer lives on page 01.
        self.cycle_limit = cycle_limit

        self.INS = None

        self.enableBRK = enableBRK
        if self.enableBRK:
            CPU6502.OPCODES[0x00] = 'BRK'

        self.logging = logging
        if logFile:
            self.logFile = open(logFile, 'w')
        else:
            self.logFile = None

        self.action = []
        self.printActivity = printActivity

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
            'U': 0,  # Unused flag
            'V': 0,  # Overflow flag
            'N': 0   # Negative flag
        }

        self.hooks = {
            'KBD': 0xD010,
            'KBDCR': 0xD011,
            'DSP': 0xD012,
            'DSPCR': 0xD013
        }

        self.initializeMemory()
        self.cycles = 0
        self.initializeLog()

        self.chars = 0

    def initializeMemory(self):
        self.memory = [0x00] * CPU6502.MAX_MEMORY_SIZE
        self.value = 0x0D

    def memoryDump(self, startingAddress=None, endingAddress=None, display_format='Hex'):
        # print('\nMemory Dump:\n')
        print()
        line = ''  # to clear issues with pylance
        header = ''
        row = ''
        while startingAddress <= endingAddress and startingAddress <= CPU6502.MAX_MEMORY_SIZE:
            if display_format == 'Hex':
                header = '0x{0:0{1}X}:'.format(startingAddress, 4) + '\t'
                row = '\t'.join('0x{0:0{1}X}'.format(self.memory[v], 2) for v in range(startingAddress, min(startingAddress + 8, CPU6502.MAX_MEMORY_SIZE)))
            elif display_format == 'Dec':
                header = '0x{0:0{1}X}:'.format(startingAddress, 4) + '\t'
                row = '\t'.join('%-5s' % str(self.memory[v]) for v in range(startingAddress, min(startingAddress + 8, CPU6502.MAX_MEMORY_SIZE)))
            line = header + row
            print(line)
            startingAddress += 8

    @timetrack
    def extraFunctions(self):
        # Printing character to the screen
        if (self.memory[self.hooks['DSP']] & 0b10000000) > 0:
            self.memory[self.hooks['DSP']] = self.memory[self.hooks['DSP']] & 0b01111111
            self.value = self.memory[self.hooks['DSP']]
            # if self.value != 0x0D:
            if self.value >= 0x20 or self.value == 0x08:
                # print(chr(0x20 + ((self.value + 0x20) % 0x40)), end='', flush=True)
                # print(f'{(self.value + 0x20):02X}')
                # print(chr((self.value + 32)), end='', flush=True)
                print(chr((self.value)), end='', flush=True)
                self.chars += 1
            # else:
            if self.value == 0x0D or self.chars >= 40:
                # print('\r', end='', flush=True)
                print('', flush=True)
                self.chars = 0

            # if self.chars >= 40:
                # print('', flush=True)
                # self.chars = 0

        # Handling keyboard input
        if msvcrt.kbhit():
            key = msvcrt.getch().upper()
            key_ascii = ord(key)
            self.memory[self.hooks['KBD']] = key_ascii | 0b10000000
            self.memory[self.hooks['KBDCR']] = self.memory[self.hooks['KBDCR']] | 0b10000000

    @timetrack
    def cycleInc(self):
        if self.logging:
            self.logState()
            if self.printActivity:
                self.printState()
            self.action = []
        self.cycles += 1

    def logAction(self, action=''):
        if self.logging:
            self.action.append(action)

    @timetrack
    def programCounterInc(self):
        self.program_counter += 1
        if self.program_counter >= CPU6502.MAX_MEMORY_SIZE:
            self.program_counter = 0

    @timetrack
    def stackPointerDec(self):
        self.stack_pointer -= 1
        if self.stack_pointer < 0x00:
            self.stack_pointer = 0xFF

    @timetrack
    def stackPointerInc(self):
        self.cycleInc()
        self.stack_pointer += 1
        if self.stack_pointer > 0xFF:
            self.stack_pointer = 0x00

    @timetrack
    def getStackPointerAddress(self):
        return self.stack_pointer | 0x0100

    @timetrack
    def savePCAtStackPointer(self):
        if self.INS == 'BRK':
            hi_byte = ((self.program_counter) & 0b1111111100000000) >> 8
            lo_byte = (self.program_counter) & 0b0000000011111111
        else:
            hi_byte = ((self.program_counter - 1) & 0b1111111100000000) >> 8
            lo_byte = (self.program_counter - 1) & 0b0000000011111111
        self.writeMemory(data=hi_byte, address=self.getStackPointerAddress(), bytes=1)
        self.stackPointerDec()
        self.writeMemory(data=lo_byte, address=self.getStackPointerAddress(), bytes=1)
        self.stackPointerDec()

    @timetrack
    def saveByteAtStackPointer(self, data=None):
        # Enforce 1 byte size
        assert(0x00 <= data <= 0xFF)
        assert(data is not None)
        self.writeMemory(data=data, address=self.getStackPointerAddress(), bytes=1)
        self.stackPointerDec()

    @timetrack
    def loadPCFromStackPointer(self):
        self.stackPointerInc()
        lo_byte = self.readMemory(increment_pc=False, address=self.getStackPointerAddress(), bytes=1)
        self.stackPointerInc()
        hi_byte = self.readMemory(increment_pc=False, address=self.getStackPointerAddress(), bytes=1)
        self.program_counter = lo_byte
        self.program_counter += (hi_byte << 8)

    @timetrack
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
        self.flags['U'] = 1
        # self.flags['B'] = 1

    @timetrack
    def readMemory(self, increment_pc=True, address=None, bytes=1) -> int:
        if address:
            assert(0x0000 <= address <= 0xFFFF)
        data = 0
        for byte in range(bytes):
            self.cycleInc()
            if not address:
                data += (self.memory[self.program_counter] * (0x100 ** byte))
                if self.logging:
                    self.logAction(f'Read  memory address [{self.program_counter:04X}] : value [{self.memory[self.program_counter]:02X}]')
            else:
                data += (self.memory[address + byte] * (0x100 ** byte))
                if self.logging:
                    self.logAction(f'Read  memory address [{(address + byte):04X}] : value [{self.memory[address + byte]:02X}]')

            if increment_pc:
                self.programCounterInc()

            # Begin Apple I hooks
            if address is not None and (address + byte) == self.hooks['KBD']:  # Reading KBD clears b7 on KBDCR
                self.memory[self.hooks['KBDCR']] = self.memory[self.hooks['KBDCR']] & 0b01111111

        return data

    @timetrack
    def writeMemory(self, data, address, bytes=1):
        if address:
            assert(0x0000 <= address <= 0xFFFF)

        for byte in range(bytes):
            self.cycleInc()
            self.memory[address + byte] = data
            if self.logging:
                self.logAction(f'Write memory address [{address + byte:04X}] : value [{data:02X}]')

            # Begin Apple I hooks
            if (address + byte) == self.hooks['DSP']:
                self.memory[self.hooks['DSP']] = self.memory[self.hooks['DSP']] | 0b10000000

    @timetrack
    def setFlagsByRegister(self, register=None, flags=[]):
        if 'Z' in flags:
            if self.registers[register] == 0:
                self.flags['Z'] = 1
            else:
                self.flags['Z'] = 0
            if self.logging:
                self.logAction(action=f'Setting Z flag based on register [{register}] : value [{self.registers[register]:02X}]')

        if 'N' in flags:
            self.flags['N'] = self.registers[register] >> 7 & 1
            if self.logging:
                self.logAction(action=f'Setting N flag based on register [{register}] : value [{self.registers[register]:>08b}]')

    @timetrack
    def setFlagsByValue(self, value=None, flags=[]):
        if value is None or len(flags) == 0:
            return

        if 'Z' in flags:
            if value == 0:
                self.flags['Z'] = 1
            else:
                self.flags['Z'] = 0
            if self.logging:
                self.logAction(action=f'Setting Z flag based on value [{value:02X}]')

        if 'N' in flags:
            if value & 0b10000000 > 0:
                self.flags['N'] = 1
            else:
                self.flags['N'] = 0
            if self.logging:
                self.logAction(action=f'Setting N flag based on value [{value:>08b}]')

    @timetrack
    def setFlagsManually(self, flags=[], value=None):
        if value is None or value < 0 or value > 1:
            return
        for flag in flags:
            self.flags[flag] = value
            if self.logging:
                self.logAction(action=f'Setting {flag} flag manually to [{value}]')

    @timetrack
    def determineAddress(self, mode):
        address = 0
        if mode == 'ZP':
            address = self.readMemory()
            return address
        elif mode == 'ZP_X':
            address = self.readMemory()
            address += self.registers['X']
            # Zero Page address wraps around if the value exceeds 0xFF
            address = address % 0x100
            self.cycleInc()
            return address
        elif mode == 'ZP_Y':
            address = self.readMemory()
            address += self.registers['Y']
            # Zero Page address wraps around if the value exceeds 0xFF
            address = address % 0x100
            self.cycleInc()
            return address
        elif mode == 'ABS':
            address = self.readMemory(bytes=2)
            return address
        elif mode == 'ABS_X':
            address = self.readMemory(bytes=2)
            address += self.registers['X']
            if int(address / 0x100) != int((address - self.registers['X']) / 0x100) or (self.INS[0:3] in CPU6502.OPCODES_WRITE_TO_MEMORY):
                self.cycleInc()  # Only if PAGE crossed or instruction writes to memory
            return address
        elif mode == 'ABS_Y':
            address = self.readMemory(bytes=2)
            address += self.registers['Y']
            if (int(address / 0x100) != int((address - self.registers['Y']) / 0x100)) or (self.INS[0:3] in CPU6502.OPCODES_WRITE_TO_MEMORY):
                self.cycleInc()  # Only if PAGE crossed or instruction writes to memory
            return address
        elif mode == 'IND':  # Indirect
            address = self.readMemory(bytes=2)
            return address
        elif mode == 'IND_X':
            address = self.readMemory()
            address += self.registers['X']
            # Zero Page address wraps around if the value exceeds 0xFF
            address = address % 0x100
            self.cycleInc()
            address = self.readMemory(address=address, increment_pc=False, bytes=2)
            return address
        elif mode == 'IND_Y':
            address = self.readMemory()
            address = self.readMemory(address=address, increment_pc=False, bytes=2)
            address += self.registers['Y']
            if int(address / 0x100) != int((address - self.registers['Y']) / 0x100) or (self.INS[0:3] in CPU6502.OPCODES_WRITE_TO_MEMORY):
                self.cycleInc()  # Only if PAGE crossed or instruction writes to memory
            return address

        return address

    @timetrack
    def getProcessorStatus(self) -> int:
        order = ['C', 'Z', 'I', 'D', 'B', 'U', 'V', 'N']
        state = 0
        for shift, flag in enumerate(order):
            state += (self.flags[flag] << shift)
        return state

    @timetrack
    def getProcessorStatusString(self) -> str:
        order = ['C', 'Z', 'I', 'D', 'B', 'U', 'V', 'N']
        flag_string = ''
        for shift, flag in enumerate(reversed(order)):
            # flag_string += bcolors.CBLUEBG + flag.upper() + bcolors.ENDC if self.flags[flag] == 1 else bcolors.CGREY + flag.lower() + bcolors.ENDC
            # flag_string += flag.upper() if self.flags[flag] == 1 else flag.lower()
            flag_string += flag.upper() if self.flags.get(flag, 1) == 1 else flag.lower()
        return flag_string

    @timetrack
    def setProcessorStatus(self, flags: int):
        order = ['C', 'Z', 'I', 'D', 'B', 'U', 'V', 'N']
        for shift, flag in enumerate(order):
            flag_value = (flags >> shift) & 0b00000001
            self.setFlagsManually(flags=[flag], value=flag_value)

    def handleBRK(self):
        address = self.memory[0xFFFF] << 8
        address += self.memory[0xFFFE]
        self.program_counter = address

    def handleSingleByteInstruction(self):
        self.cycleInc()
        # self.readMemory()

    @timetrack
    def execute(self):
        try:
            self.start_time = datetime.datetime.now()
            # Set starting position based on 0xFFFE/F
            # self.handleBRK()

            self.OPCODE = self.readMemory()
            self.INS = CPU6502.OPCODES.get(self.OPCODE, None)
            bne_count = 0
            while self.INS is not None and self.cycles <= self.cycle_limit and bne_count <= 20:

                self.extraFunctions()

                # Remove this when done testing

                if self.INS == 'BNE' or self.program_counter in [0x336D, 0x336E, 0x336F]:
                    bne_count += 1
                else:
                    bne_count = 0

                if self.INS == 'BRK' and self.enableBRK:
                    # Reference wiki.nesdev.com/w/index.php/Status_flags
                    # Possibly need a readMemory() call here according to http://nesdev.com/the%20%27B%27%20flag%20&%20BRK%20instruction.txt
                    self.readMemory()  # BRK is 2 byte instruction - this byte is read and ignored
                    # Save program counter to stack
                    self.savePCAtStackPointer()
                    # Save flags to stack
                    value = self.getProcessorStatus()
                    # Manually set bits 4 and 5 to 1
                    value = value | 0b00110000
                    self.saveByteAtStackPointer(data=value)
                    # Set B flag
                    self.setFlagsManually(['B'], 1)
                    # Set interrupt disable flag
                    self.setFlagsManually(['I'], 1)
                    # Manually change PC to 0xFFFE
                    self.handleBRK()

                elif self.INS == 'RTI':
                    # Set flags from stack
                    flags = self.loadByteFromStackPointer()
                    # PLP and BRK should ignore bits 4 & 5
                    self.setProcessorStatus(flags=flags)
                    # Get PC from stack
                    self.loadPCFromStackPointer()

                elif self.INS in ['PHP_IMP', 'PLP_IMP']:
                    # Push
                    if self.INS == 'PHP_IMP':
                        value = self.getProcessorStatus()
                        # Manually set bits 4 and 5 to 1
                        value = value | 0b00110000
                        self.saveByteAtStackPointer(data=value)
                        self.handleSingleByteInstruction()
                    elif self.INS == 'PLP_IMP':
                        # Pull
                        # PLP and BRK should ignore bits 4 & 5
                        flags = self.loadByteFromStackPointer()
                        self.setProcessorStatus(flags=flags)
                        self.handleSingleByteInstruction()

                elif self.INS in ['BIT_ZP', 'BIT_ABS']:
                    ins_set = self.INS.split('_')
                    address_mode = '_'.join(_ for _ in ins_set[1:])
                    address = self.determineAddress(mode=address_mode)
                    value = self.readMemory(address=address, increment_pc=False, bytes=1)

                    zero_flag = 1 if (self.registers['A'] & value) == 0 else 0
                    self.setFlagsManually(flags=['Z'], value=zero_flag)

                    self.setFlagsByValue(value=value, flags=['N'])

                    overflow_flag = (value & 0b01000000) >> 6
                    self.setFlagsManually(flags=['V'], value=overflow_flag)

                elif self.INS == 'PHA_IMP':
                    value = self.registers['A']
                    self.saveByteAtStackPointer(data=value)
                    self.handleSingleByteInstruction()

                elif self.INS == 'PLA_IMP':
                    value = self.loadByteFromStackPointer()
                    self.registers['A'] = value
                    self.setFlagsByRegister(register='A', flags=['N', 'Z'])
                    self.handleSingleByteInstruction()

                elif self.INS in ['ROL_ACC', 'ROL_ZP', 'ROL_ZP_X', 'ROL_ABS', 'ROL_ABS_X', 'ROR_ACC', 'ROR_ZP', 'ROR_ZP_X', 'ROR_ABS', 'ROR_ABS_X']:
                    ins_set = self.INS.split('_')
                    address_mode = '_'.join(_ for _ in ins_set[1:])
                    if address_mode == 'ACC':
                        value = self.registers['A']
                        self.handleSingleByteInstruction()
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

                elif self.INS in ['CMP_IM', 'CMP_ZP', 'CMP_ZP_X', 'CMP_ABS', 'CMP_ABS_X', 'CMP_ABS_Y', 'CMP_IND_X', 'CMP_IND_Y',
                                  'CPX_IM', 'CPX_ZP', 'CPX_ABS',
                                  'CPY_IM', 'CPY_ZP', 'CPY_ABS']:
                    target = 'A' if self.INS[2] not in ['X', 'Y'] else self.INS[2]
                    if self.INS in ['CMP_IM', 'CPX_IM', 'CPY_IM']:
                        value = self.readMemory()
                    else:
                        ins_set = self.INS.split('_')
                        address_mode = '_'.join(_ for _ in ins_set[1:])
                        address = self.determineAddress(mode=address_mode)
                        value = self.readMemory(address=address, increment_pc=False, bytes=1)

                    compare = self.registers[target]
                    self.setFlagsManually(['C'], 0)
                    self.setFlagsManually(['Z'], 0)
                    if compare >= value:
                        self.setFlagsManually(['C'], 1)
                        # self.setFlagsManually(['Z'], 0)
                    if compare == value:
                        # self.setFlagsManually(['C'], 0)
                        self.setFlagsManually(['Z'], 1)
                    # if compare < value:
                    result = (compare - value) & 0b0000000011111111
                    self.setFlagsByValue(value=result, flags=['N'])

                elif self.INS in ['BEQ', 'BNE',
                                  'BCC', 'BCS',
                                  'BMI', 'BPL',
                                  'BVC', 'BVS']:

                    # Instruction: [Flag, Value to Test]
                    comparisons = {
                        'BEQ': ['Z', 1],
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
                        if offset > 127:
                            offset = (256 - offset) * (-1)
                        self.program_counter += offset
                        self.cycleInc()
                        if self.logging:
                            self.logAction(f'Branch test passed. Jumping to location [{self.program_counter:04X}] offset [{offset}] bytes')
                        # Check if page was crossed
                        if ((self.program_counter & 0b1111111100000000) != ((self.program_counter - offset) & 0b1111111100000000)):
                            self.cycleInc()

                elif self.INS in ['TAX_IMP', 'TXA_IMP', 'TAY_IMP', 'TYA_IMP']:
                    source = self.INS[1]
                    dest = self.INS[2]
                    self.registers[dest] = self.registers[source]
                    self.setFlagsByRegister(register=dest, flags=['N', 'Z'])
                    self.handleSingleByteInstruction()  # 1 byte instruction -- read next byte and ignore

                elif self.INS in ['TXS_IMP', 'TSX_IMP']:
                    source = self.INS[1]
                    dest = self.INS[2]
                    if dest == 'X':
                        self.registers[dest] = self.stack_pointer
                        self.setFlagsByRegister(register=dest, flags=['N', 'Z'])
                    elif dest == 'S':
                        self.stack_pointer = self.registers[source]

                    self.handleSingleByteInstruction()  # 1 byte instruction -- read next byte and ignore

                elif self.INS in ['ASL_ACC', 'ASL_ZP', 'ASL_ZP_X', 'ASL_ABS', 'ASL_ABS_X']:
                    if self.INS == 'ASL_ACC':
                        value = self.registers['A']
                        carry_flag = 1 if (value & 0b10000000) > 0 else 0
                        value = value << 1
                        value = value & 0b0000000011111110
                        self.registers['A'] = value
                        self.setFlagsByRegister(register='A', flags=['Z', 'N'])
                        self.setFlagsManually(flags=['C'], value=carry_flag)
                        self.handleSingleByteInstruction()  # 1 byte instruction -- read next byte and ignore
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

                elif self.INS in ['LSR_ACC', 'LSR_ZP', 'LSR_ZP_X', 'LSR_ABS', 'LSR_ABS_X']:
                    if self.INS == 'LSR_ACC':
                        value = self.registers['A']
                        carry_flag = 1 if (value & 0b00000001) > 0 else 0
                        value = value >> 1
                        value = value & 0b0000000001111111
                        self.registers['A'] = value
                        self.setFlagsByRegister(register='A', flags=['Z', 'N'])
                        self.setFlagsManually(flags=['C'], value=carry_flag)
                        self.handleSingleByteInstruction()  # 1 byte instruction -- read next byte and ignore
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

                elif self.INS == 'ORA_IM':
                    value = self.readMemory()
                    result = self.registers['A'] | value
                    self.registers['A'] = result
                    self.setFlagsByRegister(register='A', flags=['Z', 'N'])

                elif self.INS in ['ORA_ZP', 'ORA_ZP_X', 'ORA_ABS', 'ORA_ABS_X', 'ORA_ABS_Y', 'ORA_IND_X', 'ORA_IND_Y']:
                    ins_set = self.INS.split('_')
                    address_mode = '_'.join(_ for _ in ins_set[1:])
                    address = self.determineAddress(mode=address_mode)
                    value = self.readMemory(address=address, increment_pc=False, bytes=1)
                    result = self.registers['A'] | value
                    self.registers['A'] = result
                    self.setFlagsByRegister(register='A', flags=['Z', 'N'])

                elif self.INS == 'EOR_IM':
                    value = self.readMemory()
                    result = self.registers['A'] ^ value
                    self.registers['A'] = result
                    self.setFlagsByRegister(register='A', flags=['Z', 'N'])

                elif self.INS in ['EOR_ZP', 'EOR_ZP_X', 'EOR_ABS', 'EOR_ABS_X', 'EOR_ABS_Y', 'EOR_IND_X', 'EOR_IND_Y']:
                    ins_set = self.INS.split('_')
                    address_mode = '_'.join(_ for _ in ins_set[1:])
                    address = self.determineAddress(mode=address_mode)
                    value = self.readMemory(address=address, increment_pc=False, bytes=1)
                    result = self.registers['A'] ^ value
                    self.registers['A'] = result
                    self.setFlagsByRegister(register='A', flags=['Z', 'N'])

                elif self.INS == 'AND_IM':
                    value = self.readMemory()
                    result = self.registers['A'] & value
                    self.registers['A'] = result
                    self.setFlagsByRegister(register='A', flags=['Z', 'N'])

                elif self.INS in ['AND_ZP', 'AND_ZP_X', 'AND_ABS', 'AND_ABS_X', 'AND_ABS_Y', 'AND_IND_X', 'AND_IND_Y']:
                    ins_set = self.INS.split('_')
                    address_mode = '_'.join(_ for _ in ins_set[1:])
                    address = self.determineAddress(mode=address_mode)
                    value = self.readMemory(address=address, increment_pc=False, bytes=1)
                    result = self.registers['A'] & value
                    self.registers['A'] = result
                    self.setFlagsByRegister(register='A', flags=['Z', 'N'])

                elif self.INS in ['SBC_ZP', 'SBC_ZP_X', 'SBC_ABS', 'SBC_ABS_X', 'SBC_ABS_Y', 'SBC_IND_X', 'SBC_IND_Y']:
                    orig_A_register_value = self.registers['A']
                    ins_set = self.INS.split('_')
                    address_mode = '_'.join(_ for _ in ins_set[1:])
                    address = self.determineAddress(mode=address_mode)
                    value = self.readMemory(address=address, increment_pc=False, bytes=1)

                    if self.flags['D'] == 0:
                        value = 0b11111111 - value
                        orig_value = value
                        value += self.registers['A'] + self.flags['C']
                        self.registers['A'] = value & 0b0000000011111111
                        self.setFlagsByRegister(register='A', flags=['Z', 'N'])
                        carry_flag = 1 if (value & 0b1111111100000000) > 0 else 0
                        self.setFlagsManually(flags=['C'], value=carry_flag)
                        overflow_flag = 0
                        if (orig_A_register_value & 0b10000000) == (orig_value & 0b10000000):
                            if ((self.registers['A'] & 0b10000000) != (orig_A_register_value & 0b10000000)) or ((self.registers['A'] & 0b10000000) != (orig_value & 0b10000000)):
                                overflow_flag = 1
                        self.setFlagsManually(flags=['V'], value=overflow_flag)
                    elif self.flags['D'] == 1:
                        value = value ^ 0xFF
                        c = (self.registers['A'] & 0x0f) + (value & 0x0f) + (self.flags['C'])
                        if (c < 0x10):
                            c = (c - 0x06) & 0x0f
                        c += (self.registers['A'] & 0xf0) + (value & 0xf0)
                        v = (c >> 1) ^ c
                        if (c < 0x100):
                            c = (c + 0xa0) & 0xff
                        self.registers['A'] = c & 0xFF
                        self.setFlagsByRegister(register='A', flags=['N', 'Z'])
                        self.setFlagsManually(flags='C', value=0)
                        if c > 0xFF:
                            self.setFlagsManually(flags='C', value=1)
                        if (((self.registers['A'] ^ value) & 0x80) != 0):
                            v = 0
                        self.setFlagsManually(flags='V', value=1 if v > 0 else 0)

                elif self.INS == 'SBC_IM':
                    orig_A_register_value = self.registers['A']
                    value = self.readMemory()
                    if self.flags['D'] == 0:
                        value = 0b11111111 - value
                        orig_value = value
                        value += self.registers['A'] + self.flags['C']
                        self.registers['A'] = value & 0b0000000011111111
                        self.setFlagsByRegister(register='A', flags=['Z', 'N'])
                        carry_flag = 1 if (value & 0b1111111100000000) > 0 else 0
                        self.setFlagsManually(flags=['C'], value=carry_flag)
                        overflow_flag = 0
                        if (orig_A_register_value & 0b10000000) == (orig_value & 0b10000000):
                            if ((self.registers['A'] & 0b10000000) != (orig_A_register_value & 0b10000000)) or ((self.registers['A'] & 0b10000000) != (orig_value & 0b10000000)):
                                overflow_flag = 1
                        self.setFlagsManually(flags=['V'], value=overflow_flag)
                    elif self.flags['D'] == 1:
                        value = value ^ 0xFF
                        c = (self.registers['A'] & 0x0f) + (value & 0x0f) + (self.flags['C'])
                        if (c < 0x10):
                            c = (c - 0x06) & 0x0f
                        c += (self.registers['A'] & 0xf0) + (value & 0xf0)
                        v = (c >> 1) ^ c
                        if (c < 0x100):
                            c = (c + 0xa0) & 0xff
                        self.registers['A'] = c & 0xFF
                        self.setFlagsByRegister(register='A', flags=['N', 'Z'])
                        self.setFlagsManually(flags='C', value=0)
                        if c > 0xFF:
                            self.setFlagsManually(flags='C', value=1)
                        if (((self.registers['A'] ^ value) & 0x80) != 0):
                            v = 0
                        self.setFlagsManually(flags='V', value=1 if v > 0 else 0)

                elif self.INS == 'ADC_IM':
                    orig_A_register_value = self.registers['A']
                    value = self.readMemory()
                    if self.flags['D'] == 0:
                        orig_value = value
                        value += self.registers['A'] + self.flags['C']
                        self.registers['A'] = value & 0b0000000011111111
                        self.setFlagsByRegister(register='A', flags=['Z', 'N'])
                        carry_flag = 1 if (value & 0b1111111100000000) > 0 else 0
                        self.setFlagsManually(flags=['C'], value=carry_flag)
                        overflow_flag = 0
                        if (orig_A_register_value & 0b10000000) == (orig_value & 0b10000000):
                            if ((self.registers['A'] & 0b10000000) != (orig_A_register_value & 0b10000000)) or ((self.registers['A'] & 0b10000000) != (orig_value & 0b10000000)):
                                overflow_flag = 1
                        self.setFlagsManually(flags=['V'], value=overflow_flag)
                    elif self.flags['D'] == 1:
                        c = (self.registers['A'] & 0x0f) + (value & 0x0f) + (self.flags['C'])
                        if c > 0x09:
                            c = (c - 0x0a) | 0x10
                        c += (self.registers['A'] & 0xf0) + (value & 0xf0)
                        v = (c >> 1) ^ c
                        if (c > 0x99):
                            c += 0x60
                        self.registers['A'] = c & 0xFF
                        self.setFlagsByRegister(register='A', flags=['N', 'Z'])
                        self.setFlagsManually(flags='C', value=0)
                        if c > 0xFF:
                            self.setFlagsManually(flags='C', value=1)
                        if (((self.registers['A'] ^ value) & 0x80) != 0):
                            v = 0
                        self.setFlagsManually(flags='V', value=1 if v > 0 else 0)

                elif self.INS in ['ADC_ZP', 'ADC_ZP_X', 'ADC_ABS', 'ADC_ABS_X', 'ADC_ABS_Y', 'ADC_IND_X', 'ADC_IND_Y']:
                    orig_A_register_value = self.registers['A']
                    ins_set = self.INS.split('_')
                    address_mode = '_'.join(_ for _ in ins_set[1:])
                    address = self.determineAddress(mode=address_mode)
                    value = self.readMemory(address=address, increment_pc=False, bytes=1)
                    if self.flags['D'] == 0:
                        orig_value = value
                        value += self.registers['A'] + self.flags['C']
                        self.registers['A'] = value & 0b0000000011111111
                        self.setFlagsByRegister(register='A', flags=['Z', 'N'])
                        carry_flag = 1 if (value & 0b1111111100000000) > 0 else 0
                        self.setFlagsManually(flags=['C'], value=carry_flag)
                        overflow_flag = 0
                        if (orig_A_register_value & 0b10000000) == (orig_value & 0b10000000):
                            if ((self.registers['A'] & 0b10000000) != (orig_A_register_value & 0b10000000)) or ((self.registers['A'] & 0b10000000) != (orig_value & 0b10000000)):
                                overflow_flag = 1
                        self.setFlagsManually(flags=['V'], value=overflow_flag)
                    elif self.flags['D'] == 1:
                        c = (self.registers['A'] & 0x0f) + (value & 0x0f) + (self.flags['C'])
                        if c > 0x09:
                            c = (c - 0x0a) | 0x10
                        c += (self.registers['A'] & 0xf0) + (value & 0xf0)
                        v = (c >> 1) ^ c
                        if (c > 0x99):
                            c += 0x60
                        self.registers['A'] = c & 0xFF
                        self.setFlagsByRegister(register='A', flags=['N', 'Z'])
                        self.setFlagsManually(flags='C', value=0)
                        if c > 0xFF:
                            self.setFlagsManually(flags='C', value=1)
                        if (((self.registers['A'] ^ value) & 0x80) != 0):
                            v = 0
                        self.setFlagsManually(flags='V', value=1 if v > 0 else 0)

                elif self.INS == 'JSR_ABS':
                    ins_set = self.INS.split('_')
                    address_mode = '_'.join(_ for _ in ins_set[1:])
                    address = self.determineAddress(mode=address_mode)
                    self.savePCAtStackPointer()
                    self.program_counter = address
                    if self.logging:
                        self.logAction(f'Jumping to location [{self.program_counter:04X}]')
                    self.cycleInc()

                elif self.INS == 'RTS_IMP':
                    self.handleSingleByteInstruction()
                    self.loadPCFromStackPointer()
                    self.programCounterInc()

                elif self.INS in ['INC_ZP', 'INC_ZP_X', 'INC_ABS', 'INC_ABS_X']:
                    ins_set = self.INS.split('_')
                    address_mode = '_'.join(_ for _ in ins_set[1:])
                    address = self.determineAddress(mode=address_mode)
                    value = self.readMemory(address=address, increment_pc=False, bytes=1)
                    value += 1
                    value = value % 0x100
                    self.cycleInc()  # Is this really necessary? -- apparently, yes
                    self.writeMemory(data=value, address=address, bytes=1)
                    self.setFlagsByValue(value=value, flags=['N', 'Z'])

                elif self.INS in ['INX_IMP', 'INY_IMP']:
                    value = self.registers[self.INS[2]]
                    value += 1
                    value = value % 0x100
                    self.cycleInc()  # Is this really necessary?
                    self.registers[self.INS[2]] = value
                    self.setFlagsByRegister(register=self.INS[2], flags=['N', 'Z'])

                elif self.INS in ['DEC_ZP', 'DEC_ZP_X', 'DEC_ABS', 'DEC_ABS_X']:
                    ins_set = self.INS.split('_')
                    address_mode = '_'.join(_ for _ in ins_set[1:])
                    address = self.determineAddress(mode=address_mode)
                    value = self.readMemory(address=address, increment_pc=False, bytes=1)
                    value -= 1
                    if value < 0:
                        value = 0xFF
                    self.cycleInc()  # Is this really necessary? -- apparently, yes
                    self.writeMemory(data=value, address=address, bytes=1)
                    self.setFlagsByValue(value=value, flags=['N', 'Z'])

                elif self.INS in ['DEX_IMP', 'DEY_IMP']:
                    self.handleSingleByteInstruction()
                    value = self.registers[self.INS[2]]
                    value -= 1
                    if value < 0:
                        value = 0xFF
                    self.registers[self.INS[2]] = value
                    self.setFlagsByRegister(register=self.INS[2], flags=['N', 'Z'])

                elif self.INS.startswith('ST'):
                    ins_set = self.INS.split('_')
                    target = ins_set[0][2]
                    address_mode = '_'.join(_ for _ in ins_set[1:])
                    address = self.determineAddress(mode=address_mode)
                    self.writeMemory(data=self.registers[target], address=address, bytes=1)

                elif self.INS in ['CLC_IMP', 'CLI_IMP', 'CLD_IMP', 'CLV_IMP', 'SEC_IMP', 'SED_IMP', 'SEI_IMP']:
                    if self.INS in ['CLC_IMP', 'CLI_IMP', 'CLD_IMP', 'CLV_IMP']:
                        self.setFlagsManually(flags=[self.INS[2]], value=0)
                    else:
                        self.setFlagsManually(flags=[self.INS[2]], value=1)
                    self.handleSingleByteInstruction()

                elif self.INS.startswith('LD'):
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

                elif self.INS in ['JMP_ABS']:
                    ins_set = self.INS.split('_')
                    address_mode = '_'.join(_ for _ in ins_set[1:])
                    address = self.determineAddress(mode=address_mode)
                    self.program_counter = address
                    if self.logging:
                        self.logAction(f'Jumping to location [{self.program_counter:04X}]')

                elif self.INS == 'JMP_IND':
                    address = self.determineAddress(mode='IND')
                    address = self.readMemory(address=address, increment_pc=False, bytes=2)
                    self.program_counter = address
                    if self.logging:
                        self.logAction(f'Jumping to location [{self.program_counter:04X}]')

                elif self.INS == 'NOP':
                    self.handleSingleByteInstruction()

                self.OPCODE = self.readMemory()
                self.INS = CPU6502.OPCODES.get(self.OPCODE, None)

        except Exception as e:
            print(traceback.print_exc())

        finally:

            # Cleanup
            self.execution_time = datetime.datetime.now() - self.start_time
            self.printBenchmarkInfo()
            if self.logging:
                if self.logFile:
                    self.logFile.close()

    @timetrack
    def getLogString(self):
        combined = {**{'%-10s' % 'Cycle': '%-10s' % str(self.cycles),
                    '%-10s' % 'INS': '%-10s' % self.INS},
                    **self.registers,
                    **self.flags,
                    **{'SP': '0x{0:0{1}X}'.format(self.getStackPointerAddress(), 4),
                    'PC': '0x{0:0{1}X}'.format(self.program_counter, 4),
                        'MEM': '0x{0:0{1}X}'.format(self.memory[self.program_counter], 2),
                        '%-10s' % 'FLAGS': '%-10s' % self.getProcessorStatusString()
                       },
                    '%-20s' % 'ACTION': '%-20s' % ' -> '.join(self.action)
                    }
        return combined

    @timetrack
    def getLogHeaderString(self):
        combined = self.getLogString()
        # headerString = bcolors.OKBLUE + '\t'.join(combined.keys()) + bcolors.ENDC
        headerString = '\t'.join(combined.keys())
        return headerString

    @timetrack
    def printState(self):
        combined = self.getLogString()
        headerString = self.getLogHeaderString()
        valueString = '\t'.join(str(v) for v in combined.values())
        if self.cycles == 0:
            print(headerString)
        print(valueString)

    @timetrack
    def initializeLog(self):
        self.log = []
        headerString = self.getLogHeaderString()
        self.log.append(headerString)
        if self.logFile:
            self.logFile.write(headerString)

    @timetrack
    def logState(self):
        if self.logging:
            combined = self.getLogString()
            # valueString = bcolors.ENDC + '\t'.join(str(v) for v in combined.values()) + bcolors.ENDC
            valueString = '\t'.join(str(v) for v in combined.values())
            self.log.append(valueString)
            if self.logFile:
                if self.cycles % 250000 == 0:
                    self.logFile.close()
                    self.logFile = open(self.logFile.name, 'w')
                    self.log = []
                self.logFile.write(valueString + '\n')

    def printLog(self):
        for line in self.log:
            print(line)

    def benchmarkInfo(self) -> str:
        return f'\nCycles: {self.cycles - 1:,} :: Elapsed time: {self.execution_time} :: Cycles/sec: {(self.cycles - 1) / (.0001 + self.execution_time.total_seconds()):0,.2f}'

    def printBenchmarkInfo(self):
        print(self.benchmarkInfo())
        pass

    @timetrack
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
    cpu = CPU6502(cycle_limit=1000, printActivity=False)
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
    cpu = CPU6502(cycle_limit=100, printActivity=True)
    cpu.reset(program_counter=0x2000)

    program = [0xA9, 0x19,        # LDA_IM 25 ; Load initial value
               0x0A,              # ASL ACC ; Double accumulator value
               0x8D, 0x00, 0x30,  # STA [0x3000] ; Store doubled value in memory
               0x0A,              # ASL ACC ; Double accumulator again (x4 total)
               0x0A,              # ASL ACC ; Double accumulator again (x8 total)
               0x18,              # CLC ; Clear carry flag for some reason
               0x6D, 0x00, 0x30,  # ADC [0x3000] ; Add memory to accumulator (effectively value x 8 + value x 2 = value x 10)
               0x8D, 0x01, 0x30,  # STA [0x3000] ; Store accumulator value in memory
               ]
    cpu.loadProgram(instructions=program, memoryAddress=0x2000, mainProgram=True)
    cpu.execute()
    cpu.memoryDump(startingAddress=0x2000, endingAddress=0x2017)
    cpu.memoryDump(startingAddress=0x3000, endingAddress=0x3001, display_format='Dec')


def flags_test():
    cpu = CPU6502(cycle_limit=10)
    cpu.setFlagsManually(['C', 'Z', 'I', 'D', 'B', 'U', 'V', 'N'], 0)
    cpu.getProcessorStatus()
    cpu.setFlagsManually(['C', 'Z', 'I', 'D', 'B', 'U', 'V', 'N'], 1)
    cpu.getProcessorStatus()
    cpu.setFlagsManually(['C', 'Z', 'I', 'D', 'B', 'U', 'V', 'N'], 0)
    flags = ['N', 'V', 'U', 'B', 'D', 'I', 'Z', 'C']
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


def functional_test_program():
    program = []
    with open('binary/6502_functional_test.bin', 'rb') as f:
        data = f.read()
    for d in data:
        program.append(d)

    # print(program[0x03F6: 0x040F])
    # print(len(program))
    cpu = None
    cpu = CPU6502(cycle_limit=200_000_000, printActivity=False, enableBRK=True, logging=True, logFile='log.txt')
    cpu.reset(program_counter=0x0400)
    cpu.loadProgram(instructions=program, memoryAddress=0x000A, mainProgram=False)
    cpu.program_counter = 0x0400
    # print(cpu.memory[0x400:0x40F])
    cpu.execute()
    print(f'{cpu.cycles:,} cycles. Elapesd time {cpu.execution_time}.')


def runBenchmark():
    cpu = None
    cpu = CPU6502(cycle_limit=750_000, printActivity=False, enableBRK=False, logFile=None)
    cpu.reset(program_counter=0x8000)
    cpu.memory[0x0090] = 0
    program = [
        0xA2, 0x00,  # LDX 0
        0xA0, 0x00,  # LDY 0
        0xE8,  # INX ; 0x8004
        0xE0, 0xFF,  # CPX 255
        0xF0, 0x03,  # BEQ +4
        0x4C, 0x04, 0x80,  # JMP to 0x8004
        0xC8,  # INY
        0xC0, 0xFF,  # CPY 255
        0xF0, 0x03,  # BEQ +4
        0x4C, 0x04, 0x80,  # JMP to 0x8004
        0x00,  # BRK
    ]
    cpu.loadProgram(instructions=program, memoryAddress=0x8000, mainProgram=True)
    cpu.execute()
    print(f'Cycles: {cpu.cycles - 1:,} :: Elapsed time: {cpu.execution_time} :: Cycles/sec: {(cpu.cycles - 1) / cpu.execution_time.total_seconds():0,.2f}')


def hundred_doors():
    import programs.hundred_doors
    program = programs.hundred_doors.program
    starting_address = programs.hundred_doors.starting_address

    cpu = None
    cpu = CPU6502(cycle_limit=1000, printActivity=True, enableBRK=False)
    cpu.reset(program_counter=starting_address)
    cpu.loadProgram(instructions=program, memoryAddress=starting_address, mainProgram=True)
    cpu.execute()

    for test in programs.hundred_doors.tests:
        cpu.memoryDump(startingAddress=test['memory_range'][0], endingAddress=test['memory_range'][1] + 1, display_format='Dec')
        if test['expected_values'] is not None:
            print(cpu.memory[test['memory_range'][0]:test['memory_range'][1] + 1] == test['expected_values'])

    print(cpu.benchmarkInfo())


def sieve_of_erastosthenes():
    import programs.sieve_of_eratosthenes
    program = programs.sieve_of_eratosthenes.program
    starting_address = programs.sieve_of_eratosthenes.starting_address
    cpu = None
    cpu = CPU6502(cycle_limit=100_000, printActivity=False, enableBRK=False)
    cpu.reset(program_counter=starting_address)
    cpu.loadProgram(instructions=program, memoryAddress=starting_address, mainProgram=True)
    # cpu.memory[0x0601] = 0x64
    cpu.execute()

    for test in programs.sieve_of_eratosthenes.tests:
        cpu.memoryDump(startingAddress=test['memory_range'][0], endingAddress=test['memory_range'][1], display_format='Dec')
        if test['expected_values'] is not None:
            print(cpu.memory[test['memory_range'][0]:test['memory_range'][1] + 1] == test['expected_values'])

    print(cpu.benchmarkInfo())


def wozmon():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000, printActivity=False, enableBRK=False)
    cpu.reset(program_counter=0xFF00)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    cpu.program_counter = wozmon_address
    cpu.execute()


def apple_i_basic():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.apple_1_basic
    basic_program = programs.apple_1_basic.program
    basic_address = programs.apple_1_basic.starting_address

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=False)
    cpu.reset(program_counter=basic_address)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    cpu.loadProgram(instructions=basic_program, memoryAddress=basic_address, mainProgram=False)
    cpu.program_counter = wozmon_address
    print(f'{basic_address:04X}')
    cpu.execute()


def apple_i_print_chars():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.apple_1_print_characters
    char_program = programs.apple_1_print_characters.program
    char_address = programs.apple_1_print_characters.starting_address

    cpu = None
    cpu = CPU6502(cycle_limit=10_000, printActivity=False, enableBRK=False, logging=True, logFile='log.txt')
    cpu.reset(program_counter=char_address)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    cpu.loadProgram(instructions=char_program, memoryAddress=char_address, mainProgram=False)
    cpu.program_counter = char_address
    cpu.execute()


def blackjack():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.apple_1_basic
    basic_program = programs.apple_1_basic.program
    basic_address = programs.apple_1_basic.starting_address

    import programs.blackjack

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=True, logging=False)
    cpu.reset(program_counter=basic_address)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    cpu.loadProgram(instructions=basic_program, memoryAddress=basic_address, mainProgram=False)

    for tape in programs.blackjack.tapes:
        cpu.loadProgram(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)

    cpu.program_counter = wozmon_address
    print(f'Running {programs.blackjack.name}...')
    print(programs.blackjack.instructions)
    cpu.execute()


def lunar_lander():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.apple_1_basic
    basic_program = programs.apple_1_basic.program
    basic_address = programs.apple_1_basic.starting_address

    import programs.lunar_lander

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=True, logging=True, logFile='log.txt')
    cpu.reset(program_counter=basic_address)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    cpu.loadProgram(instructions=basic_program, memoryAddress=basic_address, mainProgram=False)

    for tape in programs.lunar_lander.tapes:
        cpu.loadProgram(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)

    cpu.program_counter = wozmon_address
    print(programs.lunar_lander.instructions)
    cpu.execute()


def hammurabi():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.apple_1_basic
    basic_program = programs.apple_1_basic.program
    basic_address = programs.apple_1_basic.starting_address

    import programs.hammurabi

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=True, logging=False)
    cpu.reset(program_counter=basic_address)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    cpu.loadProgram(instructions=basic_program, memoryAddress=basic_address, mainProgram=False)

    for tape in programs.hammurabi.tapes:
        cpu.loadProgram(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)

    cpu.program_counter = wozmon_address
    print(programs.hammurabi.instructions)
    cpu.execute()


def microchess():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.microchess as game

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=False, logging=False)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    # cpu.loadProgram(instructions=basic_program, memoryAddress=basic_address, mainProgram=False)

    for tape in game.tapes:
        cpu.loadProgram(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)

    cpu.program_counter = wozmon_address
    print(game.instructions)
    cpu.execute()


def shut_the_box():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.shut_the_box as game

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=False, logging=False)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    # cpu.loadProgram(instructions=basic_program, memoryAddress=basic_address, mainProgram=False)

    for tape in game.tapes:
        cpu.loadProgram(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)

    cpu.program_counter = wozmon_address
    print(game.instructions)
    cpu.execute()


def codebreaker():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.codebreaker as game

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=False, logging=False)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    # cpu.loadProgram(instructions=basic_program, memoryAddress=basic_address, mainProgram=False)

    for tape in game.tapes:
        cpu.loadProgram(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)

    cpu.program_counter = wozmon_address
    print(game.instructions)
    cpu.execute()


def applesoft_basic():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.applesoft_basic as game

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=True, logging=False)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)

    for tape in game.tapes:
        cpu.loadProgram(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)

    cpu.program_counter = wozmon_address
    print(f'Running {game.name}...')
    print(game.instructions)
    cpu.execute()


def apple_30th():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.apple_30th as game

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=True, logging=False)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)

    for tape in game.tapes:
        cpu.loadProgram(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)

    cpu.program_counter = wozmon_address
    print(f'Running {game.name}...')
    print(game.description)
    print(game.instructions)
    cpu.execute()


def startrek():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.apple_1_basic
    basic_program = programs.apple_1_basic.program
    basic_address = programs.apple_1_basic.starting_address

    import programs.startrek as game

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=True, logging=False)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    cpu.loadProgram(instructions=basic_program, memoryAddress=basic_address, mainProgram=False)

    for tape in game.tapes:
        cpu.loadProgram(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)

    cpu.program_counter = wozmon_address
    print(f'Running {game.name}...')
    print(game.description)
    print(game.instructions)
    cpu.execute()


if __name__ == '__main__':
    # run()
    # fibonacci_test()
    # print()
    # fast_multiply_10()
    # print()
    # flags_test()
    # print()
    # functional_test_program()
    # print()
    # runBenchmark()
    # print()
    # hundred_doors()
    # print()
    # sieve_of_erastosthenes()
    # print()
    # wozmon()
    # print()
    # apple_i_basic()
    # print()
    # apple_i_print_chars()
    # print()
    blackjack()
    # print()
    # lunar_lander()
    # print()
    # hammurabi()
    # print()
    # microchess()
    # print()
    # shut_the_box()
    # print()
    # codebreaker()
    # print()
    # applesoft_basic()
    # print()
    # apple_30th()
    # startrek()
