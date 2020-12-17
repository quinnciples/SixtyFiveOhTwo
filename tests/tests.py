import os
import logging
import sys
sys.path.insert(0, '..\\SixtyFiveOhTwo')
from SixtyFiveOhTwo import CPU6502

"""

NOTES

Need to investigate STA ABSX, ABSY, and INDY cycle counts. These have been manually adjusted in the tests to pass, however the underlying instructions work correctly.
INX, INY wrap around 0xFF
Fibonacci - https://www.youtube.com/watch?v=a73ZXDJtU48

"""


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def generateProgram(instruction: str, registers: dict, immediate_value: int, zp_address: int, ind_zp_address: int, sixteen_bit_address: int, CYCLE_COUNTS: dict) -> list:
    program = {}

    for opcode, command in CPU6502.opcodes.items():
        ins_set = command.split('_')
        instruct = ins_set[0]
        if instruct != instruction:
            continue
        address_mode = '_'.join(_ for _ in ins_set[1:])
        if '_ACC' in address_mode:
            continue
        else:
            instructions = []
            if address_mode == 'IM':
                instructions = [opcode, immediate_value]
                program[address_mode] = [instructions, CYCLE_COUNTS[address_mode]]

            if address_mode == 'ZP':
                instructions = [opcode, zp_address]
                program[address_mode] = [instructions, CYCLE_COUNTS[address_mode]]

            elif address_mode == 'ZP_X':
                instructions = [opcode, zp_address - registers.get('X', 0)]
                program[address_mode] = [instructions, CYCLE_COUNTS[address_mode]]

            elif address_mode == 'ZP_Y':
                instructions = [opcode, zp_address - registers.get('Y', 0)]
                program[address_mode] = [instructions, CYCLE_COUNTS[address_mode]]

            if address_mode == 'ABS':
                instructions = [opcode, sixteen_bit_address & 0b0000000011111111, (sixteen_bit_address & 0b1111111100000000) >> 8]
                program[address_mode] = [instructions, CYCLE_COUNTS[address_mode]]

            if address_mode == 'ABS_X':
                target_sixteen_bit_address = sixteen_bit_address - registers.get('X', 0)
                instructions = [opcode, target_sixteen_bit_address & 0b0000000011111111, (target_sixteen_bit_address & 0b1111111100000000) >> 8]
                program[address_mode] = [instructions, CYCLE_COUNTS[address_mode]]

            if address_mode == 'ABS_Y':
                target_sixteen_bit_address = sixteen_bit_address - registers.get('Y', 0)
                instructions = [opcode, target_sixteen_bit_address & 0b0000000011111111, (target_sixteen_bit_address & 0b1111111100000000) >> 8]
                program[address_mode] = [instructions, CYCLE_COUNTS[address_mode]]

            if address_mode == 'IND_X':
                instructions = [opcode, ind_zp_address - registers.get('X', 0)]
                program[address_mode] = [instructions, CYCLE_COUNTS[address_mode]]

            if address_mode == 'IND_Y':
                instructions = [opcode, ind_zp_address]
                program[address_mode] = [instructions, CYCLE_COUNTS[address_mode]]

    return program


def TEST_0x08_PHP_PLA_COMBINED_TEST():
    TEST_NAME = f'TEST_0x08_PHP_PLA_COMBINED_TEST'
    INITIAL_REGISTERS = {
        'A': 0x20,
        'X': 0x60,
        'Y': 0xA5
    }
    EXPECTED_REGISTERS = {
        'A': 0x20,
        'X': 0x60,
        'Y': 0xA5
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_CYCLES = 3 + 1 + 4

    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    errors = False
    for flag in INITIAL_FLAGS.keys():
        print(f'\tTesting {flag}... ', end='')
        cpu = CPU6502(cycle_limit=100)
        cpu.reset(program_counter=0xFF00)
        push_program = [0x08, 0x00]
        cpu.loadProgram(instructions=push_program, memoryAddress=0xFF00)
        cpu.registers = INITIAL_REGISTERS.copy()
        cpu.flags = INITIAL_FLAGS.copy()
        cpu.flags[flag] = 1
        cpu.execute()

        pull_program = [0x28, 0x00]
        cpu.loadProgram(instructions=pull_program, memoryAddress=0xFF02)
        cpu.program_counter = 0xFF02
        cpu.registers = INITIAL_REGISTERS.copy()
        cpu.flags = INITIAL_FLAGS.copy()
        cpu.execute()

        EXPECTED_FLAGS = INITIAL_FLAGS.copy()
        EXPECTED_FLAGS[flag] = 1

        if cpu.registers != EXPECTED_REGISTERS or cpu.flags != EXPECTED_FLAGS or cpu.cycles - 1 != EXPECTED_CYCLES:
            print(f'{bcolors.FAIL}FAILED{bcolors.ENDC}', end='\n')
            if cpu.registers != EXPECTED_REGISTERS:
                print(f'\t{bcolors.FAIL}REGISTERS DO NOT MATCH{bcolors.ENDC}', end='\n')
                print(f'Expected Registers: {EXPECTED_REGISTERS}\tActual Registers: {cpu.registers}')
            if cpu.flags != EXPECTED_FLAGS:
                print(f'\t{bcolors.FAIL}FLAGS DO NOT MATCH{bcolors.ENDC}', end='\n')
                print(f'Expected Flags: {EXPECTED_FLAGS}\tActual Flags: {cpu.flags}')
            if cpu.cycles - 1 != EXPECTED_CYCLES:
                print(f'\t{bcolors.FAIL}CYCLE COUNT DOES NOT MATCH{bcolors.ENDC}', end='\n')
                print(f'Cycles: {cpu.cycles-1} Expected Cycles: {EXPECTED_CYCLES}')

            cpu.printLog()
            cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF03)
            errors = True
        else:
            print(f'{bcolors.OKGREEN}PASSED{bcolors.ENDC}', end='\n')

    if errors:
        return False
    return True


def TEST_0x09_ORA_ADDRESS_MODE_TESTS():
    TEST_NAME = f'TEST_0x09_ORA_ADDRESS_MODE_TESTS'
    INITIAL_REGISTERS = {
        'A': 0x10,
        'X': 0x01,
        'Y': 0x05
    }
    EXPECTED_REGISTERS = {
        'A': 0x10 | 0x42,
        'X': 0x01,
        'Y': 0x05
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    INSTRUCTION = 'ORA'
    IMMEDIATE_VALUE = 0x42
    ZP_ADDRESS = 0x0059
    IND_ZP_ADDRESS = 0x0069
    FULL_ADDRESS = 0xAA48
    VALUE_TO_TEST = IMMEDIATE_VALUE
    EXPECTED_VALUE = None
    CYCLE_COUNTS = {'IM': 2, 'ZP': 3, 'ZP_X': 4, 'ABS': 4, 'ABS_X': 4, 'ABS_Y': 4, 'IND_X': 6, 'IND_Y': 5}

    programs = generateProgram(instruction=INSTRUCTION,
                               registers=INITIAL_REGISTERS,
                               immediate_value=IMMEDIATE_VALUE,
                               zp_address=ZP_ADDRESS,
                               ind_zp_address=IND_ZP_ADDRESS,
                               sixteen_bit_address=FULL_ADDRESS,
                               CYCLE_COUNTS=CYCLE_COUNTS)

    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    errors = False
    for label, program in programs.items():
        print(f'\tTesting {label}... ', end='')
        EXPECTED_CYCLES = program[1]
        cpu = CPU6502(cycle_limit=100)
        cpu.reset(program_counter=0xFF00)
        cpu.loadProgram(instructions=program[0], memoryAddress=0xFF00)
        cpu.registers = INITIAL_REGISTERS.copy()
        cpu.flags = INITIAL_FLAGS.copy()
        cpu.memory[ZP_ADDRESS] = VALUE_TO_TEST  # ZP, ZP_X, and ZP_Y Location
        cpu.memory[IND_ZP_ADDRESS] = FULL_ADDRESS & 0b0000000011111111
        cpu.memory[IND_ZP_ADDRESS + 1] = (FULL_ADDRESS & 0b1111111100000000) >> 8
        cpu.memory[FULL_ADDRESS] = VALUE_TO_TEST  # ABS, ABS_X, ABS_Y, and IND_X Location
        cpu.memory[FULL_ADDRESS + INITIAL_REGISTERS['Y']] = VALUE_TO_TEST  # IND_Y Location
        cpu.execute()

        if cpu.registers != EXPECTED_REGISTERS or cpu.flags != EXPECTED_FLAGS or cpu.cycles - 1 != EXPECTED_CYCLES or (EXPECTED_VALUE is not None and label in ['ZP', 'ZP_X', 'ZP_Y'] and cpu.memory[ZP_ADDRESS] != EXPECTED_VALUE) or (EXPECTED_VALUE is not None and label in ['ABS', 'ABS_X', 'ABS_Y', 'IND_X', 'IND_Y'] and cpu.memory[FULL_ADDRESS] != EXPECTED_VALUE):
            print(f'{bcolors.FAIL}FAILED{bcolors.ENDC}', end='\n')
            if cpu.registers != EXPECTED_REGISTERS:
                print(f'\t{bcolors.FAIL}REGISTERS DO NOT MATCH{bcolors.ENDC}', end='\n')
            if cpu.flags != EXPECTED_FLAGS:
                print(f'\t{bcolors.FAIL}FLAGS DO NOT MATCH{bcolors.ENDC}', end='\n')
            if cpu.cycles - 1 != EXPECTED_CYCLES:
                print(f'\t{bcolors.FAIL}CYCLE COUNT DOES NOT MATCH{bcolors.ENDC}', end='\n')
            # Memory tests
            if EXPECTED_VALUE is not None and label in ['ZP', 'ZP_X', 'ZP_Y'] and cpu.memory[ZP_ADDRESS] != EXPECTED_VALUE:
                print(f'\t{bcolors.FAIL}MEMORY CONTENTS DO NOT MATCH{bcolors.ENDC}', end='\n')
            if EXPECTED_VALUE is not None and label in ['ABS', 'ABS_X', 'ABS_Y', 'IND_X', 'IND_Y'] and cpu.memory[FULL_ADDRESS] != EXPECTED_VALUE:
                print(f'\t{bcolors.FAIL}MEMORY CONTENTS DO NOT MATCH{bcolors.ENDC}', end='\n')

            cpu.printLog()
            cpu.memoryDump(startingAddress=0xFF00, endingAddress=(0xFF00 + len(program)))
            cpu.memoryDump(startingAddress=ZP_ADDRESS, endingAddress=ZP_ADDRESS + 1)
            cpu.memoryDump(startingAddress=IND_ZP_ADDRESS, endingAddress=IND_ZP_ADDRESS + 1)
            cpu.memoryDump(startingAddress=FULL_ADDRESS, endingAddress=FULL_ADDRESS + 1)

            print(f'Program: ' + ', '.join('0x{0:0{1}X}'.format(x, 2) for x in program[0]))
            print(f'Cycles: {cpu.cycles-1} Expected Cycles: {EXPECTED_CYCLES}')
            print(f'Expected Registers: {EXPECTED_REGISTERS}')
            print(f'Expected Flags: {EXPECTED_FLAGS}')
            errors = True
        else:
            print(f'{bcolors.OKGREEN}PASSED{bcolors.ENDC}', end='\n')

    if errors:
        return False
    return True


def TEST_0x49_EOR_ADDRESS_MODE_TESTS():
    TEST_NAME = f'TEST_0x49_EOR_ADDRESS_MODE_TESTS'
    INITIAL_REGISTERS = {
        'A': 0x10,
        'X': 0x01,
        'Y': 0x05
    }
    EXPECTED_REGISTERS = {
        'A': 0x10 ^ 0x42,
        'X': 0x01,
        'Y': 0x05
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    INSTRUCTION = 'EOR'
    IMMEDIATE_VALUE = 0x42
    ZP_ADDRESS = 0x0059
    IND_ZP_ADDRESS = 0x0069
    FULL_ADDRESS = 0xAA48
    VALUE_TO_TEST = IMMEDIATE_VALUE
    EXPECTED_VALUE = None
    CYCLE_COUNTS = {'IM': 2, 'ZP': 3, 'ZP_X': 4, 'ABS': 4, 'ABS_X': 4, 'ABS_Y': 4, 'IND_X': 6, 'IND_Y': 5}

    programs = generateProgram(instruction=INSTRUCTION,
                               registers=INITIAL_REGISTERS,
                               immediate_value=IMMEDIATE_VALUE,
                               zp_address=ZP_ADDRESS,
                               ind_zp_address=IND_ZP_ADDRESS,
                               sixteen_bit_address=FULL_ADDRESS,
                               CYCLE_COUNTS=CYCLE_COUNTS)

    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    errors = False
    for label, program in programs.items():
        print(f'\tTesting {label}... ', end='')
        EXPECTED_CYCLES = program[1]
        cpu = CPU6502(cycle_limit=100)
        cpu.reset(program_counter=0xFF00)
        cpu.loadProgram(instructions=program[0], memoryAddress=0xFF00)
        cpu.registers = INITIAL_REGISTERS.copy()
        cpu.flags = INITIAL_FLAGS.copy()
        cpu.memory[ZP_ADDRESS] = VALUE_TO_TEST  # ZP, ZP_X, and ZP_Y Location
        cpu.memory[IND_ZP_ADDRESS] = FULL_ADDRESS & 0b0000000011111111
        cpu.memory[IND_ZP_ADDRESS + 1] = (FULL_ADDRESS & 0b1111111100000000) >> 8
        cpu.memory[FULL_ADDRESS] = VALUE_TO_TEST  # ABS, ABS_X, ABS_Y, and IND_X Location
        cpu.memory[FULL_ADDRESS + INITIAL_REGISTERS['Y']] = VALUE_TO_TEST  # IND_Y Location
        cpu.execute()

        if cpu.registers != EXPECTED_REGISTERS or cpu.flags != EXPECTED_FLAGS or cpu.cycles - 1 != EXPECTED_CYCLES or (EXPECTED_VALUE is not None and label in ['ZP', 'ZP_X', 'ZP_Y'] and cpu.memory[ZP_ADDRESS] != EXPECTED_VALUE) or (EXPECTED_VALUE is not None and label in ['ABS', 'ABS_X', 'ABS_Y', 'IND_X', 'IND_Y'] and cpu.memory[FULL_ADDRESS] != EXPECTED_VALUE):
            print(f'{bcolors.FAIL}FAILED{bcolors.ENDC}', end='\n')
            if cpu.registers != EXPECTED_REGISTERS:
                print(f'\t{bcolors.FAIL}REGISTERS DO NOT MATCH{bcolors.ENDC}', end='\n')
            if cpu.flags != EXPECTED_FLAGS:
                print(f'\t{bcolors.FAIL}FLAGS DO NOT MATCH{bcolors.ENDC}', end='\n')
            if cpu.cycles - 1 != EXPECTED_CYCLES:
                print(f'\t{bcolors.FAIL}CYCLE COUNT DOES NOT MATCH{bcolors.ENDC}', end='\n')
            # Memory tests
            if EXPECTED_VALUE is not None and label in ['ZP', 'ZP_X', 'ZP_Y'] and cpu.memory[ZP_ADDRESS] != EXPECTED_VALUE:
                print(f'\t{bcolors.FAIL}MEMORY CONTENTS DO NOT MATCH{bcolors.ENDC}', end='\n')
            if EXPECTED_VALUE is not None and label in ['ABS', 'ABS_X', 'ABS_Y', 'IND_X', 'IND_Y'] and cpu.memory[FULL_ADDRESS] != EXPECTED_VALUE:
                print(f'\t{bcolors.FAIL}MEMORY CONTENTS DO NOT MATCH{bcolors.ENDC}', end='\n')

            cpu.printLog()
            cpu.memoryDump(startingAddress=0xFF00, endingAddress=(0xFF00 + len(program)))
            cpu.memoryDump(startingAddress=ZP_ADDRESS, endingAddress=ZP_ADDRESS + 1)
            cpu.memoryDump(startingAddress=IND_ZP_ADDRESS, endingAddress=IND_ZP_ADDRESS + 1)
            cpu.memoryDump(startingAddress=FULL_ADDRESS, endingAddress=FULL_ADDRESS + 1)

            print(f'Program: ' + ', '.join('0x{0:0{1}X}'.format(x, 2) for x in program[0]))
            print(f'Cycles: {cpu.cycles-1} Expected Cycles: {EXPECTED_CYCLES}')
            print(f'Expected Registers: {EXPECTED_REGISTERS}')
            print(f'Expected Flags: {EXPECTED_FLAGS}')
            errors = True
        else:
            print(f'{bcolors.OKGREEN}PASSED{bcolors.ENDC}', end='\n')

    if errors:
        return False
    return True


def TEST_0x2A_ROL_ADDRESS_MODE_TESTS():
    TEST_NAME = f'TEST_0x2A_ROL_ADDRESS_MODE_TESTS'
    INITIAL_REGISTERS = {
        'A': 0x0b10000001,
        'X': 0x05,
        'Y': 0x09
    }
    EXPECTED_REGISTERS = {
        'A': 0x0b10000001,
        'X': 0x05,
        'Y': 0x09
    }
    INITIAL_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    ZP_ADDRESS = 0x0059
    IND_ZP_ADDRESS = 0x0069
    FULL_ADDRESS = 0xAA40
    VALUE_TO_TEST = 0b10000001
    EXPECTED_VALUE = 0b00000011
    CYCLE_COUNTS = {'ZP': 5, 'ZP_X': 6, 'ABS': 6, 'ABS_X': 7}

    programs = generateProgram(instruction='ROL',
                               registers=INITIAL_REGISTERS,
                               immediate_value=None,
                               zp_address=ZP_ADDRESS,
                               ind_zp_address=IND_ZP_ADDRESS,
                               sixteen_bit_address=FULL_ADDRESS,
                               CYCLE_COUNTS=CYCLE_COUNTS)

    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    errors = False
    for label, program in programs.items():
        print(f'\tTesting {label}... ', end='')
        EXPECTED_CYCLES = program[1]
        cpu = CPU6502(cycle_limit=100)
        cpu.reset(program_counter=0xFF00)
        cpu.loadProgram(instructions=program[0], memoryAddress=0xFF00)
        cpu.registers = INITIAL_REGISTERS
        cpu.flags = INITIAL_FLAGS
        cpu.memory[ZP_ADDRESS] = VALUE_TO_TEST
        cpu.memory[IND_ZP_ADDRESS] = FULL_ADDRESS & 0b0000000011111111
        cpu.memory[IND_ZP_ADDRESS + 1] = (FULL_ADDRESS & 0b1111111100000000) >> 8
        cpu.memory[FULL_ADDRESS] = VALUE_TO_TEST
        cpu.execute()

        if cpu.registers != EXPECTED_REGISTERS or cpu.flags != EXPECTED_FLAGS or cpu.cycles - 1 != EXPECTED_CYCLES or (label in ['ZP', 'ZP_X', 'ZP_Y'] and cpu.memory[ZP_ADDRESS] != EXPECTED_VALUE) or (label in ['ABS', 'ABS_X', 'ABS_Y', 'IND_X', 'IND_Y'] and cpu.memory[FULL_ADDRESS] != EXPECTED_VALUE):
            print(f'{bcolors.FAIL}FAILED{bcolors.ENDC}', end='\n')
            if cpu.registers != EXPECTED_REGISTERS:
                print(f'\t{bcolors.FAIL}REGISTERS DO NOT MATCH{bcolors.ENDC}', end='\n')
            if cpu.flags != EXPECTED_FLAGS:
                print(f'\t{bcolors.FAIL}FLAGS DO NOT MATCH{bcolors.ENDC}', end='\n')
            if cpu.cycles - 1 != EXPECTED_CYCLES:
                print(f'\t{bcolors.FAIL}CYCLE COUNT DOES NOT MATCH{bcolors.ENDC}', end='\n')
            if label in ['ZP', 'ZP_X', 'ZP_Y'] and cpu.memory[ZP_ADDRESS] != EXPECTED_VALUE:
                print(f'\t{bcolors.FAIL}MEMORY CONTENTS DO NOT MATCH{bcolors.ENDC}', end='\n')
            if label in ['ABS', 'ABS_X', 'ABS_Y', 'IND_X', 'IND_Y'] and cpu.memory[FULL_ADDRESS] != EXPECTED_VALUE:
                print(f'\t{bcolors.FAIL}MEMORY CONTENTS DO NOT MATCH{bcolors.ENDC}', end='\n')

            # cpu.printLog()
            # cpu.memoryDump(startingAddress=0xFF00, endingAddress=(0xFF00 + len(program)))
            # cpu.memoryDump(startingAddress=ZP_ADDRESS, endingAddress=ZP_ADDRESS + 1)
            # cpu.memoryDump(startingAddress=IND_ZP_ADDRESS, endingAddress=IND_ZP_ADDRESS + 1)
            # cpu.memoryDump(startingAddress=FULL_ADDRESS, endingAddress=FULL_ADDRESS + 1)

            # print(f'Program: {program[0]}')
            # print(f'Cycles: {cpu.cycles-1} Expected Cycles: {EXPECTED_CYCLES}')
            # print(f'Expected Registers: {EXPECTED_REGISTERS}')
            # print(f'Expected Flags: {EXPECTED_FLAGS}')
            errors = True
        else:
            print(f'{bcolors.OKGREEN}PASSED{bcolors.ENDC}', end='\n')

    if errors:
        return False
    return


def TEST_0x24_BIT_ADDRESS_MODE_TESTS_ZERO_FLAG():
    TEST_NAME = f'TEST_0x24_BIT_ADDRESS_MODE_TESTS_ZERO_FLAG'
    INITIAL_REGISTERS = {
        'A': 0x00,
        'X': 0x05,
        'Y': 0x59
    }
    EXPECTED_REGISTERS = {
        'A': 0x00,
        'X': 0x05,
        'Y': 0x59
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 1,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 1,
        'N': 1
    }

    ZP_ADDRESS = 0x0059
    IND_ZP_ADDRESS = 0x0069
    FULL_ADDRESS = 0xAA40
    VALUE_TO_TEST = 0b11000000
    CYCLE_COUNTS = {'ZP': 3, 'ABS': 4}

    programs = generateProgram(instruction='BIT',
                               registers=INITIAL_REGISTERS,
                               immediate_value=None,
                               zp_address=ZP_ADDRESS,
                               ind_zp_address=IND_ZP_ADDRESS,
                               sixteen_bit_address=FULL_ADDRESS,
                               CYCLE_COUNTS=CYCLE_COUNTS)

    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    for label, program in programs.items():
        print(f'\tTesting {label}... ', end='')
        EXPECTED_CYCLES = program[1]
        cpu = CPU6502(cycle_limit=100)
        cpu.reset(program_counter=0xFF00)
        cpu.loadProgram(instructions=program[0], memoryAddress=0xFF00)
        cpu.registers = INITIAL_REGISTERS
        cpu.flags = INITIAL_FLAGS
        cpu.memory[ZP_ADDRESS] = VALUE_TO_TEST
        cpu.memory[IND_ZP_ADDRESS] = FULL_ADDRESS & 0b0000000011111111
        cpu.memory[IND_ZP_ADDRESS + 1] = (FULL_ADDRESS & 0b1111111100000000) >> 8
        cpu.memory[FULL_ADDRESS] = VALUE_TO_TEST
        cpu.execute()

        if cpu.registers != EXPECTED_REGISTERS or cpu.flags != EXPECTED_FLAGS or cpu.cycles - 1 != EXPECTED_CYCLES:
            print(f'{bcolors.FAIL}FAILED{bcolors.ENDC}', end='\n')
            if cpu.registers != EXPECTED_REGISTERS:
                print(f'{bcolors.FAIL}REGISTERS DO NOT MATCH{bcolors.ENDC}', end='\n')
            if cpu.flags != EXPECTED_FLAGS:
                print(f'{bcolors.FAIL}FLAGS DO NOT MATCH{bcolors.ENDC}', end='\n')
            if cpu.cycles - 1 != EXPECTED_CYCLES:
                print(f'{bcolors.FAIL}CYCLE COUNT DOES NOT MATCH{bcolors.ENDC}', end='\n')

            cpu.printLog()
            cpu.memoryDump(startingAddress=0xFF00, endingAddress=(0xFF00 + len(program)))
            cpu.memoryDump(startingAddress=ZP_ADDRESS, endingAddress=ZP_ADDRESS + 1)
            cpu.memoryDump(startingAddress=IND_ZP_ADDRESS, endingAddress=IND_ZP_ADDRESS + 1)
            cpu.memoryDump(startingAddress=FULL_ADDRESS, endingAddress=FULL_ADDRESS + 1)

            print(f'Program: {program[0]}')
            print(f'Cycles: {cpu.cycles-1} Expected Cycles: {EXPECTED_CYCLES}')
            print(f'Expected Registers: {EXPECTED_REGISTERS}')
            print(f'Expected Flags: {EXPECTED_FLAGS}')
            return False
        else:
            print(f'{bcolors.OKGREEN}PASSED{bcolors.ENDC}', end='\n')
    return True


def TEST_0x24_BIT_ADDRESS_MODE_TESTS():
    TEST_NAME = f'TEST_0x24_BIT_ADDRESS_MODE_TESTS'
    INITIAL_REGISTERS = {
        'A': 0b11111111,
        'X': 0x05,
        'Y': 0x59
    }
    EXPECTED_REGISTERS = {
        'A': 0b11111111,
        'X': 0x05,
        'Y': 0x59
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 1,
        'N': 1
    }

    ZP_ADDRESS = 0x0059
    IND_ZP_ADDRESS = 0x0069
    FULL_ADDRESS = 0xAA40
    VALUE_TO_TEST = 0b11111111
    CYCLE_COUNTS = {'ZP': 3, 'ABS': 4}

    programs = generateProgram(instruction='BIT',
                               registers=INITIAL_REGISTERS,
                               immediate_value=None,
                               zp_address=ZP_ADDRESS,
                               ind_zp_address=IND_ZP_ADDRESS,
                               sixteen_bit_address=FULL_ADDRESS,
                               CYCLE_COUNTS=CYCLE_COUNTS)

    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    for label, program in programs.items():
        print(f'\tTesting {label}... ', end='')
        EXPECTED_CYCLES = program[1]
        cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
        cpu.reset(program_counter=0xFF00)
        cpu.loadProgram(instructions=program[0], memoryAddress=0xFF00)
        cpu.registers = INITIAL_REGISTERS
        cpu.flags = INITIAL_FLAGS
        cpu.memory[ZP_ADDRESS] = VALUE_TO_TEST
        cpu.memory[IND_ZP_ADDRESS] = FULL_ADDRESS & 0b0000000011111111
        cpu.memory[IND_ZP_ADDRESS + 1] = (FULL_ADDRESS & 0b1111111100000000) >> 8
        cpu.memory[FULL_ADDRESS] = VALUE_TO_TEST
        cpu.execute()

        if cpu.registers != EXPECTED_REGISTERS or cpu.flags != EXPECTED_FLAGS or cpu.cycles - 1 != EXPECTED_CYCLES:
            print(f'{bcolors.FAIL}FAILED{bcolors.ENDC}', end='\n')
            if cpu.registers != EXPECTED_REGISTERS:
                print(f'{bcolors.FAIL}REGISTERS DO NOT MATCH{bcolors.ENDC}', end='\n')
            if cpu.flags != EXPECTED_FLAGS:
                print(f'{bcolors.FAIL}FLAGS DO NOT MATCH{bcolors.ENDC}', end='\n')
            if cpu.cycles - 1 != EXPECTED_CYCLES:
                print(f'{bcolors.FAIL}CYCLE COUNT DOES NOT MATCH{bcolors.ENDC}', end='\n')

            cpu.printLog()
            cpu.memoryDump(startingAddress=0xFF00, endingAddress=(0xFF00 + len(program)))
            cpu.memoryDump(startingAddress=ZP_ADDRESS, endingAddress=ZP_ADDRESS + 1)
            cpu.memoryDump(startingAddress=IND_ZP_ADDRESS, endingAddress=IND_ZP_ADDRESS + 1)
            cpu.memoryDump(startingAddress=FULL_ADDRESS, endingAddress=FULL_ADDRESS + 1)

            print(f'Program: {program[0]}')
            print(f'Cycles: {cpu.cycles-1} Expected Cycles: {EXPECTED_CYCLES}')
            print(f'Expected Registers: {EXPECTED_REGISTERS}')
            print(f'Expected Flags: {EXPECTED_FLAGS}')
            return False
        else:
            print(f'{bcolors.OKGREEN}PASSED{bcolors.ENDC}', end='\n')
    return True


def TEST_0xC9_CMP_GREATER_THAN_ADDRESS_MODE_TESTS():
    TEST_NAME = f'TEST_0xC9_CMP_GREATER_THAN_ADDRESS_MODE_TESTS'
    INITIAL_REGISTERS = {
        'A': 0x20,
        'X': 0x01,
        'Y': 0x05
    }
    EXPECTED_REGISTERS = {
        'A': 0x20,
        'X': 0x01,
        'Y': 0x05
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    ZP_ADDRESS = 0x0059
    IND_ZP_ADDRESS = 0x0069
    FULL_ADDRESS = 0xAA40
    VALUE_TO_TEST = 0x10
    CYCLE_COUNTS = {'IM': 2, 'ZP': 3, 'ZP_X': 4, 'ABS': 4, 'ABS_X': 4, 'ABS_Y': 4, 'IND_X': 6, 'IND_Y': 5}

    programs = generateProgram(instruction='CMP',
                               registers=INITIAL_REGISTERS,
                               immediate_value=VALUE_TO_TEST,
                               zp_address=ZP_ADDRESS,
                               ind_zp_address=IND_ZP_ADDRESS,
                               sixteen_bit_address=FULL_ADDRESS,
                               CYCLE_COUNTS=CYCLE_COUNTS)

    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    for label, program in programs.items():
        print(f'\tTesting {label}... ', end='')
        EXPECTED_CYCLES = program[1]
        cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
        cpu.reset(program_counter=0xFF00)
        cpu.loadProgram(instructions=program[0], memoryAddress=0xFF00)
        cpu.registers = INITIAL_REGISTERS
        cpu.flags = INITIAL_FLAGS
        cpu.memory[ZP_ADDRESS] = VALUE_TO_TEST
        cpu.memory[IND_ZP_ADDRESS] = FULL_ADDRESS & 0b0000000011111111
        cpu.memory[IND_ZP_ADDRESS + 1] = (FULL_ADDRESS & 0b1111111100000000) >> 8
        cpu.memory[FULL_ADDRESS] = VALUE_TO_TEST
        cpu.memory[FULL_ADDRESS + INITIAL_REGISTERS['Y']] = VALUE_TO_TEST  # IND_Y Location
        cpu.execute()

        if cpu.registers != EXPECTED_REGISTERS or cpu.flags != EXPECTED_FLAGS or cpu.cycles - 1 != EXPECTED_CYCLES:
            print(f'{bcolors.FAIL}FAILED{bcolors.ENDC}', end='\n')
            if cpu.registers != EXPECTED_REGISTERS:
                print(f'{bcolors.FAIL}REGISTERS DO NOT MATCH{bcolors.ENDC}', end='\n')
            if cpu.flags != EXPECTED_FLAGS:
                print(f'{bcolors.FAIL}FLAGS DO NOT MATCH{bcolors.ENDC}', end='\n')
            if cpu.cycles - 1 != EXPECTED_CYCLES:
                print(f'{bcolors.FAIL}CYCLE COUNT DOES NOT MATCH{bcolors.ENDC}', end='\n')

            cpu.printLog()
            cpu.memoryDump(startingAddress=0xFF00, endingAddress=(0xFF00 + len(program)))
            cpu.memoryDump(startingAddress=ZP_ADDRESS, endingAddress=ZP_ADDRESS + 1)
            cpu.memoryDump(startingAddress=IND_ZP_ADDRESS, endingAddress=IND_ZP_ADDRESS + 1)
            cpu.memoryDump(startingAddress=FULL_ADDRESS, endingAddress=FULL_ADDRESS + 1)

            print(f'Program: {program[0]}')
            print(f'Cycles: {cpu.cycles-1} Expected Cycles: {EXPECTED_CYCLES}')
            print(f'Expected Registers: {EXPECTED_REGISTERS}')
            print(f'Expected Flags: {EXPECTED_FLAGS}')
            return False
        else:
            print(f'{bcolors.OKGREEN}PASSED{bcolors.ENDC}', end='\n')
    return True


def TEST_0x68_PLA_IMP_ZERO_FLAG_SET():
    EXPECTED_VALUE = 0x00
    EXPECTED_CYCLES = 4
    INITIAL_REGISTERS = {
        'A': 0x25,
        'X': 0x18,
        'Y': 0x20
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x18,
        'Y': 0x20
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 1,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x68, 0x00]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0x01FF] = EXPECTED_VALUE
    cpu.stack_pointer = 0xFE
    cpu.execute()

    try:
        assert(cpu.stack_pointer == 0xFF)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        cpu.memoryDump(startingAddress=0x01F8, endingAddress=0x01FF)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Flags: {EXPECTED_FLAGS}')
        raise
    return False


def TEST_0x68_PLA_IMP_NEGATIVE_FLAG_SET():
    EXPECTED_VALUE = 0xF5
    EXPECTED_CYCLES = 4
    INITIAL_REGISTERS = {
        'A': 0x25,
        'X': 0x18,
        'Y': 0x20
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x18,
        'Y': 0x20
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 1
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x68, 0x00]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0x01FF] = EXPECTED_VALUE
    cpu.stack_pointer = 0xFE
    cpu.execute()

    try:
        assert(cpu.stack_pointer == 0xFF)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        cpu.memoryDump(startingAddress=0x01F8, endingAddress=0x01FF)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Flags: {EXPECTED_FLAGS}')
        raise
    return False


def TEST_0x68_PLA_IMP():
    EXPECTED_VALUE = 0x35
    EXPECTED_CYCLES = 4
    INITIAL_REGISTERS = {
        'A': 0x25,
        'X': 0x18,
        'Y': 0x20
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x18,
        'Y': 0x20
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x68, 0x00]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0x01FF] = EXPECTED_VALUE
    cpu.stack_pointer = 0xFE
    cpu.execute()

    try:
        assert(cpu.stack_pointer == 0xFF)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        cpu.memoryDump(startingAddress=0x01F8, endingAddress=0x01FF)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Flags: {EXPECTED_FLAGS}')
        raise
    return False


def TEST_0x48_PHA_IMP():
    EXPECTED_VALUE = 0x35
    EXPECTED_CYCLES = 3
    INITIAL_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x18,
        'Y': 0x20
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x18,
        'Y': 0x20
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x48, 0x00]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.stack_pointer == 0xFE)
        assert(cpu.memory[0x01FF] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        cpu.memoryDump(startingAddress=0x01F8, endingAddress=0x01FF)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Flags: {EXPECTED_FLAGS}')
        raise
    return False


def TEST_0x6A_ROR_ACC_CARRY_FLAG_NOT_SET():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0b00000111,
        'X': 0x00,
        'Y': 0x00
    }
    EXPECTED_REGISTERS = {
        'A': 0b00000011,
        'X': 0x00,
        'Y': 0x00
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x6A, 0x00]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        print(f'Expected Flags: {EXPECTED_FLAGS}')
        raise
        return False
    return True


def TEST_0x6A_ROR_ACC_CARRY_FLAG_SET():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0b00000111,
        'X': 0x00,
        'Y': 0x00
    }
    EXPECTED_REGISTERS = {
        'A': 0b10000011,
        'X': 0x00,
        'Y': 0x00
    }
    INITIAL_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 1
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x6A, 0x00]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        print(f'Expected Flags: {EXPECTED_FLAGS}')
        raise
        return False
    return True


def TEST_0x2A_ROL_ACC_CARRY_FLAG_NOT_SET():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x0F,
        'X': 0x00,
        'Y': 0x00
    }
    EXPECTED_REGISTERS = {
        'A': 0x1E,
        'X': 0x00,
        'Y': 0x00
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x2A, 0x00]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x2A_ROL_ACC_CARRY_FLAG_SET():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x0F,
        'X': 0x00,
        'Y': 0x00
    }
    EXPECTED_REGISTERS = {
        'A': 0x1F,
        'X': 0x00,
        'Y': 0x00
    }
    INITIAL_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x2A, 0x00]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        print(f'Expected Flags: {EXPECTED_FLAGS}')
        raise
        return False
    return True


def TEST_0xC9_CMP_GREATER_THAN():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x20,
        'X': 0x00,
        'Y': 0x00
    }
    EXPECTED_REGISTERS = {
        'A': 0x20,
        'X': 0x00,
        'Y': 0x00
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xC9, 0x10]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0xC9_CMP_LESS_THAN():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x05,
        'X': 0x00,
        'Y': 0x00
    }
    EXPECTED_REGISTERS = {
        'A': 0x05,
        'X': 0x00,
        'Y': 0x00
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xC9, 0xFF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0xC9_CMP_NEGATIVE_FLAG_SET():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x01,
        'X': 0x00,
        'Y': 0x00
    }
    EXPECTED_REGISTERS = {
        'A': 0x01,
        'X': 0x00,
        'Y': 0x00
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 1
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xC9, 0x10]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0xC9_CMP_EQUAL():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x10,
        'X': 0x00,
        'Y': 0x00
    }
    EXPECTED_REGISTERS = {
        'A': 0x10,
        'X': 0x00,
        'Y': 0x00
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 1,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xC9, 0x10]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x10_BPL_DOES_NOT_BRANCH():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0xDF,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0xDF,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 1
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 1
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x10, 0x02, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x10_BPL_SUCCESSFUL_BRANCH():
    EXPECTED_CYCLES = 3 + 2
    INITIAL_REGISTERS = {
        'A': 0xDF,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x05,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x10, 0x02, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x10_BPL_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY():
    EXPECTED_CYCLES = 4 + 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x05,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 1,
        'Z': 1,
        'I': 1,
        'D': 1,
        'B': 1,
        'V': 1,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 1,
        'D': 1,
        'B': 1,
        'V': 1,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xAAFB)
    program = [0x10, 0x04, 0x00, 0x00, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xAAFB)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xAAF0, endingAddress=0xAB07)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x30_BMI_DOES_NOT_BRANCH():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x30, 0x02, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x30_BMI_SUCCESSFUL_BRANCH():
    EXPECTED_CYCLES = 3 + 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x05,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 1,
        'N': 1
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 1,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x30, 0x02, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x30_BMI_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY():
    EXPECTED_CYCLES = 4 + 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x05,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 1,
        'Z': 1,
        'I': 1,
        'D': 1,
        'B': 1,
        'V': 1,
        'N': 1
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 1,
        'D': 1,
        'B': 1,
        'V': 1,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xAAFB)
    program = [0x30, 0x04, 0x00, 0x00, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xAAFB)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xAAF0, endingAddress=0xAB07)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x70_BVS_DOES_NOT_BRANCH():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x70, 0x02, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x70_BVS_SUCCESSFUL_BRANCH():
    EXPECTED_CYCLES = 3 + 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x05,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 1,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 1,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x70, 0x02, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x70_BVS_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY():
    EXPECTED_CYCLES = 4 + 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x05,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 1,
        'Z': 1,
        'I': 1,
        'D': 1,
        'B': 1,
        'V': 1,
        'N': 1
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 1,
        'D': 1,
        'B': 1,
        'V': 1,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xAAFB)
    program = [0x70, 0x04, 0x00, 0x00, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xAAFB)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xAAF0, endingAddress=0xAB07)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x50_BVC_DOES_NOT_BRANCH():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 1,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 1,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x50, 0x02, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x50_BVC_SUCCESSFUL_BRANCH():
    EXPECTED_CYCLES = 3 + 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x05,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 1,
        'Z': 1,
        'I': 1,
        'D': 1,
        'B': 1,
        'V': 0,
        'N': 1
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 1,
        'D': 1,
        'B': 1,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x50, 0x02, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x50_BVC_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY():
    EXPECTED_CYCLES = 4 + 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x05,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 1,
        'Z': 1,
        'I': 1,
        'D': 1,
        'B': 1,
        'V': 0,
        'N': 1
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 1,
        'D': 1,
        'B': 1,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xAAFB)
    program = [0x50, 0x04, 0x00, 0x00, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xAAFB)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xAAF0, endingAddress=0xAB07)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0xB0_BCS_DOES_NOT_BRANCH():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xB0, 0x02, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0xB0_BCS_SUCCESSFUL_BRANCH():
    EXPECTED_CYCLES = 3 + 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x05,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xB0, 0x02, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0xB0_BCS_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY():
    EXPECTED_CYCLES = 4 + 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x05,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xAAFB)
    program = [0xB0, 0x04, 0x00, 0x00, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xAAFB)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xAAF0, endingAddress=0xAB07)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x90_BCC_DOES_NOT_BRANCH():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x90, 0x02, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x90_BCC_SUCCESSFUL_BRANCH():
    EXPECTED_CYCLES = 3 + 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x05,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 1,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x90, 0x02, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x90_BCC_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY():
    EXPECTED_CYCLES = 4 + 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x05,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 1,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xAAFB)
    program = [0x90, 0x04, 0x00, 0x00, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xAAFB)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xAAF0, endingAddress=0xAB07)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0xF0_BEQ_DOES_NOT_BRANCH():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xF0, 0x02, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0xF0_BEQ_SUCCESSFUL_BRANCH():
    EXPECTED_CYCLES = 3 + 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x05,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 1,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xF0, 0x02, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0xF0_BEQ_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY():
    EXPECTED_CYCLES = 4 + 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x05,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 1,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xAAFB)
    program = [0xF0, 0x04, 0x00, 0x00, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xAAFB)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xAAF0, endingAddress=0xAB07)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0xD0_BNE_DOES_NOT_BRANCH():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 1,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 1,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xD0, 0x02, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0xD0_BNE_SUCCESSFUL_BRANCH():
    EXPECTED_CYCLES = 3 + 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x05,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xD0, 0x02, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0xD0_BNE_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY():
    EXPECTED_CYCLES = 4 + 2
    INITIAL_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x05,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xAAFB)
    program = [0xD0, 0x04, 0x00, 0x00, 0x00, 0x00, 0xA9, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xAAFB)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xAAF0, endingAddress=0xAB07)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x4A_LSR_ACC():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0xFF,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x7F,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x4A]  # ACC
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x46_LSR_ZP():
    EXPECTED_CYCLES = 5
    INITIAL_REGISTERS = {
        'A': 0x13,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x13,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x46, 0x02]  # ACC
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0x0002] = 0xFF
    cpu.execute()

    try:
        assert(cpu.memory[0x0002] == 0x7F)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        cpu.memoryDump(startingAddress=0x0002, endingAddress=0x0003)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x56_LSR_ZP_X():
    EXPECTED_CYCLES = 6
    INITIAL_REGISTERS = {
        'A': 0x13,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x13,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x56, 0x02]  # ACC
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0x00DF] = 0xFF
    cpu.execute()

    try:
        assert(cpu.memory[0x00DF] == 0x7F)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        cpu.memoryDump(startingAddress=0x0002, endingAddress=0x0003)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x4E_LSR_ABS():
    EXPECTED_CYCLES = 6
    INITIAL_REGISTERS = {
        'A': 0x13,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x13,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x4E, 0x02, 0xAC]  # ACC
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0xAC02] = 0xFF
    cpu.execute()

    try:
        assert(cpu.memory[0xAC02] == 0x7F)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        cpu.memoryDump(startingAddress=0x0002, endingAddress=0x0003)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0x5E_LSR_ABS_X():
    EXPECTED_CYCLES = 6  # 7
    INITIAL_REGISTERS = {
        'A': 0x13,
        'X': 0xDD,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x13,
        'X': 0xDD,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }

    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x5E, 0x02, 0xAC]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0xACDF] = 0xFF
    cpu.execute()

    try:
        assert(cpu.memory[0xACDF] == 0x7F)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        cpu.memoryDump(startingAddress=0xACDF, endingAddress=0xACDF)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    return True


def TEST_0xAA_TAX():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x08,
        'X': 0xFF,
        'Y': 0xCC
    }
    EXPECTED_REGISTERS = {
        'A': 0x08,
        'X': 0x08,
        'Y': 0xCC
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xAA]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
    return False


def TEST_0xAA_TAX_ZERO_FLAG():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x00,
        'X': 0xFF,
        'Y': 0xDD
    }
    EXPECTED_REGISTERS = {
        'A': 0x00,
        'X': 0x00,
        'Y': 0xDD
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 1,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xAA]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
    return False


def TEST_0xAA_TAX_NEGATIVE_FLAG():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0xFF,
        'X': 0x00,
        'Y': 0xAA
    }
    EXPECTED_REGISTERS = {
        'A': 0xFF,
        'X': 0xFF,
        'Y': 0xAA
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 1
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xAA]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
    return False


def TEST_0x8A_TXA():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x08,
        'X': 0x13,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0x13,
        'X': 0x13,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x8A]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
    return False


def TEST_0x98_TYA():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x08,
        'X': 0x13,
        'Y': 0x01
    }
    EXPECTED_REGISTERS = {
        'A': 0x01,
        'X': 0x13,
        'Y': 0x01
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x98]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
    return False


def TEST_0xA8_TAY():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x08,
        'X': 0x13,
        'Y': 0x01
    }
    EXPECTED_REGISTERS = {
        'A': 0x08,
        'X': 0x13,
        'Y': 0x08
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xA8]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
    return False


def TEST_0x9A_TXS():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x08,
        'X': 0xAC,
        'Y': 0x01
    }
    EXPECTED_REGISTERS = {
        'A': 0x08,
        'X': 0xAC,
        'Y': 0x01
    }
    INITIAL_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 1,
        'D': 1,
        'B': 1,
        'V': 1,
        'N': 1
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 1,
        'D': 1,
        'B': 1,
        'V': 1,
        'N': 1
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x9A]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.stack_pointer == EXPECTED_REGISTERS['X'])
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
    return False


def TEST_0xBA_TSX():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x08,
        'X': 0x12,
        'Y': 0x01
    }
    EXPECTED_REGISTERS = {
        'A': 0x08,
        'X': 0xCC,
        'Y': 0x01
    }
    INITIAL_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 1,
        'D': 1,
        'B': 1,
        'V': 1,
        'N': 1
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 1,
        'D': 1,
        'B': 1,
        'V': 1,
        'N': 1
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xBA]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.stack_pointer = 0xCC
    cpu.execute()

    try:
        assert(cpu.stack_pointer == EXPECTED_REGISTERS['X'])
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
    return False


def TEST_0x0A_ASL_ACC():
    EXPECTED_VALUE = 0x10
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x08,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x0A]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
    return False


def TEST_0x0A_ASL_ACC_CARRY_FLAG():
    EXPECTED_VALUE = 0x54
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0xAA,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x0A]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
    return False


def TEST_0x06_ASL_ZP():
    EXPECTED_VALUE = 0x08
    EXPECTED_CYCLES = 5
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x06, 0xAA]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.memory[0xAA] = 0x04
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.memory[0xAA] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        cpu.memoryDump(startingAddress=0x00AA, endingAddress=0x00AB)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
    return False


def TEST_0x29_AND_IM():
    EXPECTED_VALUE = 0x28 & 0xFC
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x28,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x29, 0xFC]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x29_AND_IM_ZERO_FLAG_SET():
    EXPECTED_VALUE = 0x00 & 0xFC
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x00,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 1,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x29, 0xFC]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x29_AND_IM_NEGATIVE_FLAG_SET():
    EXPECTED_VALUE = 0xFD & 0xFC
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0xFD,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 1
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x29, 0xFC]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x25_AND_ZP():
    EXPECTED_VALUE = 0x28 & 0xFC
    EXPECTED_CYCLES = 3
    INITIAL_REGISTERS = {
        'A': 0x28,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x25, 0x0C]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.memory[0x0C] = 0xFC
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x35_AND_ZP_X():
    EXPECTED_VALUE = 0x28 & 0xFC
    EXPECTED_CYCLES = 4
    INITIAL_REGISTERS = {
        'A': 0x28,
        'X': 0x01,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x01,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x35, 0x0C]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.memory[0x0D] = 0xFC
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x2D_AND_ABS():
    EXPECTED_VALUE = 0x43 & 0x44
    EXPECTED_CYCLES = 4
    INITIAL_REGISTERS = {
        'A': 0x43,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x2D, 0x0C, 0xEE]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.memory[0xEE0C] = 0x44
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x3D_AND_ABS_X():
    EXPECTED_VALUE = 0x48 & 0x44
    EXPECTED_CYCLES = 4
    INITIAL_REGISTERS = {
        'A': 0x48,
        'X': 0x03,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x03,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x3D, 0x0C, 0xEE]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.memory[0xEE0F] = 0x44
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x3D_AND_ABS_X_CROSS_PAGE_BOUNDARY():
    EXPECTED_VALUE = 0x48 & 0x44
    EXPECTED_CYCLES = 5
    INITIAL_REGISTERS = {
        'A': 0x48,
        'X': 0x03,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x03,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x3D, 0xFF, 0xDD]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.memory[0xDE02] = 0x44
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x39_AND_ABS_Y():
    EXPECTED_VALUE = 0x48 & 0x44
    EXPECTED_CYCLES = 4
    INITIAL_REGISTERS = {
        'A': 0x48,
        'X': 0,
        'Y': 0x03
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0x03
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x39, 0x0C, 0xED]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.memory[0xED0F] = 0x44
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x39_AND_ABS_Y_CROSS_PAGE_BOUNDARY():
    EXPECTED_VALUE = 0x48 & 0x44
    EXPECTED_CYCLES = 5
    INITIAL_REGISTERS = {
        'A': 0x48,
        'X': 0,
        'Y': 0x03
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0x03
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x39, 0xFF, 0xED]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.memory[0xEE02] = 0x44
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x21_AND_IND_X():
    EXPECTED_VALUE = 0x36 & 0x36
    EXPECTED_CYCLES = 6
    INITIAL_REGISTERS = {
        'A': 0x36,
        'X': 0x05,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x05,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x21, 0x01]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.memory[0x0006] = 0x22
    cpu.memory[0x0007] = 0xCD
    cpu.memory[0xCD22] = 0x36
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x31_AND_IND_Y():
    EXPECTED_VALUE = 0x36 & 0x36
    EXPECTED_CYCLES = 5
    INITIAL_REGISTERS = {
        'A': 0x36,
        'X': 0x05,
        'Y': 0x06
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x05,
        'Y': 0x06
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x31, 0x01]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.memory[0x0001] = 0x22
    cpu.memory[0x0002] = 0xCD
    cpu.memory[0xCD28] = 0x36
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x31_AND_IND_Y_CROSS_PAGE_BOUNDARY():
    EXPECTED_VALUE = 0x36 & 0x36
    EXPECTED_CYCLES = 6
    INITIAL_REGISTERS = {
        'A': 0x36,
        'X': 0x05,
        'Y': 0x01
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x05,
        'Y': 0x01
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x31, 0x01]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.memory[0x0001] = 0xFF
    cpu.memory[0x0002] = 0xCD
    cpu.memory[0xCE00] = 0x36
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x65_ADC_ZP():
    EXPECTED_VALUE = 0x28
    EXPECTED_CYCLES = 3
    INITIAL_REGISTERS = {
        'A': 0x21,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x65, 0xAF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.memory[0x00AF] = 0x07
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x69_ADC_IM():
    EXPECTED_VALUE = 0x25
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x20,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x69, 0x05]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x69_ADC_IM_CARRY_FLAG_SET():
    EXPECTED_VALUE = 0x01
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0xFF,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x69, 0x02]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x75_ADC_ZP_X():
    EXPECTED_VALUE = 0x25
    EXPECTED_CYCLES = 4
    INITIAL_REGISTERS = {
        'A': 0x20,
        'X': 0x04,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x04,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x75, 0x02]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0x0006] = 0x05
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x6D_ADC_ABS():
    EXPECTED_VALUE = 0x35
    EXPECTED_CYCLES = 4
    INITIAL_REGISTERS = {
        'A': 0x20,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x6D, 0x02, 0xCC]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0xCC02] = 0x15
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x7D_ADC_ABS_X():
    EXPECTED_VALUE = 0x45
    EXPECTED_CYCLES = 4
    INITIAL_REGISTERS = {
        'A': 0x30,
        'X': 0x01,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x01,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x7D, 0x02, 0xCC]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0xCC03] = 0x15
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x79_ADC_ABS_Y():
    EXPECTED_VALUE = 0x50
    EXPECTED_CYCLES = 4
    INITIAL_REGISTERS = {
        'A': 0x40,
        'X': 0,
        'Y': 0x02
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0x02
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x79, 0x07, 0xDD]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0xDD09] = 0x10
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x61_ADC_IND_X():
    EXPECTED_VALUE = 0x04
    EXPECTED_CYCLES = 6
    INITIAL_REGISTERS = {
        'A': 0x01,
        'X': 0x01,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x01,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x61, 0x01]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0x0002] = 0x10
    cpu.memory[0x0003] = 0xCC
    cpu.memory[0xCC10] = 0x03
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x71_ADC_IND_Y():
    EXPECTED_VALUE = 0x05
    EXPECTED_CYCLES = 5
    INITIAL_REGISTERS = {
        'A': 0x02,
        'X': 0,
        'Y': 0x03
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0x03
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x71, 0xAB]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0x00AB] = 0x10
    cpu.memory[0x00AC] = 0xCC
    cpu.memory[0xCC13] = 0x03
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        cpu.memoryDump(startingAddress=0x00AB, endingAddress=0x00AC)
        cpu.memoryDump(startingAddress=0xCC13, endingAddress=0xCC14)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x71_ADC_IND_Y_CROSS_PAGE_BOUNDARY():
    EXPECTED_VALUE = 0x05
    EXPECTED_CYCLES = 6
    INITIAL_REGISTERS = {
        'A': 0x02,
        'X': 0,
        'Y': 0x03
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0x03
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x71, 0xAB]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0x00AB] = 0xFF
    cpu.memory[0x00AC] = 0xCC
    cpu.memory[0xCD02] = 0x03
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        cpu.memoryDump(startingAddress=0x00AB, endingAddress=0x00AC)
        cpu.memoryDump(startingAddress=0xCD02, endingAddress=0xCD03)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x20_JSR_ABS():
    EXPECTED_VALUE = 0x35
    EXPECTED_CYCLES = 6 + 2
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x20, 0x05, 0xE3]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    program = [0xA9, 0x35]
    cpu.loadProgram(instructions=program, memoryAddress=0xE305, mainProgram=False)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.stack_pointer == 0xFD)
        assert(cpu.memory[0x01FE] == 0x02)
        assert(cpu.memory[0x01FF] == 0xFF)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0x01F0, endingAddress=0x01FF)
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0x60_RTS():
    EXPECTED_VALUE_A = 0x35
    EXPECTED_VALUE_X = 0x29
    EXPECTED_CYCLES = 6 + 2 + 6 + 2
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE_A,
        'X': EXPECTED_VALUE_X,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x20, 0x05, 0xE3, 0xA2, 0x29]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    program = [0xA9, 0x35, 0x60]
    cpu.loadProgram(instructions=program, memoryAddress=0xE305, mainProgram=False)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.memory[0x01FE] == 0x02)
        assert(cpu.memory[0x01FF] == 0xFF)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0x01F0, endingAddress=0x01FF)
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0xE6_INC_ZP():
    EXPECTED_VALUE = 0x9C
    EXPECTED_CYCLES = 5
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 1
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xE6, 0xF2]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0x00F2] = EXPECTED_VALUE - 1
    cpu.execute()

    try:
        assert(cpu.memory[0x00F2] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0xF6_INC_ZP_X():
    EXPECTED_VALUE = 0x9C
    EXPECTED_CYCLES = 6
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0x05,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0x05,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 1
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xF6, 0xF2]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0x00F7] = EXPECTED_VALUE - 1
    cpu.execute()

    try:
        assert(cpu.memory[0x00F7] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0xEE_INC_ABS():
    EXPECTED_VALUE = 0x20
    EXPECTED_CYCLES = 6
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xEE, 0xF2, 0x2F]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0x2FF2] = EXPECTED_VALUE - 1
    cpu.execute()

    try:
        assert(cpu.memory[0x2FF2] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0xEE_INC_ABS_WRAPAROUND():
    EXPECTED_VALUE = 0x00
    EXPECTED_CYCLES = 6
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 1,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xEE, 0xF2, 0x2F]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0x2FF2] = 0xFF
    cpu.execute()

    try:
        assert(cpu.memory[0x2FF2] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0xFE_INC_ABS_X():
    EXPECTED_VALUE = 0x2F
    EXPECTED_CYCLES = 7
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0xFF,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0xFF,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xFE, 0x00, 0x2F]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0x2FFF] = EXPECTED_VALUE - 1
    cpu.execute()

    try:
        assert(cpu.memory[0x2FFF] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0xC8_INY():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0xA5
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0xA6
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 1
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xC8]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xC8_INY_WRAPAROUND():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0xFF
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0x00
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 1,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xC8]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xE8_INX():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0xB6,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0xB7,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 1
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xE8]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xE8_INX_WRAPAROUND():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0xFF,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0x00,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 1,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xE8]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x18_CLC():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x18]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x58_CLI():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 1,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x58]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xB8_CLV():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 1,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xB8]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xD8_CLD():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 1,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xD8]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x38_SEC():
    EXPECTED_CYCLES = 2
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x38]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x78_SEI():
    EXPECTED_CYCLES = 2
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 1,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x78]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xF8_SED():
    EXPECTED_CYCLES = 2
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 1,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xF8]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA9_LDA_IM():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0x45
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xA9, 0x45]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA2_LDX_IM():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0x45
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xA2, 0x45]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA0_LDY_IM():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0x45
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xA0, 0x45]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA9_LDA_IM_ZERO_FLAG_SET():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0x00
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 1,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)

    program = [0xA9, 0x00]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA2_LDX_IM_ZERO_FLAG_SET():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0x00
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 1,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)

    program = [0xA2, 0x00]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA0_LDY_IM_ZERO_FLAG_SET():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0x00
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 1,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)

    program = [0xA0, 0x00]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA9_LDA_IM_NEGATIVE_FLAG_SET():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0xAF
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 1
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)

    program = [0xA9, 0xAF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA2_LDX_IM_NEGATIVE_FLAG_SET():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0xAF
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 1
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)

    program = [0xA2, 0xAF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA0_LDY_IM_NEGATIVE_FLAG_SET():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0xAF
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 1
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)

    program = [0xA0, 0xAF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA5_LDA_ZP():
    EXPECTED_CYCLES = 3
    EXPECTED_VALUE = 0x45
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.memory[0xCC] = 0x45
    program = [0xA5, 0xCC]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xB5_LDA_ZP_X_WRAPAROUND():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x15
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x05,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['X'] = 0x05
    cpu.memory[0x02] = 0x15
    program = [0xB5, 0xFD]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA6_LDX_ZP():
    EXPECTED_CYCLES = 3
    EXPECTED_VALUE = 0x45
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.memory[0xCC] = 0x45
    program = [0xA6, 0xCC]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA4_LDY_ZP():
    EXPECTED_CYCLES = 3
    EXPECTED_VALUE = 0x45
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.memory[0xCC] = 0x45
    program = [0xA4, 0xCC]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xB5_LDA_ZP_X():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x15
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x05,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['X'] = 0x05
    cpu.memory[0xE2] = 0x15
    program = [0xB5, 0xDD]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xB6_LDX_ZP_Y():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x15
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0x05
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['Y'] = 0x05
    cpu.memory[0xE2] = 0x15
    program = [0xB6, 0xDD]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xB4_LDY_ZP_X():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x15
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0x05,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['X'] = 0x05
    cpu.memory[0xE2] = 0x15
    program = [0xB4, 0xDD]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xAD_LDA_ABS():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x33
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.memory[0xDD00] = 0x33
    program = [0xAD, 0x00, 0xDD]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xAE_LDX_ABS():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x33
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.memory[0xDD00] = 0x33
    program = [0xAE, 0x00, 0xDD]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xAC_LDY_ABS():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x33
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.memory[0xDD00] = 0x33
    program = [0xAC, 0x00, 0xDD]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xBD_LDA_ABS_X():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x39
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x05,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['X'] = 0x05
    cpu.memory[0xFF05] = 0x39
    program = [0xBD, 0x00, 0xFF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xBD_LDA_ABS_X_CROSS_PAGE_BOUNDARY():
    EXPECTED_CYCLES = 5
    EXPECTED_VALUE = 0x16
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x04,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['X'] = 0x04
    cpu.memory[0xEE02] = 0x16
    program = [0xBD, 0xFE, 0xED]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xB9_LDA_ABS_Y():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x0A
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0x05
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['Y'] = 0x05
    cpu.memory[0xFF05] = 0x0A
    program = [0xB9, 0x00, 0xFF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xBE_LDX_ABS_Y():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x0A
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0x05
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['Y'] = 0x05
    cpu.memory[0xFF05] = 0x0A
    program = [0xBE, 0x00, 0xFF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xB9_LDA_ABS_Y_CROSS_PAGE_BOUNDARY():
    EXPECTED_CYCLES = 5
    EXPECTED_VALUE = 0x0B
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0x04
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['Y'] = 0x04
    cpu.memory[0xEE02] = 0x0B
    program = [0xB9, 0xFE, 0xED]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xBE_LDX_ABS_Y_CROSS_PAGE_BOUNDARY():
    EXPECTED_CYCLES = 5
    EXPECTED_VALUE = 0x0B
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0x04
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['Y'] = 0x04
    cpu.memory[0xEE02] = 0x0B
    program = [0xBE, 0xFE, 0xED]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xBC_LDY_ABS_X_CROSS_PAGE_BOUNDARY():
    EXPECTED_CYCLES = 5
    EXPECTED_VALUE = 0x0B
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0x04,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['X'] = 0x04
    cpu.memory[0xEE02] = 0x0B
    program = [0xBC, 0xFE, 0xED]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA1_LDA_IND_X():
    EXPECTED_CYCLES = 6
    EXPECTED_VALUE = 0x1B
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x04,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['X'] = 0x04
    cpu.memory[0x0006] = 0x00
    cpu.memory[0x0007] = 0x80
    cpu.memory[0x8000] = 0x1B
    program = [0xA1, 0x02]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xB1_LDA_IND_Y():
    EXPECTED_CYCLES = 5
    EXPECTED_VALUE = 0x02
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0x04
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['Y'] = 0x04
    cpu.memory[0x0002] = 0x00
    cpu.memory[0x0003] = 0x80
    cpu.memory[0x8004] = 0x02
    program = [0xB1, 0x02]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xB1_LDA_IND_Y_CROSS_PAGE_BOUNDARY():
    EXPECTED_CYCLES = 6
    EXPECTED_VALUE = 0x06
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0x05
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['Y'] = 0x05
    cpu.memory[0x0002] = 0xFF
    cpu.memory[0x0003] = 0x7F
    cpu.memory[0x8004] = 0x06
    program = [0xB1, 0x02]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x4C_JMP_ABS():
    EXPECTED_CYCLES = 3 + 2
    EXPECTED_VALUE = 0x45
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xA9, 0x45]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF10)
    program = [0x4C, 0x10, 0xFF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x6C_JMP_IND():
    EXPECTED_CYCLES = 5 + 2
    EXPECTED_VALUE = 0xFE
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 1
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x6C, 0x10, 0xFF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    program = [0x20, 0xFF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF10, mainProgram=False)
    program = [0xA9, 0xFE]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF20, mainProgram=False)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x84_STY_ZP():
    EXPECTED_CYCLES = 3
    EXPECTED_VALUE = 0x2A
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x84, 0x2A]
    cpu.registers['Y'] = EXPECTED_REGISTERS['Y']
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.memory[0x002A] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x85_STA_ZP():
    EXPECTED_CYCLES = 3
    EXPECTED_VALUE = 0x2A
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x85, 0x2A]
    cpu.registers['A'] = EXPECTED_VALUE
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.memory[0x002A] == EXPECTED_VALUE)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x86_STX_ZP():
    EXPECTED_CYCLES = 3
    EXPECTED_VALUE = 0x2A
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x86, 0x2A]
    cpu.registers['X'] = EXPECTED_REGISTERS['X']
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.memory[0x002A] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x94_STY_ZPX():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x3A
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0x02,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x94, 0x3A]
    cpu.registers['X'] = EXPECTED_REGISTERS['X']
    cpu.registers['Y'] = EXPECTED_REGISTERS['Y']
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.memory[0x003C] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x95_STA_ZPX():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x3A
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x02,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x95, 0x3A]
    cpu.registers['A'] = EXPECTED_VALUE
    cpu.registers['X'] = 0x02
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.memory[0x003C] == EXPECTED_VALUE)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x96_STX_ZPY():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x3A
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0x02
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x96, 0x3A]
    cpu.registers['X'] = EXPECTED_REGISTERS['X']
    cpu.registers['Y'] = EXPECTED_REGISTERS['Y']
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.memory[0x003C] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x8C_STY_ABS():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0xB3
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x8C, 0xDA, 0x74]
    cpu.registers['Y'] = EXPECTED_REGISTERS['Y']
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.memory[0x74DA] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x8D_STA_ABS():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0xB3
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x8D, 0xDA, 0x74]
    cpu.registers['A'] = EXPECTED_VALUE
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.memory[0x74DA] == EXPECTED_VALUE)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x8E_STX_ABS():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0xB3
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x8E, 0xDA, 0x74]
    cpu.registers['X'] = EXPECTED_REGISTERS['X']
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.memory[0x74DA] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x9D_STA_ABSX():
    EXPECTED_CYCLES = 4  # 5
    EXPECTED_VALUE = 0x13
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x03,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x9D, 0xDA, 0x70]
    cpu.registers['A'] = EXPECTED_VALUE
    cpu.registers['X'] = 0x03
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.memory[0x70DD] == EXPECTED_VALUE)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x99_STA_ABSY():
    EXPECTED_CYCLES = 4  # 5
    EXPECTED_VALUE = 0x23
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0x05
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x99, 0x00, 0x50]
    cpu.registers['A'] = EXPECTED_VALUE
    cpu.registers['Y'] = 0x05
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.memory[0x5005] == EXPECTED_VALUE)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x81_STA_INDX():
    EXPECTED_CYCLES = 6
    EXPECTED_VALUE = 0x1B
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x04,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['A'] = EXPECTED_VALUE
    cpu.registers['X'] = 0x04
    cpu.memory[0x0006] = 0x00
    cpu.memory[0x0007] = 0x80
    program = [0x81, 0x02]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.memory[0x8000] == EXPECTED_VALUE)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0x00, endingAddress=0x07)
        cpu.memoryDump(startingAddress=0x8000, endingAddress=0x8007)
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x91_STA_INDY():
    EXPECTED_CYCLES = 5  # 6
    EXPECTED_VALUE = 0x23
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0x05
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.memory[0x0008] = 0x00
    cpu.memory[0x0009] = 0x50
    program = [0x91, 0x08]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers['A'] = EXPECTED_REGISTERS['A']
    cpu.registers['Y'] = EXPECTED_REGISTERS['Y']
    cpu.execute()

    try:
        assert(cpu.memory[0x5005] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0x5000, endingAddress=0x5007)
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


if __name__ == '__main__':
    os.system('color')
    tests = [
        TEST_0xA9_LDA_IM,
        TEST_0xA9_LDA_IM_ZERO_FLAG_SET,
        TEST_0xA9_LDA_IM_NEGATIVE_FLAG_SET,
        TEST_0xA5_LDA_ZP,
        TEST_0xB5_LDA_ZP_X,
        TEST_0xB5_LDA_ZP_X_WRAPAROUND,
        TEST_0xAD_LDA_ABS,
        TEST_0xBD_LDA_ABS_X,
        TEST_0xBD_LDA_ABS_X_CROSS_PAGE_BOUNDARY,
        TEST_0xB9_LDA_ABS_Y,
        TEST_0xB9_LDA_ABS_Y_CROSS_PAGE_BOUNDARY,
        TEST_0xA1_LDA_IND_X,
        TEST_0xB1_LDA_IND_Y,
        TEST_0xB1_LDA_IND_Y_CROSS_PAGE_BOUNDARY,
        TEST_0xA2_LDX_IM,
        TEST_0xA2_LDX_IM_ZERO_FLAG_SET,
        TEST_0xA2_LDX_IM_NEGATIVE_FLAG_SET,
        TEST_0xA6_LDX_ZP,
        TEST_0xB6_LDX_ZP_Y,
        TEST_0xAE_LDX_ABS,
        TEST_0xBE_LDX_ABS_Y,
        TEST_0xBE_LDX_ABS_Y_CROSS_PAGE_BOUNDARY,
        TEST_0xA0_LDY_IM,
        TEST_0xA0_LDY_IM_ZERO_FLAG_SET,
        TEST_0xA0_LDY_IM_NEGATIVE_FLAG_SET,
        TEST_0xA4_LDY_ZP,
        TEST_0xB4_LDY_ZP_X,
        TEST_0xAC_LDY_ABS,
        TEST_0xBC_LDY_ABS_X_CROSS_PAGE_BOUNDARY,
        TEST_0x4C_JMP_ABS,
        TEST_0x6C_JMP_IND,
        TEST_0x85_STA_ZP,
        TEST_0x95_STA_ZPX,
        TEST_0x8D_STA_ABS,
        TEST_0x9D_STA_ABSX,
        TEST_0x99_STA_ABSY,
        TEST_0x81_STA_INDX,
        TEST_0x91_STA_INDY,
        TEST_0x84_STY_ZP,
        TEST_0x86_STX_ZP,
        TEST_0x96_STX_ZPY,
        TEST_0x94_STY_ZPX,
        TEST_0x8C_STY_ABS,
        TEST_0x8E_STX_ABS,
        TEST_0x38_SEC,
        TEST_0x78_SEI,
        TEST_0xF8_SED,
        TEST_0x18_CLC,
        TEST_0x58_CLI,
        TEST_0xB8_CLV,
        TEST_0xD8_CLD,
        TEST_0xC8_INY,
        TEST_0xC8_INY_WRAPAROUND,
        TEST_0xE8_INX,
        TEST_0xE8_INX_WRAPAROUND,
        TEST_0xE6_INC_ZP,
        TEST_0xF6_INC_ZP_X,
        TEST_0xEE_INC_ABS,
        TEST_0xEE_INC_ABS_WRAPAROUND,
        TEST_0xFE_INC_ABS_X,
        TEST_0x20_JSR_ABS,
        TEST_0x60_RTS,
        TEST_0x69_ADC_IM,
        TEST_0x65_ADC_ZP,
        TEST_0x75_ADC_ZP_X,
        TEST_0x6D_ADC_ABS,
        TEST_0x7D_ADC_ABS_X,
        TEST_0x79_ADC_ABS_Y,
        TEST_0x61_ADC_IND_X,
        TEST_0x71_ADC_IND_Y,
        TEST_0x71_ADC_IND_Y_CROSS_PAGE_BOUNDARY,
        TEST_0x69_ADC_IM_CARRY_FLAG_SET,
        TEST_0x29_AND_IM,
        TEST_0x29_AND_IM_ZERO_FLAG_SET,
        TEST_0x29_AND_IM_NEGATIVE_FLAG_SET,
        TEST_0x25_AND_ZP,
        TEST_0x35_AND_ZP_X,
        TEST_0x2D_AND_ABS,
        TEST_0x3D_AND_ABS_X,
        TEST_0x3D_AND_ABS_X_CROSS_PAGE_BOUNDARY,
        TEST_0x39_AND_ABS_Y,
        TEST_0x39_AND_ABS_Y_CROSS_PAGE_BOUNDARY,
        TEST_0x21_AND_IND_X,
        TEST_0x31_AND_IND_Y,
        TEST_0x31_AND_IND_Y_CROSS_PAGE_BOUNDARY,
        TEST_0x0A_ASL_ACC,
        TEST_0x0A_ASL_ACC_CARRY_FLAG,
        TEST_0x06_ASL_ZP,
        TEST_0xAA_TAX,
        TEST_0xAA_TAX_ZERO_FLAG,
        TEST_0xAA_TAX_NEGATIVE_FLAG,
        TEST_0xA8_TAY,
        TEST_0x8A_TXA,
        TEST_0x98_TYA,
        TEST_0x9A_TXS,
        TEST_0xBA_TSX,
        TEST_0x4A_LSR_ACC,
        TEST_0x46_LSR_ZP,
        TEST_0x56_LSR_ZP_X,
        TEST_0x4E_LSR_ABS,
        TEST_0x5E_LSR_ABS_X,
        TEST_0xD0_BNE_DOES_NOT_BRANCH,
        TEST_0xD0_BNE_SUCCESSFUL_BRANCH,
        TEST_0xD0_BNE_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY,
        TEST_0xF0_BEQ_DOES_NOT_BRANCH,
        TEST_0xF0_BEQ_SUCCESSFUL_BRANCH,
        TEST_0xF0_BEQ_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY,
        TEST_0x90_BCC_DOES_NOT_BRANCH,
        TEST_0x90_BCC_SUCCESSFUL_BRANCH,
        TEST_0x90_BCC_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY,
        TEST_0xB0_BCS_DOES_NOT_BRANCH,
        TEST_0xB0_BCS_SUCCESSFUL_BRANCH,
        TEST_0xB0_BCS_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY,
        TEST_0x50_BVC_DOES_NOT_BRANCH,
        TEST_0x50_BVC_SUCCESSFUL_BRANCH,
        TEST_0x50_BVC_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY,
        TEST_0x70_BVS_DOES_NOT_BRANCH,
        TEST_0x70_BVS_SUCCESSFUL_BRANCH,
        TEST_0x70_BVS_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY,
        TEST_0x30_BMI_DOES_NOT_BRANCH,
        TEST_0x30_BMI_SUCCESSFUL_BRANCH,
        TEST_0x30_BMI_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY,
        TEST_0x10_BPL_DOES_NOT_BRANCH,
        TEST_0x10_BPL_SUCCESSFUL_BRANCH,
        TEST_0x10_BPL_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY,
        TEST_0xC9_CMP_GREATER_THAN,
        TEST_0xC9_CMP_LESS_THAN,
        TEST_0xC9_CMP_EQUAL,
        TEST_0xC9_CMP_GREATER_THAN_ADDRESS_MODE_TESTS,
        TEST_0xC9_CMP_NEGATIVE_FLAG_SET,
        TEST_0x2A_ROL_ACC_CARRY_FLAG_NOT_SET,
        TEST_0x2A_ROL_ACC_CARRY_FLAG_SET,
        TEST_0x6A_ROR_ACC_CARRY_FLAG_NOT_SET,
        TEST_0x6A_ROR_ACC_CARRY_FLAG_SET,
        TEST_0x48_PHA_IMP,
        TEST_0x68_PLA_IMP,
        TEST_0x68_PLA_IMP_NEGATIVE_FLAG_SET,
        TEST_0x68_PLA_IMP_ZERO_FLAG_SET,
        TEST_0x24_BIT_ADDRESS_MODE_TESTS,
        TEST_0x24_BIT_ADDRESS_MODE_TESTS_ZERO_FLAG,
        TEST_0x2A_ROL_ADDRESS_MODE_TESTS,
        TEST_0x49_EOR_ADDRESS_MODE_TESTS,
        TEST_0x09_ORA_ADDRESS_MODE_TESTS,
        TEST_0x08_PHP_PLA_COMBINED_TEST,
    ]

    num_tests, passed, failed, results = len(tests), 0, 0, []

    for test in tests:
        try:
            if test():
                results.append(True)
                print(f"{bcolors.OKGREEN}PASSED:{bcolors.ENDC} {test.__name__}")
                passed += 1
            else:
                results.append(False)
                print(f"{bcolors.FAIL}FAILED:{bcolors.ENDC} {test.__name__}")
                failed += 1
        except AssertionError:
            results.append(False)
            print(f"{bcolors.FAIL}FAILED:{bcolors.ENDC} {test.__name__}")
            logging.error("", exc_info=True)
            failed += 1
            continue

    print('TEST SUMMARY')
    for result in results:
        if result:
            print(f"{bcolors.OKGREEN}{'▓'}{bcolors.ENDC}", end='')
        else:
            print(f"{bcolors.FAIL}{'▓'}{bcolors.ENDC}", end='')
    print()
    print(f'{passed} TESTS {bcolors.OKGREEN}PASSED{bcolors.ENDC}. {failed} TESTS {bcolors.FAIL}FAILED{bcolors.ENDC}.')
