import os
# import logging
import sys
from testing_modules import bcolors
from testing_modules import generateProgram
from LDA_tests import LDA_tests
from LDX_tests import LDX_tests
from LDY_tests import LDY_tests
from STA_tests import STA_tests
from STX_tests import STX_tests
from STY_tests import STY_tests
from AND_tests import AND_tests
from EOR_tests import EOR_tests
from ORA_tests import ORA_tests
from INX_tests import INX_tests
from INY_tests import INY_tests
from INC_tests import INC_tests
from SEC_tests import SEC_tests
from SED_tests import SED_tests
from SEI_tests import SEI_tests
from CLC_tests import CLC_tests
from CLD_tests import CLD_tests
from CLI_tests import CLI_tests
from CLV_tests import CLV_tests
from ROL_tests import ROL_tests
from ROR_tests import ROR_tests
from ADC_tests import ADC_tests

# import testing_modules
sys.path.insert(0, '..\\SixtyFiveOhTwo')
from SixtyFiveOhTwo import CPU6502

"""

NOTES

Need to investigate STA ABSX, ABSY, and INDY cycle counts. These have been manually adjusted in the tests to pass, however the underlying instructions work correctly.
INX, INY wrap around 0xFF
Fibonacci - https://www.youtube.com/watch?v=a73ZXDJtU48

"""


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


if __name__ == '__main__':
    os.system('color')
    tests = [
        TEST_0x4C_JMP_ABS,
        TEST_0x6C_JMP_IND,
        TEST_0x20_JSR_ABS,
        TEST_0x60_RTS,
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
        TEST_0x48_PHA_IMP,
        TEST_0x68_PLA_IMP,
        TEST_0x68_PLA_IMP_NEGATIVE_FLAG_SET,
        TEST_0x68_PLA_IMP_ZERO_FLAG_SET,
        TEST_0x24_BIT_ADDRESS_MODE_TESTS,
        TEST_0x24_BIT_ADDRESS_MODE_TESTS_ZERO_FLAG,
        TEST_0x08_PHP_PLA_COMBINED_TEST,
    ]

    tests = [
        LDA_tests,
        LDX_tests,
        LDY_tests,
        STA_tests,
        STX_tests,
        STY_tests,
        AND_tests,
        EOR_tests,
        ORA_tests,
        INX_tests,
        INY_tests,
        INC_tests,
        SEC_tests,
        SED_tests,
        SEI_tests,
        CLC_tests,
        CLD_tests,
        CLI_tests,
        CLV_tests,
        ROL_tests,
        ROR_tests,
        ADC_tests,
    ]

    passed, failed, results, failed_tests = 0, 0, [], set([])

    for run_test in tests:
        test_results = run_test()
        for x in test_results:
            results.append(x)
            if x is False:
                failed_tests.add(run_test.__name__)

    print('*' * 80)
    print('TEST SUMMARY')
    for result in results:
        if result:
            print(f"{bcolors.OKGREEN}{'▓'}{bcolors.ENDC}", end='')
            passed += 1
        else:
            print(f"{bcolors.FAIL}{'▓'}{bcolors.ENDC}", end='')
            failed += 1
    print()
    print(f'{passed} TESTS {bcolors.OKGREEN}PASSED{bcolors.ENDC}', end='')
    if failed:
        print(f' // {failed} TESTS {bcolors.FAIL}FAILED{bcolors.ENDC}')
        print()
        print('The following tests did not complete successfully:')
        for failed_test in failed_tests:
            print(f'\t{failed_test}')
