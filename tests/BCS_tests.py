from testing_modules import bcolors
from testing_modules import generateProgram
import sys
sys.path.insert(0, '..\\SixtyFiveOhTwo')
from cpu6502 import CPU6502


def TEST_0xB0_BCS_DOES_NOT_BRANCH():
    TEST_NAME = 'TEST_0xB0_BCS_DOES_NOT_BRANCH'
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

    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    label = 'REL'
    print(f'\tTesting {label}... ', end='')
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
        print(f'{bcolors.FAIL}FAILED{bcolors.ENDC}', end='\n')
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    print(f'{bcolors.OKGREEN}PASSED{bcolors.ENDC}', end='\n')
    return True


def TEST_0xB0_BCS_SUCCESSFUL_BRANCH():
    TEST_NAME = 'TEST_0xB0_BCS_SUCCESSFUL_BRANCH'
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

    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    label = 'REL'
    print(f'\tTesting {label}... ', end='')
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
        print(f'{bcolors.FAIL}FAILED{bcolors.ENDC}', end='\n')
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    print(f'{bcolors.OKGREEN}PASSED{bcolors.ENDC}', end='\n')
    return True


def TEST_0xB0_BCS_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY():
    TEST_NAME = 'TEST_0xB0_BCS_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY'
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

    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    label = 'REL'
    print(f'\tTesting {label}... ', end='')
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
        print(f'{bcolors.FAIL}FAILED{bcolors.ENDC}', end='\n')
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xAAF0, endingAddress=0xAB07)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
        return False
    print(f'{bcolors.OKGREEN}PASSED{bcolors.ENDC}', end='\n')
    return True


def BCS_tests():
    tests = [
        TEST_0xB0_BCS_DOES_NOT_BRANCH,
        TEST_0xB0_BCS_SUCCESSFUL_BRANCH,
        TEST_0xB0_BCS_SUCCESSFUL_BRANCH_CROSS_PAGE_BOUNDARY,
    ]
    results = []
    for test in tests:
        results.append(test())
    return results


if __name__ == '__main__':
    BCS_tests()
