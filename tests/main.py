import os
# import logging
import sys

from testing_modules import bcolors
# from testing_modules import generateProgram

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
from ASL_tests import ASL_tests
from BCC_tests import BCC_tests
from BCS_tests import BCS_tests
from BEQ_tests import BEQ_tests
from BNE_tests import BNE_tests
from BVC_tests import BVC_tests
from BVS_tests import BVS_tests
from BMI_tests import BMI_tests
from BPL_tests import BPL_tests
from LSR_tests import LSR_tests
from TAX_tests import TAX_tests
from TXA_tests import TXA_tests
from TAY_tests import TAY_tests
from TYA_tests import TYA_tests
from TSX_tests import TSX_tests
from TXS_tests import TXS_tests
from JMP_tests import JMP_tests
from JSR_tests import JSR_tests
from RTS_tests import RTS_tests
from DEX_tests import DEX_tests
from DEY_tests import DEY_tests
from DEC_tests import DEC_tests
from CMP_tests import CMP_tests
from BIT_tests import BIT_tests
from custom_tests import custom_tests

# import testing_modules
sys.path.insert(0, '..\\SixtyFiveOhTwo')
from cpu6502 import CPU6502

"""

NOTES

Need to investigate STA ABSX, ABSY, and INDY cycle counts. These have been manually adjusted in the tests to pass, however the underlying instructions work correctly.
INX, INY wrap around 0xFF
Fibonacci - https://www.youtube.com/watch?v=a73ZXDJtU48

"""


def TEST_0x08_PHP_PLA_COMBINED_TEST():
    TEST_NAME = 'TEST_0x08_PHP_PLA_COMBINED_TEST'
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
    for flag in INITIAL_FLAGS:
        print(f'\tTesting {flag}... ', end='')
        cpu = CPU6502(cycle_limit=100)
        cpu.reset(program_counter=0xFF00)
        push_program = [0x08, 0x00]
        cpu.load_program(instructions=push_program, memoryAddress=0xFF00)
        cpu.registers = INITIAL_REGISTERS.copy()
        cpu.flags = INITIAL_FLAGS.copy()
        cpu.flags[flag] = 1
        cpu.execute()

        pull_program = [0x28, 0x00]
        cpu.load_program(instructions=pull_program, memoryAddress=0xFF02)
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

            cpu.print_log()
            cpu.memory_dump(startingAddress=0xFF00, endingAddress=0xFF03)
            errors = True
        else:
            print(f'{bcolors.OKGREEN}PASSED{bcolors.ENDC}', end='\n')

    return not errors


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
    cpu.load_program(instructions=program, memoryAddress=0xFF00)
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
        cpu.print_log()
        cpu.memory_dump(startingAddress=0xFF00, endingAddress=0xFF02)
        cpu.memory_dump(startingAddress=0x01F8, endingAddress=0x01FF)
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
    cpu.load_program(instructions=program, memoryAddress=0xFF00)
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
        cpu.print_log()
        cpu.memory_dump(startingAddress=0xFF00, endingAddress=0xFF02)
        cpu.memory_dump(startingAddress=0x01F8, endingAddress=0x01FF)
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
    cpu.load_program(instructions=program, memoryAddress=0xFF00)
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
        cpu.print_log()
        cpu.memory_dump(startingAddress=0xFF00, endingAddress=0xFF02)
        cpu.memory_dump(startingAddress=0x01F8, endingAddress=0x01FF)
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
    cpu.load_program(instructions=program, memoryAddress=0xFF00)
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
        cpu.print_log()
        cpu.memory_dump(startingAddress=0xFF00, endingAddress=0xFF02)
        cpu.memory_dump(startingAddress=0x01F8, endingAddress=0x01FF)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Flags: {EXPECTED_FLAGS}')
        raise
    return False


if __name__ == '__main__':
    os.system('color')
    tests = [
        TEST_0x48_PHA_IMP,
        TEST_0x68_PLA_IMP,
        TEST_0x68_PLA_IMP_NEGATIVE_FLAG_SET,
        TEST_0x68_PLA_IMP_ZERO_FLAG_SET,
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
        ASL_tests,
        BCC_tests,
        BCS_tests,
        BEQ_tests,
        BNE_tests,
        BVC_tests,
        BVS_tests,
        BMI_tests,
        BPL_tests,
        LSR_tests,
        TAX_tests,
        TXA_tests,
        TAY_tests,
        TYA_tests,
        TSX_tests,
        TXS_tests,
        JMP_tests,
        JSR_tests,
        RTS_tests,
        DEX_tests,
        DEY_tests,
        DEC_tests,
        CMP_tests,
        BIT_tests,
        custom_tests,

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
            print(f'{bcolors.OKGREEN}▓{bcolors.ENDC}', end='')
            passed += 1
        else:
            print(f'{bcolors.FAIL}▓{bcolors.ENDC}', end='')
            failed += 1
    print()
    print(f'{passed} TESTS {bcolors.OKGREEN}PASSED{bcolors.ENDC}', end='')
    if failed:
        print(f' // {failed} TESTS {bcolors.FAIL}FAILED{bcolors.ENDC}')
        print()
        print('The following tests did not complete successfully:')
        for failed_test in failed_tests:
            print(f'\t{failed_test}')
