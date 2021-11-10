from testing_modules import bcolors
from testing_modules import generateProgram
import sys
sys.path.insert(0, '..\\SixtyFiveOhTwo')
from cpu6502 import CPU6502


def TEST_0x4C_JMP_ABS():
    TEST_NAME = 'TEST_0x4C_JMP_ABS'
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
        'U': 1,
        'V': 0,
        'N': 0
    }
    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    label = 'ABS'
    print(f'\tTesting {label}... ', end='')
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xA9, 0x45]
    cpu.load_program(instructions=program, memoryAddress=0xFF10)
    program = [0x4C, 0x10, 0xFF]
    cpu.load_program(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        print(f'{bcolors.OKGREEN}PASSED{bcolors.ENDC}', end='\n')
        return True
    except AssertionError:
        print(f'{bcolors.FAIL}FAILED{bcolors.ENDC}', end='\n')
        cpu.print_log()
        cpu.memory_dump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x6C_JMP_IND():
    TEST_NAME = 'TEST_0x6C_JMP_IND'
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
        'U': 1,
        'V': 0,
        'N': 1
    }
    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    label = 'IND'
    print(f'\tTesting {label}... ', end='')
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x6C, 0x10, 0xFF]
    cpu.load_program(instructions=program, memoryAddress=0xFF00)
    program = [0x20, 0xFF]
    cpu.load_program(instructions=program, memoryAddress=0xFF10, mainProgram=False)
    program = [0xA9, 0xFE]
    cpu.load_program(instructions=program, memoryAddress=0xFF20, mainProgram=False)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        print(f'{bcolors.OKGREEN}PASSED{bcolors.ENDC}', end='\n')
        return True
    except AssertionError:
        print(f'{bcolors.FAIL}FAILED{bcolors.ENDC}', end='\n')
        cpu.print_log()
        cpu.memory_dump(startingAddress=0xFF00, endingAddress=0xFF02)
        cpu.memory_dump(startingAddress=0xFF10, endingAddress=0xFF12)
        cpu.memory_dump(startingAddress=0xFF20, endingAddress=0xFF22)
        raise
    return False


def JMP_tests():
    tests = [
        TEST_0x4C_JMP_ABS,
        TEST_0x6C_JMP_IND,
    ]
    results = []
    for test in tests:
        results.append(test())
    return results


if __name__ == '__main__':
    JMP_tests()
