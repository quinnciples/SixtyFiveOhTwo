from testing_modules import bcolors
from testing_modules import generateProgram
import sys
sys.path.insert(0, '..\\SixtyFiveOhTwo')
from cpu6502 import CPU6502


def TEST_0x9A_TXS():
    TEST_NAME = 'TEST_0x9A_TXS'
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0x08,
        'X': 0x12,
        'Y': 0x01
    }
    EXPECTED_REGISTERS = {
        'A': 0x08,
        'X': 0x12,
        'Y': 0x01
    }
    INITIAL_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 1,
        'D': 0,
        'B': 1,
        'V': 0,
        'N': 1
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 1,
        'D': 0,
        'B': 1,
        'V': 0,
        'N': 1
    }
    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    label = 'REL'
    print(f'\tTesting {label}... ', end='')
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x9A]
    cpu.load_program(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.stack_pointer = 0x0C
    cpu.execute()

    try:
        assert(cpu.stack_pointer == EXPECTED_REGISTERS['X'])
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        print(f'{bcolors.OKGREEN}PASSED{bcolors.ENDC}', end='\n')
        return True
    except AssertionError:
        print(f'{bcolors.FAIL}FAILED{bcolors.ENDC}', end='\n')
        cpu.print_log()
        cpu.memory_dump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        print(f'Expected Registers: {EXPECTED_REGISTERS}')
        raise
    return False


def TXS_tests():
    tests = [
        TEST_0x9A_TXS,
    ]
    results = []
    for test in tests:
        results.append(test())
    return results


if __name__ == '__main__':
    TXS_tests()
