# 6502 machine code processor
import datetime
import time
# from bcolors import bcolors as bcolors
import traceback
import os
import pyjion
pyjion.enable()
os.system("cls")


global tabcount
tabcount = 0

monitoring = False
if monitoring:
    global log
    log = open('time.txt', 'w')


def time_track(func):
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

    VERSION = '0.97'
    MAX_MEMORY_SIZE = 1024 * 64  # 64k memory size
    EIGHT_BIT_MASK = 0b11111111
    SIXTEEN_BIT_HIGH_BYTE_MASK = 0b1111111100000000
    SIXTEEN_BIT_LOW_BYTE_MASK = 0b0000000011111111
    OPCODES_WRITE_TO_MEMORY = ('STA', 'STX', 'STY', 'ROL', 'ROR', 'ASL', 'LSR', 'INC', 'DEC')
    OPCODES_BRANCHING_TABLE = {
        # Instruction: [Flag, Value to Test]
        'BEQ': ['Z', 1],
        'BNE': ['Z', 0],
        'BCC': ['C', 0],
        'BCS': ['C', 1],
        'BMI': ['N', 1],
        'BPL': ['N', 0],
        'BVS': ['V', 1],
        'BVC': ['V', 0],
    }
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

    def __init__(self, cycle_limit=10_000, logging=False, printActivity=False, logFile=None, enableBRK=False, continuous=True):

        self.program_counter = 0xFFFE
        self.stack_pointer = 0xFF  # This is technically 0x01FF since the stack pointer lives on page 01.
        self.cycle_limit = cycle_limit
        self.continuous = continuous

        self.INS = None
        self.start_time = None

        self.enableBRK = enableBRK
        if self.enableBRK:
            CPU6502.OPCODES[0x00] = 'BRK'

        self.logging = logging
        self.log_file = open(logFile, 'w') if logFile else None
        self.action = []
        self.print_activity = printActivity

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

        self.initialize_memory()
        self.cycles = 0
        self.initialize_log()

        self.hooks = {
            'KBD': 0xD010,
            'KBDCR': 0xD011,
            'DSP': 0xD012,
            'DSPCR': 0xD013
        }

    def initialize_memory(self):
        self.memory = [0x00] * CPU6502.MAX_MEMORY_SIZE
        # self.value = 0x0D

    def get_memory(self):
        return self.memory

    def memory_dump(self, startingAddress=None, endingAddress=None, display_format='Hex', items_per_row: int = 8):
        # print('\nMemory Dump:\n')
        print()
        line = ''  # to clear issues with pylance
        header = ''
        row = ''
        while startingAddress <= endingAddress and startingAddress <= CPU6502.MAX_MEMORY_SIZE:
            if display_format == 'Hex':
                header = '0x{0:0{1}X}:'.format(startingAddress, 4) + '\t'
                row = '\t'.join('0x{0:0{1}X}'.format(self.memory[v], 2) for v in range(startingAddress, min(startingAddress + items_per_row, CPU6502.MAX_MEMORY_SIZE)))
            elif display_format == 'Dec':
                header = '0x{0:0{1}X}:'.format(startingAddress, 4) + '\t'
                row = '\t'.join('%-5s' % str(self.memory[v]) for v in range(startingAddress, min(startingAddress + items_per_row, CPU6502.MAX_MEMORY_SIZE)))
            line = header + row
            print(line)
            startingAddress += items_per_row

    @time_track
    def extraFunctions(self):
        pass

    @time_track
    def cycle(self):
        if self.logging:
            self.log_state()
            if self.print_activity:
                self.print_state()
            self.action = []
        self.cycles += 1

    def log_action(self, action=''):
        if self.logging:
            self.action.append(action)

    @time_track
    def program_counter_increment(self):
        self.program_counter += 1
        if self.program_counter >= CPU6502.MAX_MEMORY_SIZE:
            self.program_counter = 0

    @time_track
    def stack_pointer_decrement(self):
        self.stack_pointer -= 1
        if self.stack_pointer < 0x00:
            self.stack_pointer = 0xFF

    @time_track
    def stack_pointer_increment(self):
        self.cycle()
        self.stack_pointer += 1
        if self.stack_pointer > 0xFF:
            self.stack_pointer = 0x00

    @time_track
    def get_stack_pointer_address(self):
        return self.stack_pointer | 0x0100

    @time_track
    def save_pc_at_stack_pointer(self):
        if self.INS == 'BRK':
            hi_byte = ((self.program_counter) & CPU6502.SIXTEEN_BIT_HIGH_BYTE_MASK) >> 8
            lo_byte = (self.program_counter) & CPU6502.SIXTEEN_BIT_LOW_BYTE_MASK
        else:
            hi_byte = ((self.program_counter - 1) & CPU6502.SIXTEEN_BIT_HIGH_BYTE_MASK) >> 8
            lo_byte = (self.program_counter - 1) & CPU6502.SIXTEEN_BIT_LOW_BYTE_MASK
        self.write_memory(data=hi_byte, address=self.get_stack_pointer_address(), bytes=1)
        self.stack_pointer_decrement()
        self.write_memory(data=lo_byte, address=self.get_stack_pointer_address(), bytes=1)
        self.stack_pointer_decrement()

    @time_track
    def save_byte_at_stack_pointer(self, data=None):
        # Enforce 1 byte size
        assert(0x00 <= data <= 0xFF)
        assert(data is not None)
        self.write_memory(data=data, address=self.get_stack_pointer_address(), bytes=1)
        self.stack_pointer_decrement()

    @time_track
    def load_pc_from_stack_pointer(self):
        self.stack_pointer_increment()
        lo_byte = self.read_memory(increment_pc=False, address=self.get_stack_pointer_address(), bytes=1)
        self.stack_pointer_increment()
        hi_byte = self.read_memory(increment_pc=False, address=self.get_stack_pointer_address(), bytes=1)
        self.program_counter = lo_byte
        self.program_counter += (hi_byte << 8)

    @time_track
    def load_byte_from_stack_pointer(self):
        self.stack_pointer_increment()
        return self.read_memory(
            increment_pc=False, address=self.get_stack_pointer_address(), bytes=1
        )

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

    @time_track
    def read_memory(self, increment_pc=True, address=None, bytes=1) -> int:
        if address:
            assert(0x0000 <= address <= 0xFFFF)
        data = 0
        for byte in range(bytes):
            self.cycle()
            if not address:
                data += (self.memory[self.program_counter] * (0x100 ** byte))
                if self.logging:
                    self.log_action(f'Read  memory address [{self.program_counter:04X}] : value [{self.memory[self.program_counter]:02X}]')
            else:
                data += (self.memory[address + byte] * (0x100 ** byte))
                if self.logging:
                    self.log_action(f'Read  memory address [{(address + byte):04X}] : value [{self.memory[address + byte]:02X}]')

            if increment_pc:
                self.program_counter_increment()

            # Begin Apple I hooks
            if address is not None and (address + byte) == self.hooks['KBD']:  # Reading KBD clears b7 on KBDCR
                self.memory[self.hooks['KBDCR']] = self.memory[self.hooks['KBDCR']] & 0b01111111

        return data

    @time_track
    def write_memory(self, data, address, bytes=1):
        if address:
            assert(0x0000 <= address <= 0xFFFF)

        for byte in range(bytes):
            self.cycle()
            self.memory[address + byte] = data
            if self.logging:
                self.log_action(f'Write memory address [{address + byte:04X}] : value [{data:02X}]')

            # Begin Apple I hooks
            if (address + byte) == self.hooks['DSP']:
                self.memory[self.hooks['DSP']] = self.memory[self.hooks['DSP']] | 0b10000000

    @time_track
    def set_flags_by_register(self, register=None, flags=[]):
        if 'Z' in flags:
            self.flags['Z'] = 1 if self.registers[register] == 0 else 0
            if self.logging:
                self.log_action(action=f'Setting Z flag based on register [{register}] : value [{self.registers[register]:02X}]')

        if 'N' in flags:
            self.flags['N'] = self.registers[register] >> 7 & 1
            if self.logging:
                self.log_action(action=f'Setting N flag based on register [{register}] : value [{self.registers[register]:>08b}]')

    @time_track
    def set_flags_by_value(self, value=None, flags=[]):
        if value is None or len(flags) == 0:
            return

        if 'Z' in flags:
            self.flags['Z'] = 1 if value == 0 else 0
            if self.logging:
                self.log_action(action=f'Setting Z flag based on value [{value:02X}]')

        if 'N' in flags:
            self.flags['N'] = 1 if value & 0b10000000 > 0 else 0
            if self.logging:
                self.log_action(action=f'Setting N flag based on value [{value:>08b}]')

    @time_track
    def set_flags_manually(self, flags=[], value=None):
        if value is None or value < 0 or value > 1:
            return
        for flag in flags:
            self.flags[flag] = value
            if self.logging:
                self.log_action(action=f'Setting {flag} flag manually to [{value}]')

    @time_track
    def determine_address(self, mode):
        address = 0
        if mode == 'IM':
            address = self.program_counter
            self.program_counter_increment()
            return address
        elif mode == 'ZP':
            address = self.read_memory()
            return address
        elif mode == 'ZP_X':
            address = self.read_memory()
            address += self.registers['X']
            # Zero Page address wraps around if the value exceeds 0xFF
            address = address % 0x100
            self.cycle()
            return address
        elif mode == 'ZP_Y':
            address = self.read_memory()
            address += self.registers['Y']
            # Zero Page address wraps around if the value exceeds 0xFF
            address = address % 0x100
            self.cycle()
            return address
        elif mode == 'ABS':
            address = self.read_memory(bytes=2)
            return address
        elif mode == 'ABS_X':
            address = self.read_memory(bytes=2)
            address += self.registers['X']
            if int(address / 0x100) != int((address - self.registers['X']) / 0x100) or (self.INS[0:3] in CPU6502.OPCODES_WRITE_TO_MEMORY):
                self.cycle()  # Only if PAGE crossed or instruction writes to memory
            return address
        elif mode == 'ABS_Y':
            address = self.read_memory(bytes=2)
            address += self.registers['Y']
            if (int(address / 0x100) != int((address - self.registers['Y']) / 0x100)) or (self.INS[0:3] in CPU6502.OPCODES_WRITE_TO_MEMORY):
                self.cycle()  # Only if PAGE crossed or instruction writes to memory
            return address
        elif mode == 'IND':  # Indirect
            address = self.read_memory(bytes=2)
            return address
        elif mode == 'IND_X':
            address = self.read_memory()
            address += self.registers['X']
            # Zero Page address wraps around if the value exceeds 0xFF
            address = address % 0x100
            self.cycle()
            address = self.read_memory(address=address, increment_pc=False, bytes=2)
            return address
        elif mode == 'IND_Y':
            address = self.read_memory()
            address = self.read_memory(address=address, increment_pc=False, bytes=2)
            address += self.registers['Y']
            if int(address / 0x100) != int((address - self.registers['Y']) / 0x100) or (self.INS[0:3] in CPU6502.OPCODES_WRITE_TO_MEMORY):
                self.cycle()  # Only if PAGE crossed or instruction writes to memory
            return address

        return address

    @time_track
    def get_processor_status(self) -> int:
        order = ['C', 'Z', 'I', 'D', 'B', 'U', 'V', 'N']
        return sum((self.flags[flag] << shift) for shift, flag in enumerate(order))

    @time_track
    def get_processor_status_string(self) -> str:
        order = ['C', 'Z', 'I', 'D', 'B', 'U', 'V', 'N']
        return ''.join(
            flag.upper() if self.flags.get(flag, 1) == 1 else flag.lower()
            for shift, flag in enumerate(reversed(order))
        )

    @time_track
    def set_processor_status(self, flags: int):
        order = ['C', 'Z', 'I', 'D', 'B', 'U', 'V', 'N']
        for shift, flag in enumerate(order):
            flag_value = (flags >> shift) & 0b00000001
            self.set_flags_manually(flags=[flag], value=flag_value)

    def handleBRK(self):
        address = self.memory[0xFFFF] << 8
        address += self.memory[0xFFFE]
        self.program_counter = address

    def handle_single_byte_instruction(self):
        self.cycle()
        # self.readMemory()

    def read_next_instruction(self) -> bool:
        self.OPCODE = self.read_memory()
        self.INS = CPU6502.OPCODES.get(self.OPCODE, None)
        if self.INS:
            self.INS_FAMILY = '_'.join(('INS', self.INS[0:3]))
            self.INS_SET = self.INS.split('_')
            self.ADDRESS_MODE = '_'.join(self.INS_SET[1:])
        return self.INS is not None

    ################################################################
    #
    # BEGIN INSTRUCTION METHODS
    #
    ################################################################

    def INS_ADC(self) -> None:
        orig_A_register_value = self.registers['A']
        address = self.determine_address(mode=self.ADDRESS_MODE)
        value = self.read_memory(address=address, increment_pc=False, bytes=1)
        if self.flags['D'] == 0:
            orig_value = value
            value += self.registers['A'] + self.flags['C']
            self.registers['A'] = value & 0b0000000011111111
            self.set_flags_by_register(register='A', flags=['Z', 'N'])
            carry_flag = 1 if (value & 0b1111111100000000) > 0 else 0
            self.set_flags_manually(flags=['C'], value=carry_flag)
            overflow_flag = 0
            if (orig_A_register_value & 0b10000000) == (orig_value & 0b10000000):
                if ((self.registers['A'] & 0b10000000) != (orig_A_register_value & 0b10000000)) or ((self.registers['A'] & 0b10000000) != (orig_value & 0b10000000)):
                    overflow_flag = 1
            self.set_flags_manually(flags=['V'], value=overflow_flag)
        elif self.flags['D'] == 1:
            c = (self.registers['A'] & 0x0f) + (value & 0x0f) + (self.flags['C'])
            if c > 0x09:
                c = (c - 0x0a) | 0x10
            c += (self.registers['A'] & 0xf0) + (value & 0xf0)
            v = (c >> 1) ^ c
            if (c > 0x99):
                c += 0x60
            self.registers['A'] = c & 0xFF
            self.set_flags_by_register(register='A', flags=['N', 'Z'])
            self.set_flags_manually(flags='C', value=0)
            if c > 0xFF:
                self.set_flags_manually(flags='C', value=1)
            if (((self.registers['A'] ^ value) & 0x80) != 0):
                v = 0
            self.set_flags_manually(flags='V', value=1 if v > 0 else 0)

    def INS_AND(self) -> None:
        address = self.determine_address(mode=self.ADDRESS_MODE)
        value = self.read_memory(address=address, increment_pc=False, bytes=1)
        result = self.registers['A'] & value
        self.registers['A'] = result
        self.set_flags_by_register(register='A', flags=['Z', 'N'])

    def handle_branching_opcodes(self) -> None:
        """
        Covers BCC, BCS, BEQ, BMI, BNE, BPL, BVC, BVS
        """
        offset = self.read_memory()
        flag, test_value = CPU6502.OPCODES_BRANCHING_TABLE[self.INS]
        if self.flags[flag] == test_value:
            if offset > 127:
                offset = (256 - offset) * (-1)
            self.program_counter += offset
            self.cycle()
            if self.logging:
                self.log_action(f'Branch test passed. Jumping to location [{self.program_counter:04X}] offset [{offset}] bytes')
            # Check if page was crossed
            if ((self.program_counter & CPU6502.SIXTEEN_BIT_HIGH_BYTE_MASK) != ((self.program_counter - offset) & CPU6502.SIXTEEN_BIT_HIGH_BYTE_MASK)):
                self.cycle()
        elif self.logging:
            self.log_action('Branch test failed')

    def INS_BCC(self) -> None:
        self.handle_branching_opcodes()

    def INS_BCS(self) -> None:
        self.handle_branching_opcodes()

    def INS_BEQ(self) -> None:
        self.handle_branching_opcodes()

    def INS_BMI(self) -> None:
        self.handle_branching_opcodes()

    def INS_BNE(self) -> None:
        self.handle_branching_opcodes()

    def INS_BPL(self) -> None:
        self.handle_branching_opcodes()

    def INS_BVC(self) -> None:
        self.handle_branching_opcodes()

    def INS_BVS(self) -> None:
        self.handle_branching_opcodes()

    def INS_ASL(self) -> None:
        if self.ADDRESS_MODE == 'ACC':
            value = self.registers['A']
            carry_flag = 1 if (value & 0b10000000) > 0 else 0
            value = value << 1
            value = value & 0b0000000011111110
            self.registers['A'] = value
            self.set_flags_by_register(register='A', flags=['Z', 'N'])
            self.set_flags_manually(flags=['C'], value=carry_flag)
            self.handle_single_byte_instruction()  # 1 byte instruction -- read next byte and ignore
        else:
            address = self.determine_address(mode=self.ADDRESS_MODE)
            value = self.read_memory(address=address, increment_pc=False, bytes=1)
            carry_flag = 1 if (value & 0b10000000) > 0 else 0
            value = value << 1
            value = value & 0b0000000011111110
            self.cycle()  # Extra cycle for modify stage in RMW instruction per note at top.
            self.write_memory(data=value, address=address, bytes=1)
            self.set_flags_by_value(value=value, flags=['Z', 'N'])
            self.set_flags_manually(flags=['C'], value=carry_flag)

    def INS_BIT(self) -> None:
        address = self.determine_address(mode=self.ADDRESS_MODE)
        value = self.read_memory(address=address, increment_pc=False, bytes=1)
        zero_flag = 1 if (self.registers['A'] & value) == 0 else 0
        self.set_flags_manually(flags=['Z'], value=zero_flag)
        self.set_flags_by_value(value=value, flags=['N'])
        overflow_flag = (value & 0b01000000) >> 6
        self.set_flags_manually(flags=['V'], value=overflow_flag)

    def INS_BRK(self) -> None:
        # Reference wiki.nesdev.com/w/index.php/Status_flags
        # Possibly need a readMemory() call here according to http://nesdev.com/the%20%27B%27%20flag%20&%20BRK%20instruction.txt
        self.read_memory()  # BRK is 2 byte instruction - this byte is read and ignored
        # Save program counter to stack
        self.save_pc_at_stack_pointer()
        # Save flags to stack
        value = self.get_processor_status()
        # Manually set bits 4 and 5 to 1
        value = value | 0b00110000
        self.save_byte_at_stack_pointer(data=value)
        # Set B flag
        self.set_flags_manually(['B'], 1)
        # Set interrupt disable flag
        self.set_flags_manually(['I'], 1)
        # Manually change PC to 0xFFFE
        self.handleBRK()

    def INS_CLC(self) -> None:
        self.set_flags_manually(flags=[self.INS[2]], value=0)
        self.handle_single_byte_instruction()

    def INS_CLD(self) -> None:
        self.set_flags_manually(flags=[self.INS[2]], value=0)
        self.handle_single_byte_instruction()

    def INS_CLI(self) -> None:
        self.set_flags_manually(flags=[self.INS[2]], value=0)
        self.handle_single_byte_instruction()

    def INS_CLV(self) -> None:
        self.set_flags_manually(flags=[self.INS[2]], value=0)
        self.handle_single_byte_instruction()

    def handle_comparison_opcodes(self, compare: int, value: int) -> None:
        self.set_flags_manually(['C'], 0)
        self.set_flags_manually(['Z'], 0)
        if compare >= value:
            self.set_flags_manually(['C'], 1)
            # self.setFlagsManually(['Z'], 0)
        if compare == value:
            # self.setFlagsManually(['C'], 0)
            self.set_flags_manually(['Z'], 1)
        # if compare < value:
        result = (compare - value) & CPU6502.EIGHT_BIT_MASK
        self.set_flags_by_value(value=result, flags=['N'])

    def INS_CMP(self) -> None:
        target = 'A' if self.INS[2] not in ['X', 'Y'] else self.INS[2]
        address = self.determine_address(mode=self.ADDRESS_MODE)
        value = self.read_memory(address=address, increment_pc=False, bytes=1)
        compare = self.registers[target]
        self.handle_comparison_opcodes(compare=compare, value=value)

    def INS_CPX(self) -> None:
        target = 'A' if self.INS[2] not in ['X', 'Y'] else self.INS[2]
        address = self.determine_address(mode=self.ADDRESS_MODE)
        value = self.read_memory(address=address, increment_pc=False, bytes=1)
        compare = self.registers[target]
        self.handle_comparison_opcodes(compare=compare, value=value)

    def INS_CPY(self) -> None:
        target = 'A' if self.INS[2] not in ['X', 'Y'] else self.INS[2]
        address = self.determine_address(mode=self.ADDRESS_MODE)
        value = self.read_memory(address=address, increment_pc=False, bytes=1)
        compare = self.registers[target]
        self.handle_comparison_opcodes(compare=compare, value=value)

    def INS_DEC(self) -> None:
        address = self.determine_address(mode=self.ADDRESS_MODE)
        value = self.read_memory(address=address, increment_pc=False, bytes=1)
        value -= 1
        if value < 0:
            value = 0xFF
        self.cycle()  # Is this really necessary? -- apparently, yes
        self.write_memory(data=value, address=address, bytes=1)
        self.set_flags_by_value(value=value, flags=['N', 'Z'])

    def INS_DEX(self) -> None:
        self.handle_single_byte_instruction()
        value = self.registers[self.INS[2]]
        value -= 1
        if value < 0:
            value = 0xFF
        self.registers[self.INS[2]] = value
        self.set_flags_by_register(register=self.INS[2], flags=['N', 'Z'])

    def INS_DEY(self) -> None:
        self.handle_single_byte_instruction()
        value = self.registers[self.INS[2]]
        value -= 1
        if value < 0:
            value = 0xFF
        self.registers[self.INS[2]] = value
        self.set_flags_by_register(register=self.INS[2], flags=['N', 'Z'])

    def INS_EOR(self) -> None:
        address = self.determine_address(mode=self.ADDRESS_MODE)
        value = self.read_memory(address=address, increment_pc=False, bytes=1)
        result = self.registers['A'] ^ value
        self.registers['A'] = result
        self.set_flags_by_register(register='A', flags=['Z', 'N'])

    def INS_INC(self) -> None:
        address = self.determine_address(mode=self.ADDRESS_MODE)
        value = self.read_memory(address=address, increment_pc=False, bytes=1)
        value += 1
        value = value % 0x100
        self.cycle()  # Is this really necessary? -- apparently, yes
        self.write_memory(data=value, address=address, bytes=1)
        self.set_flags_by_value(value=value, flags=['N', 'Z'])

    def INS_INX(self) -> None:
        value = self.registers[self.INS[2]]
        value += 1
        value = value % 0x100
        self.cycle()  # Is this really necessary?
        self.registers[self.INS[2]] = value
        self.set_flags_by_register(register=self.INS[2], flags=['N', 'Z'])

    def INS_INY(self) -> None:
        value = self.registers[self.INS[2]]
        value += 1
        value = value % 0x100
        self.cycle()  # Is this really necessary?
        self.registers[self.INS[2]] = value
        self.set_flags_by_register(register=self.INS[2], flags=['N', 'Z'])

    def INS_JMP(self) -> None:
        address = self.determine_address(mode=self.ADDRESS_MODE)
        if self.ADDRESS_MODE == 'IND':
            address = self.read_memory(address=address, increment_pc=False, bytes=2)

        self.program_counter = address
        if self.logging:
            self.log_action(f'Jumping to location [{self.program_counter:04X}]')

    def INS_JSR(self) -> None:
        address = self.determine_address(mode=self.ADDRESS_MODE)
        self.save_pc_at_stack_pointer()
        self.program_counter = address
        if self.logging:
            self.log_action(f'Jumping to location [{self.program_counter:04X}]')
        self.cycle()

    def INS_LDA(self) -> None:
        register = self.INS_SET[0][2]
        address = self.determine_address(mode=self.ADDRESS_MODE)
        data = self.read_memory(address=address, increment_pc=False)
        self.registers[register] = data
        self.set_flags_by_register(register=register, flags=['Z', 'N'])

    def INS_LDX(self) -> None:
        register = self.INS_SET[0][2]
        address = self.determine_address(mode=self.ADDRESS_MODE)
        data = self.read_memory(address=address, increment_pc=False)
        self.registers[register] = data
        self.set_flags_by_register(register=register, flags=['Z', 'N'])

    def INS_LDY(self) -> None:
        register = self.INS_SET[0][2]
        address = self.determine_address(mode=self.ADDRESS_MODE)
        data = self.read_memory(address=address, increment_pc=False)
        self.registers[register] = data
        self.set_flags_by_register(register=register, flags=['Z', 'N'])

    def INS_LSR(self) -> None:
        """
        May need to move self.handleSingleByteInstruction() to beginning
        IF THE BIG TEST BREAKS, THIS IS WHY!!!
        """
        if self.ADDRESS_MODE == 'ACC':
            value = self.registers['A']
        else:
            address = self.determine_address(mode=self.ADDRESS_MODE)
            value = self.read_memory(address=address, increment_pc=False, bytes=1)

        carry_flag = 1 if (value & 0b00000001) > 0 else 0
        value = value >> 1
        value = value & 0b0000000001111111

        if self.ADDRESS_MODE == 'ACC':
            self.registers['A'] = value
            self.set_flags_by_register(register='A', flags=['Z', 'N'])
            self.set_flags_manually(flags=['C'], value=carry_flag)
            self.handle_single_byte_instruction()  # 1 byte instruction -- read next byte and ignore
        else:
            self.cycle()  # Extra cycle for modify stage in RMW instruction per note at top.
            self.write_memory(data=value, address=address, bytes=1)
            self.set_flags_by_value(value=value, flags=['Z', 'N'])
            self.set_flags_manually(flags=['C'], value=carry_flag)

    def INS_NOP(self) -> None:
        self.handle_single_byte_instruction()

    def INS_PHA(self) -> None:
        """
        May need to move self.handleSingleByteInstruction() to beginning
        IF THE BIG TEST BREAKS, THIS IS WHY!!!
        """
        value = self.registers['A']
        self.save_byte_at_stack_pointer(data=value)
        self.handle_single_byte_instruction()

    def INS_PHP(self) -> None:
        """
        May need to move self.handleSingleByteInstruction() to beginning
        IF THE BIG TEST BREAKS, THIS IS WHY!!!
        """
        value = self.get_processor_status()
        # Manually set bits 4 and 5 to 1
        value = value | 0b00110000
        self.save_byte_at_stack_pointer(data=value)
        self.handle_single_byte_instruction()

    def INS_PLA(self) -> None:
        """
        May need to move self.handleSingleByteInstruction() to beginning
        IF THE BIG TEST BREAKS, THIS IS WHY!!!
        """
        value = self.load_byte_from_stack_pointer()
        self.registers['A'] = value
        self.set_flags_by_register(register='A', flags=['N', 'Z'])
        self.handle_single_byte_instruction()

    def INS_PLP(self) -> None:
        # Pull
        # PLP and BRK should ignore bits 4 & 5
        flags = self.load_byte_from_stack_pointer()
        self.set_processor_status(flags=flags)
        self.handle_single_byte_instruction()

    def INS_ROL(self) -> None:
        """
        May need to move self.handleSingleByteInstruction() to beginning
        IF THE BIG TEST BREAKS, THIS IS WHY!!!
        """
        if self.ADDRESS_MODE == 'ACC':
            value = self.registers['A']
            self.handle_single_byte_instruction()
        else:
            address = self.determine_address(mode=self.ADDRESS_MODE)
            value = self.read_memory(address=address, increment_pc=False, bytes=1)

        # Carry flag
        determine_carry_flag = (value & 0b10000000) >> 7
        current_carry_flag = self.flags['C']
        value = value << 1
        value = value & CPU6502.EIGHT_BIT_MASK  # 8 bit mask
        value = value | 0b00000001 if current_carry_flag == 1 else value & 0b11111110
        if self.ADDRESS_MODE != 'ACC':
            self.cycle()  # Necessary according to notes above

        self.set_flags_manually(value=determine_carry_flag, flags=['C'])

        # Negative flag and Zero flag
        self.set_flags_by_value(value=value, flags=['N', 'Z'])

        if self.ADDRESS_MODE == 'ACC':
            self.registers['A'] = value
        else:
            self.write_memory(data=value, address=address, bytes=1)

    def INS_ROR(self) -> None:
        """
        May need to move self.handleSingleByteInstruction() to beginning
        IF THE BIG TEST BREAKS, THIS IS WHY!!!
        """
        if self.ADDRESS_MODE == 'ACC':
            value = self.registers['A']
            self.handle_single_byte_instruction()
        else:
            address = self.determine_address(mode=self.ADDRESS_MODE)
            value = self.read_memory(address=address, increment_pc=False, bytes=1)

        # Carry flag
        determine_carry_flag = value & 0b00000001
        current_carry_flag = self.flags['C']
        value = value >> 1
        value = value & CPU6502.EIGHT_BIT_MASK  # 8 bit mask
        value = value | 0b10000000 if current_carry_flag == 1 else value & 0b01111111
        if self.ADDRESS_MODE != 'ACC':
            self.cycle()  # Necessary according to notes above
        self.set_flags_manually(value=determine_carry_flag, flags=['C'])

        # Negative flag and Zero flag
        self.set_flags_by_value(value=value, flags=['N', 'Z'])

        if self.ADDRESS_MODE == 'ACC':
            self.registers['A'] = value
        else:
            self.write_memory(data=value, address=address, bytes=1)

    def INS_RTI(self) -> None:
        # Set flags from stack
        flags = self.load_byte_from_stack_pointer()
        # PLP and BRK should ignore bits 4 & 5
        self.set_processor_status(flags=flags)
        # Get PC from stack
        self.load_pc_from_stack_pointer()

    def INS_RTS(self) -> None:
        """
        May need to move self.handleSingleByteInstruction() to beginning
        IF THE BIG TEST BREAKS, THIS IS WHY!!!
        """
        self.handle_single_byte_instruction()
        self.load_pc_from_stack_pointer()
        self.program_counter_increment()

    def INS_SBC(self) -> None:
        orig_A_register_value = self.registers['A']
        address = self.determine_address(mode=self.ADDRESS_MODE)
        value = self.read_memory(address=address, increment_pc=False, bytes=1)

        if self.flags['D'] == 0:
            value = 0b11111111 - value
            orig_value = value
            value += self.registers['A'] + self.flags['C']
            self.registers['A'] = value & 0b0000000011111111
            self.set_flags_by_register(register='A', flags=['Z', 'N'])
            carry_flag = 1 if (value & 0b1111111100000000) > 0 else 0
            self.set_flags_manually(flags=['C'], value=carry_flag)
            overflow_flag = 0
            if (orig_A_register_value & 0b10000000) == (orig_value & 0b10000000):
                if ((self.registers['A'] & 0b10000000) != (orig_A_register_value & 0b10000000)) or ((self.registers['A'] & 0b10000000) != (orig_value & 0b10000000)):
                    overflow_flag = 1
            self.set_flags_manually(flags=['V'], value=overflow_flag)
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
            self.set_flags_by_register(register='A', flags=['N', 'Z'])
            self.set_flags_manually(flags='C', value=0)
            if c > 0xFF:
                self.set_flags_manually(flags='C', value=1)
            if (((self.registers['A'] ^ value) & 0x80) != 0):
                v = 0
            self.set_flags_manually(flags='V', value=1 if v > 0 else 0)

    def INS_SEC(self) -> None:
        """
        May need to move self.handleSingleByteInstruction() to beginning
        IF THE BIG TEST BREAKS, THIS IS WHY!!!
        """
        self.set_flags_manually(flags=[self.INS[2]], value=1)
        self.handle_single_byte_instruction()

    def INS_SED(self) -> None:
        """
        May need to move self.handleSingleByteInstruction() to beginning
        IF THE BIG TEST BREAKS, THIS IS WHY!!!
        """
        self.set_flags_manually(flags=[self.INS[2]], value=1)
        self.handle_single_byte_instruction()

    def INS_SEI(self) -> None:
        """
        May need to move self.handleSingleByteInstruction() to beginning
        IF THE BIG TEST BREAKS, THIS IS WHY!!!
        """
        self.set_flags_manually(flags=[self.INS[2]], value=1)
        self.handle_single_byte_instruction()

    def INS_STA(self) -> None:
        target = self.INS_SET[0][2]
        address = self.determine_address(mode=self.ADDRESS_MODE)
        self.write_memory(data=self.registers[target], address=address, bytes=1)

    def INS_STX(self) -> None:
        target = self.INS_SET[0][2]
        address = self.determine_address(mode=self.ADDRESS_MODE)
        self.write_memory(data=self.registers[target], address=address, bytes=1)

    def INS_STY(self) -> None:
        target = self.INS_SET[0][2]
        address = self.determine_address(mode=self.ADDRESS_MODE)
        self.write_memory(data=self.registers[target], address=address, bytes=1)

    def INS_TAX(self) -> None:
        """
        May need to move self.handleSingleByteInstruction() to beginning
        IF THE BIG TEST BREAKS, THIS IS WHY!!!
        """
        source = self.INS[1]
        dest = self.INS[2]
        self.registers[dest] = self.registers[source]
        self.set_flags_by_register(register=dest, flags=['N', 'Z'])
        self.handle_single_byte_instruction()  # 1 byte instruction -- read next byte and ignore

    def INS_TAY(self) -> None:
        """
        May need to move self.handleSingleByteInstruction() to beginning
        IF THE BIG TEST BREAKS, THIS IS WHY!!!
        """
        source = self.INS[1]
        dest = self.INS[2]
        self.registers[dest] = self.registers[source]
        self.set_flags_by_register(register=dest, flags=['N', 'Z'])
        self.handle_single_byte_instruction()  # 1 byte instruction -- read next byte and ignore

    def INS_TXA(self) -> None:
        """
        May need to move self.handleSingleByteInstruction() to beginning
        IF THE BIG TEST BREAKS, THIS IS WHY!!!
        """
        source = self.INS[1]
        dest = self.INS[2]
        self.registers[dest] = self.registers[source]
        self.set_flags_by_register(register=dest, flags=['N', 'Z'])
        self.handle_single_byte_instruction()  # 1 byte instruction -- read next byte and ignore

    def INS_TXS(self) -> None:
        """
        May need to move self.handleSingleByteInstruction() to beginning
        IF THE BIG TEST BREAKS, THIS IS WHY!!!
        """
        self.stack_pointer = self.registers['X']
        self.handle_single_byte_instruction()  # 1 byte instruction -- read next byte and ignore

    def INS_TSX(self) -> None:
        """
        May need to move self.handleSingleByteInstruction() to beginning
        IF THE BIG TEST BREAKS, THIS IS WHY!!!
        """
        self.registers['X'] = self.stack_pointer
        self.set_flags_by_register(register='X', flags=['N', 'Z'])
        self.handle_single_byte_instruction()  # 1 byte instruction -- read next byte and ignore

    def INS_TYA(self) -> None:
        """
        May need to move self.handleSingleByteInstruction() to beginning
        IF THE BIG TEST BREAKS, THIS IS WHY!!!
        """
        source = self.INS[1]
        dest = self.INS[2]
        self.registers[dest] = self.registers[source]
        self.set_flags_by_register(register=dest, flags=['N', 'Z'])
        self.handle_single_byte_instruction()  # 1 byte instruction -- read next byte and ignore

    def INS_ORA(self) -> None:
        address = self.determine_address(mode=self.ADDRESS_MODE)
        value = self.read_memory(address=address, increment_pc=False, bytes=1)
        result = self.registers['A'] | value
        self.registers['A'] = result
        self.set_flags_by_register(register='A', flags=['Z', 'N'])

    ################################################################
    #
    # END INSTRUCTION METHODS
    #
    ################################################################

    @time_track
    def execute(self):
        try:
            if not self.start_time:
                self.start_time = datetime.datetime.now()
            # Set starting position based on 0xFFFE/F
            # self.handleBRK()

            while self.read_next_instruction() and self.cycles <= self.cycle_limit:

                self.__getattribute__(self.INS_FAMILY)()

                if not self.continuous:
                    break

        except Exception as e:
            self.exception_message = str(e)
            print(traceback.print_exc())

        finally:
            self.execution_time = datetime.datetime.now() - self.start_time

    @time_track
    def get_log_string(self):
        return {
            **{
                '%-10s' % 'Cycle': '%-10s' % str(self.cycles),
                '%-10s' % 'INS': '%-10s' % self.INS,
            },
            **self.registers,
            **self.flags,
            **{
                'SP': '0x{0:0{1}X}'.format(self.get_stack_pointer_address(), 4),
                'PC': '0x{0:0{1}X}'.format(self.program_counter, 4),
                'MEM': '0x{0:0{1}X}'.format(self.memory[self.program_counter], 2),
                '%-10s' % 'FLAGS': '%-10s' % self.get_processor_status_string(),
            },
            '%-20s' % 'ACTION': '%-20s' % ' -> '.join(self.action),
        }

    @time_track
    def get_log_header_string(self):
        combined = self.get_log_string()
        return '\t'.join(combined.keys())

    @time_track
    def print_state(self):
        combined = self.get_log_string()
        headerString = self.get_log_header_string()
        valueString = '\t'.join(str(v) for v in combined.values())
        if self.cycles == 0:
            print(headerString)
        print(valueString)

    @time_track
    def initialize_log(self):
        self.log = []
        headerString = self.get_log_header_string()
        self.log.append(headerString)
        if self.log_file:
            self.log_file.write(headerString)

    @time_track
    def log_state(self):
        if self.logging:
            combined = self.get_log_string()
            # valueString = bcolors.ENDC + '\t'.join(str(v) for v in combined.values()) + bcolors.ENDC
            valueString = '\t'.join(str(v) for v in combined.values())
            self.log.append(valueString)
            if self.log_file:
                if self.cycles % 250000 == 0:
                    self.log_file.close()
                    self.log_file = open(self.log_file.name, 'w')
                    self.log = []
                self.log_file.write(valueString + '\n')

    def print_log(self):
        for line in self.log:
            print(line)

    def benchmark_info(self) -> str:
        return f'\nCycles: {self.cycles - 1:,} :: Elapsed time: {self.execution_time} :: Cycles/sec: {(self.cycles - 1) / (.0001 + self.execution_time.total_seconds()):0,.2f}'

    def print_benchmark_info(self):
        print(self.benchmark_info())

    @time_track
    def load_program(self, instructions=[], memoryAddress=0x0000, mainProgram=True):
        if mainProgram:
            # self.memory[0xFFFE] = memoryAddress & 0b0000000011111111
            # self.memory[0xFFFF] = (memoryAddress >> 8) & 0b0000000011111111
            self.memory[0xFFFE] = memoryAddress & CPU6502.EIGHT_BIT_MASK
            self.memory[0xFFFF] = (memoryAddress >> 8) & CPU6502.EIGHT_BIT_MASK
        for ins in instructions:
            self.memory[memoryAddress] = ins
            memoryAddress += 1
            if memoryAddress > CPU6502.MAX_MEMORY_SIZE:
                print(memoryAddress, ins)
                memoryAddress = 0
                raise('Memory size limit exceeded!')
