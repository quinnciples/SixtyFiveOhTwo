import os
import sys
sys.path.insert(0, '..\\SixtyFiveOhTwo')
from SixtyFiveOhTwo import CPU6502


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


def TEST_0xA9_LDA_IM():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0x45
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0,
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
    # cpu.printLog()
    # cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)

    assert(EXPECTED_CYCLES == cpu.cycles - 1)
    assert(cpu.registers == EXPECTED_REGISTERS)
    # print(inspect.currentframe().f_code.co_name + ' PASSED.')
    return True


def TEST_0xA9_LDA_IM_ZERO_FLAG_SET():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0x00
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0,
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
    # cpu.printLog()
    # cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)

    assert(EXPECTED_CYCLES == cpu.cycles - 1)
    assert(cpu.registers == EXPECTED_REGISTERS)
    # print(inspect.currentframe().f_code.co_name + ' PASSED.')


def TEST_0xA9_LDA_IM_NEGATIVE_FLAG_SET():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0xAF
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0,
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
    # cpu.printLog()
    # cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)

    assert(EXPECTED_CYCLES == cpu.cycles - 1)
    assert(cpu.registers == EXPECTED_REGISTERS)
    # print(inspect.currentframe().f_code.co_name + ' PASSED.')


if __name__ == '__main__':
    os.system('color')
    tests = [
        TEST_0xA9_LDA_IM
        , TEST_0xA9_LDA_IM_ZERO_FLAG_SET
        , TEST_0xA9_LDA_IM_NEGATIVE_FLAG_SET
    ]

    for test in tests:
        try:
            test()
            print(f"{bcolors.OKGREEN}PASSED:{bcolors.ENDC} {test.__name__}")
        except Exception:
            print(f"{bcolors.FAIL}FAILED:{bcolors.ENDC} {test.__name__}")
