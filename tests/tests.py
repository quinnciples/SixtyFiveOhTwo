import os
import logging
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

    try:
        assert(EXPECTED_CYCLES == cpu.cycles - 1)
        assert(cpu.registers == EXPECTED_REGISTERS)
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

    try:
        assert(EXPECTED_CYCLES == cpu.cycles - 1)
        assert(cpu.registers == EXPECTED_REGISTERS)
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

    try:
        assert(EXPECTED_CYCLES == cpu.cycles - 1)
        assert(cpu.registers == EXPECTED_REGISTERS)
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
    cpu.memory[0xCC] = 0x45
    program = [0xA5, 0xCC]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()
    # cpu.printLog()
    # cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)

    try:
        assert(EXPECTED_CYCLES == cpu.cycles - 1)
        assert(cpu.registers == EXPECTED_REGISTERS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA5_LDA_ZP_X():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x15
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x05,
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
    cpu.registers['X'] = 0x05
    cpu.memory[0xE2] = 0x15
    program = [0xB5, 0xDD]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()
    # cpu.printLog()
    # cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)

    try:
        assert(EXPECTED_CYCLES == cpu.cycles - 1)
        assert(cpu.registers == EXPECTED_REGISTERS)
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
    cpu.memory[0xDD00] = 0x33
    program = [0xAD, 0x00, 0xDD]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(EXPECTED_CYCLES == cpu.cycles - 1)
        assert(cpu.registers == EXPECTED_REGISTERS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


if __name__ == '__main__':
    os.system('color')
    tests = [
        TEST_0xA9_LDA_IM
        , TEST_0xA9_LDA_IM_ZERO_FLAG_SET
        , TEST_0xA9_LDA_IM_NEGATIVE_FLAG_SET
        , TEST_0xA5_LDA_ZP
        , TEST_0xA5_LDA_ZP_X
        , TEST_0xAD_LDA_ABS
    ]

    for test in tests:
        try:
            if test():
                print(f"{bcolors.OKGREEN}PASSED:{bcolors.ENDC} {test.__name__}")
            else:
                print(f"{bcolors.FAIL}FAILED:{bcolors.ENDC} {test.__name__}")
        except AssertionError:
            print(f"{bcolors.FAIL}FAILED:{bcolors.ENDC} {test.__name__}")
            logging.error("", exc_info=True)
