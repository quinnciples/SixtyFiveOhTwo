from testing_modules import bcolors
from testing_modules import generateProgram
import sys
sys.path.insert(0, '..\\SixtyFiveOhTwo')
from cpu6502 import CPU6502


def TEST_0x60_RTS():
    TEST_NAME = 'TEST_0x60_RTS'
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
    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    label = 'IMP'
    print(f'\tTesting {label}... ', end='')
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x20, 0x05, 0xE3, 0xA2, 0x29]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    program = [0xA9, 0x35, 0x60, 0x00]
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
        print(f'{bcolors.OKGREEN}PASSED{bcolors.ENDC}', end='\n')
        return True
    except AssertionError:
        print(f'{bcolors.FAIL}FAILED{bcolors.ENDC}', end='\n')
        cpu.printLog()
        cpu.memoryDump(startingAddress=0x01F0, endingAddress=0x01FF)
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def RTS_tests():
    tests = [
        TEST_0x60_RTS,
    ]
    results = []
    for test in tests:
        results.append(test())
    return results


if __name__ == '__main__':
    RTS_tests()
